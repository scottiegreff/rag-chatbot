# AI Chatbot Project Structure

This document outlines the organized file structure of the AI Chatbot project.

## 📁 Root Directory Structure

```
AI-Chatbot/
├── 📁 backend/                    # Backend Python application
│   ├── 📁 models/                # Database models
│   ├── 📁 routes/                # API routes
│   ├── 📁 services/              # Business logic services
│   ├── 📁 utils/                 # Utility functions
│   └── 📁 tests/                 # Backend-specific tests
├── 📁 frontend/                   # Frontend HTML/JS application
│   ├── 📁 css/                   # Stylesheets
│   ├── 📁 js/                    # JavaScript files
│   └── 📁 static/                # Static assets
├── 📁 tests/                      # All test files
│   ├── 📁 backend/               # Backend tests
│   ├── 📁 integration/           # Integration tests
│   ├── 📁 performance/           # Performance tests
│   ├── 📁 debug/                 # Debug tests
│   ├── 📁 embedding/             # Embedding model tests
│   ├── 📁 frontend/              # Frontend tests
│   ├── 📁 unit/                  # Unit tests
│   └── 📁 data/                  # Test data
├── 📁 scripts/                    # Utility scripts
│   ├── 📁 environment/           # Environment switching scripts
│   ├── 📁 deployment/            # Deployment scripts
│   └── 📁 debug/                 # Debug scripts
├── 📁 docs/                       # Documentation
│   ├── 📁 performance/           # Performance documentation
│   ├── 📁 deployment/            # Deployment documentation
│   └── 📁 environment/           # Environment documentation
├── 📁 data/                       # Data files
│   ├── 📁 database/              # Database files
│   └── 📁 backups/               # Backup files
├── 📁 config/                     # Configuration files
├── 📁 dev/                        # Development utilities
├── 📁 logs/                       # Log files
├── 📁 models/                     # AI model files
├── 📁 deployment/                 # Deployment configuration
├── 📁 terraform/                  # Infrastructure as code
└── 📁 testing_summaries/          # Test result summaries
```

## 📋 File Categories

### 🔧 **Configuration Files**
- `docker-compose.yml` - Main Docker Compose configuration
- `docker-compose.override.yml` - Docker Compose overrides
- `docker-compose.prod.yml` - Production Docker configuration
- `docker-compose.aws-gpu.yml` - AWS GPU Docker configuration
- `Dockerfile.backend` - Backend Docker image
- `Dockerfile.frontend` - Frontend Docker image
- `nginx.conf` - Nginx configuration
- `config/env_template.txt` - Environment template

### 🚀 **Deployment Files**
- `scripts/deployment/deploy.sh` - Main deployment script
- `scripts/deployment/deploy_fresh.sh` - Fresh deployment
- `scripts/deployment/deploy-aws-gpu.sh` - AWS GPU deployment
- `scripts/deployment/docker-setup.sh` - Docker setup
- `deployment/` - Deployment configuration files
- `terraform/` - Infrastructure as code

### 🔄 **Environment Scripts**
- `scripts/environment/switch-to-local.sh` - Switch to local M1 GPU
- `scripts/environment/switch-to-docker.sh` - Switch to Docker CPU
- `scripts/environment/quick-switch-local.sh` - Quick local switch
- `scripts/environment/quick-switch-docker.sh` - Quick Docker switch
- `scripts/environment/switch-embedding-model.sh` - Switch embedding models
- `scripts/environment/status.sh` - Check environment status

### 🧪 **Test Files**
- `tests/backend/test_enhanced_sql.py` - Enhanced SQL testing
- `tests/integration/test_rag_query.py` - RAG integration tests
- `tests/performance/test_m1_gpu_only.py` - M1 GPU performance tests
- `tests/embedding/test_embedding_models.py` - Embedding model tests
- `tests/debug/debug_performance_test.py` - Performance debugging

### 📚 **Documentation**
- `docs/performance/PERFORMANCE_ANALYSIS_SUMMARY.md` - Performance analysis
- `docs/deployment/AWS_GPU_DEPLOYMENT.md` - AWS deployment guide
- `docs/environment/ENVIRONMENT_SWITCHING_GUIDE.md` - Environment guide
- `README.md` - Main project documentation

### 💾 **Data Files**
- `data/database/database_documentation.txt` - Database schema docs
- `data/backups/chatbot.db.backup` - Database backup
- `ecommerce_schema.sql` - Database schema
- `ecommerce_dummy_data.sql` - Sample data

### 🔧 **Development Files**
- `dev/simple_server.py` - Simple development server
- `dev/start_backend.py` - Backend startup script
- `dev/optimization.txt` - Performance optimization tracker
- `dev/optimize-models.md` - Model optimization docs

### 📊 **Logs and Results**
- `logs/backend.log` - Backend application logs
- `logs/debug_backend.log` - Debug logs
- `testing_summaries/` - Performance test results

## 🎯 **Key Benefits of This Organization**

1. **Clear Separation**: Each file type has its dedicated directory
2. **Easy Navigation**: Related files are grouped together
3. **Maintainable**: Easy to find and update specific components
4. **Scalable**: Structure supports project growth
5. **Documented**: Each directory has README files explaining its purpose

## 🚀 **Usage Examples**

### Switch Environment
```bash
./scripts/environment/switch-to-local.sh
./scripts/environment/status.sh
```

### Run Tests
```bash
python -m pytest tests/backend/
python tests/performance/test_m1_gpu_only.py
```

### Deploy
```bash
./scripts/deployment/deploy.sh
./scripts/deployment/deploy-aws-gpu.sh
```

### View Documentation
```bash
open docs/performance/PERFORMANCE_ANALYSIS_SUMMARY.md
open docs/deployment/AWS_GPU_DEPLOYMENT.md
```

This organized structure makes the project much more maintainable and professional! 