# Triton Agentic - Docker Setup Guide

Complete guide for deploying Triton Agentic with Docker, PostgreSQL, and Celery.

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   FastAPI   │────▶│  PostgreSQL  │     │   Celery      │
│   API       │     │   Database   │◀────│   Worker      │
│  (Port 8000)│     │  (Port 5432) │     │               │
└──────┬──────┘     └──────────────┘     └───────┬───────┘
       │                                           │
       │            ┌──────────────┐              │
       └───────────▶│    Redis     │◀─────────────┘
                    │   (Port 6379)│
                    └──────────────┘
```

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Migrations](#database-migrations)
- [API Usage](#api-usage)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later
- **AWS Credentials**: If using AWS Bedrock (configured in `~/.aws/`)

### Verify Installation

```bash
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Clone and Navigate

```bash
cd triton-agentic
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your configuration (see [Configuration](#configuration) section).

### 3. Start All Services

```bash
# Start all services (API, Worker, PostgreSQL, Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run Alembic migrations
docker-compose exec api alembic upgrade head

# Verify database is accessible
docker-compose exec postgres psql -U triton -d triton_db -c "\dt"
```

### 5. Verify Services

```bash
# Check API health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
```

---

## Configuration

### Environment Variables (.env)

#### Essential Configuration

```env
# Database
POSTGRES_DB=triton_db
POSTGRES_USER=triton
POSTGRES_PASSWORD=your_secure_password_here

# Model Provider (choose one)
DEFAULT_MODEL_PROVIDER=aws_bedrock  # or: anthropic, openai, google, groq
DEFAULT_MODEL_NAME=us.anthropic.claude-sonnet-4-20250514-v1:0
```

#### AWS Bedrock Configuration (Option 1: AWS Profile)

```env
AWS_PROFILE=your-profile-name
AWS_REGION=us-east-1
AWS_CONFIG_DIR=~/.aws
```

#### AWS Bedrock Configuration (Option 2: Access Keys)

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

#### Direct API Keys (Alternative to AWS Bedrock)

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...
```

---

## Running the Application

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d api worker postgres redis

# Start with Flower (Celery monitoring)
docker-compose --profile with-flower up -d

# Start with Celery Beat (scheduled tasks)
docker-compose --profile with-beat up -d
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop and remove everything including images
docker-compose down --rmi all -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 worker
```

### Scaling Workers

```bash
# Scale to 3 worker instances
docker-compose up -d --scale worker=3

# Verify
docker-compose ps worker
```

---

## Database Migrations

### Using Alembic

```bash
# Create a new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback one migration
docker-compose exec api alembic downgrade -1

# View migration history
docker-compose exec api alembic history

# View current revision
docker-compose exec api alembic current
```

### Direct PostgreSQL Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U triton -d triton_db

# Run SQL file
docker-compose exec postgres psql -U triton -d triton_db -f /path/to/file.sql

# Backup database
docker-compose exec postgres pg_dump -U triton triton_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U triton triton_db < backup.sql
```

---

## API Usage

### Service URLs

- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Flower (if enabled)**: http://localhost:5555

### Example API Workflow

#### 1. Create a Client

```bash
curl -X POST http://localhost:8000/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HealthTech Solutions",
    "industry": "Healthcare Technology"
  }'

# Response:
# {
#   "id": "123e4567-e89b-12d3-a456-426614174000",
#   "name": "HealthTech Solutions",
#   "industry": "Healthcare Technology",
#   ...
# }
```

#### 2. Create a Value Proposition

```bash
CLIENT_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X POST http://localhost:8000/clients/$CLIENT_ID/value-propositions \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Our AI-powered clinical decision support platform reduces diagnostic errors by 35% and improves patient outcomes through real-time evidence-based recommendations.",
    "is_active": true
  }'
```

#### 3. Generate Templates (Async)

```bash
curl -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "123e4567-e89b-12d3-a456-426614174000"
  }'

# Response:
# {
#   "job_id": "456e7890-e89b-12d3-a456-426614174111",
#   "status": "pending",
#   "celery_task_id": "abc123...",
#   ...
# }
```

#### 4. Check Job Status

```bash
JOB_ID="456e7890-e89b-12d3-a456-426614174111"

curl http://localhost:8000/jobs/$JOB_ID

# Response:
# {
#   "job_id": "456e7890-e89b-12d3-a456-426614174111",
#   "status": "completed",  # or: pending, running, failed
#   "generation_duration_ms": 45230,
#   ...
# }
```

#### 5. List Generated Templates

```bash
curl "http://localhost:8000/templates/?page=1&page_size=10"
```

---

## Monitoring

### Service Health Checks

```bash
# API health (includes database status)
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U triton

# Redis health
docker-compose exec redis redis-cli ping

# Worker health
docker-compose exec worker celery -A worker inspect ping
```

### Flower (Celery Monitoring)

Start with Flower profile:

```bash
docker-compose --profile with-flower up -d
```

Access at: http://localhost:5555

Features:
- Real-time task monitoring
- Worker status and statistics
- Task history and details
- Task revocation

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Container logs size
docker-compose ps -q | xargs docker inspect --format='{{.Name}} {{.HostConfig.LogConfig.Config.max-size}}'
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Problem**: `connection refused` or `could not connect to server`

**Solutions**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Verify database credentials in .env match docker-compose.yml
```

#### 2. Worker Not Processing Tasks

**Problem**: Jobs stuck in "pending" status

**Solutions**:
```bash
# Check worker status
docker-compose ps worker
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Check Celery can connect to Redis
docker-compose exec worker celery -A worker inspect ping

# Check Redis is accessible
docker-compose exec redis redis-cli ping
```

#### 3. Migration Errors

**Problem**: `Target database is not up to date`

**Solutions**:
```bash
# View current migration status
docker-compose exec api alembic current

# Apply pending migrations
docker-compose exec api alembic upgrade head

# If migrations fail, check logs
docker-compose exec api alembic history
```

#### 4. AWS Credentials Not Found

**Problem**: `Unable to locate credentials`

**Solutions**:
```bash
# Verify AWS credentials directory is mounted
docker-compose config | grep aws

# Check AWS_CONFIG_DIR in .env points to correct location
# Default: ~/.aws

# Ensure credentials file exists
ls -la ~/.aws/credentials
```

#### 5. Port Already in Use

**Problem**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solutions**:
```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in .env
API_PORT=8001
```

### Debugging Tips

#### Access Container Shell

```bash
# API container
docker-compose exec api /bin/bash

# Worker container
docker-compose exec worker /bin/bash

# Database container
docker-compose exec postgres /bin/bash
```

#### Run Python Commands

```bash
# Python REPL in API container
docker-compose exec api python

# Run specific script
docker-compose exec api python triton_app.py
```

#### View Environment Variables

```bash
# All env vars in API container
docker-compose exec api env

# Specific variable
docker-compose exec api env | grep POSTGRES
```

#### Clean Restart

```bash
# Stop everything
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

## Production Considerations

### Security

- [ ] Change default passwords in `.env`
- [ ] Enable authentication on Redis (set `REDIS_PASSWORD`)
- [ ] Restrict CORS origins in `app.py`
- [ ] Use secrets management (AWS Secrets Manager, Vault, etc.)
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Use read-only database user for read operations

### Performance

- [ ] Scale workers based on load (`docker-compose up -d --scale worker=N`)
- [ ] Tune database connection pool settings (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`)
- [ ] Configure Celery task time limits (`CELERY_TASK_TIME_LIMIT`)
- [ ] Enable Redis persistence if needed
- [ ] Set up database indexes for query optimization

### Reliability

- [ ] Set up database backups (automated pg_dump)
- [ ] Configure log rotation
- [ ] Set up health check monitoring (Prometheus, Datadog, etc.)
- [ ] Configure restart policies in docker-compose.yml
- [ ] Set up alerting for failures

### Deployment

- [ ] Use Docker Swarm or Kubernetes for orchestration
- [ ] Set up CI/CD pipeline
- [ ] Use environment-specific configuration files
- [ ] Implement blue-green or canary deployments
- [ ] Set up load balancer for API

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

## Support

For issues and questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker-compose logs -f`
3. Check API documentation: http://localhost:8000/docs
4. Open an issue in the project repository

---

**Last Updated**: 2025-01-26
