"""
Book service for managing book operations.
"""

from sqlalchemy.orm import Session
from ..models.book import Book
from ..infrastructure.database import get_session, close_session

class BookService:
    """Service for book operations."""
    
    def create_book(self, title: str, author: str, isbn: str = None) -> Book:
        """Create a new book."""
        session = get_session()
        try:
            book = Book(title=title, author=author, isbn=isbn)
            session.add(book)
            session.commit()
            session.refresh(book)
            return book
        finally:
            close_session(session)
    
    def get_book(self, book_id: int) -> Book:
        """Get a book by ID."""
        session = get_session()
        try:
            return session.query(Book).filter(Book.id == book_id).first()
        finally:
            close_session(session)
    
    def get_all_books(self):
        """Get all books."""
        session = get_session()
        try:
            return session.query(Book).all()
        finally:
            close_session(session)
    
    def update_book(self, book_id: int, title: str = None, author: str = None, isbn: str = None) -> Book:
        """Update a book."""
        session = get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                if title:
                    book.title = title
                if author:
                    book.author = author
                if isbn:
                    book.isbn = isbn
                session.commit()
                session.refresh(book)
            return book
        finally:
            close_session(session)
    
    def delete_book(self, book_id: int) -> bool:
        """Delete a book."""
        session = get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                session.delete(book)
                session.commit()
                return True
            return False
        finally:
            close_session(session) 