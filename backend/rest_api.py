from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Library REST API"})

# Books endpoints
@app.route('/books', methods=['GET'])
def get_books():
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
        
        return jsonify(book_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        book = book_service.get_book(book_id)
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/books', methods=['POST'])
def create_book():
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        data = request.get_json()
        book = book_service.create_book(
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn')
        )
        
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        from app.services.book_service import BookService
        book_service = BookService()
        data = request.get_json()
        book = book_service.update_book(
            book_id=book_id,
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn')
        )
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'created_at': book.created_at.isoformat() if book.created_at else None,
            'updated_at': book.updated_at.isoformat() if book.updated_at else None
        })
    except Exception as e:
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
    try:
        from app.services.member_service import MemberService
        member_service = MemberService()
        data = request.get_json()
        member = member_service.create_member(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone')
        )
        
        return jsonify({
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'phone': member.phone,
            'created_at': member.created_at.isoformat() if member.created_at else None,
            'updated_at': member.updated_at.isoformat() if member.updated_at else None
        }), 201
    except Exception as e:
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
    try:
        from app.services.borrowing_service import BorrowingService
        borrowing_service = BorrowingService()
        data = request.get_json()
        borrowing = borrowing_service.borrow_book(
            book_id=data.get('book_id'),
            member_id=data.get('member_id')
        )
        
        return jsonify({
            'id': borrowing.id,
            'book_id': borrowing.book_id,
            'member_id': borrowing.member_id,
            'borrow_date': borrowing.borrow_date.isoformat() if borrowing.borrow_date else None,
            'return_date': borrowing.return_date.isoformat() if borrowing.return_date else None,
            'is_returned': borrowing.return_date is not None
        }), 201
    except Exception as e:
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
    print(f"Starting Library REST API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False) 