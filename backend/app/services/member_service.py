"""
Member service for managing member operations.
"""

from ..models.member import Member
from ..schemas.member_schemas import MemberCreateSchema, MemberUpdateSchema
from ..services.validation_service import validation_service
from ..services.base_service import BaseService
from ..exceptions.base import ValidationError
from ..exceptions.library_exceptions import MemberNotFoundError, MemberAlreadyExistsError

class MemberService(BaseService):
    """Service for member operations."""
    
    def __init__(self):
        """Initialize the service with logger."""
        super().__init__("member")
    
    def create_member(self, name: str, email: str, phone: str = None) -> Member:
        """Create a new member."""
        # Validate input data
        try:
            member_data = {
                "name": name,
                "email": email,
                "phone": phone
            }
            validated_data = validation_service.validate_data(
                member_data, 
                MemberCreateSchema,
                context={"operation": "create_member"}
            )
        except ValidationError as e:
            self._handle_validation_error(e, "create_member", {"name": name, "email": email, "phone": phone})
        
        # Create the member
        return self._create_record(
            Member,
            "create_member",
            context={"name": name, "email": email, "phone": phone},
            name=validated_data.name,
            email=validated_data.email,
            phone=validated_data.phone
        )
    
    def get_member(self, member_id: int) -> Member:
        """Get a member by ID."""
        # Validate member ID
        try:
            validated_id = validation_service.validate_id(member_id, "Member ID")
        except ValidationError as e:
            self._handle_validation_error(e, "get_member", {"member_id": member_id})
        
        return self._get_by_id(
            Member,
            validated_id,
            "get_member",
            MemberNotFoundError,
            {"member_id": validated_id}
        )
    
    def get_all_members(self):
        """Get all members."""
        return self._get_all(Member, "get_all_members")
    
    def update_member(self, member_id: int, name: str = None, email: str = None, phone: str = None) -> Member:
        """Update a member."""
        log_function_call(self.logger, "update_member", member_id=member_id, name=name, email=email, phone=phone)
        
        # Validate member ID
        try:
            validated_id = validation_service.validate_id(member_id, "Member ID")
        except ValidationError as e:
            log_exception(self.logger, "Member ID validation failed", e, member_id=member_id)
            raise
        
        # Validate update data if any fields are provided
        if any([name, email, phone]):
            try:
                update_data = {
                    "name": name,
                    "email": email,
                    "phone": phone
                }
                validated_data = validation_service.validate_data(
                    update_data, 
                    MemberUpdateSchema,
                    context={"operation": "update_member", "member_id": validated_id}
                )
            except ValidationError as e:
                log_exception(self.logger, "Member update validation failed", e, member_id=validated_id, name=name, email=email, phone=phone)
                raise
        
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == validated_id).first()
            if member:
                if name is not None:
                    member.name = validated_data.name
                if email is not None:
                    member.email = validated_data.email
                if phone is not None:
                    member.phone = validated_data.phone
                session.commit()
                session.refresh(member)
                log_function_result(self.logger, "update_member", result=f"Updated member: {member.name}", member_id=validated_id)
            else:
                self.logger.warning(f"Member with ID {validated_id} not found for update")
            return member
        except Exception as e:
            log_exception(self.logger, "Failed to update member", e, member_id=validated_id, name=name, email=email, phone=phone)
            raise
        finally:
            close_session(session)
    
    def delete_member(self, member_id: int) -> bool:
        """Delete a member."""
        log_function_call(self.logger, "delete_member", member_id=member_id)
        
        # Validate member ID
        try:
            validated_id = validation_service.validate_id(member_id, "Member ID")
        except ValidationError as e:
            log_exception(self.logger, "Member ID validation failed", e, member_id=member_id)
            raise
        
        session = get_session()
        try:
            member = session.query(Member).filter(Member.id == validated_id).first()
            if member:
                session.delete(member)
                session.commit()
                log_function_result(self.logger, "delete_member", result=f"Deleted member: {member.name}", member_id=validated_id)
                return True
            else:
                self.logger.warning(f"Member with ID {validated_id} not found for deletion")
                return False
        except Exception as e:
            log_exception(self.logger, "Failed to delete member", e, member_id=validated_id)
            raise
        finally:
            close_session(session) 