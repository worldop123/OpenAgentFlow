# 部署指南

## 概述

本指南涵盖OpenAgentFlow在各种环境中的部署，包括开发环境、生产环境和云平台。

## 部署选项

### 1. 本地开发部署
快速搭建开发环境，适合开发者和贡献者。

### 2. Docker容器部署
使用Docker和Docker Compose进行标准化部署。

### 3. Kubernetes集群部署
企业级生产环境部署，支持高可用和自动扩缩容。

### 4. 云平台部署
在AWS、Azure、GCP等云平台上部署。

## 本地开发部署

### 系统要求

- **操作系统**: Linux/macOS/Windows (WSL2)
- **Python**: 3.11+
- **PostgreSQL**: 14+
- **Redis**: 6+
- **Node.js**: 18+ (前端开发)

### 安装步骤

#### 1. 下载项目

```bash
# 克隆项目
git clone https://github.com/worldop123/OpenAgentFlow.git
cd OpenAgentFlow

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 安装前端依赖（如果需要）
cd frontend
npm install
npm run build
cd ..
```

#### 3. 配置数据库

```bash
# 安装PostgreSQL（Ubuntu/Debian）
sudo apt update
sudo apt install postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql

# 在PostgreSQL shell中执行
CREATE DATABASE openagentflow;
CREATE USER openagentflow WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE openagentflow TO openagentflow;
\q

# 安装Redis
sudo apt install redis-server
sudo systemctl enable redis-server
```

#### 4. 配置环境变量

```bash
# 创建环境变量文件
cp .env.example .env

# 编辑配置
nano .env
```

**`.env` 文件内容示例**:

```bash
# 应用配置
APP_NAME=OpenAgentFlow
APP_ENV=development
DEBUG=true
LOG_LEVEL=debug
SECRET_KEY=your-secret-key-change-this

# 数据库配置
DATABASE_URL=postgresql://openagentflow:your_password@localhost:5432/openagentflow

# Redis配置
REDIS_URL=redis://localhost:6379/0

# AI服务配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_TIMEOUT=30

# 企业工具配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
DINGTALK_APP_KEY=your_app_key
DINGTALK_APP_SECRET=your_app_secret
WECOM_CORP_ID=your_corp_id
WECOM_CORP_SECRET=your_corp_secret

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# 安全配置
JWT_SECRET=your-jwt-secret-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# 邮件配置（可选）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@openagentflow.ai

# 文件存储配置
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=50MB
```

#### 5. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或使用初始化脚本
python scripts/init_db.py

# 创建管理员用户
python scripts/create_admin.py \
  --username admin \
  --email admin@example.com \
  --password Admin@123
```

#### 6. 启动服务

```bash
# 启动后端服务
python main.py

# 或使用uvicorn热重载
uvicorn backend.server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload

# 启动前端开发服务器（如果需要）
cd frontend
npm run dev

# 前端访问地址：http://localhost:3000
# API访问地址：http://localhost:8000
# API文档：http://localhost:8000/docs
```

### 7. 验证部署

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试API端点
curl http://localhost:8000/api/v1/agents

# 测试数据库连接
python scripts/test_db.py

# 测试Redis连接
python scripts/test_redis.py
```

## Docker容器部署

### Docker Compose文件

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: openagentflow-postgres
    environment:
      POSTGRES_DB: openagentflow
      POSTGRES_USER: openagentflow
      POSTGRES_PASSWORD: ${DB_PASSWORD:-change_this}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U openagentflow"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - openagentflow-network

  redis:
    image: redis:7-alpine
    container_name: openagentflow-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - openagentflow-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: openagentflow-backend
    environment:
      DATABASE_URL: postgresql://openagentflow:${DB_PASSWORD:-change_this}@postgres:5432/openagentflow
      REDIS_URL: redis://redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      FEISHU_APP_ID: ${FEISHU_APP_ID}
      FEISHU_APP_SECRET: ${FEISHU_APP_SECRET}
      DINGTALK_APP_KEY: ${DINGTALK_APP_KEY}
      DINGTALK_APP_SECRET: ${DINGTALK_APP_SECRET}
      JWT_SECRET: ${JWT_SECRET:-change_this_secret}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - uploads:/app/uploads
      - logs:/app/logs
    networks:
      - openagentflow-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    container_name: openagentflow-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - openagentflow-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: openagentflow-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - openagentflow-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  uploads:
  logs:

networks:
  openagentflow-network:
    driver: bridge
```

### Dockerfile配置

**后端Dockerfile** (`Dockerfile.backend`):

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# 创建工作目录
WORKDIR $APP_HOME

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY alembic.ini .
COPY .env.example .env

# 创建必要的目录
RUN mkdir -p uploads logs

# 设置权限
RUN chmod +x ./scripts/*.py

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**前端Dockerfile** (`Dockerfile.frontend`):

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx配置

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 压缩设置
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/xml application/xml+rss application/javascript
               application/json application/x-protobuf;

    # SSL设置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name openagentflow.example.com;

        # SSL证书
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 前端静态文件
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API请求
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 健康检查
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }

        # API文档
        location /docs {
            proxy_pass http://backend/docs;
        }

        # 文件上传
        location /uploads/ {
            proxy_pass http://backend/uploads/;
        }
    }
}
```

### 部署步骤

#### 1. 准备环境

```bash
# 克隆项目
git clone https://github.com/worldop123/OpenAgentFlow.git
cd OpenAgentFlow

# 创建环境变量文件
cp .env.example .env

# 编辑环境变量
nano .env
```

#### 2. 生成SSL证书（可选）

```bash
# 创建证书目录
mkdir -p ssl

# 生成自签名证书（开发环境）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=OpenAgentFlow/CN=localhost"
```

#### 3. 启动服务

```bash
# 构建并启动所有容器
docker-compose up -d --build

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### 4. 初始化数据库

```bash
# 运行数据库迁移
docker-compose exec backend \
  python -c "import scripts.migrate_db; scripts.migrate_db.run()"

# 或直接运行Alembic
docker-compose exec backend \
  alembic upgrade head
```

#### 5. 验证部署

```bash
# 测试健康检查
curl -k https://localhost/health

# 测试API
curl -k https://localhost/api/v1/agents

# 查看Nginx访问日志
docker-compose logs nginx
```

### 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 查看服务日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash

# 查看资源使用情况
docker-compose stats

# 清理未使用的资源
docker system prune -a
```

## Kubernetes部署

### 集群要求

- **Kubernetes**: 1.24+
- **Ingress Controller**: Nginx/Traefik
- **Storage Class**: 支持动态卷配置
- **监控**: Prometheus/Grafana（可选）

### Kubernetes清单文件

#### 命名空间配置 (`namespace.yaml`):

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openagentflow
  labels:
    name: openagentflow
```

#### 配置映射 (`configmap.yaml`):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openagentflow-config
  namespace: openagentflow
data:
  APP_NAME: "OpenAgentFlow"
  APP_ENV: "production"
  DEBUG: "false"
  LOG_LEVEL: "info"
  CORS_ORIGINS: "https://openagentflow.example.com"
  DEFAULT_MODEL: "gpt-3.5-turbo"
  STORAGE_TYPE: "s3"
  MAX_UPLOAD_SIZE: "50MB"
```

#### 密钥配置 (`secrets.yaml`):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openagentflow-secrets
  namespace: openagentflow
type: Opaque
stringData:
  DATABASE_URL: "postgresql://openagentflow:${DB_PASSWORD}@postgres.openagentflow.svc.cluster.local:5432/openagentflow"
  REDIS_URL: "redis://redis.openagentflow.svc.cluster.local:6379/0"
  JWT_SECRET: "${JWT_SECRET}"
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
  FEISHU_APP_ID: "${FEISHU_APP_ID}"
  FEISHU_APP_SECRET: "${FEISHU_APP_SECRET}"
```

#### 后端部署 (`backend-deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openagentflow-backend
  namespace: openagentflow
  labels:
    app: openagentflow-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openagentflow-backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: openagentflow-backend
    spec:
      containers:
      - name: backend
        image: openagentflow/backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: openagentflow-config
        - secretRef:
            name: openagentflow-secrets
        env:
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
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
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 1
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: openagentflow-uploads-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: openagentflow-logs-pvc
      nodeSelector:
        node-type: application
```

#### 后端服务 (`backend-service.yaml`):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: openagentflow-backend
  namespace: openagentflow
spec:
  selector:
    app: openagentflow-backend
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
```

#### 持久卷声明 (`pvc.yaml`):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: openagentflow-uploads-pvc
  namespace: openagentflow
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: nfs-client

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: openagentflow-logs-pvc
  namespace: openagentflow
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
  storageClassName: nfs-client
```

#### Ingress配置 (`ingress.yaml`):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: openagentflow-ingress
  namespace: openagentflow
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - openagentflow.example.com
    secretName: openagentflow-tls
  rules:
  - host: openagentflow.example.com
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: openagentflow-backend
            port:
              number: 80
      - pathType: Prefix
        path: "/api"
        backend:
          service:
            name: openagentflow-backend
            port:
              number: 80
```

#### Horizontal Pod Autoscaler (`hpa.yaml`):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openagentflow-backend-hpa
  namespace: openagentflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openagentflow-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 部署步骤

#### 1. 创建命名空间

```bash
kubectl apply -f namespace.yaml
```

#### 2. 创建配置映射和密钥

```bash
# 创建配置映射
kubectl create configmap openagentflow-config \
  --from-file=config.yaml \
  --namespace=openagentflow

# 创建密钥
kubectl create secret generic openagentflow-secrets \
  --from-literal=DATABASE_URL=${DATABASE_URL} \
  --from-literal=OPENAI_API_KEY=${OPENAI_API_KEY} \
  --namespace=openagentflow
```

#### 3. 部署数据库和Redis

```bash
# 部署PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --namespace openagentflow \
  --set auth.database=openagentflow \
  --set auth.username=openagentflow \
  --set auth.password=${DB_PASSWORD} \
  --set persistence.size=10Gi

# 部署Redis
helm install redis bitnami/redis \
  --namespace openagentflow \
  --set auth.password=${REDIS_PASSWORD} \
  --set master.persistence.size=5Gi \
  --set replica.persistence.size=5Gi
```

#### 4. 部署应用

```bash
# 构建镜像
docker build -t openagentflow/backend:latest -f Dockerfile.backend .
docker push openagentflow/backend:latest

# 部署后端
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# 部署持久卷声明
kubectl apply -f pvc.yaml

# 部署Ingress
kubectl apply -f ingress.yaml

# 部署HPA
kubectl apply -f hpa.yaml
```

#### 5. 初始化数据库

```bash
# 运行数据库迁移
kubectl run alembic-migration \
  --image=openagentflow/backend:latest \
  --namespace=openagentflow \
  --restart=OnFailure \
  --command -- sh -c "alembic upgrade head"

# 等待迁移完成
kubectl wait --for=condition=complete \
  --timeout=300s \
  job/alembic-migration \
  --namespace=openagentflow

# 清理临时Pod
kubectl delete job alembic-migration \
  --namespace=openagentflow
```

#### 6. 验证部署

```bash
# 查看Pod状态
kubectl get pods -n openagentflow

# 查看服务状态
kubectl get svc -n openagentflow

# 查看Ingress状态
kubectl get ingress -n openagentflow

# 测试端点
curl -H "Host: openagentflow.example.com" \
  https://your-ingress-ip/health
```

## 云平台部署

### AWS部署

#### 使用ECS部署

```yaml
# task-definition.json
{
  "family": "openagentflow",
  "networkMode": "awsvpc",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "openagentflow/backend:latest",
      "cpu": 256,
      "memory": 512,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@your-db-host:5432/dbname"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:ssm:region:account-id:parameter/openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/openagentflow",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 使用Elastic Beanstalk

```bash
# 创建应用
eb init openagentflow \
  --platform python-3.11 \
  --region us-east-1

# 创建环境
eb create openagentflow-env \
  --cname openagentflow \
  --envvars DATABASE_URL=postgresql://... \
  --instance-type t3.small \
  --vpc.id vpc-xxxxx \
  --vpc.subnets subnet-xxxxx \
  --vpc.securitygroups sg-xxxxx
```

### Azure部署

#### 使用Azure Container Instances

```yaml
# aci-deploy.yaml
apiVersion: 2019-12-01
location: eastus
name: openagentflow
properties:
  containers:
  - name: backend
    properties:
      image: openagentflow/backend:latest
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 0.5
      ports:
      - port: 8000
      environmentVariables:
      - name: DATABASE_URL
        value: "postgresql://user:pass@db-host:5432/dbname"
  osType: Linux
  restartPolicy: Always
tags: null
type: Microsoft.ContainerInstance/containerGroups
```

#### 使用Azure App Service

```bash
# 创建应用服务
az webapp create \
  --resource-group OpenAgentFlow \
  --plan AppServicePlan \
  --name openagentflow \
  --runtime "PYTHON|3.11"

# 配置环境变量
az webapp config appsettings set \
  --resource-group OpenAgentFlow \
  --name openagentflow \
  --settings \
    DATABASE_URL="postgresql://..." \
    OPENAI_API_KEY="sk-..."
```

### Google Cloud部署

#### 使用Cloud Run

```bash
# 构建镜像
gcloud builds submit \
  --tag gcr.io/your-project/openagentflow-backend:latest

# 部署到Cloud Run
gcloud run deploy openagentflow-backend \
  --image gcr.io/your-project/openagentflow-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://..." \
  --set-secrets "OPENAI_API_KEY=openai-key:latest"
```

## 监控和日志

### 监控配置

```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'openagentflow-backend'
    static_configs:
      - targets: ['openagentflow-backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres:5432']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### 日志聚合

```yaml
# fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: openagentflow
data:
  fluent.conf: |
    <source>
      @type forward
      port 24224
    </source>
    
    <match **>
      @type elasticsearch
      host elasticsearch.openagentflow.svc.cluster.local
      port 9200
      logstash_format true
      flush_interval 10s
    </match>
```

### 告警规则

```yaml
# alert-rules.yaml
groups:
  - name: openagentflow-alerts
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status="5xx"}[5m]) * 100 / rate(http_requests_total[5m]) > 5
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value }}%"
    
    - alert: HighCPUUsage
      expr: 100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High CPU usage"
        description: "CPU usage is {{ $value }}%"
```

## 备份和恢复

### 数据库备份

```bash
#!/bin/bash
# backup-database.sh

# 备份PostgreSQL
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份
pg_dump -h postgres -U openagentflow openagentflow \
  > "$BACKUP_DIR/openagentflow_$DATE.sql"

# 压缩备份
gzip "$BACKUP_DIR/openagentflow_$DATE.sql"

# 保留最近7天备份
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete
```

### Redis备份

```bash
#!/bin/bash
# backup-redis.sh

BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份
redis-cli -h redis save
cp /data/dump.rdb "$BACKUP_DIR/dump_$DATE.rdb"

# 保留最近7天备份
find "$BACKUP_DIR" -name "*.rdb" -mtime +7 -delete
```

### 文件存储备份

```bash
#!/bin/bash
# backup-files.sh

BACKUP_DIR="/backups/files"
UPLOAD_DIR="/app/uploads"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份上传文件
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" "$UPLOAD_DIR"

# 保留最近7天备份
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
```

## 安全配置

### SSL/TLS配置

```nginx
# nginx-ssl.conf
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;

ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;

ssl_stapling on;
ssl_stapling_verify on;
```

### 安全头配置

```nginx
# security-headers.conf
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;" always;
```

### 速率限制

```nginx
# rate-limiting.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend;
}
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查数据库状态
kubectl get pods -n openagentflow | grep postgres

# 查看数据库日志
kubectl logs postgresql-0 -n openagentflow

# 测试数据库连接
kubectl run test-db-connection \
  --image=postgres:15-alpine \
  --restart=Never \
  --rm -it -- \
  psql -h postgres.openagentflow.svc.cluster.local \
  -U openagentflow \
  -d openagentflow \
  -c "SELECT 1;"
```

#### 2. Redis连接失败

```bash
# 检查Redis状态
kubectl get pods -n openagentflow | grep redis

# 测试Redis连接
kubectl run test-redis-connection \
  --image=redis:7-alpine \
  --restart=Never \
  --rm -it -- \
  redis-cli -h redis.openagentflow.svc.cluster.local ping
```

#### 3. 应用启动失败

```bash
# 查看应用日志
kubectl logs deployment/openagentflow-backend \
  -n openagentflow

# 检查Pod状态
kubectl describe pod \
