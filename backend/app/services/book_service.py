"""
Book service for managing book operations.
"""

from ..models.book import Book
from ..schemas.book_schemas import BookCreateSchema, BookUpdateSchema
from ..services.validation_service import validation_service
from ..services.base_service import BaseService
from ..exceptions.base import ValidationError
from ..exceptions.library_exceptions import BookNotFoundError, BookAlreadyExistsError

class BookService(BaseService):
    """Service for book operations."""
    
    def __init__(self):
        """Initialize the service with logger."""
        super().__init__("book")
    
    def create_book(self, title: str, author: str, isbn: str = None) -> Book:
        """Create a new book."""
        # Validate input data
        try:
            book_data = {
                "title": title,
                "author": author,
                "isbn": isbn
            }
            validated_data = validation_service.validate_data(
                book_data, 
                BookCreateSchema,
                context={"operation": "create_book"}
            )
        except ValidationError as e:
            self._handle_validation_error(e, "create_book", {"title": title, "author": author, "isbn": isbn})
        
        # Create the book
        return self._create_record(
            Book,
            "create_book",
            context={"title": title, "author": author, "isbn": isbn},
            title=validated_data.title,
            author=validated_data.author,
            isbn=validated_data.isbn
        )
    
    def get_book(self, book_id: int) -> Book:
        """Get a book by ID."""
        # Validate book ID
        try:
            validated_id = validation_service.validate_id(book_id, "Book ID")
        except ValidationError as e:
            self._handle_validation_error(e, "get_book", {"book_id": book_id})
        
        return self._get_by_id(
            Book,
            validated_id,
            "get_book",
            BookNotFoundError,
            {"book_id": validated_id}
        )
    
    def get_all_books(self):
        """Get all books."""
        return self._get_all(Book, "get_all_books")
    
    def update_book(self, book_id: int, title: str = None, author: str = None, isbn: str = None) -> Book:
        """Update a book."""
        # Validate book ID
        try:
            validated_id = validation_service.validate_id(book_id, "Book ID")
        except ValidationError as e:
            self._handle_validation_error(e, "update_book", {"book_id": book_id})
        
        # Validate update data if any fields are provided
        if any([title, author, isbn]):
            try:
                update_data = {
                    "title": title,
                    "author": author,
                    "isbn": isbn
                }
                validated_data = validation_service.validate_data(
                    update_data, 
                    BookUpdateSchema,
                    context={"operation": "update_book", "book_id": validated_id}
                )
            except ValidationError as e:
                self._handle_validation_error(e, "update_book", {"book_id": validated_id, "title": title, "author": author, "isbn": isbn})
        
        # Update the book
        update_kwargs = {}
        if title is not None:
            update_kwargs["title"] = validated_data.title
        if author is not None:
            update_kwargs["author"] = validated_data.author
        if isbn is not None:
            update_kwargs["isbn"] = validated_data.isbn
        
        return self._update_record(
            Book,
            validated_id,
            "update_book",
            BookNotFoundError,
            {"book_id": validated_id, "title": title, "author": author, "isbn": isbn},
            **update_kwargs
        )
    
    def delete_book(self, book_id: int) -> bool:
        """Delete a book."""
        # Validate book ID
        try:
            validated_id = validation_service.validate_id(book_id, "Book ID")
        except ValidationError as e:
            self._handle_validation_error(e, "delete_book", {"book_id": book_id})
        
        return self._delete_record(
            Book,
            validated_id,
            "delete_book",
            BookNotFoundError,
            {"book_id": validated_id}
        ) 