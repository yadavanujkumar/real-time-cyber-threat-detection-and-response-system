# Real-Time Cyber Threat Detection and Response System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An enterprise-grade, production-ready system for real-time detection and response to cyber threats using machine learning and advanced analytics.

## 🚀 Features

- **Real-time Threat Detection**: ML-powered threat analysis with sub-second response times
- **RESTful API**: FastAPI-based endpoints with automatic OpenAPI documentation
- **Scalable Architecture**: Containerized services with Docker and Kubernetes support
- **Advanced ML Pipeline**: Feature engineering, model training, and inference
- **Production Monitoring**: Prometheus metrics, structured logging, and distributed tracing
- **High Availability**: Circuit breaker patterns, rate limiting, and graceful degradation
- **Security First**: JWT authentication, input validation, and SQL injection prevention
- **Database Integration**: PostgreSQL for persistent storage with ORM support
- **Caching Layer**: Redis for high-performance caching and real-time data

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Contributing](#contributing)

## 🏗️ Architecture

The system follows a microservices architecture with the following components:

- **API Layer**: FastAPI application handling HTTP requests
- **ML Pipeline**: Data preprocessing, training, and inference
- **Database Layer**: PostgreSQL for persistent storage
- **Cache Layer**: Redis for high-speed data access
- **Task Queue**: Celery for asynchronous task processing
- **Monitoring**: Prometheus + Grafana for observability

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture diagrams.

## 📦 Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)
- Git

## 🔧 Installation

### Option 1: Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yadavanujkumar/real-time-cyber-threat-detection-and-response-system.git
   cd real-time-cyber-threat-detection-and-response-system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python src/core/model.py
   ```

6. **Run the application**
   ```bash
   uvicorn src.api.endpoints:app --reload --host 0.0.0.0 --port 8000
   ```

### Option 2: Docker Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yadavanujkumar/real-time-cyber-threat-detection-and-response-system.git
   cd real-time-cyber-threat-detection-and-response-system
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Check service health**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

## ⚙️ Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | Secret key for cryptographic operations | Required |
| `JWT_SECRET` | JWT token secret | Required |
| `LOG_LEVEL` | Logging level | `INFO` |

See [.env.example](.env.example) for all available options.

## 🎯 Usage

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Threat Detection
```bash
curl -X POST http://localhost:8000/api/v1/threat-detection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### Python SDK Example

```python
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Detect threat
response = requests.post(
    f"{API_URL}/threat-detection",
    json={
        "ip_address": "10.0.0.1",
        "user_agent": "Suspicious Agent"
    },
    headers=headers
)

print(response.json())
```

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for detailed API documentation.

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suites
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Load tests
pytest tests/load/ -v
```

### Test Coverage
```bash
pytest --cov=src --cov-report=html tests/
```

## 🚀 Deployment

### Kubernetes Deployment

```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET`
- [ ] Configure production database with SSL
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Enable HTTPS/TLS
- [ ] Set up backup and disaster recovery
- [ ] Review and harden security settings

## 📊 Monitoring

### Prometheus Metrics

Metrics are exposed at `http://localhost:8001/metrics`

Key metrics:
- `http_requests_total`: Total HTTP requests
- `http_request_latency_seconds`: Request latency
- `service_health`: Service health status

### Logs

Structured JSON logs are written to:
- Console (stdout)
- `app.log` (rotating file handler)

### Health Checks

- **Liveness**: `GET /api/v1/health`
- **Readiness**: `GET /api/v1/readiness`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Support

For support and questions:
- Open an issue on GitHub
- Contact: support@example.com

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Scikit-learn for machine learning capabilities
- PostgreSQL and Redis for data storage
- The open-source community