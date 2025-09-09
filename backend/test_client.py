#!/usr/bin/env python3
"""
Simple test client for the Library Service.
"""

import grpc
import sys
import os

# Add app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.api import library_pb2, library_pb2_grpc
from app.utils.logger import LoggerConfig, log_exception

def test_library_service():
    """Test the library service."""
    logger = LoggerConfig.get_logger("test_client")
    logger.info("Testing Library Service...")
    logger.info("=" * 50)
    
    # Connect to the gRPC server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = library_pb2_grpc.LibraryServiceStub(channel)
        
        try:
            # Test 1: Create a book
            logger.info("Test 1: Creating a book...")
            book_request = library_pb2.Book(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                isbn="978-0743273565"
            )
            book_response = stub.CreateBook(book_request)
            logger.info(f"Book created with ID: {book_response.id}")
            
            # Test 2: Create a member
            logger.info("Test 2: Creating a member...")
            member_request = library_pb2.Member(
                name="John Doe",
                email="john@example.com",
                phone="555-1234"
            )
            member_response = stub.CreateMember(member_request)
            logger.info(f"Member created with ID: {member_response.id}")
            
            # Test 3: Get the book
            logger.info("Test 3: Getting the book...")
            book_id_request = library_pb2.BookId(id=book_response.id)
            book = stub.GetBook(book_id_request)
            logger.info(f"Book retrieved: {book.title} by {book.author}")
            
            # Test 4: List all books
            logger.info("Test 4: Listing all books...")
            empty_request = library_pb2.Empty()
            books = stub.ListBooks(empty_request)
            logger.info(f"Found {len(books.books)} books:")
            for book in books.books:
                logger.info(f"   - {book.title} by {book.author}")
            
            # Test 5: Borrow the book
            logger.info("Test 5: Borrowing the book...")
            borrow_request = library_pb2.BorrowRequest(
                member_id=member_response.id,
                book_id=book_response.id
            )
            borrowing = stub.BorrowBook(borrow_request)
            logger.info("Book borrowed successfully!")
            
            logger.info("All tests passed! Service is working correctly.")
            
        except grpc.RpcError as e:
            logger.error(f"gRPC Error: {e.code()}: {e.details()}")
        except Exception as e:
            log_exception(logger, "Test failed with error", e)

if __name__ == "__main__":
    test_library_service() 