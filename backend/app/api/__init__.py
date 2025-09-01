"""
gRPC API layer for the Library Service.
"""

from .grpc_server import LibraryServiceServicer
from .grpc_server import create_grpc_server

__all__ = ['LibraryServiceServicer', 'create_grpc_server'] 