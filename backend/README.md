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