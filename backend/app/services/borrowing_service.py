"""
Borrowing service for managing book lending operations.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from ..models.borrowing import Borrowing
from ..models.book import Book
from ..models.member import Member
from ..infrastructure.database import get_session, close_session
from ..utils.logger import LoggerConfig, log_exception, log_function_call, log_function_result
from ..schemas.borrowing_schemas import BorrowingCreateSchema, BorrowingReturnSchema
from ..services.validation_service import validation_service
from ..utils.validators import ValidationError

class BorrowingService:
    """Service for borrowing operations."""
    
    def __init__(self):
        """Initialize the service with logger."""
        self.logger = LoggerConfig.get_logger("services.borrowing")
    
    def borrow_book(self, book_id: int, member_id: int) -> Borrowing:
        """Borrow a book."""
        log_function_call(self.logger, "borrow_book", book_id=book_id, member_id=member_id)
        
        # Validate input data
        try:
            borrowing_data = {
                "book_id": book_id,
                "member_id": member_id
            }
            validated_data = validation_service.validate_data(
                borrowing_data, 
                BorrowingCreateSchema,
                context={"operation": "borrow_book"}
            )
        except ValidationError as e:
            log_exception(self.logger, "Borrowing validation failed", e, book_id=book_id, member_id=member_id)
            raise
        
        session = get_session()
        try:
            # Check if book exists and is available
            book = session.query(Book).filter(Book.id == validated_data.book_id).first()
            if not book:
                self.logger.warning(f"Book with ID {validated_data.book_id} not found for borrowing")
                raise ValueError("Book not found")
            
            # Check if member exists
            member = session.query(Member).filter(Member.id == validated_data.member_id).first()
            if not member:
                self.logger.warning(f"Member with ID {validated_data.member_id} not found for borrowing")
                raise ValueError("Member not found")
            
            # Check if book is already borrowed
            existing_borrowing = session.query(Borrowing).filter(
                Borrowing.book_id == validated_data.book_id,
                Borrowing.return_date.is_(None)
            ).first()
            
            if existing_borrowing:
                self.logger.warning(f"Book {validated_data.book_id} is already borrowed by member {existing_borrowing.member_id}")
                raise ValueError("Book is already borrowed")
            
            # Create borrowing record
            borrowing = Borrowing(
                book_id=validated_data.book_id,
                member_id=validated_data.member_id,
                borrow_date=datetime.utcnow()
            )
            session.add(borrowing)
            session.commit()
            session.refresh(borrowing)
            log_function_result(self.logger, "borrow_book", result=f"Book borrowed successfully", book_id=validated_data.book_id, member_id=validated_data.member_id, borrowing_id=borrowing.id)
            return borrowing
        except Exception as e:
            log_exception(self.logger, "Failed to borrow book", e, book_id=book_id, member_id=member_id)
            raise
        finally:
            close_session(session)
    
    def return_book(self, book_id: int, member_id: int) -> Borrowing:
        """Return a borrowed book."""
        log_function_call(self.logger, "return_book", book_id=book_id, member_id=member_id)
        
        # Validate input data
        try:
            return_data = {
                "book_id": book_id,
                "member_id": member_id
            }
            validated_data = validation_service.validate_data(
                return_data, 
                BorrowingReturnSchema,
                context={"operation": "return_book"}
            )
        except ValidationError as e:
            log_exception(self.logger, "Return validation failed", e, book_id=book_id, member_id=member_id)
            raise
        
        session = get_session()
        try:
            # Find active borrowing
            borrowing = session.query(Borrowing).filter(
                Borrowing.book_id == validated_data.book_id,
                Borrowing.member_id == validated_data.member_id,
                Borrowing.return_date.is_(None)
            ).first()
            
            if not borrowing:
                self.logger.warning(f"No active borrowing found for book {validated_data.book_id} and member {validated_data.member_id}")
                raise ValueError("No active borrowing found for this book and member")
            
            # Mark as returned
            borrowing.return_date = datetime.utcnow()
            session.commit()
            session.refresh(borrowing)
            log_function_result(self.logger, "return_book", result=f"Book returned successfully", book_id=validated_data.book_id, member_id=validated_data.member_id, borrowing_id=borrowing.id)
            return borrowing
        except Exception as e:
            log_exception(self.logger, "Failed to return book", e, book_id=book_id, member_id=member_id)
            raise
        finally:
            close_session(session)
    
    def get_member_borrowings(self, member_id: int):
        """Get all borrowings for a member."""
        log_function_call(self.logger, "get_member_borrowings", member_id=member_id)
        
        # Validate member ID
        try:
            validated_id = validation_service.validate_id(member_id, "Member ID")
        except ValidationError as e:
            log_exception(self.logger, "Member ID validation failed", e, member_id=member_id)
            raise
        
        session = get_session()
        try:
            borrowings = session.query(Borrowing).filter(Borrowing.member_id == validated_id).all()
            log_function_result(self.logger, "get_member_borrowings", result=f"Retrieved {len(borrowings)} borrowings for member", member_id=validated_id)
            return borrowings
        except Exception as e:
            log_exception(self.logger, "Failed to get member borrowings", e, member_id=validated_id)
            raise
        finally:
            close_session(session)
    
    def get_active_borrowings(self):
        """Get all active (unreturned) borrowings."""
        log_function_call(self.logger, "get_active_borrowings")
        session = get_session()
        try:
            borrowings = session.query(Borrowing).filter(Borrowing.return_date.is_(None)).all()
            log_function_result(self.logger, "get_active_borrowings", result=f"Retrieved {len(borrowings)} active borrowings")
            return borrowings
        except Exception as e:
            log_exception(self.logger, "Failed to get active borrowings", e)
            raise
        finally:
            close_session(session)
    
    def get_borrowing(self, borrowing_id: int) -> Borrowing:
        """Get a borrowing by ID."""
        log_function_call(self.logger, "get_borrowing", borrowing_id=borrowing_id)
        
        # Validate borrowing ID
        try:
            validated_id = validation_service.validate_id(borrowing_id, "Borrowing ID")
        except ValidationError as e:
            log_exception(self.logger, "Borrowing ID validation failed", e, borrowing_id=borrowing_id)
            raise
        
        session = get_session()
        try:
            borrowing = session.query(Borrowing).filter(Borrowing.id == validated_id).first()
            if borrowing:
                log_function_result(self.logger, "get_borrowing", result=f"Found borrowing for book {borrowing.book_id}", borrowing_id=validated_id)
            else:
                self.logger.warning(f"Borrowing with ID {validated_id} not found")
            return borrowing
        except Exception as e:
            log_exception(self.logger, "Failed to get borrowing", e, borrowing_id=validated_id)
            raise
        finally:
            close_session(session) 