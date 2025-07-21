import weaviate
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. RAG functionality will be limited.")
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from datetime import datetime
import time
from .search_service import SearchService
from backend.services.langchain_sql_service import langchain_sql_service
from weaviate.connect import ConnectionParams
from weaviate.collections.classes.config import DataType, Property, Vectorizers, Configure
from weaviate.collections.classes.filters import Filter
from weaviate.classes.data import DataObject
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Global singleton instance
_rag_service_instance = None

# Get chunking parameters from environment variables with defaults
DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
DEFAULT_OVERLAP = int(os.getenv("OVERLAP", "50"))
# Force CPU usage for RAG to avoid GPU contention with LLM
RAG_USE_CPU = os.getenv("RAG_USE_CPU", "true").lower() == "true"
# Enable internet search
ENABLE_INTERNET_SEARCH = os.getenv("ENABLE_INTERNET_SEARCH", "true").lower() == "true"
# Weaviate configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
COLLECTION_NAME = "Documents"

# Embedding model configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/e5-small")
# Available models: intfloat/e5-small, intfloat/e5-large, sentence-transformers/all-MiniLM-L6-v2

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks of chunk_size with overlap."""
    # Use environment variables if not specified
    if chunk_size is None:
        chunk_size = DEFAULT_CHUNK_SIZE
    if overlap is None:
        overlap = DEFAULT_OVERLAP
        
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

class RAGService:
    def __new__(cls):
        global _rag_service_instance
        if _rag_service_instance is None:
            logger.info("🆕 Creating new RAGService instance (singleton)")
            _rag_service_instance = super(RAGService, cls).__new__(cls)
        else:
            logger.info("♻️  Reusing existing RAGService instance (singleton)")
        return _rag_service_instance
    
    def __init__(self):
        # Only initialize if not already initialized
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Initialize Weaviate client lazily (will connect when first used)
        self.client = None
        logger.info(f"🔍 RAG service initialized (Weaviate client will connect when needed)")
        
        # Load the embedding model
        logger.info(f"🔄 Loading embedding model: {EMBEDDING_MODEL}...")
        # Use CPU by default to avoid GPU/Metal contention with LLM
        device = 'cpu' if RAG_USE_CPU else 'auto'
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            # Load the specified embedding model
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL, device=device)
            logger.info(f"✅ Using embedding model: {EMBEDDING_MODEL}")
        else:
            self.embedding_model = None
            logger.warning("⚠️  sentence-transformers not available, embedding functionality disabled")
        logger.info(f"✅ Embedding model loaded ({device} mode)")
        logger.info(f"📊 Chunking parameters: chunk_size={DEFAULT_CHUNK_SIZE}, overlap={DEFAULT_OVERLAP}")
        
        # Initialize search service if internet search is enabled
        self.search_service = None
        if ENABLE_INTERNET_SEARCH:
            try:
                logger.info("🌐 Initializing internet search service...")
                self.search_service = SearchService()
                logger.info("✅ Internet search service initialized")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize search service: {e}")
                self.search_service = None

    def _ensure_weaviate_connected(self):
        """Ensure Weaviate client is connected, connecting if necessary."""
        if self.client is None:
            logger.info(f"🔍 Connecting to Weaviate at {WEAVIATE_URL}...")
            try:
                # Parse the URL to extract host and port
                parsed_url = urlparse(WEAVIATE_URL)
                host = parsed_url.hostname
                port = parsed_url.port or 8080
                secure = parsed_url.scheme == 'https'
                
                self.client = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    http_secure=secure,
                    grpc_host=host,
                    grpc_port=50051,
                    grpc_secure=secure,
                    skip_init_checks=True
                )
                logger.info("✅ Weaviate client connected successfully")
                # Create collection if it doesn't exist
                self._create_collection_if_not_exists()
            except Exception as e:
                logger.error(f"❌ Failed to connect to Weaviate: {e}")
                raise

    def _create_collection_if_not_exists(self):
        """Create the Documents collection if it doesn't exist."""
        try:
            # Check if collection exists (v4 API returns dict with collection names as keys)
            collections = self.client.collections.list_all()
            collection_exists = COLLECTION_NAME in collections
            
            if collection_exists:
                logger.info(f"✅ Collection '{COLLECTION_NAME}' already exists")
                return
            
            logger.info(f"📝 Creating Weaviate collection: {COLLECTION_NAME}")
            properties = [
                Property(name="content", data_type=DataType.TEXT),
                Property(name="document_id", data_type=DataType.TEXT),
                Property(name="chunk_index", data_type=DataType.INT),
                Property(name="category", data_type=DataType.TEXT),
                Property(name="location", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
                Property(name="upload_date", data_type=DataType.DATE)
            ]
            self.client.collections.create(
                name=COLLECTION_NAME,
                properties=properties,
                vectorizer_config=Configure.Vectorizer.none(),
                description="A collection for storing document chunks with embeddings"
            )
            logger.info(f"✅ Created collection: {COLLECTION_NAME}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create collection: {e}")
            raise

    def add_document(self, document_id, text, metadata=None, chunk_size=None, overlap=None):
        """Add a document to the vector store, chunking if needed."""
        try:
            # Ensure Weaviate is connected
            self._ensure_weaviate_connected()
            
            # Use environment variables if not specified
            if chunk_size is None:
                chunk_size = DEFAULT_CHUNK_SIZE
            if overlap is None:
                overlap = DEFAULT_OVERLAP
                
            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            
            # Prepare data for batch insertion
            data_objects = []
            
            for idx, chunk in enumerate(chunks):
                chunk_metadata = dict(metadata) if metadata else {}
                chunk_metadata.update({
                    "document_id": document_id, 
                    "chunk_index": idx,
                    "content": chunk
                })
                # Generate embedding
                embedding = self.embedding_model.encode(chunk).tolist() if self.embedding_model else None
                # Format upload_date as RFC3339 with milliseconds and Z
                upload_date = chunk_metadata.get("upload_date")
                if not upload_date:
                    dt = datetime.utcnow()
                    upload_date = dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"
                elif isinstance(upload_date, datetime):
                    upload_date = upload_date.strftime("%Y-%m-%dT%H:%M:%S.") + f"{upload_date.microsecond // 1000:03d}Z"
                elif isinstance(upload_date, str) and not upload_date.endswith('Z'):
                    # If it's a string but doesn't end with Z, add it
                    upload_date = upload_date + 'Z'
                
                # Create DataObject with properties and vector
                data_object = DataObject(
                    properties={
                        "content": chunk,
                        "document_id": document_id,
                        "chunk_index": idx,
                        "category": chunk_metadata.get("category", ""),
                        "location": chunk_metadata.get("location", ""),
                        "source": chunk_metadata.get("source", ""),
                        "upload_date": upload_date
                    },
                    vector=embedding
                )
                data_objects.append(data_object)
                
            # Batch insert into Weaviate v4
            collection = self.client.collections.get(COLLECTION_NAME)
            collection.data.insert_many(data_objects)
            logger.info(f"Document {document_id} added as {len(chunks)} chunk(s).")
        except Exception as e:
            logger.error(f"Error adding document {document_id}: {e}")
            raise

    def add_document_from_file(self, document_id, file_path, metadata=None, chunk_size=None, overlap=None):
        """Add a document from a file to the vector store, extracting text and chunking if needed."""
        try:
            import PyPDF2
            from docx import Document
            import pandas as pd
            
            # Determine file type and extract text
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.pdf':
                # Extract text from PDF
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                        
            elif file_extension == '.docx':
                # Extract text from DOCX
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                    
            elif file_extension == '.txt':
                # Read text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    
            elif file_extension in ['.csv', '.xlsx']:
                # Extract text from spreadsheet
                if file_extension == '.csv':
                    df = pd.read_csv(file_path)
                else:  # .xlsx
                    df = pd.read_excel(file_path)
                text = df.to_string()
                
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Add the extracted text as a document
            self.add_document(document_id, text, metadata, chunk_size, overlap)
            
        except ImportError as e:
            logger.error(f"Missing required library for file processing: {e}")
            raise ImportError(f"Please install required libraries: pip install PyPDF2 python-docx pandas openpyxl")
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise

    def query_documents(self, query, n_results=5, include_scores=True, metadata_filter=None):
        """
        Query the vector store for similar documents with optional metadata filtering.
        """
        try:
            # Ensure Weaviate is connected
            self._ensure_weaviate_connected()
            
            query_embedding = self.embedding_model.encode(query).tolist() if self.embedding_model else None

            collection = self.client.collections.get(COLLECTION_NAME)
            
            if metadata_filter:
                # Only support single property equality for now
                if len(metadata_filter) == 1:
                    prop, value = next(iter(metadata_filter.items()))
                    filters = Filter.by_property(prop).equal(value)
                else:
                    # For multiple filters, use AND
                    filters = Filter.all([
                        Filter.by_property(prop).equal(value)
                        for prop, value in metadata_filter.items()
                    ])
                results = collection.query.fetch_objects(filters=filters, limit=n_results)
            else:
                # For vector search, use near_vector with proper limit
                results = collection.query.near_vector(
                    near_vector=query_embedding,
                    limit=n_results
                )
                
            # Weaviate v4 returns a list of GenerativeObject directly
            return results
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            raise

    def list_documents_by_category(self, category=None):
        """List all documents, optionally filtered by category."""
        try:
            collection = self.client.collections.get(COLLECTION_NAME)
            if category:
                filters = Filter.by_property("category").equal(category)
                results = collection.query.fetch_objects(filters=filters)
            else:
                results = collection.query.fetch_objects()
            return results
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def clear_all_documents(self):
        """Clear all documents from the vector store."""
        try:
            # Ensure Weaviate is connected
            self._ensure_weaviate_connected()
            
            collection = self.client.collections.get(COLLECTION_NAME)
            
            # Drop and recreate the collection to clear all documents
            logger.info(f"🗑️  Dropping collection: {COLLECTION_NAME}")
            self.client.collections.delete(COLLECTION_NAME)
            logger.info(f"✅ Dropped collection: {COLLECTION_NAME}")
            
            # Recreate the collection
            self._create_collection_if_not_exists()
            logger.info(f"✅ Cleared all documents from collection: {COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            raise

    def hybrid_search(self, query: str, n_local_results: int = 3, n_web_results: int = 3, 
                     include_internet: bool = True) -> Dict:
        """
        Perform a hybrid search combining local RAG with internet search.
        
        Args:
            query: The search query
            n_local_results: Number of local document results to return
            n_web_results: Number of web search results to return
            include_internet: Whether to include internet search
            
        Returns:
            Dict containing both local and web results
        """
        results = {
            'local_results': None,
            'web_results': None,
            'summary': ''
        }
        
                    # Get local RAG results
        try:
            logger.info(f"🔍 Performing local RAG search for: {query}")
            local_results = self.query_documents(query, n_results=n_local_results)
            results['local_results'] = local_results
            # Handle Weaviate v4 GenerativeReturn object
            if hasattr(local_results, 'objects'):
                result_count = len(local_results.objects) if local_results.objects else 0
            elif isinstance(local_results, list):
                result_count = len(local_results)
            else:
                result_count = 0
            logger.info(f"✅ Found {result_count} local results")
        except Exception as e:
            logger.error(f"❌ Local RAG search failed: {e}")
            results['local_results'] = {'documents': [], 'metadatas': [], 'ids': []}
        
        # Get internet search results if enabled
        if include_internet and self.search_service:
            try:
                logger.info(f"🌐 Performing internet search for: {query}")
                # Use the configured search engine from environment
                search_engine = os.getenv('SEARCH_ENGINE', 'duckduckgo')
                web_results = self.search_service.search(query, num_results=n_web_results, engine=search_engine)
                results['web_results'] = web_results
                logger.info(f"✅ Found {len(web_results)} web results")
                
                # Create search summary
                if web_results:
                    results['summary'] = self.search_service.get_search_summary(query, web_results)
                else:
                    results['summary'] = f"I couldn't find any recent information about '{query}' on the internet."
                    
            except Exception as e:
                logger.error(f"❌ Internet search failed: {e}")
                results['web_results'] = []
                results['summary'] = f"Internet search is currently unavailable. Here's what I found in your documents:"
        
        return results

    def get_context_for_query(self, query: str) -> str:
        """
        Get relevant context for a query by combining local RAG and internet search.
        """
        try:
            # Get hybrid search results
            hybrid_results = self.hybrid_search(query, n_local_results=3, n_web_results=2)
            context_parts = []
            
            # Add local document context
            local_results = hybrid_results.get('local_results')
            if hasattr(local_results, 'objects') and local_results.objects:
                context_parts.append("📄 Relevant Documents:")
                for i, obj in enumerate(local_results.objects, 1):
                    content = obj.properties.get('content', '') if hasattr(obj, 'properties') else ''
                    source = obj.properties.get('source', 'Unknown') if hasattr(obj, 'properties') else 'Unknown'
                    source_info = f" (Source: {source})" if source != 'Unknown' else ""
                    context_parts.append(f"{i}. {content[:200]}...{source_info}")
            elif isinstance(local_results, list) and len(local_results) > 0:
                context_parts.append("📄 Relevant Documents:")
                for i, obj in enumerate(local_results, 1):
                    content = obj.properties.get('content', '') if hasattr(obj, 'properties') else ''
                    source = obj.properties.get('source', 'Unknown') if hasattr(obj, 'properties') else 'Unknown'
                    source_info = f" (Source: {source})" if source != 'Unknown' else ""
                    context_parts.append(f"{i}. {content[:200]}...{source_info}")
            else:
                context_parts.append("No relevant local documents found.")
            
            # Add internet search context
            web_results = hybrid_results.get('web_results', [])
            if web_results:
                context_parts.append("\n🌐 Recent Information:")
                for i, result in enumerate(web_results[:2], 1):
                    context_parts.append(f"{i}. {result.get('title', 'No title')}")
                    context_parts.append(f"   {result.get('snippet', 'No snippet')[:150]}...")
                    context_parts.append(f"   Source: {result.get('link', 'No link')}")
            
            # Add search summary if available
            summary = hybrid_results.get('summary', '')
            if summary:
                context_parts.append(f"\n📝 Summary: {summary}")
            
            return "\n".join(context_parts) if context_parts else "No relevant context found."
        except Exception as e:
            logger.error(f"❌ Context retrieval failed: {e}")
            return f"Error retrieving context: {str(e)}"

    def process_database_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query that might require database information.
        This method combines RAG with database querying capabilities.
        
        Args:
            query: The user query
            
        Returns:
            Dict containing processed results and context
        """
        try:
            # First, try to get relevant context from documents
            context = self.get_context_for_query(query)
            
            # Then, try to get any database-specific information
            db_results = None
            try:
                db_results = langchain_sql_service.process_query(query)
            except Exception as e:
                logger.warning(f"❌ Database query failed: {e}")
            
            return {
                'query': query,
                'context': context,
                'database_results': db_results,
                'has_database_results': db_results is not None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Database query processing failed: {e}")
            return {
                'query': query,
                'context': f"Error processing query: {str(e)}",
                'database_results': None,
                'has_database_results': False,
                'timestamp': datetime.utcnow().isoformat()
            } 