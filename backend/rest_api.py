from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add app to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.logger import LoggerConfig, log_exception
from app.schemas.book_schemas import BookCreateSchema, BookUpdateSchema
from app.schemas.member_schemas import MemberCreateSchema, MemberUpdateSchema
from app.schemas.borrowing_schemas import BorrowingCreateSchema, BorrowingReturnSchema
from app.services.validation_service import validation_service
from app.utils.validators import ValidationError as OldValidationError
from app.exceptions.base import ValidationError, LibraryServiceError
from app.exceptions.error_handler import error_handler

app = Flask(__name__)
CORS(app)

# Initialize logger for REST API
logger = LoggerConfig.get_logger("rest_api")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Library REST API"})

# Books endpoints
@app.route('/books', methods=['GET'])
def get_books():
    logger.info("GET /books - Retrieving all books")
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        books = book_service.get_all_books()
        
        book_list = []
        for book in books:
            book_list.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'created_at': book.created_at.isoformat() if book.created_at else None,
                'updated_at': book.updated_at.isoformat() if book.updated_at else None
            })
        
        logger.info(f"Successfully retrieved {len(book_list)} books")
        return jsonify(book_list)
    except Exception as e:
        log_exception(logger, "Failed to retrieve books", e)
        return jsonify({"error": str(e)}), 500

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    logger.info(f"GET /books/{book_id} - Retrieving book")
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        book = book_service.get_book(book_id)
        
        if not book:
            logger.warning(f"Book with ID {book_id} not found")
            return jsonify({"error": "Book not found"}), 404
        
        logger.info(f"Successfully retrieved book: {book.title}")
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        })
    except Exception as e:
        log_exception(logger, f"Failed to retrieve book {book_id}", e, book_id=book_id)
        return jsonify({"error": str(e)}), 500

@app.route('/books', methods=['POST'])
def create_book():
    logger.info("POST /books - Creating new book")
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided for book creation")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate input data
        try:
            validated_data = validation_service.validate_data(
                data, 
                BookCreateSchema,
                context={"endpoint": "POST /books", "operation": "create_book"}
            )
        except LibraryServiceError as e:
            _, http_status, error_response = error_handler.handle_rest_exception(
                e,
                context={"data": data},
                operation="create_book"
            )
            return jsonify(error_response), http_status
        
        book = book_service.create_book(
            title=validated_data.title,
            author=validated_data.author,
            isbn=validated_data.isbn
        )
        
        logger.info(f"Successfully created book: {book.title} (ID: {book.id})")
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        }), 201
    except LibraryServiceError as e:
        _, http_status, error_response = error_handler.handle_rest_exception(
            e,
            context={"data": data},
            operation="create_book"
        )
        return jsonify(error_response), http_status
    except Exception as e:
        _, http_status, error_response = error_handler.handle_rest_exception(
            e,
            context={"data": data},
            operation="create_book"
        )
        return jsonify(error_response), http_status

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    logger.info(f"PUT /books/{book_id} - Updating book")
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided for book update")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate input data
        try:
            validated_data = validation_service.validate_data(
                data, 
                BookUpdateSchema,
                context={"endpoint": f"PUT /books/{book_id}", "operation": "update_book", "book_id": book_id}
            )
        except ValidationError as e:
            error_response = validation_service.create_validation_error_response(e, 400)
            logger.warning(f"Book update validation failed: {e.message}")
            return jsonify(error_response), 400
        
        book = book_service.update_book(
            book_id=book_id,
            title=validated_data.title,
            author=validated_data.author,
            isbn=validated_data.isbn
        )
        
        if not book:
            logger.warning(f"Book with ID {book_id} not found for update")
            return jsonify({"error": "Book not found"}), 404
        
        logger.info(f"Successfully updated book: {book.title} (ID: {book.id})")
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        })
    except ValidationError as e:
        error_response = validation_service.create_validation_error_response(e, 400)
        logger.warning(f"Book update validation failed: {e.message}")
        return jsonify(error_response), 400
    except Exception as e:
        log_exception(logger, f"Failed to update book {book_id}", e, book_id=book_id, data=data)
        return jsonify({"error": str(e)}), 500

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        success = book_service.delete_book(book_id)
        
        if not success:
            return jsonify({"error": "Book not found"}), 404
        
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Members endpoints
@app.route('/members', methods=['GET'])
def get_members():
    try:
        from app.services.member_service import MemberService
        member_service = MemberService()
        members = member_service.get_all_members()
        
        member_list = []
        for member in members:
            member_list.append({
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'phone': member.phone,
                'created_at': member.created_at.isoformat() if member.created_at else None,
                'updated_at': member.updated_at.isoformat() if member.updated_at else None
            })
        
        return jsonify(member_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        from app.services.member_service import MemberService
        member_service = MemberService()
        member = member_service.get_member(member_id)
        
        if not member:
            return jsonify({"error": "Member not found"}), 404
        
        return jsonify({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'phone': member.phone,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'updated_at': member.updated_at.isoformat() if member.updated_at else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/members', methods=['POST'])
def create_member():
    logger.info("POST /members - Creating new member")
    try:
        from app.services.member_service import MemberService
        member_service = MemberService()
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided for member creation")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate input data
        try:
            validated_data = validation_service.validate_data(
                data, 
                MemberCreateSchema,
                context={"endpoint": "POST /members", "operation": "create_member"}
            )
        except ValidationError as e:
            error_response = validation_service.create_validation_error_response(e, 400)
            logger.warning(f"Member creation validation failed: {e.message}")
            return jsonify(error_response), 400
        
        member = member_service.create_member(
            name=validated_data.name,
            email=validated_data.email,
            phone=validated_data.phone
        )
        
        logger.info(f"Successfully created member: {member.name} (ID: {member.id})")
        return jsonify({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'phone': member.phone,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'updated_at': member.updated_at.isoformat() if member.updated_at else None
        }), 201
    except ValidationError as e:
        error_response = validation_service.create_validation_error_response(e, 400)
        logger.warning(f"Member creation validation failed: {e.message}")
        return jsonify(error_response), 400
    except Exception as e:
        log_exception(logger, "Failed to create member", e, data=data)
        return jsonify({"error": str(e)}), 500

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    try:
        from app.services.member_service import MemberService
        member_service = MemberService()
        data = request.get_json()
        member = member_service.update_member(
            member_id=member_id,
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone')
        )
        
        if not member:
            return jsonify({"error": "Member not found"}), 404
        
        return jsonify({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'phone': member.phone,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'updated_at': member.updated_at.isoformat() if member.updated_at else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        from app.services.member_service import MemberService
        member_service = MemberService()
        success = member_service.delete_member(member_id)
        
        if not success:
            return jsonify({"error": "Member not found"}), 404
        
        return jsonify({"message": "Member deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Borrowings endpoints
@app.route('/borrowings', methods=['GET'])
def get_borrowings():
    try:
        from app.services.borrowing_service import BorrowingService
        borrowing_service = BorrowingService()
        borrowings = borrowing_service.get_active_borrowings()
        
        borrowing_list = []
        for borrowing in borrowings:
            borrowing_list.append({
                'id': borrowing.id,
                'book_id': borrowing.book_id,
                'member_id': borrowing.member_id,
                'borrow_date': borrowing.borrow_date.isoformat() if borrowing.borrow_date else None,
                'return_date': borrowing.return_date.isoformat() if borrowing.return_date else None,
                'is_returned': borrowing.return_date is not None
            })
        
        return jsonify(borrowing_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/borrowings', methods=['POST'])
def borrow_book():
    logger.info("POST /borrowings - Borrowing book")
    try:
        from app.services.borrowing_service import BorrowingService
        borrowing_service = BorrowingService()
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided for book borrowing")
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate input data
        try:
            validated_data = validation_service.validate_data(
                data, 
                BorrowingCreateSchema,
                context={"endpoint": "POST /borrowings", "operation": "borrow_book"}
            )
        except ValidationError as e:
            error_response = validation_service.create_validation_error_response(e, 400)
            logger.warning(f"Book borrowing validation failed: {e.message}")
            return jsonify(error_response), 400
        
        borrowing = borrowing_service.borrow_book(
            book_id=validated_data.book_id,
            member_id=validated_data.member_id
        )
        
        logger.info(f"Successfully borrowed book {borrowing.book_id} by member {borrowing.member_id}")
        return jsonify({
            'id': borrowing.id,
            'book_id': borrowing.book_id,
            'member_id': borrowing.member_id,
            'borrow_date': borrowing.borrow_date.isoformat() if borrowing.borrow_date else None,
            'return_date': borrowing.return_date.isoformat() if borrowing.return_date else None,
            'is_returned': borrowing.return_date is not None
        }), 201
    except ValidationError as e:
        error_response = validation_service.create_validation_error_response(e, 400)
        logger.warning(f"Book borrowing validation failed: {e.message}")
        return jsonify(error_response), 400
    except ValueError as e:
        logger.warning(f"Business logic error in book borrowing: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        log_exception(logger, "Failed to borrow book", e, data=data)
        return jsonify({"error": str(e)}), 500

@app.route('/borrowings/return', methods=['POST'])
def return_book():
    try:
        from app.services.borrowing_service import BorrowingService
        borrowing_service = BorrowingService()
        data = request.get_json()
        borrowing = borrowing_service.return_book(
            book_id=data.get('book_id'),
            member_id=data.get('member_id')
        )
        
        if not borrowing:
            return jsonify({"error": "Borrowing not found"}), 404
        
        return jsonify({
            'id': borrowing.id,
            'book_id': borrowing.book_id,
            'member_id': borrowing.member_id,
            'borrow_date': borrowing.borrow_date.isoformat() if borrowing.borrow_date else None,
            'return_date': borrowing.return_date.isoformat() if borrowing.return_date else None,
            'is_returned': borrowing.return_date is not None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/borrowings/member/<int:member_id>', methods=['GET'])
def get_member_borrowings(member_id):
    try:
        from app.services.borrowing_service import BorrowingService
        borrowing_service = BorrowingService()
        borrowings = borrowing_service.get_member_borrowings(member_id)
        
        borrowing_list = []
        for borrowing in borrowings:
            borrowing_list.append({
                'id': borrowing.id,
                'book_id': borrowing.book_id,
                'member_id': borrowing.member_id,
                'borrow_date': borrowing.borrow_date.isoformat() if borrowing.borrow_date else None,
                'return_date': borrowing.return_date.isoformat() if borrowing.return_date else None,
                'is_returned': borrowing.return_date is not None
            })
        
        return jsonify(borrowing_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('REST_PORT', 8000))
    logger.info(f"Starting Library REST API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False) 