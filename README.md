# Subscription Management API

A robust, modular Flask-based REST API for managing subscription services with automatic renewals, payment processing, and comprehensive coverage tracking.

## 🌟 Features

- **Automatic 24-hour subscription renewals**
- **Off command with 24-hour grace period**
- **Payment processing simulation**
- **Real-time coverage tracking**
- **Historical reporting**
- **Background service management**
- **Data persistence with JSON storage**
- **Comprehensive logging and monitoring**
- **Production-ready configuration management**

## 📁 Project Structure

```
subscription-api/
├── 📄 models.py              # Data models and type definitions
├── 🔧 services.py            # Business logic and core services
├── 🌐 routes.py              # API route handlers and validation
├── 🏭 app.py                 # Flask application factory
├── 🚀 server.py              # Main server entry point
├── ⚙️  config.py              # Configuration management
├── 📦 requirements.txt       # Python dependencies
├── 🧪 api_examples.py        # API testing and usage examples
├── 📋 README.md              # This documentation
├── 🔒 .env                   # Environment variables (create this)
├── 📊 subscription_data.json # Data storage (auto-created)
└── 📁 logs/
    └── subscription_api.log  # Application logs
```

## 📄 File Descriptions

### Core Application Files

#### `models.py` - Data Models
**Purpose**: Defines data structures and business entities
- `SubscriptionState` enum (ACTIVE, PENDING_OFF, OFF)
- `User` class with subscription data and methods
- `PaymentResult` and `ServiceResponse` for structured responses
- Serialization/deserialization methods for JSON storage

```python
# Example usage
user = User("user123")
user.state = SubscriptionState.ACTIVE
user.add_payment(10.0, "success")
```

#### `services.py` - Business Logic
**Purpose**: Contains all business logic and service classes
- `SubscriptionService`: Main subscription management
- `PaymentService`: Payment processing simulation
- `DataService`: File-based data persistence
- `CoverageService`: Coverage calculation and reporting

```python
# Example usage
subscription_service = SubscriptionService()
result = subscription_service.purchase_subscription("user123")
```

#### `routes.py` - API Routes
**Purpose**: HTTP request handling and API endpoint definitions
- Request validation and error handling
- JSON serialization/deserialization
- Blueprint organization (API routes + Admin routes)
- Input sanitization and response formatting

```python
# Endpoints defined:
# POST /subscription/purchase
# POST /subscription/off
# GET  /subscription/status/{user_id}
# GET  /subscription/coverage/{user_id}
# GET  /admin/users
```

#### `app.py` - Application Factory
**Purpose**: Flask application creation and dependency injection
- Environment-specific app configuration
- Service initialization and wiring
- Blueprint registration
- Error handler setup
- Request/response middleware

```python
# Usage
app, service = create_app()
app, service = create_production_app()
app, service = create_development_app()
```

#### `server.py` - Main Entry Point
**Purpose**: Server startup, configuration, and lifecycle management
- Command-line interface
- Signal handling for graceful shutdown
- Environment detection
- Service startup coordination
- Logging configuration

```bash
# Usage
python server.py
FLASK_ENV=production python server.py
```

#### `config.py` - Configuration Management
**Purpose**: Environment-specific configuration and validation
- `Config` base class with common settings
- `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`
- Environment variable parsing
- Configuration validation
- Security settings

```python
# Usage
config = get_config('production')
is_valid, errors = validate_environment()
```

### Support Files

#### `requirements.txt` - Dependencies
**Purpose**: Python package dependencies
```
Flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
```

#### `api_examples.py` - Testing and Examples
**Purpose**: Comprehensive testing suite and usage examples
- `SubscriptionAPIClient` class for API interaction
- Automated test suite
- Lifecycle demonstration
- cURL examples for manual testing

```bash
python api_examples.py test   # Run tests
python api_examples.py demo   # Run demo
python api_examples.py curl   # Show cURL examples
```

## 🚀 Quick Start Guide

### 1. Installation

```bash
# Clone or create project directory
mkdir subscription-api && cd subscription-api

# Install dependencies
pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# Environment Configuration
FLASK_ENV=development          # development, production, or testing

# Server Settings
HOST=0.0.0.0                  # Server host
PORT=5013                     # Server port

# Application Settings
DATA_FILE=subscription_data.json           # Data storage file
RENEWAL_INTERVAL_HOURS=24                  # Auto-renewal interval
PAYMENT_SUCCESS_RATE=0.9                   # Payment simulation success rate
SUBSCRIPTION_PRICE=10.0                    # Subscription price

# Logging
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
LOG_FILE=subscription_api.log # Log file path

# Security (IMPORTANT for production)
SECRET_KEY=your-super-secret-key-change-this
```

### 3. Start the Server

```bash
# Development mode
FLASK_ENV=development python server.py

# Production mode
FLASK_ENV=production python server.py

# Custom port
PORT=8080 python server.py
```

**Expected Output:**
```
🚀 Starting development server...
✅ Subscription service started
🌐 Server starting on http://0.0.0.0:5013
📝 Environment: development
🔧 Debug mode: True
💾 Data file: dev_subscription_data.json
⏰ Renewal interval: 1 hours

📚 API Documentation:
  Health Check:      GET  /health
  Purchase Sub:      POST /subscription/purchase
  Turn Off Sub:      POST /subscription/off
  Check Status:      GET  /subscription/status/{user_id}
  Coverage Report:   GET  /subscription/coverage/{user_id}
  Admin - All Users: GET  /admin/users
  
🔗 Quick test: curl http://localhost:5013/health
🛑 Press Ctrl+C to stop
```

### 4. Verify Installation

```bash
# Health check
curl http://localhost:5013/health

# Expected response
{
  "status": "healthy",
  "service": {
    "service_running": true,
    "total_users": 0,
    "active_users": 0,
    "pending_off_users": 0,
    "inactive_users": 0,
    "renewal_interval_hours": 24.0
  },
  "timestamp": "2025-07-31T12:00:00"
}
```

## 📚 API Usage Guide

### Authentication
Currently, no authentication is required. In production, add authentication middleware.

### Request Format
All POST requests require `Content-Type: application/json`

### Response Format
All responses follow this structure:
```json
{
  "success": true,
  "message": "Description of result",
  "data": { /* optional data object */ },
  "timestamp": "2025-07-31T12:00:00"
}
```

### Core API Endpoints

#### 1. Purchase Subscription

```bash
curl -X POST http://localhost:5013/subscription/purchase \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Subscription activated for user user123",
  "data": {
    "user_state": {
      "user_id": "user123",
      "state": "active",
      "is_covered": true,
      "subscription_start": "2025-07-31T12:00:00",
      "last_renewal": "2025-07-31T12:00:00",
      "next_renewal": "2025-08-01T12:00:00"
    }
  },
  "timestamp": "2025-07-31T12:00:00"
}
```

#### 2. Check Subscription Status

```bash
curl http://localhost:5013/subscription/status/user123
```

**Response:**
```json
{
  "user_id": "user123",
  "state": "active",
  "is_covered": true,
  "subscription_start": "2025-07-31T12:00:00",
  "last_renewal": "2025-07-31T12:00:00",
  "off_command_time": null,
  "next_renewal": "2025-08-01T12:00:00",
  "payment_history_count": 1,
  "coverage_periods_count": 1
}
```

#### 3. Issue Off Command

```bash
curl -X POST http://localhost:5013/subscription/off \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Off command processed for user user123. Subscription will end after 24 hours.",
  "data": {
    "user_state": {
      "user_id": "user123",
      "state": "pending_off",
      "is_covered": true,
      "off_command_time": "2025-07-31T12:00:00"
    }
  },
  "timestamp": "2025-07-31T12:00:00"
}
```

#### 4. Get Coverage Report

```bash
curl "http://localhost:5013/subscription/coverage/user123?start_date=2025-07-30T12:00:00&end_date=2025-07-31T12:00:00"
```

**Response:**
```json
{
  "user_id": "user123",
  "period_start": "2025-07-30T12:00:00",
  "period_end": "2025-07-31T12:00:00",
  "coverage_percentage": 50.0,
  "covered_hours": 12,
  "total_hours": 24,
  "payment_count": 1,
  "successful_payments": 1,
  "failed_payments": 0
}
```

### Admin Endpoints

#### Get All Users
```bash
curl http://localhost:5013/admin/users
```

#### Service Management
```bash
# Get service status
curl http://localhost:5013/admin/service/status

# Start service
curl -X POST http://localhost:5013/admin/service/start

# Stop service
curl -X POST http://localhost:5013/admin/service/stop
```

## 🧪 Testing

### Automated Testing

```bash
# Run comprehensive API tests
python api_examples.py test

# Run subscription lifecycle demo
python api_examples.py demo

# Show cURL examples
python api_examples.py curl
```

### Manual Testing Workflow

1. **Start server**: `python server.py`
2. **Health check**: `curl http://localhost:5013/health`
3. **Purchase subscription**: Test with `api_examples.py`
4. **Monitor logs**: Check `subscription_api.log`
5. **Test edge cases**: Invalid user IDs, failed payments, etc.

### Test Scenarios

```bash
# Valid user flow
curl -X POST http://localhost:5013/subscription/purchase -H "Content-Type: application/json" -d '{"user_id": "test_user"}'
curl http://localhost:5013/subscription/status/test_user
curl -X POST http://localhost:5013/subscription/off -H "Content-Type: application/json" -d '{"user_id": "test_user"}'

# Error cases
curl http://localhost:5013/subscription/status/nonexistent_user  # 404
curl -X POST http://localhost:5013/subscription/purchase -H "Content-Type: application/json" -d '{"user_id": ""}'  # 400
curl -X POST http://localhost:5013/subscription/purchase -H "Content-Type: application/json" -d '{}'  # 400
```

## 🚀 Production Deployment

### Environment Setup

```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key-here
export DATA_FILE=/app/data/subscription_data.json
export LOG_LEVEL=INFO
export HOST=0.0.0.0
export PORT=5013
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 5013

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5013/health || exit 1

# Run application
CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t subscription-api .
docker run -p 5013:5013 -v ./data:/app/data subscription-api
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  subscription-api:
    build: .
    ports:
      - "5013:5013"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATA_FILE=/app/data/subscription_data.json
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5013/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Process Management

#### Using systemd (Linux)

Create `/etc/systemd/system/subscription-api.service`:
```ini
[Unit]
Description=Subscription Management API
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/app/subscription-api
Environment=FLASK_ENV=production
Environment=SECRET_KEY=your-secret-key
ExecStart=/app/subscription-api/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable subscription-api
sudo systemctl start subscription-api
sudo systemctl status subscription-api
```

#### Using supervisor

Create `/etc/supervisor/conf.d/subscription-api.conf`:
```ini
[program:subscription-api]
command=/app/subscription-api/venv/bin/python server.py
directory=/app/subscription-api
user=app
autostart=true
autorestart=true
environment=FLASK_ENV=production,SECRET_KEY=your-secret-key
stdout_logfile=/var/log/subscription-api.log
stderr_logfile=/var/log/subscription-api-error.log
```

## 🔧 Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Environment mode |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5013` | Server port |
| `SECRET_KEY` | *(required in production)* | Flask secret key |
| `DATA_FILE` | `subscription_data.json` | Data storage file path |
| `RENEWAL_INTERVAL_HOURS` | `24` | Hours between renewals |
| `PAYMENT_SUCCESS_RATE` | `0.9` | Payment simulation success rate |
| `SUBSCRIPTION_PRICE` | `10.0` | Subscription price |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | `subscription_api.log` | Log file path |

### Configuration Validation

```bash
# Validate configuration
python config.py

# Output example:
=== Configuration Validation ===

DEVELOPMENT Configuration:
✅ Validation passed
  Data file: dev_subscription_data.json
  Renewal interval: 1h
  Payment success rate: 0.9
  Debug mode: True

PRODUCTION Configuration:
❌ Validation failed:
  - SECRET_KEY must be set for production
```

## 📊 Monitoring and Logging

### Log Files

- **Application logs**: `subscription_api.log`
- **Error logs**: Included in main log with ERROR level
- **Access logs**: Request/response logging

### Log Format

```
2025-07-31 12:00:00,123 - subscription_service - INFO - Subscription activated for user user123
2025-07-31 12:01:00,456 - payment_service - WARNING - Payment failed for user user456
2025-07-31 12:02:00,789 - app - ERROR - Database connection failed
```

### Health Monitoring

```bash
# Health endpoint
curl http://localhost:5013/health

# Admin status
curl http://localhost:5013/admin/service/status

# Response includes:
# - Service running status
# - User count statistics
# - Background service status
# - Configuration details
```

### Metrics Available

- Total users
- Active subscriptions
- Pending off commands
- Payment success/failure rates
- Coverage statistics
- Service uptime

## 🔒 Security Considerations

### Development vs Production

**Development (FLASK_ENV=development):**
- Debug mode enabled
- Detailed error messages
- No authentication required
- Permissive CORS

**Production (FLASK_ENV=production):**
- Debug mode disabled
- Generic error messages
- Secure secret key required
- Production logging

### Security Checklist

- [ ] Set strong `SECRET_KEY` in production
- [ ] Use HTTPS in production
- [ ] Implement authentication/authorization
- [ ] Add rate limiting
- [ ] Validate all inputs
- [ ] Sanitize error messages
- [ ] Use secure headers
- [ ] Regular security updates

## 🐛 Troubleshooting

### Common Issues

#### Server won't start
```bash
# Check port availability
netstat -tulpn | grep :5013

# Check permissions
ls -la subscription_data.json

# Check configuration
python config.py
```

#### Payment failures
```bash
# Check payment success rate
grep "PAYMENT_SUCCESS_RATE" .env

# Monitor payment logs
tail -f subscription_api.log | grep payment
```

#### Data persistence issues
```bash
# Check file permissions
ls -la subscription_data.json

# Verify JSON format
python -m json.tool subscription_data.json

# Check disk space
df -h
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python server.py

# Check specific service
python -c "
from services import SubscriptionService
service = SubscriptionService()
print(service.get_service_status())
"
```

### Log Analysis

```bash
# Error analysis
grep ERROR subscription_api.log

# Payment tracking
grep "payment" subscription_api.log

# User activity
grep "user123" subscription_api.log
```

## 🚀 Extending the System

### Adding New Features

#### 1. New API Endpoint

```python
# In routes.py
@api_bp.route('/subscription/pause', methods=['POST'])
@require_json
def pause_subscription():
    # Implementation
    pass
```

#### 2. New Service

```python
# In services.py
class NotificationService:
    def send_renewal_reminder(self, user_id):
        # Implementation
        pass
```

#### 3. New Configuration

```python
# In config.py
class Config:
    NOTIFICATION_ENABLED = os.getenv('NOTIFICATION_ENABLED', 'False').lower() == 'true'
```

### Integration Examples

#### Database Integration

Replace `DataService` with database implementation:

```python
class DatabaseService:
    def __init__(self, connection_string):
        self.db = connect(connection_string)
    
    def save_users(self, users):
        # Database implementation
        pass
```

#### External Payment Processor

Replace `PaymentService` with real payment integration:

```python
class StripePaymentService:
    def __init__(self, api_key):
        self.stripe = stripe
        stripe.api_key = api_key
    
    def process_payment(self, user_id, amount):
        # Stripe implementation
        pass
```

## 📝 API Documentation

### OpenAPI/Swagger Integration

To add API documentation, install and configure:

```bash
pip install flask-restx
```

Then extend `app.py`:

```python
from flask_restx import Api, Resource

api = Api(app, doc='/docs/')
```

### Postman Collection

Import the following endpoints into Postman:

1. Health Check: `GET {{base_url}}/health`
2. Purchase: `POST {{base_url}}/subscription/purchase`
3. Status: `GET {{base_url}}/subscription/status/{{user_id}}`
4. Off Command: `POST {{base_url}}/subscription/off`
5. Coverage: `GET {{base_url}}/subscription/coverage/{{user_id}}`

## 🤝 Contributing

### Development Workflow

1. **Setup development environment**
   ```bash
   FLASK_ENV=development python server.py
   ```

2. **Make changes following the architecture**
   - Models in `models.py`
   - Business logic in `services.py`
   - API routes in `routes.py`

3. **Test changes**
   ```bash
   python api_examples.py test
   ```

4. **Validate configuration**
   ```bash
   python config.py
   ```

### Code Style

- Follow PEP 8
- Use type hints where possible
- Add comprehensive docstrings
- Include error handling
- Write tests for new features

### Architecture Guidelines

- **Single Responsibility**: Each file/class has one purpose
- **Dependency Injection**: Pass dependencies rather than importing
- **Configuration**: Use environment variables
- **Error Handling**: Comprehensive error handling at each layer
- **Logging**: Log important events and errors
- **Testing**: Write testable code with clear interfaces

## 📞 Support

### Getting Help

1. **Check logs**: `tail -f subscription_api.log`
2. **Validate config**: `python config.py`
3. **Test API**: `python api_examples.py test`
4. **Health check**: `curl http://localhost:5013/health`

### Common Commands

```bash
# Quick start
python server.py

# Test everything
python api_examples.py test

# Check configuration
python config.py

# View logs
tail -f subscription_api.log

# Production start
FLASK_ENV=production python server.py
```

---

**Version**: 1.0.0  
**License**: MIT  
**Author**: Subscription Management Team  
**Last Updated**: July 31, 2025