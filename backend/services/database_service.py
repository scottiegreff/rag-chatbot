import sqlite3
import psycopg2
import mysql.connector
# import pandas as pd  # Temporarily disabled for minimal build
from typing import Dict, List, Any, Optional, Union
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import json
import time

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for connecting to SQL databases and executing queries.
    Supports SQLite, PostgreSQL, and MySQL.
    """
    
    def __init__(self, db_type: str = "sqlite", connection_string: str = None):
        """
        Initialize database service.
        
        Args:
            db_type: Type of database ('sqlite', 'postgresql', 'mysql')
            connection_string: Database connection string
        """
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.engine = None
        self.connection = None
        
        # Database-specific configurations
        self.db_configs = {
            'sqlite': {
                'driver': 'sqlite',
                'default_path': './database.db'
            },
            'postgresql': {
                'driver': 'postgresql',
                'default_host': 'localhost',
                'default_port': 5432,
                'default_db': 'postgres'
            },
            'mysql': {
                'driver': 'mysql+pymysql',
                'default_host': 'localhost',
                'default_port': 3306,
                'default_db': 'mysql'
            }
        }
        
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            if self.db_type == 'sqlite':
                # SQLite connection
                db_path = self.connection_string or self.db_configs['sqlite']['default_path']
                self.engine = create_engine(f"sqlite:///{db_path}")
                logger.info(f"✅ Connected to SQLite database: {db_path}")
                
            elif self.db_type == 'postgresql':
                # PostgreSQL connection
                if not self.connection_string:
                    raise ValueError("PostgreSQL requires connection string")
                self.engine = create_engine(self.connection_string)
                logger.info("✅ Connected to PostgreSQL database")
                
            elif self.db_type == 'mysql':
                # MySQL connection
                if not self.connection_string:
                    raise ValueError("MySQL requires connection string")
                self.engine = create_engine(self.connection_string)
                logger.info("✅ Connected to MySQL database")
                
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_database_schema(self) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Returns:
            Dictionary containing tables, columns, and their types
        """
        try:
            inspector = inspect(self.engine)
            schema = {
                'tables': {},
                'database_type': self.db_type
            }
            
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        'name': column['name'],
                        'type': str(column['type']),
                        'nullable': column.get('nullable', True),
                        'default': column.get('default', None)
                    })
                
                # Get primary keys
                primary_keys = inspector.get_pk_constraint(table_name)
                
                # Get foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                schema['tables'][table_name] = {
                    'columns': columns,
                    'primary_keys': primary_keys.get('constrained_columns', []),
                    'foreign_keys': foreign_keys
                }
            
            logger.info(f"📊 Retrieved schema for {len(schema['tables'])} tables")
            return schema
            
        except Exception as e:
            logger.error(f"❌ Failed to get database schema: {e}")
            return {'error': str(e)}
    
    def execute_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (for prepared statements)
            
        Returns:
            Dictionary containing results, metadata, and execution info
        """
        try:
            start_time = time.time()
            
            # Execute query
            with self.engine.connect() as connection:
                if params:
                    result = connection.execute(text(query), params)
                else:
                    result = connection.execute(text(query))
                
                # Fetch results
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    # Convert to list of dictionaries
                    data = []
                    for row in rows:
                        data.append(dict(zip(columns, row)))
                    
                    # Create summary statistics (simplified without pandas)
                    summary = self._generate_summary_simple(data)
                    
                    result_data = {
                        'success': True,
                        'data': data,
                        'columns': list(columns),
                        'row_count': len(data),
                        'summary': summary,
                        'execution_time': time.time() - start_time
                    }
                else:
                    # For INSERT, UPDATE, DELETE operations
                    result_data = {
                        'success': True,
                        'data': [],
                        'row_count': result.rowcount,
                        'message': f"Query executed successfully. {result.rowcount} rows affected.",
                        'execution_time': time.time() - start_time
                    }
            
            logger.info(f"✅ Query executed successfully in {result_data['execution_time']:.3f}s")
            return result_data
            
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for query results.
        
        Args:
            df: Pandas DataFrame with query results
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_types': df.dtypes.to_dict(),
            'numeric_columns': [],
            'text_columns': [],
            'date_columns': []
        }
        
        for col in df.columns:
            col_type = str(df[col].dtype)
            
            if 'int' in col_type or 'float' in col_type:
                summary['numeric_columns'].append({
                    'column': col,
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None,
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                    'count': int(df[col].count())
                })
            elif 'datetime' in col_type:
                summary['date_columns'].append({
                    'column': col,
                    'min': str(df[col].min()) if not df[col].isna().all() else None,
                    'max': str(df[col].max()) if not df[col].isna().all() else None,
                    'count': int(df[col].count())
                })
            else:
                summary['text_columns'].append({
                    'column': col,
                    'unique_values': int(df[col].nunique()),
                    'most_common': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                    'count': int(df[col].count())
                })
        
        return summary
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Validate a SQL query without executing it.
        
        Args:
            query: SQL query string
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Try to parse the query
            parsed = text(query)
            
            # Basic validation checks
            query_lower = query.lower().strip()
            
            validation = {
                'valid': True,
                'query_type': 'unknown',
                'warnings': []
            }
            
            # Determine query type
            if query_lower.startswith('select'):
                validation['query_type'] = 'select'
            elif query_lower.startswith('insert'):
                validation['query_type'] = 'insert'
            elif query_lower.startswith('update'):
                validation['query_type'] = 'update'
            elif query_lower.startswith('delete'):
                validation['query_type'] = 'delete'
            elif query_lower.startswith('create'):
                validation['query_type'] = 'ddl'
            elif query_lower.startswith('drop'):
                validation['query_type'] = 'ddl'
            elif query_lower.startswith('alter'):
                validation['query_type'] = 'ddl'
            
            # Check for potential issues
            if 'drop table' in query_lower or 'drop database' in query_lower:
                validation['warnings'].append('DROP operations can be destructive')
            
            if 'delete from' in query_lower and 'where' not in query_lower:
                validation['warnings'].append('DELETE without WHERE clause will affect all rows')
            
            if 'update' in query_lower and 'where' not in query_lower:
                validation['warnings'].append('UPDATE without WHERE clause will affect all rows')
            
            logger.info(f"✅ Query validation successful: {validation['query_type']}")
            return validation
            
        except Exception as e:
            logger.error(f"❌ Query validation failed: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get sample data from a table.
        
        Args:
            table_name: Name of the table
            limit: Number of sample rows to return
            
        Returns:
            Dictionary with sample data
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"❌ Failed to get sample data from {table_name}: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("🔌 Database connection closed")
    
    def _generate_summary_simple(self, data):
        # Simple summary for minimal build (no pandas)
        if not data:
            return {'total_rows': 0, 'total_columns': 0}
        return {
            'total_rows': len(data),
            'total_columns': len(data[0]) if data else 0,
            'columns': list(data[0].keys()) if data else []
        } 