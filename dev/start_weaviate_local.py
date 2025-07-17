#!/usr/bin/env python3
"""
Script to start Weaviate locally for testing.
This script helps you start a local Weaviate instance using Docker.
"""

import subprocess
import time
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Docker found: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ Docker not found or not working")
            return False
    except FileNotFoundError:
        logger.error("❌ Docker not installed")
        return False

def check_weaviate_running():
    """Check if Weaviate is already running."""
    try:
        response = requests.get("http://localhost:8080/v1/.well-known/ready", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Weaviate is already running on http://localhost:8080")
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def start_weaviate():
    """Start Weaviate using Docker."""
    try:
        logger.info("🚀 Starting Weaviate...")
        
        # Check if container already exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=weaviate-local', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        
        if 'weaviate-local' in result.stdout:
            logger.info("🔄 Found existing Weaviate container, starting it...")
            subprocess.run(['docker', 'start', 'weaviate-local'], check=True)
        else:
            logger.info("🆕 Creating new Weaviate container...")
            cmd = [
                'docker', 'run', '-d',
                '--name', 'weaviate-local',
                '-p', '8080:8080',
                '-e', 'QUERY_DEFAULTS_LIMIT=25',
                '-e', 'AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true',
                '-e', 'PERSISTENCE_DATA_PATH=/var/lib/weaviate',
                '-e', 'DEFAULT_VECTORIZER_MODULE=none',
                '-e', 'ENABLE_MODULES=',
                '-e', 'CLUSTER_HOSTNAME=node1',
                'semitechnologies/weaviate:1.24.9'
            ]
            subprocess.run(cmd, check=True)
        
        logger.info("✅ Weaviate container started successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start Weaviate: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def wait_for_weaviate():
    """Wait for Weaviate to be ready."""
    logger.info("⏳ Waiting for Weaviate to be ready...")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get("http://localhost:8080/v1/.well-known/ready", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Weaviate is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        attempt += 1
        time.sleep(2)
        if attempt % 5 == 0:
            logger.info(f"   Still waiting... ({attempt}/{max_attempts})")
    
    logger.error("❌ Weaviate failed to start within expected time")
    return False

def show_weaviate_info():
    """Show information about the running Weaviate instance."""
    try:
        response = requests.get("http://localhost:8080/v1/meta", timeout=5)
        if response.status_code == 200:
            meta = response.json()
            logger.info("📊 Weaviate Information:")
            logger.info(f"   Version: {meta.get('version', 'Unknown')}")
            logger.info(f"   Modules: {list(meta.get('modules', {}).keys())}")
            logger.info(f"   Hostname: {meta.get('hostname', 'Unknown')}")
        else:
            logger.warning("⚠️  Could not retrieve Weaviate metadata")
    except Exception as e:
        logger.warning(f"⚠️  Could not retrieve Weaviate metadata: {e}")

def main():
    """Main function to start Weaviate."""
    logger.info("🔧 Weaviate Local Setup")
    logger.info("=" * 40)
    
    # Check Docker
    if not check_docker():
        logger.error("💡 Please install Docker first: https://docs.docker.com/get-docker/")
        return False
    
    # Check if already running
    if check_weaviate_running():
        show_weaviate_info()
        return True
    
    # Start Weaviate
    if not start_weaviate():
        return False
    
    # Wait for it to be ready
    if not wait_for_weaviate():
        return False
    
    # Show information
    show_weaviate_info()
    
    logger.info("\n🎉 Weaviate is ready for testing!")
    logger.info("💡 You can now run: python test_weaviate_integration.py")
    logger.info("💡 Or start your FastAPI backend to test the full integration")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 