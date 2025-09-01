#!/usr/bin/env python3
"""
Simple test client for the Library Service.
"""

import grpc
from app.api import library_pb2, library_pb2_grpc

def test_library_service():
    """Test the library service."""
    print("🧪 Testing Library Service...")
    print("=" * 50)
    
    # Connect to the gRPC server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = library_pb2_grpc.LibraryServiceStub(channel)
        
        try:
            # Test 1: Create a book
            print("📚 Test 1: Creating a book...")
            book_request = library_pb2.Book(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                isbn="978-0743273565"
            )
            book_response = stub.CreateBook(book_request)
            print(f"✅ Book created with ID: {book_response.id}")
            
            # Test 2: Create a member
            print("\n👤 Test 2: Creating a member...")
            member_request = library_pb2.Member(
                name="John Doe",
                email="john@example.com",
                phone="555-1234"
            )
            member_response = stub.CreateMember(member_request)
            print(f"✅ Member created with ID: {member_response.id}")
            
            # Test 3: Get the book
            print("\n🔍 Test 3: Getting the book...")
            book_id_request = library_pb2.BookId(id=book_response.id)
            book = stub.GetBook(book_id_request)
            print(f"✅ Book retrieved: {book.title} by {book.author}")
            
            # Test 4: List all books
            print("\n📋 Test 4: Listing all books...")
            empty_request = library_pb2.Empty()
            books = stub.ListBooks(empty_request)
            print(f"✅ Found {len(books.books)} books:")
            for book in books.books:
                print(f"   - {book.title} by {book.author}")
            
            # Test 5: Borrow the book
            print("\n📖 Test 5: Borrowing the book...")
            borrow_request = library_pb2.BorrowRequest(
                member_id=member_response.id,
                book_id=book_response.id
            )
            borrowing = stub.BorrowBook(borrow_request)
            print(f"✅ Book borrowed successfully!")
            
            print("\n🎉 All tests passed! Service is working correctly.")
            
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e.code()}: {e.details()}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_library_service() 