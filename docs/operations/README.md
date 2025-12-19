# Operations & Deployment Documentation

**Purpose:** Setup, deployment, testing, and operational guides

---

## Overview

This folder contains documentation for **deploying, running, and maintaining** the Triton platform. Whether you're setting up a development environment, deploying to production, or troubleshooting issues, start here.

---

## 📚 Documentation Files

### Getting Started

| File | Purpose | Time Required |
|------|---------|---------------|
| [QUICKSTART.md](./QUICKSTART.md) | 5-minute setup and first run | 5-10 minutes |
| [API_README.md](./API_README.md) | REST API reference and endpoints | Reference |

### Deployment & Infrastructure

| File | Purpose | Audience |
|------|---------|----------|
| [DOCKER_SETUP.md](./DOCKER_SETUP.md) | Container deployment guide | DevOps, Backend |
| [MONITORING_SETUP.md](./MONITORING_SETUP.md) | Prometheus, Grafana, observability | DevOps, SRE |

### Testing & Quality

| File | Purpose | Audience |
|------|---------|----------|
| [TESTING_AND_MONITORING_GUIDE.md](./TESTING_AND_MONITORING_GUIDE.md) | Testing and monitoring best practices | All developers |
| [SYSTEM_VERIFICATION_REPORT.md](./SYSTEM_VERIFICATION_REPORT.md) | System verification results | QA, DevOps |
| [HYBRID_PDF_PROCESSING_GUIDE.md](./HYBRID_PDF_PROCESSING_GUIDE.md) | Hybrid PDF processing implementation | Backend, DevOps |

### Data Lineage & Audit

| File | Purpose | Audience |
|------|---------|----------|
| [DATA_LINEAGE_API_GUIDE.md](./DATA_LINEAGE_API_GUIDE.md) | ⭐ Complete lineage tracking guide with curl examples | Backend, DevOps, Compliance |

### Security & Access Control

| File | Purpose | Audience |
|------|---------|----------|
| [ALL_ENDPOINTS_LIST.md](./ALL_ENDPOINTS_LIST.md) | ⭐ **Complete endpoint list** - All 122 endpoints with function names, paths, and descriptions | All developers, QA, API consumers |
| [COMPLETE_USER_ROLE_MATRIX.md](./COMPLETE_USER_ROLE_MATRIX.md) | ⭐ **Complete user role matrix for Triton + Mare API** (122 endpoints, 4 roles, 26 permissions) | Backend, DevOps, Security, Product |

### Meta Documentation

| File | Purpose | Audience |
|------|---------|----------|
| [DOCUMENTATION_ORGANIZATION.md](./DOCUMENTATION_ORGANIZATION.md) | How documentation is organized | All developers |

---

## 🚀 Quick Start

### New Developer Setup (5 minutes)

**1. Install Dependencies**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials
```

**2. Start Development Server**
```bash
# Run REST API
uvicorn app:app --reload --port 8000

# API docs available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

**3. Test the System**
```bash
# Run prototype test
python triton_app.py

# Run API tests
python tests/test_research_api.py
```

**See [QUICKSTART.md](./QUICKSTART.md) for detailed instructions**

---

## 🐳 Docker Deployment

### Quick Docker Setup

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker logs triton-api
docker logs triton-worker

# Stop services
docker-compose down
```

### Services

| Service | Port | Purpose |
|---------|------|---------|
| `triton-api` | 8000 | FastAPI REST API |
| `triton-worker` | - | Celery worker (background jobs) |
| `triton-redis` | 6379 | Redis (message broker + cache) |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3000 | Metrics visualization |

**See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for complete deployment guide**

---

## 📊 Monitoring & Observability

### Prometheus + Grafana Stack

**Setup monitoring:**
```bash
# Start monitoring stack
docker-compose up -d prometheus grafana

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)
```

### Available Metrics

| Metric | Purpose |
|--------|---------|
| `triton_template_generation_duration_seconds` | Template generation time |
| `triton_agent_execution_duration_seconds` | Agent execution time |
| `triton_validation_failures_total` | Validation failure count |
| `triton_active_jobs` | Currently running jobs |

### Grafana Dashboards

1. **Job Performance**: Generation times, success rates
2. **System Health**: CPU, memory, request rates
3. **Agent Metrics**: LLM calls, retry counts

**See [MONITORING_SETUP.md](./MONITORING_SETUP.md) for detailed setup**

---

## 📄 PDF Processing

### Hybrid PDF Processing (NEW)

The system uses a **hybrid approach** combining traditional text extraction with Claude Vision API fallback:

**Processing Strategy:**
1. **Traditional extraction first** (PyPDF2) - Fast & cheap
2. **Quality assessment** - 0-100 score based on text density, structure, extraction confidence
3. **Vision API fallback** - For poor-quality or scanned PDFs

**Benefits:**
- ✅ **67% cost savings** vs vision-only approach
- ✅ **95%+ success rate** vs 60-70% traditional-only
- ✅ **Automatic fallback** for scanned/complex PDFs
- ✅ **Performance optimized** - Only use vision when needed

**Configuration:**
```bash
# Quality threshold (0-100)
PDF_QUALITY_THRESHOLD=70

# Enable/disable vision fallback
ENABLE_VISION_FALLBACK=true

# Maximum pages for vision processing
MAX_VISION_PAGES=100
```

**Cost Examples:**
- Traditional: ~$0.003 per 10-page document
- Vision fallback: ~$0.054 per 10-page document
- Hybrid (70% traditional, 25% vision): ~$0.011 per document average

**See [HYBRID_PDF_PROCESSING_GUIDE.md](./HYBRID_PDF_PROCESSING_GUIDE.md) for complete implementation details**

---

## 🧪 Testing

### Test Types

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **Agent Tests**: Research agent validation
4. **Load Tests**: Performance under load

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_research_api.py

# Run with coverage
pytest tests/ --cov=agents --cov=core

# Run agent tests
python test_research_agents.py
```

### Test Coverage

| Component | Coverage | Notes |
|-----------|----------|-------|
| Research Agents | ✅ 95% | WebSearch + Document Analysis |
| Template Generator | ✅ 90% | Template validation |
| API Endpoints | ✅ 85% | REST API routes |
| ROI Model Builder | ✅ 80% | Model generation |

**See [TESTING_AND_MONITORING_GUIDE.md](./TESTING_AND_MONITORING_GUIDE.md) for best practices**

---

## 📖 API Reference

### Core Endpoints

#### Template Generation
```bash
POST /templates/generate
GET  /templates/{template_id}
GET  /templates/
```

#### Research Agents
```bash
POST /research/web-search
POST /research/document-analysis
GET  /research/{job_id}
```

#### ROI Models
```bash
POST /roi-models/generate
GET  /roi-models/{model_id}
```

#### Prospect Data
```bash
POST /prospect-data/generate
GET  /prospect-data/{prospect_id}
```

#### Real-Time Updates
```bash
GET /jobs/{job_id}/subscribe  # Server-Sent Events (SSE)
```

**See [API_README.md](./API_README.md) for complete API documentation**

---

## ⚙️ Configuration

### Environment Variables

**Required:**
```bash
# AWS Bedrock
AWS_PROFILE=your-profile
AWS_REGION=us-east-1

# Model Configuration
DEFAULT_MODEL_PROVIDER=aws_bedrock
DEFAULT_MODEL_NAME=us.anthropic.claude-sonnet-4-20250514-v1:0
```

**Optional (for production):**
```bash
# Research Tool APIs
TAVILY_API_KEY=tvly-...          # Google search
FIRECRAWL_API_KEY=fc-...         # Web scraping

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_PORT=9090

# PDF Processing (Hybrid Approach)
PDF_QUALITY_THRESHOLD=70       # Quality score threshold (0-100)
ENABLE_VISION_FALLBACK=true    # Enable Claude Vision API fallback
MAX_VISION_PAGES=100           # Max pages for vision processing
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**2. AWS Credentials**
```bash
# Solution: Configure AWS credentials
aws configure --profile your-profile
```

**3. Port Already in Use**
```bash
# Solution: Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**4. Redis Connection Error**
```bash
# Solution: Start Redis
docker start triton-redis
# OR
redis-server
```

### Logs & Debugging

```bash
# Check API logs
docker logs triton-api -f

# Check worker logs
docker logs triton-worker -f

# Check Redis events
docker exec -it triton-redis redis-cli MONITOR

# Enable debug mode
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
```

---

## 📋 System Verification

### Pre-Deployment Checklist

✅ All tests passing (`pytest tests/`)
✅ Environment variables configured
✅ AWS credentials valid
✅ Redis accessible
✅ Database schema up-to-date
✅ Docker images built
✅ Monitoring stack running
✅ API documentation accessible

**See [SYSTEM_VERIFICATION_REPORT.md](./SYSTEM_VERIFICATION_REPORT.md) for detailed verification**

---

## 🚦 Deployment Checklist

### Development Environment

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] AWS credentials set
- [ ] API server running (`uvicorn app:app --reload`)
- [ ] Tests passing

### Staging/Production Environment

- [ ] Docker Compose configured
- [ ] All services running (`docker-compose ps`)
- [ ] Monitoring stack enabled (Prometheus + Grafana)
- [ ] Database migrations applied
- [ ] Redis connected
- [ ] Health checks passing (`curl http://localhost:8000/health`)
- [ ] SSL/TLS certificates installed (production only)
- [ ] API keys secured (not in code)
- [ ] Backup strategy in place

---

## 📚 Learning Paths

### DevOps Engineer Path

1. [QUICKSTART.md](./QUICKSTART.md) - Get system running
2. [DOCKER_SETUP.md](./DOCKER_SETUP.md) - Container deployment
3. [MONITORING_SETUP.md](./MONITORING_SETUP.md) - Observability setup
4. [SYSTEM_VERIFICATION_REPORT.md](./SYSTEM_VERIFICATION_REPORT.md) - Verification

### Backend Developer Path

1. [QUICKSTART.md](./QUICKSTART.md) - Get started
2. [API_README.md](./API_README.md) - API reference
3. [HYBRID_PDF_PROCESSING_GUIDE.md](./HYBRID_PDF_PROCESSING_GUIDE.md) - PDF processing implementation
4. [TESTING_AND_MONITORING_GUIDE.md](./TESTING_AND_MONITORING_GUIDE.md) - Best practices
5. [../architecture-current/](../architecture-current/) - System architecture

### QA Engineer Path

1. [TESTING_AND_MONITORING_GUIDE.md](./TESTING_AND_MONITORING_GUIDE.md) - Testing approach
2. [SYSTEM_VERIFICATION_REPORT.md](./SYSTEM_VERIFICATION_REPORT.md) - Verification procedures
3. [API_README.md](./API_README.md) - API testing

---

## 🔗 Related Documentation

- **Current Architecture**: [../architecture-current/README.md](../architecture-current/README.md)
- **Features**: [../features/README.md](../features/README.md)
- **Legacy Architecture**: [../architecture-legacy/README.md](../architecture-legacy/README.md)
- **Main Documentation Index**: [../README.md](../README.md)

---

## 📞 Support

### Documentation

- **Quickstart Issues**: See [QUICKSTART.md](./QUICKSTART.md)
- **Docker Issues**: See [DOCKER_SETUP.md](./DOCKER_SETUP.md)
- **API Issues**: See [API_README.md](./API_README.md)

### Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

---

**For architectural questions**: See [architecture-current/README.md](../architecture-current/README.md)
**For feature-specific questions**: See [features/README.md](../features/README.md)
