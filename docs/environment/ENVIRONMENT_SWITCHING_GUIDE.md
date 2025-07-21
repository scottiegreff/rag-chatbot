# Environment Switching Guide

## Quick Reference

### Switch to Local (M1 GPU)
```bash
# Kill any existing processes
pkill -f "uvicorn backend.main:app"

# Set environment variables for local development
export WEAVIATE_URL=http://localhost:8080
export PORT=8000

# Start local backend
./switch-to-local.sh
```

### Switch to Docker (CPU)
```bash
# Kill any existing processes
pkill -f "uvicorn backend.main:app"

# Start Docker backend
./switch-to-docker.sh
```

## Environment Configurations

### Local Environment (M1 GPU)
- **Backend**: Native Python on port 8000
- **Weaviate**: Docker container on port 8080
- **Database**: PostgreSQL in Docker on port 5432
- **GPU**: M1 Metal acceleration enabled
- **Performance**: ~40-50 tokens/second
- **Environment Variables**:
  ```bash
  export WEAVIATE_URL=http://localhost:8080
  export PORT=8000
  export CT_METAL=1
  export GPU_LAYERS=4
  ```

### Docker Environment (CPU)
- **Backend**: Docker container on port 8000
- **Weaviate**: Docker container on port 8080
- **Database**: PostgreSQL in Docker on port 5432
- **GPU**: CPU only (no Metal acceleration)
- **Performance**: ~35-40 tokens/second
- **Environment Variables**: Managed by Docker Compose

## Testing Commands

### Health Check
```bash
# Local environment
curl -s http://localhost:8000/test

# Docker environment
curl -s http://localhost:8000/test
```

### RAG Test
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Flying Cats Insurance Agency?", "session_id": "test"}' \
  --max-time 15
```

### Performance Test
```bash
# M1 GPU test
python test_m1_gpu_only.py

# Full performance test
PYTHONPATH=. python tests/run_performance_test.py
```

## Troubleshooting

### Port Conflicts
```bash
# Check what's using port 8000
lsof -i:8000

# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9
```

### Weaviate Connection Issues
```bash
# Check Weaviate health
curl -s http://localhost:8080/v1/meta

# Check Weaviate logs
docker logs ai-chatbot-weaviate --tail 20
```

### Docker Issues
```bash
# Check Docker containers
docker ps

# Restart Docker services
docker-compose restart

# View Docker logs
docker logs ai-chatbot-backend --tail 20
```

## Performance Comparison

| Environment | Tokens/Second | First Token Latency | Total Response Time |
|-------------|---------------|-------------------|-------------------|
| Local M1 GPU | ~40-50 | ~300-800ms | ~1.0-1.5s |
| Docker CPU | ~35-40 | ~300-700ms | ~0.8-1.2s |

## Best Practices

1. **Always kill existing processes** before switching
2. **Set environment variables** for local development
3. **Test health endpoints** after switching
4. **Check logs** if issues occur
5. **Use consistent ports** (8000 for backend, 8080 for Weaviate)

## Quick Switch Scripts

### Quick Local Switch
```bash
#!/bin/bash
pkill -f "uvicorn backend.main:app"
export WEAVIATE_URL=http://localhost:8080
export PORT=8000
./switch-to-local.sh
```

### Quick Docker Switch
```bash
#!/bin/bash
pkill -f "uvicorn backend.main:app"
./switch-to-docker.sh
```

## Current Status
- ✅ **Local Environment**: Working with M1 Metal acceleration
- ✅ **Docker Environment**: Working with CPU processing
- ✅ **RAG Functionality**: Working in both environments
- ✅ **Document Upload**: Working in both environments
- ✅ **Performance Testing**: Available for both environments 