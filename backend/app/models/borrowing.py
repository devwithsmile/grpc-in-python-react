"""
Borrowing model for the Library Service.
"""

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Index
from sqlalchemy.orm import relationship
from .base import Base


class Borrowing(Base):
    """Borrowing entity representing a book borrowing transaction."""
    
    __tablename__ = 'borrowings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False, index=True)
    borrow_date = Column(TIMESTAMP, nullable=False)
    return_date = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    member = relationship("Member", backref="borrowings")
    book = relationship("Book", backref="borrowings")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_member_book_active', 'member_id', 'book_id', 'return_date'),
    )
    
    def __repr__(self):
        return f"<Borrowing(id={self.id}, member_id={self.member_id}, book_id={self.book_id})>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None
        }
    
    @property
    def is_active(self):
        """Check if the borrowing is currently active (not returned)."""
        return self.return_date is None 