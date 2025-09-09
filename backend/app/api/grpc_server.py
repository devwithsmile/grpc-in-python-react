"""
gRPC server implementation for the Library Service.
"""

import grpc

# Import generated protobuf files
from .library_pb2 import (
    Book, BookId, Member, MemberId, Borrowing, 
    BorrowRequest, ReturnRequest, BookList, MemberList, BorrowingList, Empty
)
from .library_pb2_grpc import LibraryServiceServicer, add_LibraryServiceServicer_to_server

# Import business services
from ..services.book_service import BookService
from ..services.member_service import MemberService
from ..services.borrowing_service import BorrowingService
from ..utils.logger import LoggerConfig
from ..exceptions.base import LibraryServiceError
from ..exceptions.grpc_mapping import GRPCStatusMapper
from ..exceptions.error_handler import error_handler


class LibraryServiceServicer(LibraryServiceServicer):
    """gRPC service implementation for library operations."""
    
    def __init__(self):
        """Initialize the service with business logic services."""
        self.book_service = BookService()
        self.member_service = MemberService()
        self.borrowing_service = BorrowingService()
        self.logger = LoggerConfig.get_logger("api.grpc_server")
    
    def CreateBook(self, request, context):
        """Create a new book."""
        self.logger.info(f"gRPC CreateBook request: title='{request.title}', author='{request.author}', isbn='{request.isbn}'")
        try:
            book = self.book_service.create_book(
                title=request.title,
                author=request.author,
                isbn=request.isbn if request.isbn else None
            )
            self.logger.info(f"gRPC CreateBook success: book_id={book.id}")
            return BookId(id=book.id)
        except LibraryServiceError as e:
            grpc_status, details = GRPCStatusMapper.map_exception_to_grpc_status(e)
            context.set_code(grpc_status)
            context.set_details(details)
            return BookId()
        except Exception as e:
            error_handler.handle_grpc_exception(
                e,
                context={"title": request.title, "author": request.author, "isbn": request.isbn},
                operation="CreateBook"
            )
            grpc_status, details = GRPCStatusMapper.map_generic_exception_to_grpc_status(e)
            context.set_code(grpc_status)
            context.set_details(details)
            return BookId()
    
    def UpdateBook(self, request, context):
        """Update an existing book."""
        try:
            book = self.book_service.update_book(
                book_id=request.id,
                title=request.title,
                author=request.author,
                isbn=request.isbn if request.isbn else None
            )
            if not book:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Book not found")
                return Book()
            
            return Book(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to update book: {str(e)}")
            return Book()
    
    def GetBook(self, request, context):
        """Get a book by ID."""
        try:
            book = self.book_service.get_book(request.id)
            if not book:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Book not found")
                return Book()
            
            return Book(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get book: {str(e)}")
            return Book()
    
    def CreateMember(self, request, context):
        """Create a new member."""
        try:
            member = self.member_service.create_member(
                name=request.name,
                email=request.email,
                phone=request.phone if request.phone else None
            )
            return MemberId(id=member.id)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to create member: {str(e)}")
            return MemberId()
    
    def UpdateMember(self, request, context):
        """Update an existing member."""
        try:
            member = self.member_service.update_member(
                member_id=request.id,
                name=request.name,
                email=request.email,
                phone=request.phone if request.phone else None
            )
            if not member:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Member not found")
                return Member()
            
            return Member(
                id=member.id,
                name=member.name,
                email=member.email,
                phone=member.phone
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to update member: {str(e)}")
            return Member()
    
    def GetMember(self, request, context):
        """Get a member by ID."""
        try:
            member = self.member_service.get_member(request.id)
            if not member:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Member not found")
                return Member()
            
            return Member(
                id=member.id,
                name=member.name,
                email=member.email,
                phone=member.phone
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get member: {str(e)}")
            return Member()
    
    def BorrowBook(self, request, context):
        """Borrow a book."""
        self.logger.info(f"gRPC BorrowBook request: book_id={request.book_id}, member_id={request.member_id}")
        try:
            borrowing = self.borrowing_service.borrow_book(
                book_id=request.book_id,
                member_id=request.member_id
            )
            self.logger.info(f"gRPC BorrowBook success: borrowing_id={borrowing.id}")
            return Borrowing(
                id=borrowing.id,
                book_id=borrowing.book_id,
                member_id=borrowing.member_id,
                borrow_date=borrowing.borrow_date.isoformat() if borrowing.borrow_date else "",
                return_date=borrowing.return_date.isoformat() if borrowing.return_date else ""
            )
        except LibraryServiceError as e:
            grpc_status, details = GRPCStatusMapper.map_exception_to_grpc_status(e)
            context.set_code(grpc_status)
            context.set_details(details)
            return Borrowing()
        except Exception as e:
            error_handler.handle_grpc_exception(
                e,
                context={"book_id": request.book_id, "member_id": request.member_id},
                operation="BorrowBook"
            )
            grpc_status, details = GRPCStatusMapper.map_generic_exception_to_grpc_status(e)
            context.set_code(grpc_status)
            context.set_details(details)
            return Borrowing()
    
    def ReturnBook(self, request, context):
        """Return a borrowed book."""
        try:
            borrowing = self.borrowing_service.return_book(
                book_id=request.book_id,
                member_id=request.member_id
            )
            return Borrowing(
                id=borrowing.id,
                book_id=borrowing.book_id,
                member_id=borrowing.member_id,
                borrow_date=borrowing.borrow_date.isoformat() if borrowing.borrow_date else "",
                return_date=borrowing.return_date.isoformat() if borrowing.return_date else ""
            )
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return Borrowing()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to return book: {str(e)}")
            return Borrowing()
    
    def ListBooks(self, request, context):
        """List all books."""
        try:
            books = self.book_service.get_all_books()
            book_list = []
            for book in books:
                book_list.append(Book(
                    id=book.id,
                    title=book.title,
                    author=book.author,
                    isbn=book.isbn
                ))
            return BookList(books=book_list)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list books: {str(e)}")
            return BookList()
    
    def ListMembers(self, request, context):
        """List all members."""
        try:
            members = self.member_service.get_all_members()
            member_list = []
            for member in members:
                member_list.append(Member(
                    id=member.id,
                    name=member.name,
                    email=member.email,
                    phone=member.phone
                ))
            return MemberList(members=member_list)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list members: {str(e)}")
            return MemberList()
    
    def GetMemberBorrowings(self, request, context):
        """Get all borrowings for a member."""
        try:
            borrowings = self.borrowing_service.get_member_borrowings(request.id)
            borrowing_list = []
            for borrowing in borrowings:
                borrowing_list.append(Borrowing(
                    id=borrowing.id,
                    book_id=borrowing.book_id,
                    member_id=borrowing.member_id,
                    borrow_date=borrowing.borrow_date.isoformat() if borrowing.borrow_date else "",
                    return_date=borrowing.return_date.isoformat() if borrowing.return_date else ""
                ))
            return BorrowingList(borrowings=borrowing_list)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get member borrowings: {str(e)}")
            return BorrowingList()


def create_grpc_server(port: int = 50051, max_workers: int = 10):
    """Create and configure the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    add_LibraryServiceServicer_to_server(LibraryServiceServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    return server 