# Library Service

A simple gRPC-based library management service.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Service
```bash
python main.py
```

That's it! The service will:
- Start PostgreSQL container automatically
- Create database tables
- Start gRPC server on port 50051

## 📁 Project Structure

```
app/
├── api/           # gRPC API
├── models/        # Database models
├── services/      # Business logic
└── main.py        # Application entry point
```

## 🧪 Testing

Use any gRPC client (grpcurl, BloomRPC, etc.) to test the endpoints.

## ⚙️ Configuration

Edit `.env` file to change settings:
- Database connection
- Server port
- Environment

## 📝 Logging

The service includes a centralized logging system with:

- **Structured logging** with consistent formatting
- **Multiple log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **File rotation** to prevent log files from growing too large
- **Exception logging** with full stack traces
- **Contextual information** in log messages

### Log Configuration

Set these environment variables to configure logging:

```bash
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE=true        # Enable file logging
LOG_TO_CONSOLE=true     # Enable console logging
```

### Log Files

- `logs/library_service.log`: All log messages
- `logs/library_service_errors.log`: Only ERROR and CRITICAL messages

See [LOGGING.md](LOGGING.md) for detailed documentation.

## ✅ Input Validation

The service includes comprehensive input validation with:

- **Required field validation** for all mandatory fields
- **Data format validation** (ISBN, email, phone numbers)
- **Custom validators** using Pydantic schemas
- **Detailed error messages** for validation failures
- **Consistent error responses** across REST API and gRPC
- **Validation logging** for monitoring and debugging

### Validation Features

- **ISBN Validation**: Supports ISBN-10 and ISBN-13 with check digit validation
- **Email Validation**: Robust email format validation
- **Phone Validation**: International and local phone number formats
- **String Length**: Configurable min/max length validation
- **ID Validation**: Positive integer validation for all IDs

### Error Response Format

```json
{
    "error": "Validation Error",
    "message": "Title is required and cannot be empty",
    "field": "title",
    "value": "",
    "status_code": 400
}
```

See [VALIDATION.md](VALIDATION.md) for detailed documentation.

## 🚨 Error Handling

The service includes comprehensive error handling with:

- **Custom Exception Classes**: Specific exceptions for different error types
- **gRPC Status Code Mapping**: Proper gRPC status codes for different errors
- **REST API Error Responses**: Consistent HTTP status codes and error formats
- **Structured Error Logging**: Comprehensive logging with context and traceability
- **Error Recovery**: Retry logic and error categorization

### Error Types

- **Validation Errors**: Input validation failures (400 Bad Request)
- **Business Logic Errors**: Business rule violations (422 Unprocessable Entity)
- **Resource Errors**: Not found, conflicts, already exists (404, 409)
- **Database Errors**: Database operation failures (500 Internal Server Error)
- **System Errors**: Internal system failures (500 Internal Server Error)

### Error Response Format

```json
{
    "error": "BookNotFoundError",
    "message": "Book with ID 123 not found",
    "error_code": "RESOURCE_NOT_FOUND",
    "details": {
        "book_id": 123,
        "resource_type": "Book"
    },
    "status_code": 404
}
```

See [ERROR_HANDLING.md](ERROR_HANDLING.md) for detailed documentation.

## 🧪 Testing

The service includes comprehensive testing with unit tests, integration tests, and edge case coverage.

### Test Types

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints and service interactions
- **Validation Tests**: Test input validation and error handling
- **Edge Case Tests**: Test boundary conditions and error scenarios

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --validation    # Validation tests only

# Run with coverage report
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose
```

### Test Coverage

The test suite provides comprehensive coverage including:

- **Validation Logic**: ISBN, email, phone, and required field validation
- **Service Layer**: All CRUD operations with error handling
- **API Endpoints**: REST API and gRPC service endpoints
- **Database Operations**: Context managers and error handling
- **Edge Cases**: Boundary values, concurrent access, error recovery
- **Error Scenarios**: Validation errors, database errors, business logic errors

### Test Configuration

Tests are configured in `pytest.ini` with:
- Coverage reporting (minimum 80% coverage required)
- Test markers for different test types
- Warning filters for clean output
- HTML and XML coverage reports

### Manual Testing

```bash
# Test gRPC service
python test_client.py

# Test REST API
python rest_api.py
# Then visit http://localhost:5000/health
``` 