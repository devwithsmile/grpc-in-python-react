"""
Pytest configuration and fixtures for the Library Service tests.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.models.base import Base
from app.infrastructure.database import get_db_session, DatabaseError
from app.utils.logger import LoggerConfig

# Initialize faker for test data generation
fake = Faker()

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session")
def setup_test_db():
    """Set up test database tables."""
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def db_session(setup_test_db):
    """Provide a database session for testing."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_db_session():
    """Provide a mocked database session."""
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    session.flush = Mock()
    session.refresh = Mock()
    session.query = Mock()
    return session


@pytest.fixture
def mock_get_db_session(mock_db_session):
    """Mock the get_db_session context manager."""
    with patch('app.infrastructure.database.get_db_session') as mock:
        mock.return_value.__enter__ = Mock(return_value=mock_db_session)
        mock.return_value.__exit__ = Mock(return_value=False)
        yield mock


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def mock_validation_service():
    """Mock validation service."""
    with patch('app.services.validation_service.validation_service') as mock:
        mock.validate_data = Mock()
        mock.validate_id = Mock()
        yield mock


@pytest.fixture
def sample_book_data():
    """Sample book data for testing."""
    return {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "978-0743273565"
    }


@pytest.fixture
def sample_member_data():
    """Sample member data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567"
    }


@pytest.fixture
def sample_borrowing_data():
    """Sample borrowing data for testing."""
    return {
        "book_id": 1,
        "member_id": 1
    }


@pytest.fixture
def invalid_book_data():
    """Invalid book data for testing validation."""
    return {
        "title": "",  # Empty title
        "author": "Test Author",
        "isbn": "invalid-isbn"
    }


@pytest.fixture
def invalid_member_data():
    """Invalid member data for testing validation."""
    return {
        "name": "",  # Empty name
        "email": "invalid-email",  # Invalid email
        "phone": "123"  # Invalid phone
    }


@pytest.fixture
def invalid_borrowing_data():
    """Invalid borrowing data for testing validation."""
    return {
        "book_id": 0,  # Invalid ID
        "member_id": -1  # Invalid ID
    }


@pytest.fixture
def mock_flask_app():
    """Mock Flask app for testing."""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def mock_grpc_context():
    """Mock gRPC context for testing."""
    context = Mock()
    context.set_code = Mock()
    context.set_details = Mock()
    return context


@pytest.fixture(autouse=True)
def setup_logging():
    """Set up logging for tests."""
    # Disable logging during tests to avoid noise
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def faker_instance():
    """Provide a faker instance for generating test data."""
    return fake


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_book_data(**kwargs):
        """Create book test data."""
        return {
            "title": kwargs.get("title", fake.sentence(nb_words=3).rstrip('.')),
            "author": kwargs.get("author", fake.name()),
            "isbn": kwargs.get("isbn", fake.isbn13())
        }
    
    @staticmethod
    def create_member_data(**kwargs):
        """Create member test data."""
        return {
            "name": kwargs.get("name", fake.name()),
            "email": kwargs.get("email", fake.email()),
            "phone": kwargs.get("phone", fake.phone_number())
        }
    
    @staticmethod
    def create_borrowing_data(**kwargs):
        """Create borrowing test data."""
        return {
            "book_id": kwargs.get("book_id", fake.random_int(min=1, max=100)),
            "member_id": kwargs.get("member_id", fake.random_int(min=1, max=100))
        }


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "validation: mark test as validation test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as database test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration directory
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Add validation marker to validation tests
        elif "validation" in item.nodeid:
            item.add_marker(pytest.mark.validation)
        # Add database marker to database tests
        elif "database" in item.nodeid:
            item.add_marker(pytest.mark.database)
