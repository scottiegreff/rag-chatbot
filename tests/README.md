# Test Directory Structure

This directory contains all test files for the AI-Chatbot project, organized by type and purpose.

## Directory Structure

```
tests/
├── README.md                 # This file
├── unit/                     # Unit tests
│   ├── basic.test.js        # Basic JavaScript unit tests
│   └── chat.test.js         # Chat functionality unit tests
├── integration/              # Integration tests
│   ├── test_internet_search_integration.py  # Internet search integration tests
│   ├── test_metadata_upload_ui.py           # Metadata upload UI integration tests
│   └── test_session_isolation.py            # Session isolation integration tests
├── backend/                  # Backend-specific tests
│   ├── test_internet_search.py              # Internet search service tests
│   ├── test_upload_endpoint.py              # Upload endpoint tests
│   ├── test_metadata_system.py              # Metadata system tests
│   ├── test_session_title_update.py         # Session title update tests
│   ├── test_dinner_list.py                  # Dinner list functionality tests
│   └── test_list_response.py                # List response generation tests
├── frontend/                 # Frontend-specific tests
│   ├── test_sidebar_toggle_fix.html         # Sidebar toggle functionality test
│   ├── test_state_management.html           # State management test
│   ├── test_chat_toggle_fix.html            # Chat toggle functionality test
│   ├── test_chat_toggle.html                # Chat toggle basic test
│   └── test_frontend_sessions.html          # Frontend session management test
└── data/                     # Test data files
    ├── test_upload.txt                       # Test upload file
    └── test_document.txt                     # Test document file
```

## Test Categories

### Unit Tests (`unit/`)
- **Purpose**: Test individual functions and components in isolation
- **Technology**: JavaScript (Jest)
- **Files**: Basic functionality and chat-specific unit tests

### Integration Tests (`integration/`)
- **Purpose**: Test interactions between multiple components or services
- **Technology**: Python (requests, pytest)
- **Files**: End-to-end functionality tests, UI integration tests

### Backend Tests (`backend/`)
- **Purpose**: Test backend services, APIs, and business logic
- **Technology**: Python (requests, pytest)
- **Files**: Service tests, endpoint tests, system functionality tests

### Frontend Tests (`frontend/`)
- **Purpose**: Test frontend functionality and user interactions
- **Technology**: HTML/JavaScript (browser-based tests)
- **Files**: UI component tests, interaction tests, functionality tests

### Test Data (`data/`)
- **Purpose**: Sample files and data used by tests
- **Files**: Test documents, upload files, and other test assets

## Running Tests

### Backend Tests
```bash
# Run all backend tests
python -m pytest tests/backend/

# Run specific test file
python tests/backend/test_internet_search.py
```

### Frontend Tests
```bash
# Open test files in browser
open tests/frontend/test_sidebar_toggle_fix.html
```

### Integration Tests
```bash
# Run integration tests
python tests/integration/test_internet_search_integration.py
```

## Test Naming Convention

- **Backend tests**: `test_*.py` (Python files)
- **Frontend tests**: `test_*.html` (HTML files)
- **Unit tests**: `*.test.js` (JavaScript files)
- **Test data**: `test_*.txt` (Text files)

## Notes

- All test files have been moved from the root directory to maintain a clean project structure
- Test files are organized by functionality and technology stack
- Integration tests focus on cross-component functionality
- Frontend tests are browser-based and can be opened directly in a web browser 