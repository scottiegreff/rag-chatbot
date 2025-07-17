# Tests Directory

This directory contains all test files organized by type and purpose.

## Test Categories

### Backend Tests (`backend/`)
Backend-specific tests including database and API tests:
- `test_enhanced_sql.py` - Enhanced SQL query testing
- `test_database_accuracy.py` - Database accuracy tests
- `test_database_chat.py` - Database chat functionality tests
- `test_ecommerce_business_logic.py` - E-commerce business logic tests
- `test_internet_search.py` - Internet search functionality tests
- `test_list_response.py` - List response formatting tests
- `test_metadata_system.py` - Metadata system tests
- `test_postgres_connection.py` - PostgreSQL connection tests
- `test_session_title_update.py` - Session title update tests
- `test_upload_endpoint.py` - File upload endpoint tests

### Integration Tests (`integration/`)
End-to-end integration tests:
- `test_chatbot_api.py` - Full chatbot API integration tests
- `test_internet_search_integration.py` - Internet search integration
- `test_metadata_upload_ui.py` - Metadata upload UI integration
- `test_session_isolation.py` - Session isolation tests
- `test_weaviate_integration.py` - Weaviate vector database integration
- `test_rag_query.py` - RAG query functionality tests

### Performance Tests (`performance/`)
Performance and benchmarking tests:
- `test_m1_gpu_only.py` - M1 GPU performance tests
- `run_performance_test.py` - Comprehensive performance testing
- `run_performance_test_simple.py` - Simple performance tests

### Debug Tests (`debug/`)
Debugging and troubleshooting tests:
- `debug_performance_test.py` - Performance debugging tests
- `debug_test.py` - General debugging tests

### Embedding Tests (`embedding/`)
Embedding model and vector database tests:
- `test_single_embedding.py` - Single embedding tests
- `test_embedding_models.py` - Embedding model comparison tests

### Frontend Tests (`frontend/`)
Frontend JavaScript and UI tests:
- `test_chat_toggle.html` - Chat toggle functionality tests
- `test_chat_toggle_fix.html` - Chat toggle fix tests
- `test_frontend_sessions.html` - Frontend session tests
- `test_sidebar_toggle_fix.html` - Sidebar toggle tests
- `test_state_management.html` - State management tests

### Unit Tests (`unit/`)
Unit tests for individual components:
- `basic.test.js` - Basic unit tests
- `chat.test.js` - Chat functionality unit tests

## Running Tests

### Backend Tests
```bash
# Run all backend tests
python -m pytest tests/backend/

# Run specific test
python -m pytest tests/backend/test_enhanced_sql.py
```

### Integration Tests
```bash
# Run all integration tests
python -m pytest tests/integration/
```

### Performance Tests
```bash
# Run performance tests
python tests/performance/test_m1_gpu_only.py
python tests/run_performance_test.py
```

### Frontend Tests
```bash
# Open test files in browser
open tests/frontend/test_chat_toggle.html
```

## Test Data
Test data files are stored in `tests/data/`:
- `test_document.txt` - Sample document for testing
- `test_upload.txt` - Sample upload file for testing 