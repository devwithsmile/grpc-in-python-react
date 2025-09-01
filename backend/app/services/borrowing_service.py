"""
Borrowing service for managing book lending operations.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from ..models.borrowing import Borrowing
from ..models.book import Book
from ..models.member import Member
from ..infrastructure.database import get_session, close_session

class BorrowingService:
    """Service for borrowing operations."""
    
    def borrow_book(self, book_id: int, member_id: int) -> Borrowing:
        """Borrow a book."""
        session = get_session()
        try:
            # Check if book exists and is available
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise ValueError("Book not found")
            
            # Check if member exists
            member = session.query(Member).filter(Member.id == member_id).first()
            if not member:
                raise ValueError("Member not found")
            
            # Check if book is already borrowed
            existing_borrowing = session.query(Borrowing).filter(
                Borrowing.book_id == book_id,
                Borrowing.return_date.is_(None)
            ).first()
            
            if existing_borrowing:
                raise ValueError("Book is already borrowed")
            
            # Create borrowing record
            borrowing = Borrowing(
                book_id=book_id,
                member_id=member_id,
                borrow_date=datetime.utcnow()
            )
            session.add(borrowing)
            session.commit()
            session.refresh(borrowing)
            return borrowing
        finally:
            close_session(session)
    
    def return_book(self, book_id: int, member_id: int) -> Borrowing:
        """Return a borrowed book."""
        session = get_session()
        try:
            # Find active borrowing
            borrowing = session.query(Borrowing).filter(
                Borrowing.book_id == book_id,
                Borrowing.member_id == member_id,
                Borrowing.return_date.is_(None)
            ).first()
            
            if not borrowing:
                raise ValueError("No active borrowing found for this book and member")
            
            # Mark as returned
            borrowing.return_date = datetime.utcnow()
            session.commit()
            session.refresh(borrowing)
            return borrowing
        finally:
            close_session(session)
    
    def get_member_borrowings(self, member_id: int):
        """Get all borrowings for a member."""
        session = get_session()
        try:
            return session.query(Borrowing).filter(Borrowing.member_id == member_id).all()
        finally:
            close_session(session)
    
    def get_active_borrowings(self):
        """Get all active (unreturned) borrowings."""
        session = get_session()
        try:
            return session.query(Borrowing).filter(Borrowing.return_date.is_(None)).all()
        finally:
            close_session(session)
    
    def get_borrowing(self, borrowing_id: int) -> Borrowing:
        """Get a borrowing by ID."""
        session = get_session()
        try:
            return session.query(Borrowing).filter(Borrowing.id == borrowing_id).first()
        finally:
            close_session(session) 