#!/usr/bin/env python3
"""
Library Service - Main entry point with PostgreSQL setup and gRPC server.
"""

import os
import sys
import subprocess
import time

# Add app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import logging after path setup
from app.utils.logger import LoggerConfig, log_exception
from dotenv import load_dotenv

def start_postgres():
    """Start PostgreSQL container."""
    logger = LoggerConfig.get_logger("main.postgres")
    logger.info("Starting PostgreSQL container...")
    
    # Check if container already exists
    result = subprocess.run(['docker', 'ps', '-q', '-f', 'name=library_postgres'], 
                          capture_output=True, text=True)
    
    if result.stdout.strip():
        logger.info("PostgreSQL container already running")
        return True
    
    # Start new container
    try:
        subprocess.run([
            'docker', 'run', '-d',
            '--name', 'library_postgres',
            '-e', 'POSTGRES_DB=librarydb',
            '-e', 'POSTGRES_USER=library_user',
            '-e', 'POSTGRES_PASSWORD=library_password',
            '-p', '5432:5432',
            '-v', 'library_postgres_data:/var/lib/postgresql/data',
            'postgres:15'
        ], check=True)
        
        logger.info("PostgreSQL container started successfully")
        return True
    except subprocess.CalledProcessError as e:
        log_exception(logger, "Failed to start PostgreSQL container", e)
        return False

def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    logger = LoggerConfig.get_logger("main.postgres")
    logger.info("Waiting for PostgreSQL to be ready...")
    
    for i in range(30):  # Wait up to 30 seconds
        try:
            result = subprocess.run([
                'docker', 'exec', 'library_postgres', 
                'pg_isready', '-U', 'library_user', '-d', 'librarydb'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("PostgreSQL is ready")
                return True
        except Exception as e:
            logger.debug(f"PostgreSQL not ready yet (attempt {i+1}/30): {e}")
        
        time.sleep(1)
    
    logger.error("PostgreSQL failed to start within timeout period")
    return False

def main():
    """Main function."""
    # Initialize logging first
    logger = LoggerConfig.setup_logging()
    logger.info("Starting Library Service...")
    logger.info("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Start PostgreSQL
    if not start_postgres():
        logger.error("Failed to start PostgreSQL, exiting")
        sys.exit(1)
    
    # Wait for PostgreSQL
    if not wait_for_postgres():
        logger.error("PostgreSQL not ready, exiting")
        sys.exit(1)
    
    # Start the library service
    logger.info("Starting Library Service application...")
    logger.info("=" * 50)
    
    try:
        from app.main import main as app_main
        app_main()
    except KeyboardInterrupt:
        logger.info("Shutting down due to keyboard interrupt...")
    except Exception as e:
        log_exception(logger, "Fatal error in main application", e)
        sys.exit(1)

if __name__ == "__main__":
    main() 