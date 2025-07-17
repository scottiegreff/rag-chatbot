# Scripts Directory

This directory contains utility scripts organized by purpose:

## Environment Scripts (`environment/`)
Scripts for switching between different deployment environments:
- `switch-to-local.sh` - Switch to local M1 GPU environment
- `switch-to-docker.sh` - Switch to Docker CPU environment
- `quick-switch-local.sh` - Quick switch to local environment
- `quick-switch-docker.sh` - Quick switch to Docker environment
- `switch-embedding-model.sh` - Switch between embedding models
- `status.sh` - Check current environment status

## Deployment Scripts (`deployment/`)
Scripts for deploying the application:
- `deploy.sh` - Main deployment script
- `deploy_fresh.sh` - Fresh deployment with cleanup
- `deploy-aws-gpu.sh` - AWS GPU deployment
- `docker-setup.sh` - Docker environment setup

## Debug Scripts (`debug/`)
Scripts for debugging and troubleshooting:
- `debug_local_backend.sh` - Debug local backend issues

## Usage
Run scripts from the project root directory:
```bash
./scripts/environment/switch-to-local.sh
./scripts/deployment/deploy.sh
``` 