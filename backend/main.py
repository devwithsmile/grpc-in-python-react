#!/usr/bin/env python3
"""
Simple Library Service - Starts PostgreSQL and runs the service.
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Add app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def start_postgres():
    """Start PostgreSQL container."""
    print("🐘 Starting PostgreSQL container...")
    
    # Check if container already exists
    result = subprocess.run(['docker', 'ps', '-q', '-f', 'name=library_postgres'], 
                          capture_output=True, text=True)
    
    if result.stdout.strip():
        print("✅ PostgreSQL container already running")
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
        
        print("✅ PostgreSQL container started")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start PostgreSQL: {e}")
        return False

def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    print("⏳ Waiting for PostgreSQL to be ready...")
    
    for i in range(30):  # Wait up to 30 seconds
        try:
            result = subprocess.run([
                'docker', 'exec', 'library_postgres', 
                'pg_isready', '-U', 'library_user', '-d', 'librarydb'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL is ready")
                return True
        except:
            pass
        
        time.sleep(1)
    
    print("❌ PostgreSQL failed to start")
    return False

def main():
    """Main function."""
    print("🚀 Starting Library Service...")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Start PostgreSQL
    if not start_postgres():
        sys.exit(1)
    
    # Wait for PostgreSQL
    if not wait_for_postgres():
        sys.exit(1)
    
    # Start the library service
    print("📚 Starting Library Service...")
    print("=" * 50)
    
    try:
        from app.main import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 