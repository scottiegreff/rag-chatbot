"""
LangChain SQL Agent Service for Natural Language to SQL Conversion
Replaces the manual pattern matching with AI-powered query generation
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain.llms.base import LLM
from langchain_core.language_models.llms import LLMResult
from backend.database import engine
from backend.services.llm_service import LLMService
import re
from sqlalchemy import text

logger = logging.getLogger(__name__)

class LLMServiceWrapper(LLM):
    """Wrapper to make our LLMService compatible with LangChain"""
    
    llm_service: LLMService = None
    
    def __init__(self, llm_service: LLMService):
        super().__init__()
        self.llm_service = llm_service
    
    @property
    def _llm_type(self) -> str:
        return "llm_service_wrapper"
    
    def _call(self, prompt: str, stop: Optional[list] = None, **kwargs) -> str:
        """Synchronous call method for LangChain compatibility"""
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # If there's already a running loop, use asyncio.run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(
                    self.llm_service.generate_response(prompt), loop
                )
                return future.result()
            else:
                return asyncio.run(self.llm_service.generate_response(prompt))
        except Exception as e:
            logger.error(f"Error in LLMServiceWrapper._call: {e}")
            return f"Error: {str(e)}"
    
    async def _acall(self, prompt: str, stop: Optional[list] = None, **kwargs) -> str:
        """Async call method for LangChain compatibility"""
        try:
            return await self.llm_service.generate_response(prompt)
        except Exception as e:
            logger.error(f"Error in LLMServiceWrapper._acall: {e}")
            return f"Error: {str(e)}"

class LangChainSQLService:
    """Service for using LangChain SQL Agent to convert natural language to SQL queries"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.db = None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangChain SQL Agent"""
        try:
            # Create SQLDatabase from existing engine
            self.db = SQLDatabase(engine)
            
            # Create LangChain-compatible LLM wrapper
            langchain_llm = LLMServiceWrapper(self.llm_service)
            
            # Create toolkit with the database
            toolkit = SQLDatabaseToolkit(db=self.db, llm=langchain_llm)
            
            # Create the SQL agent
            self.agent = create_sql_agent(
                llm=langchain_llm,
                toolkit=toolkit,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
            logger.info("✅ LangChain SQL Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LangChain SQL Agent: {e}")
            self.agent = None
    
    def is_database_query(self, query: str) -> bool:
        """
        Determine if a query is likely a database query.
        
        Args:
            query: Natural language query
            
        Returns:
            True if it's likely a database query, False otherwise
        """
        query_lower = query.lower()
        
        # Database-related keywords
        db_keywords = [
            'customer', 'customers', 'product', 'products', 'order', 'orders',
            'sale', 'sales', 'revenue', 'inventory', 'stock', 'category', 'categories',
            'count', 'how many', 'list', 'show', 'total', 'amount', 'money',
            'database', 'table', 'data', 'record', 'records'
        ]
        
        # Check if query contains database-related keywords
        return any(keyword in query_lower for keyword in db_keywords)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query using LangChain SQL Agent.
        
        Args:
            query: Natural language query
            
        Returns:
            Dict containing processed results or None if not a database query
        """
        try:
            # Check if this is likely a database query
            if not self.is_database_query(query):
                logger.info(f"Query '{query}' doesn't appear to be a database query")
                return None
            
            if not self.agent:
                logger.error("LangChain SQL Agent not initialized")
                return {
                    'success': False,
                    'error': 'SQL Agent not available'
                }
            
            logger.info(f"🔍 Processing database query with LangChain: '{query}'")
            
            # Add timeout to prevent hanging
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("LangChain SQL Agent timed out")
            
            # Set timeout to 60 seconds (increased from 30)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)
            
            try:
                # Use LangChain SQL Agent to process the query
                with get_openai_callback() as cb:
                    response = self.agent.run(query)
                
                signal.alarm(0)  # Cancel the alarm
                
                logger.info(f"✅ LangChain SQL Agent response: {response}")
                logger.info(f"📊 Token usage: {cb}")
                
                return {
                    'success': True,
                    'query': query,
                    'response': response,
                    'sql_generated': True,
                    'tokens_used': {
                        'total_tokens': cb.total_tokens,
                        'prompt_tokens': cb.prompt_tokens,
                        'completion_tokens': cb.completion_tokens,
                        'total_cost': cb.total_cost
                    }
                }
                
            except TimeoutError:
                signal.alarm(0)  # Cancel the alarm
                logger.warning("⏰ LangChain SQL Agent timed out, falling back to manual query")
                return self._fallback_query(query)
                
        except Exception as e:
            logger.error(f"❌ Error processing query with LangChain SQL Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def _fallback_query(self, query: str) -> Dict[str, Any]:
        """Fallback to manual pattern matching if LangChain times out"""
        try:
            query_lower = query.lower()
            
            # More robust pattern: match any query with 'how many' and 'customer' (singular/plural)
            if re.search(r"how many.*customer(s)?", query_lower) or ("how many" in query_lower and ("customer" in query_lower or "customers" in query_lower)):
                logger.info(f"[Fallback] Matched customer count query: '{query}'")
                from backend.database import engine
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) as count FROM customers"))
                    count = result.fetchone()[0]
                return {
                    'success': True,
                    'query': query,
                    'response': f"There are {count} customers in the database.",
                    'sql_generated': False,
                    'fallback': True
                }
            elif "how many orders" in query_lower:
                from backend.database import engine
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) as count FROM orders"))
                    count = result.fetchone()[0]
                return {
                    'success': True,
                    'query': query,
                    'response': f"There are {count} orders in the database.",
                    'sql_generated': False,
                    'fallback': True
                }
            elif "how many products" in query_lower:
                from backend.database import engine
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) as count FROM products"))
                    count = result.fetchone()[0]
                return {
                    'success': True,
                    'query': query,
                    'response': f"There are {count} products in the database.",
                    'sql_generated': False,
                    'fallback': True
                }
            elif (
                "total revenue" in query_lower
                or "total sales" in query_lower
                or ("sum" in query_lower and "order" in query_lower)
            ):
                from backend.database import engine
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT SUM(total) as total FROM orders"))
                    total = result.fetchone()[0] or 0
                return {
                    'success': True,
                    'query': query,
                    'response': f"The total revenue is ${total:,.2f}.",
                    'sql_generated': False,
                    'fallback': True
                }
            elif "average order" in query_lower:
                from backend.database import engine
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT AVG(total) as avg FROM orders"))
                    avg = result.fetchone()[0] or 0
                return {
                    'success': True,
                    'query': query,
                    'response': f"The average order value is ${avg:,.2f}.",
                    'sql_generated': False,
                    'fallback': True
                }
            elif "list all products" in query_lower or "show all products" in query_lower:
                from backend.database import engine
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT name, price, category FROM products LIMIT 10"))
                    products = result.fetchall()
                product_list = "\n".join([f"- {p[0]} (${p[1]:.2f}, {p[2]})" for p in products])
                return {
                    'success': True,
                    'query': query,
                    'response': f"Here are the first 10 products:\n{product_list}",
                    'sql_generated': False,
                    'fallback': True
                }
            elif "list all customers" in query_lower or "show all customers" in query_lower:
                from backend.database import engine
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT first_name, last_name, email FROM customers LIMIT 10"))
                    customers = result.fetchall()
                customer_list = "\n".join([f"- {c[0]} {c[1]} ({c[2]})" for c in customers])
                return {
                    'success': True,
                    'query': query,
                    'response': f"Here are the first 10 customers:\n{customer_list}",
                    'sql_generated': False,
                    'fallback': True
                }
            elif (
                "customers who haven't ordered" in query_lower
                or "customers who haven't placed" in query_lower
                or "customers without orders" in query_lower
                or ("customers" in query_lower and "haven't" in query_lower and "order" in query_lower)
                or ("customers" in query_lower and "not ordered" in query_lower)
            ):
                from backend.database import engine
                with engine.connect() as conn:
                    # Get total customers
                    total_result = conn.execute(text("SELECT COUNT(*) as count FROM customers"))
                    total_customers = total_result.fetchone()[0]
                    
                    # Get customers with recent orders (last 30 days)
                    recent_result = conn.execute(text("""
                        SELECT COUNT(DISTINCT c.id) as count 
                        FROM customers c 
                        JOIN orders o ON c.id = o.customer_id 
                        WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
                    """))
                    customers_with_recent_orders = recent_result.fetchone()[0]
                    
                    # Calculate customers without recent orders
                    customers_without_recent_orders = total_customers - customers_with_recent_orders
                    
                    # Get the latest order date for context
                    latest_result = conn.execute(text("SELECT MAX(order_date) as latest FROM orders"))
                    latest_order = latest_result.fetchone()[0]
                    
                return {
                    'success': True,
                    'query': query,
                    'response': f"Based on the database, {customers_without_recent_orders} out of {total_customers} customers haven't placed an order in the last 30 days. The most recent order was placed on {latest_order.strftime('%B %d, %Y') if latest_order else 'no orders found'}.",
                    'sql_generated': False,
                    'fallback': True
                }
            else:
                return {
                    'success': False,
                    'error': 'Query not supported in fallback mode. Try: "How many customers/orders/products?", "Total revenue", "Average order value", "List all products/customers"',
                    'query': query
                }
        except Exception as e:
            logger.error(f"Fallback query failed: {e}")
            return {
                'success': False,
                'error': f'Fallback failed: {str(e)}',
                'query': query
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database schema"""
        try:
            if not self.db:
                return {'error': 'Database not initialized'}
            
            return {
                'tables': self.db.get_table_names(),
                'schema': self.db.get_table_info(),
                'sample_data': self.db.get_sample_data()
            }
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {'error': str(e)}

# Global instance
langchain_sql_service = LangChainSQLService() 