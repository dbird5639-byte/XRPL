# XRPL Ecosystem Deployment Guide

Comprehensive deployment guide for the XRPL Ecosystem platform.

## 🏗️ Architecture Overview

The XRPL Ecosystem consists of multiple components:

- **Core Services**: XRPL client, DEX engine, bridge engine, security
- **Applications**: Trading, DeFi, NFT, AI applications
- **Frontend**: Web interface, mobile wallet, AI IDE
- **Smart Contracts**: EVM sidechain contracts
- **Infrastructure**: Docker containers, Kubernetes, monitoring

## 🚀 Quick Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.21+ (for production)
- kubectl configured
- Helm 3.0+

### Local Development

```bash
# Clone the repository
git clone https://github.com/xrpl-ecosystem/xrpl-ecosystem.git
cd xrpl-ecosystem

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Production Deployment

```bash
# Deploy to Kubernetes
helm install xrpl-ecosystem ./helm/xrpl-ecosystem \
  --namespace xrpl-ecosystem \
  --create-namespace \
  --values ./helm/values/production.yaml
```

## 🐳 Docker Configuration

### Core Services

```yaml
# docker-compose.yml
version: '3.8'

services:
  xrpl-client:
    build: ./core/xrpl-client
    ports:
      - "3001:3001"
    environment:
      - XRPL_NETWORK=testnet
      - XRPL_ACCOUNT=${XRPL_ACCOUNT}
      - XRPL_SECRET=${XRPL_SECRET}
    volumes:
      - ./data:/app/data

  dex-engine:
    build: ./core/dex-engine
    ports:
      - "3002:3002"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/dex
    depends_on:
      - redis
      - postgres

  bridge-engine:
    build: ./core/bridge-engine
    ports:
      - "3003:3003"
    environment:
      - ETHEREUM_RPC_URL=${ETHEREUM_RPC_URL}
      - BSC_RPC_URL=${BSC_RPC_URL}
      - POLYGON_RPC_URL=${POLYGON_RPC_URL}

  security:
    build: ./core/security
    ports:
      - "3004:3004"
    environment:
      - AI_MODEL_ENDPOINT=${AI_MODEL_ENDPOINT}
      - AI_API_KEY=${AI_API_KEY}

  # Infrastructure
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=xrpl_ecosystem
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - xrpl-client
      - dex-engine
      - bridge-engine
      - security

volumes:
  postgres_data:
  redis_data:
```

## ☸️ Kubernetes Deployment

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: xrpl-ecosystem
  labels:
    name: xrpl-ecosystem
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: xrpl-ecosystem-config
  namespace: xrpl-ecosystem
data:
  XRPL_NETWORK: "mainnet"
  REDIS_URL: "redis://redis-service:6379"
  DATABASE_URL: "postgresql://postgres:password@postgres-service:5432/xrpl_ecosystem"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: xrpl-ecosystem-secrets
  namespace: xrpl-ecosystem
type: Opaque
data:
  XRPL_SECRET: <base64-encoded-secret>
  AI_API_KEY: <base64-encoded-api-key>
  ETHEREUM_RPC_URL: <base64-encoded-rpc-url>
```

### Deployments

```yaml
# k8s/xrpl-client-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xrpl-client
  namespace: xrpl-ecosystem
spec:
  replicas: 3
  selector:
    matchLabels:
      app: xrpl-client
  template:
    metadata:
      labels:
        app: xrpl-client
    spec:
      containers:
      - name: xrpl-client
        image: xrpl-ecosystem/xrpl-client:latest
        ports:
        - containerPort: 3001
        env:
        - name: XRPL_NETWORK
          valueFrom:
            configMapKeyRef:
              name: xrpl-ecosystem-config
              key: XRPL_NETWORK
        - name: XRPL_SECRET
          valueFrom:
            secretKeyRef:
              name: xrpl-ecosystem-secrets
              key: XRPL_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Services

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: xrpl-client-service
  namespace: xrpl-ecosystem
spec:
  selector:
    app: xrpl-client
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3001
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: xrpl-ecosystem-ingress
  namespace: xrpl-ecosystem
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.xrpl-ecosystem.org
    secretName: xrpl-ecosystem-tls
  rules:
  - host: api.xrpl-ecosystem.org
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: xrpl-client-service
            port:
              number: 80
```

## 🔧 Helm Charts

### Chart Structure

```
helm/xrpl-ecosystem/
├── Chart.yaml
├── values.yaml
├── values/
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secret.yaml
```

### Chart.yaml

```yaml
apiVersion: v2
name: xrpl-ecosystem
description: XRPL Ecosystem Platform
type: application
version: 1.0.0
appVersion: "1.0.0"
dependencies:
- name: postgresql
  version: 12.1.2
  repository: https://charts.bitnami.com/bitnami
- name: redis
  version: 16.5.0
  repository: https://charts.bitnami.com/bitnami
```

### values.yaml

```yaml
# Default values for xrpl-ecosystem
replicaCount: 3

image:
  repository: xrpl-ecosystem
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.xrpl-ecosystem.org
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: xrpl-ecosystem-tls
      hosts:
        - api.xrpl-ecosystem.org

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    postgresPassword: "password"
    database: "xrpl_ecosystem"

redis:
  enabled: true
  auth:
    enabled: false
```

## 🌐 Environment Configuration

### Development

```bash
# .env.development
XRPL_NETWORK=testnet
XRPL_ACCOUNT=your-testnet-account
XRPL_SECRET=your-testnet-secret
DATABASE_URL=postgresql://postgres:password@localhost:5432/xrpl_ecosystem_dev
REDIS_URL=redis://localhost:6379
AI_API_KEY=your-ai-api-key
```

### Staging

```bash
# .env.staging
XRPL_NETWORK=testnet
XRPL_ACCOUNT=your-staging-account
XRPL_SECRET=your-staging-secret
DATABASE_URL=postgresql://postgres:password@staging-db:5432/xrpl_ecosystem_staging
REDIS_URL=redis://staging-redis:6379
AI_API_KEY=your-staging-ai-api-key
```

### Production

```bash
# .env.production
XRPL_NETWORK=mainnet
XRPL_ACCOUNT=your-mainnet-account
XRPL_SECRET=your-mainnet-secret
DATABASE_URL=postgresql://postgres:password@prod-db:5432/xrpl_ecosystem_prod
REDIS_URL=redis://prod-redis:6379
AI_API_KEY=your-prod-ai-api-key
```

## 📊 Monitoring and Logging

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'xrpl-ecosystem'
    static_configs:
      - targets: ['xrpl-client:3001', 'dex-engine:3002', 'bridge-engine:3003']
    metrics_path: /metrics
    scrape_interval: 5s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "XRPL Ecosystem",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```yaml
# logging/fluentd.conf
<source>
  @type tail
  path /var/log/containers/*xrpl-ecosystem*.log
  pos_file /var/log/fluentd-containers.log.pos
  tag kubernetes.*
  format json
  time_key time
  time_format %Y-%m-%dT%H:%M:%S.%NZ
</source>

<match kubernetes.**>
  @type elasticsearch
  host elasticsearch.logging.svc.cluster.local
  port 9200
  index_name xrpl-ecosystem
  type_name _doc
</match>
```

## 🔒 Security Configuration

### Network Policies

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: xrpl-ecosystem-network-policy
  namespace: xrpl-ecosystem
spec:
  podSelector:
    matchLabels:
      app: xrpl-ecosystem
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: xrpl-ecosystem
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
```

### Pod Security Policy

```yaml
# k8s/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: xrpl-ecosystem-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## 🚀 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t xrpl-ecosystem/xrpl-client:latest ./core/xrpl-client
        docker build -t xrpl-ecosystem/dex-engine:latest ./core/dex-engine
        docker build -t xrpl-ecosystem/bridge-engine:latest ./core/bridge-engine
    
    - name: Push to registry
      run: |
        docker push xrpl-ecosystem/xrpl-client:latest
        docker push xrpl-ecosystem/dex-engine:latest
        docker push xrpl-ecosystem/bridge-engine:latest
    
    - name: Deploy to Kubernetes
      run: |
        helm upgrade --install xrpl-ecosystem ./helm/xrpl-ecosystem \
          --namespace xrpl-ecosystem \
          --values ./helm/values/production.yaml
```

## 📋 Health Checks

### Application Health Endpoints

```python
# health.py
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/health')
def health_check():
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'xrpl': check_xrpl_connection(),
        'external_apis': check_external_apis()
    }
    
    status = 'healthy' if all(checks.values()) else 'unhealthy'
    
    return jsonify({
        'status': status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    })

def check_database():
    try:
        # Check database connection
        return True
    except:
        return False

def check_redis():
    try:
        # Check Redis connection
        return True
    except:
        return False

def check_xrpl_connection():
    try:
        # Check XRPL connection
        return True
    except:
        return False

def check_external_apis():
    try:
        # Check external API connections
        return True
    except:
        return False
```

## 🔄 Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh

# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql s3://xrpl-ecosystem-backups/

# Cleanup old backups
find . -name "backup_*.sql" -mtime +7 -delete
```

### Disaster Recovery

```bash
#!/bin/bash
# restore.sh

# Download latest backup
aws s3 cp s3://xrpl-ecosystem-backups/latest.sql .

# Restore database
psql $DATABASE_URL < latest.sql

# Restart services
kubectl rollout restart deployment/xrpl-client -n xrpl-ecosystem
kubectl rollout restart deployment/dex-engine -n xrpl-ecosystem
kubectl rollout restart deployment/bridge-engine -n xrpl-ecosystem
```

## 📞 Support

- **Documentation**: [docs.xrpl-ecosystem.org](https://docs.xrpl-ecosystem.org)
- **Status Page**: [status.xrpl-ecosystem.org](https://status.xrpl-ecosystem.org)
- **Support**: [support@xrpl-ecosystem.org](mailto:support@xrpl-ecosystem.org)
- **Discord**: [discord.gg/xrpl-ecosystem](https://discord.gg/xrpl-ecosystem)

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
