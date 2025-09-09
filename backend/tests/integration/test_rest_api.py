"""
Integration tests for REST API endpoints.
"""

import pytest
import json
from unittest.mock import patch, Mock
from flask import Flask

# Import the REST API app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from rest_api import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestBooksAPI:
    """Test books REST API endpoints."""
    
    def test_get_books_success(self, client, mock_get_db_session):
        """Test successful GET /books."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_book = Mock()
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        mock_book.isbn = "9780743273565"
        mock_book.created_at = None
        mock_book.updated_at = None
        mock_session.query.return_value.all.return_value = [mock_book]
        
        # Execute
        response = client.get('/books')
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['title'] == "Test Book"
        assert data[0]['author'] == "Test Author"
        assert data[0]['isbn'] == "9780743273565"
    
    def test_get_book_success(self, client, mock_get_db_session, mock_validation_service):
        """Test successful GET /books/<id>."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_book = Mock()
        mock_book.id = 1
        mock_book.title = "Test Book"
        mock_book.author = "Test Author"
        mock_book.isbn = "9780743273565"
        mock_book.created_at = None
        mock_book.updated_at = None
        mock_session.query.return_value.filter.return_value.first.return_value = mock_book
        
        # Execute
        response = client.get('/books/1')
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == "Test Book"
        assert data['author'] == "Test Author"
        assert data['isbn'] == "9780743273565"
    
    def test_get_book_not_found(self, client, mock_get_db_session, mock_validation_service):
        """Test GET /books/<id> when book not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        response = client.get('/books/1')
        
        # Verify
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == "Book not found"
    
    def test_create_book_success(self, client, mock_get_db_session, mock_validation_service, sample_book_data):
        """Test successful POST /books."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="9780743273565"
        )
        mock_book = Mock()
        mock_book.id = 1
        mock_book.title = "The Great Gatsby"
        mock_book.author = "F. Scott Fitzgerald"
        mock_book.isbn = "9780743273565"
        mock_book.created_at = None
        mock_book.updated_at = None
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        response = client.post('/books', 
                             data=json.dumps(sample_book_data),
                             content_type='application/json')
        
        # Verify
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == "The Great Gatsby"
        assert data['author'] == "F. Scott Fitzgerald"
        assert data['isbn'] == "9780743273565"
    
    def test_create_book_validation_error(self, client, mock_validation_service, invalid_book_data):
        """Test POST /books with validation error."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid data", "title", "")
        
        # Execute
        response = client.post('/books',
                             data=json.dumps(invalid_book_data),
                             content_type='application/json')
        
        # Verify
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Validation Error"
        assert "Invalid data" in data['message']
    
    def test_create_book_no_json(self, client):
        """Test POST /books with no JSON data."""
        # Execute
        response = client.post('/books')
        
        # Verify
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "No JSON data provided"
    
    def test_update_book_success(self, client, mock_get_db_session, mock_validation_service):
        """Test successful PUT /books/<id>."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_validation_service.validate_data.return_value = Mock(
            title="Updated Title",
            author="Updated Author",
            isbn="9780743273565"
        )
        mock_book = Mock()
        mock_book.id = 1
        mock_book.title = "Updated Title"
        mock_book.author = "Updated Author"
        mock_book.isbn = "9780743273565"
        mock_book.created_at = None
        mock_book.updated_at = None
        mock_session.query.return_value.filter.return_value.first.return_value = mock_book
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        update_data = {
            "title": "Updated Title",
            "author": "Updated Author",
            "isbn": "978-0743273565"
        }
        
        # Execute
        response = client.put('/books/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == "Updated Title"
        assert data['author'] == "Updated Author"
        assert data['isbn'] == "9780743273565"
    
    def test_update_book_not_found(self, client, mock_get_db_session, mock_validation_service):
        """Test PUT /books/<id> when book not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_validation_service.validate_data.return_value = Mock(
            title="Updated Title",
            author="Updated Author",
            isbn="9780743273565"
        )
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        update_data = {
            "title": "Updated Title",
            "author": "Updated Author",
            "isbn": "978-0743273565"
        }
        
        # Execute
        response = client.put('/books/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        # Verify
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == "Book not found"
    
    def test_delete_book_success(self, client, mock_get_db_session, mock_validation_service):
        """Test successful DELETE /books/<id>."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_book = Mock()
        mock_book.title = "Test Book"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_book
        mock_session.delete.return_value = None
        mock_session.flush.return_value = None
        
        # Execute
        response = client.delete('/books/1')
        
        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Book deleted successfully"
    
    def test_delete_book_not_found(self, client, mock_get_db_session, mock_validation_service):
        """Test DELETE /books/<id> when book not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        response = client.delete('/books/1')
        
        # Verify
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == "Book not found"


class TestMembersAPI:
    """Test members REST API endpoints."""
    
    def test_create_member_success(self, client, mock_get_db_session, mock_validation_service, sample_member_data):
        """Test successful POST /members."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(
            name="John Doe",
            email="john.doe@example.com",
            phone="+15551234567"
        )
        mock_member = Mock()
        mock_member.id = 1
        mock_member.name = "John Doe"
        mock_member.email = "john.doe@example.com"
        mock_member.phone = "+15551234567"
        mock_member.created_at = None
        mock_member.updated_at = None
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        response = client.post('/members',
                             data=json.dumps(sample_member_data),
                             content_type='application/json')
        
        # Verify
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == "John Doe"
        assert data['email'] == "john.doe@example.com"
        assert data['phone'] == "+15551234567"
    
    def test_create_member_validation_error(self, client, mock_validation_service, invalid_member_data):
        """Test POST /members with validation error."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid email", "email", "invalid")
        
        # Execute
        response = client.post('/members',
                             data=json.dumps(invalid_member_data),
                             content_type='application/json')
        
        # Verify
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Validation Error"
        assert "Invalid email" in data['message']


class TestBorrowingsAPI:
    """Test borrowings REST API endpoints."""
    
    def test_borrow_book_success(self, client, mock_get_db_session, mock_validation_service, sample_borrowing_data):
        """Test successful POST /borrowings."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        
        # Mock book and member existence
        mock_book = Mock()
        mock_member = Mock()
        mock_session.query.return_value.filter.return_value.first.side_effect = [mock_book, mock_member, None]  # book, member, existing borrowing
        
        mock_borrowing = Mock()
        mock_borrowing.id = 1
        mock_borrowing.book_id = 1
        mock_borrowing.member_id = 1
        mock_borrowing.borrow_date = None
        mock_borrowing.return_date = None
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        response = client.post('/borrowings',
                             data=json.dumps(sample_borrowing_data),
                             content_type='application/json')
        
        # Verify
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['book_id'] == 1
        assert data['member_id'] == 1
        assert data['is_returned'] is False
    
    def test_borrow_book_validation_error(self, client, mock_validation_service, invalid_borrowing_data):
        """Test POST /borrowings with validation error."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid ID", "book_id", 0)
        
        # Execute
        response = client.post('/borrowings',
                             data=json.dumps(invalid_borrowing_data),
                             content_type='application/json')
        
        # Verify
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Validation Error"
        assert "Invalid ID" in data['message']
    
    def test_borrow_book_business_logic_error(self, client, mock_get_db_session, mock_validation_service):
        """Test POST /borrowings with business logic error."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = None  # Book not found
        
        borrowing_data = {"book_id": 1, "member_id": 1}
        
        # Execute
        response = client.post('/borrowings',
                             data=json.dumps(borrowing_data),
                             content_type='application/json')
        
        # Verify
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Book not found" in data['error']


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test GET /health."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == "healthy"
        assert data['service'] == "Library REST API"
