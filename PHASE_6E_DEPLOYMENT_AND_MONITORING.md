# 🚀 PHASE 6e - DEPLOYMENT & MONITORING

**Status:** Ready to Deploy | **Commit:** 03f4d6c

---

## Overview

Phase 6e covers production deployment, monitoring, alerting, and operational runbooks for the Sentinel-Net authentication and security system.

---

## Table of Contents

1. [Deployment Strategies](#deployment-strategies)
2. [Production Setup](#production-setup)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Monitoring & Logging](#monitoring--logging)
5. [Security Monitoring](#security-monitoring)
6. [Alerting & Incident Response](#alerting--incident-response)
7. [Performance Monitoring](#performance-monitoring)
8. [Disaster Recovery](#disaster-recovery)
9. [Operational Runbooks](#operational-runbooks)

---

## Deployment Strategies

### Option 1: Docker + Docker Compose (Recommended for Development/Small Scale)

```dockerfile
# Dockerfile - Backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile - Frontend
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy application
COPY frontend/ .

# Build
RUN npm run build

# Production server
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=0 /app/.next .next
COPY --from=0 /app/public ./public
COPY --from=0 /app/package.json ./

EXPOSE 3000
CMD ["serve", "-s", ".next"]
```

```yaml
# docker-compose.yml
version: '3.9'

services:
  backend:
    build:
      context: .
      dockerfile: backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: frontend.Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
    depends_on:
      - backend
    restart: unless-stopped

  # Optional: Prometheus for metrics
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
```

### Option 2: Kubernetes (Recommended for Production/Scale)

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentinel-backend
  namespace: default
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: sentinel-backend
  template:
    metadata:
      labels:
        app: sentinel-backend
    spec:
      containers:
      - name: backend
        image: sentinel-net/backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: sentinel-secrets
              key: database-url
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 2

---
apiVersion: v1
kind: Service
metadata:
  name: sentinel-backend
spec:
  type: LoadBalancer
  selector:
    app: sentinel-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

---

## Production Setup

### 1. Environment Configuration

```bash
# .env.production
# Database
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/sentinel
SUPABASE_URL=https://prod.supabase.co
SUPABASE_KEY=your-prod-key

# Security
JWT_SECRET=your-strong-random-secret-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
ENVIRONMENT=production
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_GLOBAL=10000
RATE_LIMIT_IP=100
RATE_LIMIT_USER=1000
AUTO_BLOCK_THRESHOLD=50
REQUEST_TIMEOUT_SECONDS=30
MAX_REQUEST_SIZE=10485760

# CORS & Trusted Hosts
API_TRUSTED_HOSTS=api.example.com,*.example.com
API_CORS_ORIGINS=https://app.example.com,https://www.example.com

# Logging
LOG_FILE=/var/log/sentinel/app.log
LOG_MAX_SIZE=104857600
LOG_BACKUP_COUNT=5

# Monitoring
PROMETHEUS_METRICS=true
METRICS_PORT=9100
```

### 2. SSL/TLS Configuration

```nginx
# nginx.conf - Reverse Proxy Configuration
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name api.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    # SSL Certificates (Let's Encrypt recommended)
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy Configuration
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 3. Database Backups

```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/sentinel"
DB_HOST="prod-db.example.com"
DB_NAME="sentinel"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/sentinel_$DATE.sql.gz"

# Create backup
pg_dump \
    -h $DB_HOST \
    -U sentinel_backup \
    -d $DB_NAME | \
    gzip > $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "sentinel_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_FILE s3://sentinel-backups/ \
    --sse AES256 \
    --storage-class STANDARD_IA

echo "Backup completed: $BACKUP_FILE"
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - 'frontend/**'
      - '.github/workflows/deploy.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run backend tests
        run: pytest backend/tests -v
      
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 18
      
      - name: Install frontend dependencies
        run: cd frontend && npm ci
      
      - name: Run frontend tests
        run: cd frontend && npm test
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker images
        run: |
          docker build -t sentinel-backend:${{ github.sha }} -f backend.Dockerfile .
          docker build -t sentinel-frontend:${{ github.sha }} -f frontend.Dockerfile .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag sentinel-backend:${{ github.sha }} sentinel-backend:latest
          docker tag sentinel-frontend:${{ github.sha }} sentinel-frontend:latest
          docker push sentinel-backend:${{ github.sha }}
          docker push sentinel-frontend:${{ github.sha }}
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to production
        run: |
          # Update Kubernetes deployments
          kubectl set image deployment/sentinel-backend \
            backend=sentinel-backend:${{ github.sha }} \
            -n default
          
          kubectl set image deployment/sentinel-frontend \
            frontend=sentinel-frontend:${{ github.sha }} \
            -n default
          
          # Wait for rollout
          kubectl rollout status deployment/sentinel-backend -n default
          kubectl rollout status deployment/sentinel-frontend -n default
```

---

## Monitoring & Logging

### Application Logging

```python
# backend/logging_config.py
import logging
import logging.handlers
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        '/var/log/sentinel/app.log',
        maxBytes=104857600,  # 100MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger

# Usage in app
from logging_config import setup_logging

logger = setup_logging()
logger.info("Application started", extra={'version': '1.0.0'})
```

### Prometheus Metrics

```python
# backend/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Request metrics
request_count = Counter(
    'sentinel_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'sentinel_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# Authentication metrics
auth_attempts = Counter(
    'sentinel_auth_attempts_total',
    'Authentication attempts',
    ['method', 'result']  # result: success, failure, locked
)

# Rate limiting metrics
rate_limit_exceeded = Counter(
    'sentinel_rate_limit_exceeded_total',
    'Rate limit exceeded',
    ['limit_type']  # global, ip, user
)

blocked_ips = Gauge(
    'sentinel_blocked_ips_count',
    'Number of currently blocked IPs'
)

# Database metrics
db_query_duration = Histogram(
    'sentinel_db_query_duration_seconds',
    'Database query duration',
    ['operation', 'table'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

def track_request(method, endpoint, status, duration):
    request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

# Start metrics server on port 9100
start_http_server(9100)
```

---

## Security Monitoring

### Rate Limiting Alerts

```yaml
# monitoring/alert-rules.yml
groups:
  - name: sentinel_security
    interval: 30s
    rules:
      # High rate limit violations
      - alert: HighRateLimitViolations
        expr: rate(sentinel_rate_limit_exceeded_total[5m]) > 10
        for: 2m
        annotations:
          summary: "High rate of rate limit violations"
          description: "{{ $value }} rate limit violations per second"
      
      # Many IPs blocked
      - alert: ManyBlockedIPs
        expr: sentinel_blocked_ips_count > 20
        for: 5m
        annotations:
          summary: "High number of blocked IPs"
          description: "{{ $value }} IPs currently blocked"
      
      # Failed authentication attempts spike
      - alert: AuthFailureSpike
        expr: rate(sentinel_auth_attempts_total{result="failure"}[5m]) > 50
        for: 2m
        annotations:
          summary: "Spike in failed authentication attempts"
          description: "{{ $value }} failures per second"
      
      # Brute force detection
      - alert: BruteForceAttackDetected
        expr: rate(sentinel_auth_attempts_total{result="failure"}[1m]) > 100
        for: 1m
        annotations:
          summary: "Possible brute force attack detected"
          description: "{{ $value }} auth failures per second"
```

### Security Log Analysis

```python
# backend/security_monitor.py
import logging
from collections import defaultdict
from datetime import datetime, timedelta

class SecurityMonitor:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.logger = logging.getLogger(__name__)
    
    def track_failed_attempt(self, ip: str, user_id: str = None):
        """Track failed authentication attempt"""
        now = datetime.utcnow()
        self.failed_attempts[ip].append(now)
        
        # Remove old attempts (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        self.failed_attempts[ip] = [
            ts for ts in self.failed_attempts[ip] if ts > cutoff
        ]
        
        # Check for brute force
        recent = [ts for ts in self.failed_attempts[ip] 
                 if ts > now - timedelta(minutes=5)]
        
        if len(recent) > 10:
            self.logger.warning(
                f"Brute force detected",
                extra={
                    'ip': ip,
                    'attempts': len(recent),
                    'time_window': '5m'
                }
            )
            self.block_ip(ip)
    
    def block_ip(self, ip: str):
        """Block IP address"""
        self.blocked_ips.add(ip)
        self.logger.error(
            f"IP blocked due to suspicious activity",
            extra={'ip': ip}
        )
    
    def is_ip_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips
    
    def unblock_ip(self, ip: str):
        """Manually unblock IP"""
        self.blocked_ips.discard(ip)
        self.logger.info(f"IP unblocked", extra={'ip': ip})

# Global instance
security_monitor = SecurityMonitor()
```

---

## Alerting & Incident Response

### Alert Configuration (PagerDuty/Slack)

```yaml
# monitoring/alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

route:
  receiver: 'default'
  group_by: ['alertname', 'cluster']
  routes:
    # Critical alerts
    - match:
        severity: critical
      receiver: 'critical-team'
      continue: true
    
    # Security alerts
    - match:
        category: security
      receiver: 'security-team'
    
    # Performance alerts
    - match:
        category: performance
      receiver: 'devops-team'

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#sentinel-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
  
  - name: 'critical-team'
    pagerduty_configs:
      - service_key: '{{ .GroupLabels.pagerduty_service_key }}'
        description: '{{ .GroupLabels.alertname }}'
    slack_configs:
      - channel: '#sentinel-critical'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
  
  - name: 'security-team'
    slack_configs:
      - channel: '#sentinel-security'
        title: '🔒 SECURITY: {{ .GroupLabels.alertname }}'
```

### Incident Response Runbook

See [INCIDENT_RESPONSE_RUNBOOK.md](INCIDENT_RESPONSE_RUNBOOK.md)

---

## Performance Monitoring

### Key Performance Indicators (KPIs)

```python
# monitoring/kpis.py
class PerformanceMonitor:
    """Track and report performance KPIs"""
    
    # SLA targets
    SLA_AVAILABILITY = 99.9  # 99.9% uptime
    SLA_RESPONSE_TIME = 200  # ms
    SLA_ERROR_RATE = 0.1  # 0.1%
    
    @staticmethod
    def calculate_availability(uptime_seconds: int, total_seconds: int) -> float:
        """Calculate availability percentage"""
        return (uptime_seconds / total_seconds) * 100
    
    @staticmethod
    def calculate_error_rate(errors: int, total: int) -> float:
        """Calculate error rate percentage"""
        return (errors / total) * 100 if total > 0 else 0
    
    @staticmethod
    def check_sla_compliance(availability: float, response_time_ms: float, error_rate: float) -> dict:
        """Check if metrics comply with SLA"""
        return {
            'availability_compliant': availability >= PerformanceMonitor.SLA_AVAILABILITY,
            'response_time_compliant': response_time_ms <= PerformanceMonitor.SLA_RESPONSE_TIME,
            'error_rate_compliant': error_rate <= PerformanceMonitor.SLA_ERROR_RATE,
            'overall_compliant': all([
                availability >= PerformanceMonitor.SLA_AVAILABILITY,
                response_time_ms <= PerformanceMonitor.SLA_RESPONSE_TIME,
                error_rate <= PerformanceMonitor.SLA_ERROR_RATE,
            ])
        }
```

---

## Disaster Recovery

### Backup & Recovery Procedures

```bash
#!/bin/bash
# recovery-procedure.sh

# 1. Verify backup integrity
echo "Verifying backup..."
pg_restore --list sentinel_backup.sql.gz | head -20

# 2. Restore to test environment
echo "Restoring to test environment..."
createdb sentinel_test
pg_restore -d sentinel_test sentinel_backup.sql.gz

# 3. Verify recovery
echo "Verifying recovered data..."
psql -d sentinel_test -c "SELECT COUNT(*) FROM users;"

# 4. If good, restore to production
echo "Restoring to production..."
pg_restore -d sentinel_prod sentinel_backup.sql.gz

# 5. Verify application connectivity
echo "Verifying application connectivity..."
curl -f http://localhost:8000/health || exit 1

echo "Recovery completed successfully!"
```

### High Availability Setup

```yaml
# kubernetes/sentinel-stateful-set.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: sentinel-backend
spec:
  serviceName: sentinel-backend
  replicas: 3  # Multi-region recommended
  selector:
    matchLabels:
      app: sentinel-backend
  template:
    metadata:
      labels:
        app: sentinel-backend
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - sentinel-backend
              topologyKey: kubernetes.io/hostname
      containers:
      - name: backend
        image: sentinel-backend:latest
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
```

---

## Operational Runbooks

### Daily Operations Checklist

```markdown
## Daily Operations Checklist

### Morning (Start of Day)
- [ ] Check system uptime and availability
- [ ] Review security logs for suspicious activity
- [ ] Verify database backups completed successfully
- [ ] Check rate limiting metrics (blocked IPs)
- [ ] Review error rate and response time metrics

### Ongoing (Throughout Day)
- [ ] Monitor Slack/PagerDuty for alerts
- [ ] Respond to critical alerts immediately
- [ ] Track major deployments
- [ ] Check user reports and support tickets

### Evening (End of Day)
- [ ] Prepare incident report if any
- [ ] Update team on any ongoing issues
- [ ] Schedule maintenance if needed
- [ ] Review tomorrow's planned changes
```

### Scaling Procedures

```bash
#!/bin/bash
# scale-up.sh

# Scale backend replicas
kubectl scale deployment sentinel-backend --replicas=5 -n production

# Verify scaling
kubectl get pods -l app=sentinel-backend -n production

# Monitor metrics during scaling
kubectl port-forward -n production svc/prometheus 9090:9090 &
echo "Prometheus available at http://localhost:9090"
```

---

## ✅ Phase 6e Checklist

- [ ] Choose deployment strategy (Docker/Kubernetes)
- [ ] Set up production environment variables
- [ ] Configure SSL/TLS certificates
- [ ] Set up automated backups
- [ ] Configure CI/CD pipeline
- [ ] Set up logging and monitoring
- [ ] Configure security monitoring
- [ ] Set up alerting system
- [ ] Create incident response procedures
- [ ] Test disaster recovery procedures
- [ ] Set up performance monitoring
- [ ] Create operational runbooks
- [ ] Train operations team
- [ ] Deploy to production
- [ ] Verify all systems operational
- [ ] Monitor for first 24 hours

---

## Next Steps

1. **Choose deployment infrastructure** (Docker/Kubernetes)
2. **Configure production environment** (.env.production)
3. **Set up CI/CD pipeline** (GitHub Actions)
4. **Deploy backend and frontend**
5. **Configure monitoring and alerts**
6. **Test disaster recovery**
7. **Go live and monitor**

---

**Ready for production deployment!** 🚀
