# System Architecture

## Overview

The Real-Time Cyber Threat Detection and Response System is built on a modern, scalable microservices architecture designed for high availability, performance, and security.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client Applications                           │
│                  (Web, Mobile, CLI, Third-party)                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         │ HTTPS/TLS
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Load Balancer / API Gateway                     │
│                    (NGINX, AWS ALB, or similar)                     │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           API Layer (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Endpoints  │  │  Middleware  │  │     Auth     │             │
│  │              │  │              │  │              │             │
│  │ - Detection  │  │ - Rate Limit │  │ - JWT        │             │
│  │ - Stats      │  │ - Security   │  │ - RBAC       │             │
│  │ - Health     │  │ - Logging    │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└────────────────────────┬────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   ML/AI     │  │  Database   │  │    Cache    │
│  Pipeline   │  │  Layer      │  │   Layer     │
│             │  │             │  │             │
│ - Preproc   │  │ PostgreSQL  │  │   Redis     │
│ - Training  │  │             │  │             │
│ - Inference │  │ - Users     │  │ - Sessions  │
│ - Models    │  │ - Threats   │  │ - Results   │
└─────────────┘  │ - Alerts    │  └─────────────┘
                 └─────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Monitoring & Observability                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Prometheus  │  │   Grafana    │  │  Structured  │             │
│  │   Metrics    │  │  Dashboards  │  │   Logging    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. API Layer (FastAPI)

**Purpose**: Entry point for all client interactions

**Key Features**:
- RESTful API design with OpenAPI/Swagger documentation
- Asynchronous request handling for high concurrency
- Built-in validation using Pydantic models
- Automatic API documentation generation

**Technologies**:
- FastAPI 0.104+
- Uvicorn (ASGI server)
- Pydantic for validation

**Endpoints**:
- `/api/v1/threat-detection` - Threat analysis
- `/api/v1/statistics` - Analytics and reporting
- `/api/v1/health` - Health checks
- `/api/v1/auth/token` - Authentication

### 2. Middleware Layer

**Purpose**: Cross-cutting concerns and request/response processing

**Components**:

#### Rate Limiting
- Token bucket algorithm
- Per-client rate tracking
- 100 requests/minute, 1000 requests/hour (configurable)
- Graceful error responses with retry headers

#### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

#### Request Logging
- Structured JSON logging
- Request/response metadata
- Performance metrics
- Correlation IDs

### 3. Authentication & Authorization

**Authentication**:
- JWT (JSON Web Tokens)
- Bearer token scheme
- Configurable expiration
- Secure secret management via environment variables

**Security Features**:
- Password hashing with bcrypt
- Token-based authentication
- Secure header validation
- Production secret validation

### 4. ML/AI Pipeline

**Purpose**: Core threat detection and analysis

**Components**:

#### Preprocessing
- Feature engineering
- Data normalization
- Categorical encoding
- Missing value handling

#### Model Training
- Scikit-learn models
- Model versioning
- Performance tracking
- Automated retraining

#### Inference
- Real-time prediction
- Batch processing support
- Model serving
- Result caching

**Technologies**:
- scikit-learn
- pandas/numpy
- TensorFlow/PyTorch (optional)

### 5. Database Layer

**Purpose**: Persistent data storage

**Technology**: PostgreSQL 15+

**Schema**:

#### Users Table
```sql
- id (UUID, primary key)
- username (string, unique)
- email (string, unique)
- hashed_password (string)
- is_active (boolean)
- is_admin (boolean)
- created_at, updated_at, deleted_at
```

#### Threats Table
```sql
- id (UUID, primary key)
- name (string)
- description (text)
- severity (integer, 1-5)
- metadata (JSONB)
- created_at, updated_at, deleted_at
```

#### Alerts Table
```sql
- id (UUID, primary key)
- user_id (UUID, foreign key)
- threat_id (UUID, foreign key)
- timestamp (datetime)
- status (string)
- details (JSONB)
- created_at, updated_at, deleted_at
```

**Features**:
- Connection pooling
- Soft deletes
- Audit columns
- Indexes for performance
- JSONB for flexible metadata

### 6. Cache Layer

**Purpose**: High-speed data access and session management

**Technology**: Redis 7+

**Use Cases**:
- Session storage
- Rate limiting counters
- Temporary result caching
- Real-time data structures
- Pub/sub messaging

**Configuration**:
- Persistence enabled
- Memory optimization
- Eviction policies
- Connection pooling

### 7. Task Queue (Optional)

**Purpose**: Asynchronous task processing

**Technology**: Celery + Redis

**Use Cases**:
- Background model training
- Batch data processing
- Scheduled tasks
- Long-running operations

### 8. Monitoring & Observability

**Components**:

#### Metrics (Prometheus)
- Request count and latency
- Error rates
- Service health
- Custom business metrics

#### Visualization (Grafana)
- Real-time dashboards
- Alert configuration
- Performance monitoring
- Capacity planning

#### Logging
- Structured JSON logs
- Multiple log levels
- Log rotation
- Centralized log aggregation

#### Distributed Tracing (OpenTelemetry)
- Request tracing
- Performance profiling
- Dependency mapping
- Latency analysis

## Data Flow

### Threat Detection Flow

1. **Request Arrival**
   ```
   Client → Load Balancer → API Gateway
   ```

2. **Authentication**
   ```
   JWT Token Validation → User Authorization
   ```

3. **Rate Limiting**
   ```
   Check Rate Limits → Update Counters
   ```

4. **Request Processing**
   ```
   Validate Input → Extract Features
   ```

5. **Threat Analysis**
   ```
   Load Model → Run Inference → Calculate Threat Level
   ```

6. **Result Storage**
   ```
   Cache Result → Store in Database → Generate Alert
   ```

7. **Response**
   ```
   Format Response → Add Headers → Return to Client
   ```

## Scalability

### Horizontal Scaling

- **Stateless API**: All API instances are identical
- **Load Balancing**: Distribute traffic across instances
- **Database Read Replicas**: Scale read operations
- **Cache Clustering**: Redis cluster for high availability

### Vertical Scaling

- Increase CPU/memory for ML workloads
- SSD storage for database performance
- Network bandwidth optimization

### Auto-scaling

- Kubernetes HPA (Horizontal Pod Autoscaler)
- Scale based on:
  - CPU utilization
  - Memory usage
  - Request rate
  - Custom metrics

## High Availability

### Redundancy

- Multiple API instances
- Database replication (primary-replica)
- Redis Sentinel for failover
- Multi-zone deployment

### Health Checks

- `/api/v1/health` - Liveness probe
- `/api/v1/readiness` - Readiness probe
- Dependency health checks
- Graceful degradation

### Disaster Recovery

- Automated backups
- Point-in-time recovery
- Cross-region replication
- Backup retention policies

## Security

### Network Security

- TLS/HTTPS encryption
- Network isolation
- Firewall rules
- VPC/subnet segregation

### Application Security

- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Security headers

### Data Security

- Encryption at rest
- Encryption in transit
- Secret management
- Access control
- Audit logging

### Authentication & Authorization

- JWT tokens
- Role-based access control (RBAC)
- Token expiration
- Refresh token mechanism

## Performance

### Optimization Strategies

1. **Caching**
   - Result caching
   - Model caching
   - Database query caching

2. **Database**
   - Proper indexing
   - Connection pooling
   - Query optimization

3. **Async Processing**
   - Non-blocking I/O
   - Background tasks
   - Event-driven architecture

4. **Load Balancing**
   - Round-robin
   - Least connections
   - Geographic routing

### Performance Targets

- API Response Time: < 100ms (p95)
- Throughput: 1000+ requests/second
- Availability: 99.9% uptime
- Database Query Time: < 50ms (p95)

## Deployment

### Containerization

- Docker for packaging
- Docker Compose for local development
- Kubernetes for orchestration

### CI/CD

- Automated testing
- Build pipelines
- Automated deployment
- Rolling updates

### Environments

- **Development**: Local development
- **Staging**: Pre-production testing
- **Production**: Live environment

## Monitoring Strategy

### Metrics to Track

1. **Application Metrics**
   - Request rate
   - Error rate
   - Response time
   - Threat detection accuracy

2. **Infrastructure Metrics**
   - CPU/Memory usage
   - Network I/O
   - Disk I/O
   - Database connections

3. **Business Metrics**
   - Active users
   - Threats detected
   - Alert response time
   - False positive rate

### Alerting

- Critical: Immediate response required
- Warning: Investigation needed
- Info: FYI notifications

## Future Enhancements

- GraphQL API support
- WebSocket for real-time updates
- Machine learning model versioning
- A/B testing framework
- Multi-tenancy support
- Advanced analytics dashboard
- Mobile SDK
- API rate limiting per user
- Advanced threat intelligence integration