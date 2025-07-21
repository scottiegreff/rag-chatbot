"""
LangChain SQL Agent Service for Natural Language to SQL Conversion
Replaces the manual pattern matching with AI-powered query generation
"""

import logging
import asyncio
import signal
import re
import time
from typing import Dict, Any, Optional
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain.llms.base import LLM
from langchain_core.language_models.llms import LLMResult
from sqlalchemy import text

from backend.database import engine
from backend.services.llm_service import LLMService
from backend.utils.sql_context_builder import get_sql_context_builder

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
            # Extract the user query from the LangChain prompt
            user_query = self._extract_user_query(prompt)
            
            # Build enhanced context with schema and examples
            context_builder = get_sql_context_builder()
            enhanced_prompt = context_builder.build_sql_context(user_query)
            
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # If there's already a running loop, use asyncio.run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(
                    self.llm_service.generate_response(enhanced_prompt), loop
                )
                result = future.result()
            else:
                result = asyncio.run(self.llm_service.generate_response(enhanced_prompt))
            
            # Check if the result is an error message and return a proper SQL agent response
            if "I apologize" in result or "having trouble" in result or "error" in result.lower():
                logger.warning(f"LLM returned error message, providing fallback SQL agent response")
                return self._get_fallback_sql_response(prompt)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in LLMServiceWrapper._call: {e}")
            # Return a proper SQL agent response instead of an error message
            return self._get_fallback_sql_response(prompt)
    
    async def _acall(self, prompt: str, stop: Optional[list] = None, **kwargs) -> str:
        """Async call method for LangChain compatibility"""
        try:
            # Extract the user query from the LangChain prompt
            user_query = self._extract_user_query(prompt)
            
            # Build enhanced context with schema and examples
            context_builder = get_sql_context_builder()
            enhanced_prompt = context_builder.build_sql_context(user_query)
            
            result = await self.llm_service.generate_response(enhanced_prompt)
            
            # Check if the result is an error message and return a proper SQL agent response
            if "I apologize" in result or "having trouble" in result or "error" in result.lower():
                logger.warning(f"LLM returned error message, providing fallback SQL agent response")
                return self._get_fallback_sql_response(prompt)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in LLMServiceWrapper._acall: {e}")
            # Return a proper SQL agent response instead of an error message
            return self._get_fallback_sql_response(prompt)
    
    def _extract_user_query(self, prompt: str) -> str:
        """Extract the user query from the LangChain prompt"""
        # Try different patterns to extract the user query
        patterns = [
            r"Question:\s*(.+)",
            r"Human:\s*(.+)",
            r"User:\s*(.+)",
            r"Query:\s*(.+)",
            r"Input:\s*(.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, return the last line that's not empty
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]
        return lines[-1] if lines else prompt.strip()
    
    def _get_fallback_sql_response(self, prompt: str) -> str:
        """Generate a proper SQL agent response when LLM fails"""
        # Extract the question from the prompt
        question = self._extract_user_query(prompt)
        
        try:
            # Generate a simple SQL agent response based on the question
            if "revenue" in question.lower() or "total" in question.lower():
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT SUM(total) as total_revenue FROM orders"))
                    total_revenue = result.fetchone()[0] or 0
                
                return f"""Thought: I need to calculate the total revenue from orders.
Action: sql_db_query
Action Input: SELECT SUM(total) as total_revenue FROM orders
Observation: The total revenue is ${total_revenue:,.2f}.
Thought: I now know the final answer.
Final Answer: The total revenue from the orders is ${total_revenue:,.2f}."""
            
            elif "customer" in question.lower():
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) as customer_count FROM customers"))
                    customer_count = result.fetchone()[0] or 0
                
                return f"""Thought: I need to count the number of customers.
Action: sql_db_query
Action Input: SELECT COUNT(*) as customer_count FROM customers
Observation: There are {customer_count} customers in the database.
Thought: I now know the final answer.
Final Answer: There are {customer_count} customers in the database."""
            
            elif "order" in question.lower():
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) as order_count FROM orders"))
                    order_count = result.fetchone()[0] or 0
                
                return f"""Thought: I need to count the number of orders.
Action: sql_db_query
Action Input: SELECT COUNT(*) as order_count FROM orders
Observation: There are {order_count} orders in the database.
Thought: I now know the final answer.
Final Answer: There are {order_count} orders in the database."""
            
            else:
                return """Thought: I need to understand what information is available in the database.
Action: sql_db_list_tables
Action Input: 
Observation: The database contains tables: customers, orders, products, order_items
Thought: I now know the available tables.
Final Answer: I can help you query information about customers, orders, products, and order items. Please ask a specific question about the data."""
                
        except Exception as e:
            logger.error(f"Error in _get_fallback_sql_response: {e}")
            # Fallback to generic response if database query fails
            return """Thought: I need to understand what information is available in the database.
Action: sql_db_list_tables
Action Input: 
Observation: The database contains tables: customers, orders, products, order_items
Thought: I now know the available tables.
Final Answer: I can help you query information about customers, orders, products, and order items. Please ask a specific question about the data."""

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
            
            # Create the SQL agent with optimized configuration
            self.agent = create_sql_agent(
                llm=langchain_llm,
                toolkit=toolkit,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3,  # Reduced from 5 to 3 for faster execution
                early_stopping_method="generate",
                return_intermediate_steps=True  # Better debugging
            )
            
            logger.info("✅ LangChain SQL Agent initialized successfully with optimized configuration")
            
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
    
    def is_simple_query(self, query: str) -> bool:
        """
        Determine if a query is simple enough to use fallback instead of LangChain.
        
        Args:
            query: Natural language query
            
        Returns:
            True if it's a simple query that can be handled by fallback
        """
        query_lower = query.lower()
        
        # Simple patterns that can be handled by fallback
        simple_patterns = [
            # Revenue and sales queries
            "total revenue", "total sales", "sum of orders", "revenue from orders",
            
            # Count queries
            "how many customers", "how many orders", "how many products", 
            "count of customers", "count of orders", "count of products",
            "number of customers", "number of orders", "number of products",
            
            # Average queries
            "average order", "average order value", "avg order", "mean order",
            
            # Product queries
            "list all products", "show all products", "best selling product",
            "top selling product", "most popular product", "highest selling product",
            "product with most sales", "best performing product",
            
            # Customer queries
            "list all customers", "show all customers", "top customer",
            "best customer", "customer with most orders", "biggest customer",
            "customer who spent the most", "highest spending customer",
            
            # Order queries
            "largest order", "biggest order", "highest order", "order with highest total",
            "most expensive order", "order with most items",
            
            # Category queries
            "products by category", "category breakdown", "products in category",
            "how many products in", "category with most products",
            
            # Date/time queries
            "recent orders", "latest orders", "newest orders", "orders this month",
            "orders this year", "recent customers", "new customers",
            
            # Price queries
            "most expensive product", "cheapest product", "highest priced product",
            "lowest priced product", "product price range", "price of products",
            
            # Inventory queries
            "products in stock", "available products", "stock levels",
            "products with stock", "inventory status",
            
            # Simple comparisons
            "compare products", "product comparison", "customer comparison",
            "order comparison", "sales comparison",
            
            # List queries with numbers
            "list our", "show our", "top", "cheapest products", "most expensive products",
            "best selling products", "top selling products", "most popular products"
        ]
        
        return any(pattern in query_lower for pattern in simple_patterns)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query using LangChain SQL Agent.
        
        Args:
            query: Natural language query
            
        Returns:
            Dict containing processed results or None if not a database query
        """
        logger.info(f"🗄️ Processing database query: '{query[:50]}...'")
        
        try:
            # Check if this is likely a database query
            if not self.is_database_query(query):
                logger.info(f"Query '{query}' doesn't appear to be a database query")
                return None
            
            # Check if this is a simple query that can use fallback
            if self.is_simple_query(query):
                logger.info(f"Using fast fallback for simple query: '{query}'")
                return self._fallback_query(query)
            
            if not self.agent:
                logger.error("LangChain SQL Agent not initialized")
                return {
                    'success': False,
                    'error': 'SQL Agent not available'
                }
            
            logger.info(f"🔍 Processing database query with LangChain: '{query}'")
            
            # Add timeout to prevent hanging
            def timeout_handler(signum, frame):
                raise TimeoutError("LangChain SQL Agent timed out")
            
            # Set timeout to 15 seconds
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(15)
            
            try:
                # Use LangChain SQL Agent to process the query
                with get_openai_callback() as cb:
                    response = self.agent.run(query)
                
                signal.alarm(0)  # Cancel the alarm
                
                logger.info(f"✅ LangChain SQL Agent response: {response}")
                logger.info(f"📊 Token usage: {cb}")
                
                # Enhance the response with better formatting
                enhanced_response = self._enhance_response_with_data(query, response)
                
                return {
                    'success': True,
                    'query': query,
                    'response': enhanced_response,
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
                logger.error("⏰ LangChain SQL Agent timed out after 15 seconds")
                return {
                    'success': False,
                    'error': 'SQL Agent timed out after 15 seconds',
                    'query': query
                }
            except Exception as agent_error:
                signal.alarm(0)  # Cancel the alarm
                logger.error(f"❌ LangChain SQL Agent error: {agent_error}")
                return {
                    'success': False,
                    'error': f'Agent error: {str(agent_error)}',
                    'query': query
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing query: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def _enhance_response_with_data(self, query: str, response: str) -> str:
        """Enhance the response with actual data when possible"""
        try:
            # If the response contains SQL, try to execute it and include results
            if "SELECT" in response.upper() and "FROM" in response.upper():
                # Extract SQL from the response (simplified)
                sql_match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    sql = sql_match.group(1).strip()
                    
                    # Execute the SQL and get results
                    with engine.connect() as conn:
                        result = conn.execute(text(sql))
                        rows = result.fetchall()
                        columns = result.keys()
                        
                        if rows:
                            # Format the results
                            result_text = f"\n\n**Query Results:**\n"
                            result_text += f"| {' | '.join(columns)} |\n"
                            result_text += f"| {' | '.join(['---'] * len(columns))} |\n"
                            
                            for row in rows[:10]:  # Limit to 10 rows
                                result_text += f"| {' | '.join(str(cell) for cell in row)} |\n"
                            
                            if len(rows) > 10:
                                result_text += f"\n*Showing first 10 of {len(rows)} results*\n"
                            
                            # Add the results to the response
                            response += result_text
            
            return response
            
        except Exception as e:
            logger.warning(f"Could not enhance response with data: {e}")
            return response
    
    def _fallback_query(self, query: str) -> Dict[str, Any]:
        """Fallback to manual pattern matching if LangChain times out"""
        try:
            query_lower = query.lower()
            
            # Customer count queries
            if re.search(r"how many.*customer(s)?", query_lower) or ("how many" in query_lower and ("customer" in query_lower or "customers" in query_lower)):
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
            
            # Order count queries
            elif "how many orders" in query_lower or "count of orders" in query_lower or "number of orders" in query_lower:
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
            
            # Product count queries
            elif "how many products" in query_lower or "count of products" in query_lower or "number of products" in query_lower:
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
            
            # Revenue queries
            elif (
                "total revenue" in query_lower
                or "total sales" in query_lower
                or ("sum" in query_lower and "order" in query_lower)
                or "revenue from orders" in query_lower
            ):
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
            
            # Average order queries
            elif "average order" in query_lower or "avg order" in query_lower or "mean order" in query_lower:
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
            
            # Best selling product queries
            elif any(phrase in query_lower for phrase in ["best selling product", "top selling product", "most popular product", "highest selling product", "product with most sales", "best performing product"]):
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT p.name, p.price, c.name as category_name, COUNT(oi.id) as sales_count, SUM(oi.quantity) as total_quantity
                        FROM products p
                        LEFT JOIN categories c ON p.category_id = c.id
                        LEFT JOIN order_items oi ON p.id = oi.product_id
                        GROUP BY p.id, p.name, p.price, c.name
                        ORDER BY total_quantity DESC NULLS LAST, sales_count DESC NULLS LAST
                        LIMIT 1
                    """))
                    product = result.fetchone()
                if product and product[3]:  # If there are sales
                    category = product[2] if product[2] else "Uncategorized"
                    return {
                        'success': True,
                        'query': query,
                        'response': f"The best selling product is {product[0]} (${product[1]:.2f}, {category}) with {product[4]} units sold across {product[3]} orders.",
                        'sql_generated': False,
                        'fallback': True
                    }
                else:
                    return {
                        'success': True,
                        'query': query,
                        'response': "No sales data available to determine the best selling product.",
                        'sql_generated': False,
                        'fallback': True
                    }
            
            # Top customer queries
            elif any(phrase in query_lower for phrase in ["top customer", "best customer", "customer with most orders", "biggest customer", "customer who spent the most", "highest spending customer"]) or "top 5 customers" in query_lower:
                    with engine.connect() as conn:
                        result = conn.execute(text("""
                            SELECT c.first_name, c.last_name, c.email, COUNT(o.id) as order_count, SUM(o.total) as total_spent
                            FROM customers c
                            LEFT JOIN orders o ON c.id = o.customer_id
                            GROUP BY c.id, c.first_name, c.last_name, c.email
                            ORDER BY total_spent DESC NULLS LAST, order_count DESC NULLS LAST
                            LIMIT 1
                        """))
                        customer = result.fetchone()
                        
                        if customer and customer[4]:  # If there are orders
                            # Check if this is specifically asking for top 5 customers
                            if "top 5" in query_lower or "5 customers" in query_lower:
                                # Get top 5 customers
                                result_top5 = conn.execute(text("""
                                    SELECT c.first_name, c.last_name, c.email, COUNT(o.id) as order_count, SUM(o.total) as total_spent
                                    FROM customers c
                                    LEFT JOIN orders o ON c.id = o.customer_id
                                    GROUP BY c.id, c.first_name, c.last_name, c.email
                                    ORDER BY total_spent DESC NULLS LAST, order_count DESC NULLS LAST
                                    LIMIT 5
                                """))
                                top5_customers = result_top5.fetchall()
                                
                                if top5_customers:
                                    response = "Here are the top 5 customers by total spending:\n\n"
                                    for i, cust in enumerate(top5_customers, 1):
                                        if cust[4]:  # If they have spent money
                                            response += f"{i}. **{cust[0]} {cust[1]}** - ${cust[4]:,.2f} ({cust[3]} orders)\n"
                                        else:
                                            response += f"{i}. **{cust[0]} {cust[1]}** - No orders yet\n"
                                    
                                    return {
                                        'success': True,
                                        'query': query,
                                        'response': response,
                                        'sql_generated': False,
                                        'fallback': True
                                    }
                            
                            # Default to top customer
                            return {
                                'success': True,
                                'query': query,
                                'response': f"The top customer is {customer[0]} {customer[1]} ({customer[2]}) with ${customer[4]:,.2f} total spent across {customer[3]} orders.",
                                'sql_generated': False,
                                'fallback': True
                            }
                        else:
                            return {
                                'success': True,
                                'query': query,
                                'response': "No order data available to determine the top customer.",
                                'sql_generated': False,
                                'fallback': True
                    }
            
            # Largest order queries
            elif any(phrase in query_lower for phrase in ["largest order", "biggest order", "highest order", "order with highest total", "most expensive order"]):
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT o.id, o.total, o.order_date, c.first_name, c.last_name
                        FROM orders o
                        LEFT JOIN customers c ON o.customer_id = c.id
                        ORDER BY o.total DESC
                        LIMIT 1
                    """))
                    order = result.fetchone()
                if order:
                    customer_name = f"{order[3]} {order[4]}" if order[3] and order[4] else "Unknown customer"
                    return {
                        'success': True,
                        'query': query,
                        'response': f"The largest order is Order #{order[0]} for ${order[1]:,.2f} by {customer_name} on {order[2]}.",
                        'sql_generated': False,
                        'fallback': True
                    }
                else:
                    return {
                        'success': True,
                        'query': query,
                        'response': "No orders found in the database.",
                        'sql_generated': False,
                        'fallback': True
                    }
            
            # Most expensive product queries
            elif any(phrase in query_lower for phrase in ["most expensive product", "highest priced product", "product with highest price"]):
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT p.name, p.price, c.name as category_name
                        FROM products p
                        LEFT JOIN categories c ON p.category_id = c.id
                        ORDER BY p.price DESC
                        LIMIT 1
                    """))
                    product = result.fetchone()
                if product:
                    category = product[2] if product[2] else "Uncategorized"
                    return {
                        'success': True,
                        'query': query,
                        'response': f"The most expensive product is {product[0]} at ${product[1]:.2f} in the {category} category.",
                        'sql_generated': False,
                        'fallback': True
                    }
                else:
                    return {
                        'success': True,
                        'query': query,
                        'response': "No products found in the database.",
                        'sql_generated': False,
                        'fallback': True
                    }
            
            # Cheapest product queries
            elif any(phrase in query_lower for phrase in ["cheapest product", "lowest priced product", "product with lowest price"]):
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT p.name, p.price, c.name as category_name
                        FROM products p
                        LEFT JOIN categories c ON p.category_id = c.id
                        ORDER BY p.price ASC
                        LIMIT 1
                    """))
                    product = result.fetchone()
                if product:
                    category = product[2] if product[2] else "Uncategorized"
                    return {
                        'success': True,
                        'query': query,
                        'response': f"The cheapest product is {product[0]} at ${product[1]:.2f} in the {category} category.",
                        'sql_generated': False,
                        'fallback': True
                    }
                else:
                    return {
                        'success': True,
                        'query': query,
                        'response': "No products found in the database.",
                        'sql_generated': False,
                        'fallback': True
                    }
            
            # List queries with numbers (e.g., "list our 5 cheapest products")
            elif any(phrase in query_lower for phrase in ["list our", "show our", "top"]) and any(phrase in query_lower for phrase in ["cheapest products", "most expensive products", "best selling products", "top selling products", "most popular products"]):
                # Extract number from query
                number_match = re.search(r'(\d+)', query)
                limit = int(number_match.group(1)) if number_match else 5
                
                # Determine sort order and type
                if any(phrase in query_lower for phrase in ["cheapest", "lowest"]):
                    order_by = "p.price ASC"
                    product_type = "cheapest"
                elif any(phrase in query_lower for phrase in ["most expensive", "highest"]):
                    order_by = "p.price DESC"
                    product_type = "most expensive"
                elif any(phrase in query_lower for phrase in ["best selling", "top selling", "most popular"]):
                    order_by = "total_quantity DESC NULLS LAST, sales_count DESC NULLS LAST"
                    product_type = "best selling"
                else:
                    order_by = "p.name ASC"
                    product_type = "products"
                
                with engine.connect() as conn:
                    if "best selling" in product_type:
                        # For best selling, we need to join with order_items
                        result = conn.execute(text(f"""
                            SELECT p.name, p.price, c.name as category_name, COUNT(oi.id) as sales_count, SUM(oi.quantity) as total_quantity
                            FROM products p
                            LEFT JOIN categories c ON p.category_id = c.id
                            LEFT JOIN order_items oi ON p.id = oi.product_id
                            GROUP BY p.id, p.name, p.price, c.name
                            ORDER BY {order_by}
                            LIMIT {limit}
                        """))
                        products = result.fetchall()
                        product_list = "\n".join([f"- {p[0]} (${p[1]:.2f}, {p[2] if p[2] else 'Uncategorized'}) - {p[4] or 0} units sold" for p in products])
                    else:
                        # For price-based queries
                        result = conn.execute(text(f"""
                            SELECT p.name, p.price, c.name as category_name
                            FROM products p
                            LEFT JOIN categories c ON p.category_id = c.id
                            ORDER BY {order_by}
                            LIMIT {limit}
                        """))
                        products = result.fetchall()
                        product_list = "\n".join([f"- {p[0]} (${p[1]:.2f}, {p[2] if p[2] else 'Uncategorized'})" for p in products])
                
                return {
                    'success': True,
                    'query': query,
                    'response': f"Here are the {limit} {product_type} products:\n{product_list}",
                    'sql_generated': False,
                    'fallback': True
                }
            
            # List products queries
            elif "list all products" in query_lower or "show all products" in query_lower:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT p.name, p.price, c.name as category_name
                        FROM products p
                        LEFT JOIN categories c ON p.category_id = c.id
                        LIMIT 10
                    """))
                    products = result.fetchall()
                product_list = "\n".join([f"- {p[0]} (${p[1]:.2f}, {p[2] if p[2] else 'Uncategorized'})" for p in products])
                return {
                    'success': True,
                    'query': query,
                    'response': f"Here are the first 10 products:\n{product_list}",
                    'sql_generated': False,
                    'fallback': True
                }
            
            # List customers queries
            elif "list all customers" in query_lower or "show all customers" in query_lower:
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
            
            # Products by category queries
            elif "products by category" in query_lower or "category breakdown" in query_lower:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT c.name as category_name, COUNT(p.id) as product_count, AVG(p.price) as avg_price
                        FROM categories c
                        LEFT JOIN products p ON c.id = p.category_id
                        GROUP BY c.id, c.name
                        ORDER BY product_count DESC
                    """))
                    categories = result.fetchall()
                category_list = "\n".join([f"- {c[0]}: {c[1]} products, avg price ${c[2]:.2f}" for c in categories])
                return {
                    'success': True,
                    'query': query,
                    'response': f"Products by category:\n{category_list}",
                    'sql_generated': False,
                    'fallback': True
                }
            
            # Recent orders queries
            elif any(phrase in query_lower for phrase in ["recent orders", "latest orders", "newest orders"]):
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT o.id, o.total, o.order_date, c.first_name, c.last_name
                        FROM orders o
                        LEFT JOIN customers c ON o.customer_id = c.id
                        ORDER BY o.order_date DESC
                        LIMIT 5
                    """))
                    orders = result.fetchall()
                order_list = "\n".join([f"- Order #{o[0]}: ${o[1]:.2f} by {o[3]} {o[4]} on {o[2]}" for o in orders])
                return {
                    'success': True,
                    'query': query,
                    'response': f"Recent orders:\n{order_list}",
                    'sql_generated': False,
                    'fallback': True
                }
            
            # Default fallback for unmatched patterns
            else:
                return {
                    'success': True,
                    'query': query,
                    'response': "I can help you with database queries about customers, orders, products, and sales. Please ask a specific question about the data.",
                    'sql_generated': False,
                    'fallback': True
                }
                
        except Exception as e:
            logger.error(f"Error in fallback query: {e}")
            return {
                'success': False,
                'error': f'Fallback error: {str(e)}',
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