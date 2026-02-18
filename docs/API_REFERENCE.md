# API Reference

## Overview

The Real-Time Cyber Threat Detection and Response System provides a RESTful API for detecting and responding to cyber threats in real-time.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: Bearer token (JWT)

## Authentication

### Generate Token

Generate a JWT token for API authentication.

**Endpoint**: `POST /api/v1/auth/token`

**Parameters**:
- `username` (string, required): Username
- `password` (string, required): Password

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

**Example Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "expires_at": "2024-01-15T11:30:00"
}
```

### Using the Token

Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Endpoints

### Health Check

Check if the API is healthy and running.

**Endpoint**: `GET /api/v1/health`

**Authentication**: Not required

**Example Request**:
```bash
curl http://localhost:8000/api/v1/health
```

**Example Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Readiness Check

Check if the API is ready to handle requests.

**Endpoint**: `GET /api/v1/readiness`

**Authentication**: Not required

**Example Request**:
```bash
curl http://localhost:8000/api/v1/readiness
```

**Example Response**:
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### API Information

Get information about the API and its configuration.

**Endpoint**: `GET /api/v1/info`

**Authentication**: Not required

**Example Request**:
```bash
curl http://localhost:8000/api/v1/info
```

**Example Response**:
```json
{
  "name": "Real-Time Cyber Threat Detection and Response System",
  "version": "1.0.0",
  "environment": "development",
  "endpoints": 8,
  "uptime": 0.0
}
```

### Threat Detection

Analyze an IP address for potential cyber threats.

**Endpoint**: `POST /api/v1/threat-detection`

**Authentication**: Required

**Request Body**:
```json
{
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Parameters**:
- `ip_address` (string, required): IPv4 address to analyze (format: xxx.xxx.xxx.xxx)
- `user_agent` (string, optional): User agent string (max 512 characters)
- `timestamp` (datetime, optional): Request timestamp (defaults to current time)

**Example Request**:
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

**Example Response**:
```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "threat_level": "low",
  "details": "Private IP address detected"
}
```

**Threat Levels**:
- `low`: Minimal or no threat detected
- `medium`: Suspicious activity detected
- `high`: Potential malicious activity detected
- `critical`: Confirmed malicious activity

### Threat Statistics

Get aggregated threat detection statistics.

**Endpoint**: `GET /api/v1/statistics`

**Authentication**: Required

**Example Request**:
```bash
curl http://localhost:8000/api/v1/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response**:
```json
{
  "total_threats_detected": 1234,
  "threats_by_level": {
    "low": 500,
    "medium": 400,
    "high": 300,
    "critical": 34
  },
  "recent_threats": 45,
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "code": "error_code",
  "message": "Human-readable error message",
  "details": "Additional error details (optional)"
}
```

### HTTP Status Codes

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Common Error Codes

- `validation_error`: Request validation failed
- `authentication_error`: Authentication failed
- `authorization_error`: Insufficient permissions
- `rate_limit_exceeded`: Too many requests
- `internal_error`: Internal server error
- `resource_not_found`: Requested resource not found

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Per Minute**: 100 requests
- **Per Hour**: 1000 requests

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-Process-Time: 0.023
```

When rate limit is exceeded, you'll receive:
- HTTP Status: `429 Too Many Requests`
- Header: `Retry-After: 60` (seconds)

## Security Headers

All responses include security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

## Interactive Documentation

The API provides interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## SDKs and Code Examples

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Get token
token_response = requests.post(
    f"{API_URL}/auth/token",
    data={"username": "testuser", "password": "testpass"}
)
token = token_response.json()["access_token"]

# Detect threat
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

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

### JavaScript

```javascript
const API_URL = "http://localhost:8000/api/v1";

// Get token
const tokenResponse = await fetch(`${API_URL}/auth/token`, {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: "username=testuser&password=testpass",
});
const { access_token } = await tokenResponse.json();

// Detect threat
const response = await fetch(`${API_URL}/threat-detection`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${access_token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    ip_address: "10.0.0.1",
    user_agent: "Suspicious Agent",
  }),
});

const result = await response.json();
console.log(result);
```

### cURL

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass" \
  | jq -r '.access_token')

# Detect threat
curl -X POST http://localhost:8000/api/v1/threat-detection \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "10.0.0.1",
    "user_agent": "Suspicious Agent"
  }'
```

## Support

For API support:
- GitHub Issues: https://github.com/yadavanujkumar/real-time-cyber-threat-detection-and-response-system/issues
- Email: support@example.com