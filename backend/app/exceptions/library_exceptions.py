"""
Library-specific business logic exceptions.
"""

from typing import Optional, Dict, Any
from .base import BusinessLogicError, ConflictError, OperationNotAllowedError, ErrorCode


class BookNotFoundError(BusinessLogicError):
    """Exception raised when a book is not found."""
    
    def __init__(self, book_id: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Book with ID {book_id} not found",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details=details or {"book_id": book_id, "resource_type": "Book"}
        )


class BookAlreadyExistsError(BusinessLogicError):
    """Exception raised when a book already exists."""
    
    def __init__(self, isbn: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Book with ISBN {isbn} already exists",
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            details=details or {"isbn": isbn, "resource_type": "Book"}
        )


class MemberNotFoundError(BusinessLogicError):
    """Exception raised when a member is not found."""
    
    def __init__(self, member_id: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Member with ID {member_id} not found",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details=details or {"member_id": member_id, "resource_type": "Member"}
        )


class MemberAlreadyExistsError(BusinessLogicError):
    """Exception raised when a member already exists."""
    
    def __init__(self, email: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Member with email {email} already exists",
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            details=details or {"email": email, "resource_type": "Member"}
        )


class BorrowingNotFoundError(BusinessLogicError):
    """Exception raised when a borrowing record is not found."""
    
    def __init__(self, borrowing_id: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Borrowing record with ID {borrowing_id} not found",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details=details or {"borrowing_id": borrowing_id, "resource_type": "Borrowing"}
        )


class BookAlreadyBorrowedError(ConflictError):
    """Exception raised when trying to borrow a book that's already borrowed."""
    
    def __init__(self, book_id: int, current_borrower_id: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Book with ID {book_id} is already borrowed by member {current_borrower_id}",
            conflicting_resource=f"Member {current_borrower_id}",
            details=details or {
                "book_id": book_id,
                "current_borrower_id": current_borrower_id,
                "conflict_type": "book_already_borrowed"
            }
        )


class BookNotBorrowedError(OperationNotAllowedError):
    """Exception raised when trying to return a book that's not borrowed."""
    
    def __init__(self, book_id: int, member_id: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            operation="return_book",
            reason=f"Book {book_id} is not currently borrowed by member {member_id}",
            details=details or {
                "book_id": book_id,
                "member_id": member_id,
                "operation": "return_book"
            }
        )


class BookNotAvailableError(OperationNotAllowedError):
    """Exception raised when a book is not available for borrowing."""
    
    def __init__(self, book_id: int, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            operation="borrow_book",
            reason=f"Book {book_id} is not available: {reason}",
            details=details or {
                "book_id": book_id,
                "reason": reason,
                "operation": "borrow_book"
            }
        )


class MemberHasActiveBorrowingsError(OperationNotAllowedError):
    """Exception raised when trying to delete a member with active borrowings."""
    
    def __init__(self, member_id: int, active_borrowings_count: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            operation="delete_member",
            reason=f"Member {member_id} has {active_borrowings_count} active borrowings",
            details=details or {
                "member_id": member_id,
                "active_borrowings_count": active_borrowings_count,
                "operation": "delete_member"
            }
        )


class BookHasActiveBorrowingsError(OperationNotAllowedError):
    """Exception raised when trying to delete a book with active borrowings."""
    
    def __init__(self, book_id: int, active_borrowings_count: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            operation="delete_book",
            reason=f"Book {book_id} has {active_borrowings_count} active borrowings",
            details=details or {
                "book_id": book_id,
                "active_borrowings_count": active_borrowings_count,
                "operation": "delete_book"
            }
        )


class BorrowingLimitExceededError(OperationNotAllowedError):
    """Exception raised when a member exceeds their borrowing limit."""
    
    def __init__(self, member_id: int, current_borrowings: int, max_borrowings: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            operation="borrow_book",
            reason=f"Member {member_id} has reached borrowing limit ({current_borrowings}/{max_borrowings})",
            details=details or {
                "member_id": member_id,
                "current_borrowings": current_borrowings,
                "max_borrowings": max_borrowings,
                "operation": "borrow_book"
            }
        )


class BorrowingOverdueError(OperationNotAllowedError):
    """Exception raised when trying to perform operations on overdue borrowings."""
    
    def __init__(self, borrowing_id: int, days_overdue: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            operation="return_book",
            reason=f"Borrowing {borrowing_id} is {days_overdue} days overdue",
            details=details or {
                "borrowing_id": borrowing_id,
                "days_overdue": days_overdue,
                "operation": "return_book"
            }
        )


class InvalidBorrowingStateError(OperationNotAllowedError):
    """Exception raised when trying to perform operations on borrowings in invalid states."""
    
    def __init__(self, borrowing_id: int, current_state: str, required_state: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            operation="borrow_book",
            reason=f"Borrowing {borrowing_id} is in state '{current_state}', expected '{required_state}'",
            details=details or {
                "borrowing_id": borrowing_id,
                "current_state": current_state,
                "required_state": required_state,
                "operation": "borrow_book"
            }
        )
