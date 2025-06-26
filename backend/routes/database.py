from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from backend.services.database_service import DatabaseService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

# Database service instance
db_service = None

def get_db_service():
    """Get or create database service instance."""
    global db_service
    if db_service is None:
        try:
            # Get database configuration from environment
            db_type = os.getenv("DB_TYPE", "sqlite")
            connection_string = os.getenv("DB_CONNECTION_STRING")
            
            db_service = DatabaseService(db_type=db_type, connection_string=connection_string)
            logger.info(f"✅ Database service initialized for {db_type}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database service: {e}")
            raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    
    return db_service

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    params: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    row_count: Optional[int] = None
    summary: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    message: Optional[str] = None

class ValidationRequest(BaseModel):
    query: str

class ValidationResponse(BaseModel):
    valid: bool
    query_type: Optional[str] = None
    warnings: Optional[List[str]] = None
    error: Optional[str] = None

class SampleDataRequest(BaseModel):
    table_name: str
    limit: Optional[int] = 5

# API Endpoints
@router.get("/schema")
async def get_schema():
    """Get database schema information."""
    try:
        db_service = get_db_service()
        schema = db_service.get_database_schema()
        
        if 'error' in schema:
            raise HTTPException(status_code=500, detail=schema['error'])
        
        return schema
        
    except Exception as e:
        logger.error(f"❌ Failed to get schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute a SQL query."""
    try:
        db_service = get_db_service()
        
        # Validate query first
        validation = db_service.validate_query(request.query)
        if not validation['valid']:
            raise HTTPException(status_code=400, detail=f"Invalid query: {validation.get('error', 'Unknown error')}")
        
        # Check for warnings
        warnings = validation.get('warnings', [])
        if warnings:
            logger.warning(f"Query warnings: {warnings}")
        
        # Execute query
        result = db_service.execute_query(request.query, request.params)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=ValidationResponse)
async def validate_query(request: ValidationRequest):
    """Validate a SQL query without executing it."""
    try:
        db_service = get_db_service()
        validation = db_service.validate_query(request.query)
        
        return ValidationResponse(**validation)
        
    except Exception as e:
        logger.error(f"❌ Query validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sample")
async def get_sample_data(request: SampleDataRequest):
    """Get sample data from a table."""
    try:
        db_service = get_db_service()
        result = db_service.get_sample_data(request.table_name, request.limit)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables")
async def list_tables():
    """List all tables in the database."""
    try:
        db_service = get_db_service()
        schema = db_service.get_database_schema()
        
        if 'error' in schema:
            raise HTTPException(status_code=500, detail=schema['error'])
        
        tables = list(schema['tables'].keys())
        return {
            "tables": tables,
            "count": len(tables)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to list tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/table/{table_name}")
async def get_table_info(table_name: str):
    """Get detailed information about a specific table."""
    try:
        db_service = get_db_service()
        schema = db_service.get_database_schema()
        
        if 'error' in schema:
            raise HTTPException(status_code=500, detail=schema['error'])
        
        if table_name not in schema['tables']:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        table_info = schema['tables'][table_name]
        
        # Get sample data
        sample_data = db_service.get_sample_data(table_name, 3)
        
        return {
            "table_name": table_name,
            "columns": table_info['columns'],
            "primary_keys": table_info['primary_keys'],
            "foreign_keys": table_info['foreign_keys'],
            "sample_data": sample_data.get('data', []) if sample_data.get('success') else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get table info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def database_health():
    """Check database connection health."""
    try:
        db_service = get_db_service()
        
        # Try a simple query
        result = db_service.execute_query("SELECT 1 as health_check")
        
        return {
            "status": "healthy",
            "database_type": db_service.db_type,
            "connection": "active"
        }
        
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 