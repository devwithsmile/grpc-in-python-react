"""
Member service for managing member operations.
"""

from sqlalchemy.orm import Session
from ..models.member import Member
from ..infrastructure.database import get_session, close_session

class MemberService:
    """Service for member operations."""
    
    def create_member(self, name: str, email: str, phone: str = None) -> Member:
        """Create a new member."""
        session = get_session()
        try:
            member = Member(name=name, email=email, phone=phone)
            session.add(member)
            session.commit()
            session.refresh(member)
            return member
        finally:
            close_session(session)
    
    def get_member(self, member_id: int) -> Member:
        """Get a member by ID."""
        session = get_session()
        try:
            return session.query(Member).filter(Member.id == member_id).first()
        finally:
            close_session(session)
    
    def get_all_members(self):
        """Get all members."""
        session = get_session()
        try:
            return session.query(Member).all()
        finally:
            close_session(session)
    
    def update_member(self, member_id: int, name: str = None, email: str = None, phone: str = None) -> Member:
        """Update a member."""
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            if member:
                if name:
                    member.name = name
                if email:
                    member.email = email
                if phone:
                    member.phone = phone
                session.commit()
                session.refresh(member)
            return member
        finally:
            close_session(session)
    
    def delete_member(self, member_id: int) -> bool:
        """Delete a member."""
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == member_id).first()
            if member:
                session.delete(member)
                session.commit()
                return True
            return False
        finally:
            close_session(session) 