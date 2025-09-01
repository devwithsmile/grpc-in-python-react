"""
Main application entry point for Library Service.
"""

import os
import signal
import sys
from concurrent import futures
import grpc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after setting up environment
from .api.library_pb2_grpc import add_LibraryServiceServicer_to_server
from .api.grpc_server import LibraryServiceServicer
from .infrastructure.database import create_tables

class LibraryServiceApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.server = None
        self.port = int(os.getenv("SERVER_PORT", "50051"))
        self.max_workers = int(os.getenv("SERVER_MAX_WORKERS", "10"))
    
    def start(self):
        """Start the gRPC server."""
        print(f"🚀 Starting Library Service on port {self.port}")
        
        # Create database tables
        print("🗄️  Setting up database...")
        create_tables()
        print("✅ Database ready")
        
        # Start gRPC server
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        add_LibraryServiceServicer_to_server(LibraryServiceServicer(), self.server)
        
        # Listen on port
        listen_addr = f"[::]:{self.port}"
        self.server.add_insecure_port(listen_addr)
        
        # Start server
        self.server.start()
        print(f"✅ gRPC server listening on port {self.port}")
        print("=" * 50)
        print("🎯 Service is ready! Use any gRPC client to connect.")
        print("=" * 50)
        
        # Wait for shutdown
        self.server.wait_for_termination()
    
    def stop(self):
        """Stop the server gracefully."""
        if self.server:
            print("\n🛑 Shutting down server...")
            self.server.stop(0)
            print("✅ Server stopped")

def main():
    """Main entry point."""
    app = LibraryServiceApp()
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n📡 Received signal {signum}")
        app.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        app.start()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        app.stop()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 