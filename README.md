# AI Chatbot

A FastAPI-based chatbot with RAG (Retrieval-Augmented Generation) capabilities, built with Python and modern AI technologies.

## Features

- **FastAPI Backend**: Modern, fast web framework for building APIs
- **PostgreSQL Database**: Reliable relational database for chat history and metadata
- **Weaviate v4 Vector Database**: High-performance vector database for RAG with semantic search
- **LLM Integration**: Local LLM support with ctransformers (Mistral, TinyLlama)
- **Document Processing**: PDF, DOCX, TXT, CSV, XLSX, and image file support
- **Internet Search**: DuckDuckGo integration for real-time information
- **Document Upload with Metadata**: Rich metadata support including categories and locations
- **Docker Support**: Containerized deployment
- **RESTful API**: Clean, documented API endpoints
- **Streaming Responses**: Real-time chat responses
- **Session Management**: Persistent chat sessions with titles

## Project Structure

```
ai-chatbot/
├── backend/                 # FastAPI backend application
│   ├── models/             # Database models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── frontend/               # HTML/JS frontend
├── models/                 # LLM model files
├── tests/                  # Test files
├── docker-compose.yml      # Docker orchestration
├── Dockerfile.backend      # Backend container
├── Dockerfile.frontend     # Frontend container
└── requirements.txt        # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- Conda (recommended for environment management)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-chatbot
   ```

2. **Create and activate conda environment:**
   ```bash
   conda create -n ai-chatbot python=3.9
conda activate ai-chatbot
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install psycopg2-binary
   ```

4. **Set up environment variables:**
   ```bash
   cp env_template.txt .env
   # Edit .env with your configuration
   ```

5. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

   > **Note:** If you already have a local PostgreSQL running on port 5432, Docker may not be able to bind to that port. In this case, you can map the Docker Postgres to a different port (e.g., 5433) by editing your `docker-compose.yml`:
   >
   > ```yaml
   >     ports:
   >       - "5433:5432"
   > ```
   >
   > Then connect to your Dockerized Postgres using port 5433 in DBeaver or other tools.

6. **Start the backend:**
   ```bash
   cd backend
   PYTHONPATH=.. python -m uvicorn main:app --reload --host 0.0.0.0 --port 8010
   ```

7. **Access the application:**
   - Web UI: http://localhost:8010/
   - API Documentation: http://localhost:8010/docs

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn weaviate-client sentence-transformers psycopg2-binary
   ```

2. **Start Weaviate:**
   ```bash
   docker run -d -p 8080:8080 -p 50051:50051 semitechnologies/weaviate:1.24.9
   ```

3. **Start PostgreSQL:**
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password1234 postgres:15
   ```

4. **Run the application:**
   ```bash
   cd backend
   PYTHONPATH=.. python -m uvicorn main:app --reload --host 0.0.0.0 --port 8010
   ```

## Configuration

### Environment Variables

- `DB_HOST` — PostgreSQL host
- `DB_PORT` — PostgreSQL port
- `DB_NAME` — Database name
- `DB_USER` — Database user
- `DB_PASSWORD` — Database password
- `WEAVIATE_URL` — Weaviate server URL
- `MODEL_PATH` — Path to LLM model file
- `ENABLE_RAG` — Enable RAG functionality
- `CHUNK_SIZE` — Document chunking size
- `OVERLAP` — Chunk overlap size

## Features Overview

### Document Upload with Metadata
- **Categories**: Human Resources, Finance & Accounting, Information Technology, Legal & Compliance, Operations & Management
- **Locations**: All Locations, Headquarters, Branch Office - North, Branch Office - South, Remote/Home Office
- **Additional Metadata**: Tags, descriptions, general questions, uploaded by information

### RAG (Retrieval-Augmented Generation)
- **Weaviate v4**: High-performance vector database with semantic search
- **Document Chunking**: Intelligent text splitting with configurable overlap
- **Metadata Filtering**: Query documents by category, location, and other metadata
- **Hybrid Search**: Combine local document search with internet search

### Chat Features
- **Streaming Responses**: Real-time chat responses
- **Session Management**: Persistent chat sessions with editable titles
- **RAG Integration**: Automatic context retrieval for better responses
- **Internet Search**: Real-time web search integration

## API Endpoints

### Chat Endpoints
| Method | Endpoint                   | Description                                 |
|--------|----------------------------|---------------------------------------------|
| POST   | `/api/chat/stream`         | Main chat endpoint (streaming, supports `bypass_rag` param) |
| GET    | `/api/chat/{session_id}`   | Retrieve chat history for a session         |
| DELETE | `/api/session/{session_id}`| Reset/delete a chat session                 |
| GET    | `/api/sessions`            | List all chat sessions with titles          |
| POST   | `/api/session/new`         | Create a new chat session                   |
| PUT    | `/api/session/{session_id}/title` | Update session title                    |

### Document Management
| Method | Endpoint                   | Description                                 |
|--------|----------------------------|---------------------------------------------|
| POST   | `/api/upload`              | Upload document with metadata               |
| GET    | `/api/categories`          | Get available document categories           |
| GET    | `/api/locations`           | Get available document locations            |
| GET    | `/api/documents`           | List documents with optional filtering      |

### Search Endpoints
| Method | Endpoint                   | Description                                 |
|--------|----------------------------|---------------------------------------------|
| POST   | `/api/search/internet`     | Internet search only                        |
| POST   | `/api/search/hybrid`       | Hybrid search (local + internet)            |
| GET    | `/api/search/status`       | Check search service availability           |

## Database Schema

### Chat Tables
| Table         | Field      | Type        | Constraints / Notes                |
|---------------|------------|-------------|------------------------------------|
| chat_sessions | id         | Integer     | Primary key, autoincrement, index  |
|               | session_id | String(36)  | Unique, indexed (UUID)             |
|               | created_at | DateTime    | Default: now                       |
|               | updated_at | DateTime    | Default: now, auto-update on change|
| chat_messages | id         | Integer     | Primary key, autoincrement, index  |
|               | session_id | Integer     | Foreign key → chat_sessions.id     |
|               | role       | String(10)  | 'user' or 'assistant'              |
|               | content    | Text        |                                    |
|               | timestamp  | DateTime    | Default: now                       |

### Document Metadata (Weaviate)
- **Collection**: `Documents`
- **Properties**: content, document_id, title, category, location, tags, description, uploaded_by, upload_date, general_questions

## LLM Models

- **Available Models:**
  - `models/mistral-7b-instruct-v0.2.Q4_K_M.gguf` (4.1GB) - High quality, slower
  - `models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` (638MB) - Fast, good for testing
- **Model Configuration**: Change the model path in your environment/config

## Performance Optimization

- **RAG Embeddings**: Forced to use CPU by default (`RAG_USE_CPU=true`)
- **GPU Acceleration**: Available for LLM inference on supported hardware
- **Production Mode**: Avoid `--reload` flag in production
- **Environment**: Use dedicated conda environment for best performance

## Troubleshooting

### Common Issues

- **psycopg2 not found**: Install with `pip install psycopg2-binary`
- **Weaviate connection issues**: Ensure Weaviate is running on port 8080
- **Model loading errors**: Check model file exists in `models/` directory
- **Slow performance**: Disable RAG with `ENABLE_RAG=false` or use CPU for embeddings

### Environment Setup
```bash
# Ensure you're in the correct environment
conda activate ai-chatbot

# Install missing dependencies
pip install psycopg2-binary

# Start backend with correct Python path
cd backend
PYTHONPATH=.. python -m uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

## Example Usage

### Upload a Document
```bash
curl -X POST http://localhost:8010/api/upload \
  -F "file=@document.pdf" \
  -F "title=Company Policy" \
  -F "category=Human Resources" \
  -F "location=All Locations" \
  -F "tags=policy,hr,handbook" \
  -F "description=Employee handbook and policies"
```

### Chat with RAG Context
```bash
curl -X POST http://localhost:8010/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the company policies regarding vacation time?"}'
```

### Get Available Categories
```bash
curl http://localhost:8010/api/categories
```

## Development

### Running Tests
```bash
# Run backend tests
python -m pytest tests/backend/

# Run integration tests
python -m pytest tests/integration/
```

### Adding Test Documents
```bash
# Add sample documents to Weaviate
PYTHONPATH=. python backend/utils/add_documents.py

# Check vector database contents
PYTHONPATH=. python backend/utils/check_vector_db.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

### DBeaver/PostgreSQL Connection Example

If you are running both a native and Dockerized PostgreSQL, and you mapped Docker to port 5433, use these settings in DBeaver:

| Setting   | Value         |
|-----------|--------------|
| Host      | localhost    |
| Port      | 5433         |
| Database  | ai_chatbot  |
| Username  | postgres     |
| Password  | password1234 |