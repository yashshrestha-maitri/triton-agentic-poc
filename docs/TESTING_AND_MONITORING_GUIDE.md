# Testing & Monitoring Guide for Triton + Mare-API

Complete guide to test the integration workflow and monitor with Grafana.

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# In triton-agentic directory
pip install -r requirements.txt

# This installs:
# - prometheus-fastapi-instrumentator
# - prometheus-client
```

### Step 2: Start All Services

```bash
# Start main services
docker-compose up -d

# Start monitoring stack
docker-compose --profile monitoring up -d

# Wait for services to be healthy (30 seconds)
sleep 30
```

### Step 3: Verify Setup

```bash
# Check all services are running
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "triton|mare|grafana"

# Test metrics endpoints
curl http://localhost:8000/metrics | head -20    # Triton API
curl http://localhost:16000/metrics | head -20   # Mare-API

# Access dashboards
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
```

### Step 4: Run Integration Test

```bash
# Run the complete workflow test
python tests/integration/test_workflow.py --verbose

# This will:
# ✓ Test health endpoints
# ✓ Create client via Mare-API
# ✓ Create value proposition
# ✓ Submit template generation job
# ✓ Poll until completion (may take 2-5 minutes)
# ✓ Retrieve generated templates
# ✓ Save results to JSON file
```

### Step 5: View Results in Grafana

```bash
# Open Grafana
open http://localhost:3000

# Login: admin / admin

# Navigate to:
# 1. Explore → Prometheus → Try sample queries
# 2. Explore → Loki → View logs
# 3. Create custom dashboards
```

## 📊 What's Been Added

### Prometheus Metrics

**Triton API (`app.py`):**
- ✅ HTTP request metrics (count, duration, status)
- ✅ Custom metrics: template generations, agent execution, active jobs, queue length
- ✅ Metrics endpoint: `http://localhost:8000/metrics`

**Mare-API (`src/main.py`):**
- ✅ HTTP request metrics (count, duration, status)
- ✅ Metrics endpoint: `http://localhost:16000/metrics`

### Test Scripts

**Integration Test** (`tests/integration/test_workflow.py`):
- Complete end-to-end workflow test
- Measures timing for each step
- Saves results to JSON
- Color-coded console output

## 📈 Sample Prometheus Queries

### API Performance

```promql
# Request rate (requests/second)
rate(http_requests_total[5m])

# Average response time
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# P95 latency
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m]))
```

### Database & Redis

```promql
# PostgreSQL connections
pg_stat_database_numbackends

# Redis memory usage (MB)
redis_memory_used_bytes / 1024 / 1024

# Redis commands per second
rate(redis_commands_processed_total[1m])
```

### Service Health

```promql
# All services up/down (1=up, 0=down)
up{job!=""}

# Container health
up{service=~"triton-api|triton-worker|mare-api"}
```

## 📝 Sample Log Queries (LogQL)

### View All Logs

```logql
# All logs from Triton API
{service="triton-api"}

# All logs from Celery worker
{service="triton-worker"}

# All services
{service=~".*"}
```

### Filter by Level

```logql
# Only errors
{service=~".*"} |= "ERROR"

# Errors and warnings
{service=~".*"} |~ "ERROR|WARNING"

# Info level from API
{service="triton-api"} |= "INFO"
```

### Search Content

```logql
# Template generation logs
{service="triton-worker"} |~ "Template generation"

# Failed jobs
{service=~".*"} |~ "failed|Failed"

# Specific job ID
{service=~".*"} |~ "job_id.*abc-123"
```

### Aggregate Logs

```logql
# Count errors per service per minute
sum(count_over_time({service=~".*"} |= "ERROR" [1m])) by (service)

# Top error messages
topk(10, sum by (message) (
  count_over_time({level="ERROR"} [1h])
))
```

## 🎯 Expected Test Results

When you run the integration test successfully, you should see:

```
[INFO] ================================================================================
[INFO] Triton + Mare-API Integration Test
[INFO] ================================================================================
[SUCCESS] ✓ Mare-API health check passed (150ms)
[SUCCESS] ✓ Triton API health check passed (120ms)
[SUCCESS] ✓ Client created: abc-123-... (250ms)
[SUCCESS] ✓ Value proposition created: def-456-... (180ms)
[SUCCESS] ✓ Job submitted: ghi-789-... (200ms)
[INFO]   Poll #1: Status=pending, Elapsed=5s
[INFO]   Poll #2: Status=running, Elapsed=10s
...
[SUCCESS] ✓ Job completed successfully (145s, 29 polls)
[SUCCESS] ✓ Retrieved 7 templates (350ms)

[INFO] ================================================================================
[INFO] Test Summary
[INFO] ================================================================================
[INFO] Total Steps: 6
[SUCCESS] Successes: 6
[INFO] Failures: 0
[INFO] Total Duration: 148.50s

[INFO] Key Metrics:
[INFO]   mare_api_health_check_time: 0.15s
[INFO]   triton_api_health_check_time: 0.12s
[INFO]   client_creation_time: 0.25s
[INFO]   value_proposition_creation_time: 0.18s
[INFO]   job_submission_time: 0.20s
[INFO]   job_completion_time: 145.30s
[INFO]   template_retrieval_time: 0.35s
[INFO]   templates_generated: 7
[INFO]   total_workflow_time: 148.50s

[SUCCESS] ✓ Results saved to: test_results_20251126_103045.json
```

## 🔍 Troubleshooting

### Test Fails at Health Check

```bash
# Check services are running
docker ps | grep -E "triton|mare"

# Check logs
docker logs triton-api --tail 50
docker logs mare-api --tail 50

# Restart services
docker-compose restart api
cd /path/to/mare-api && docker-compose restart mare-api
```

### No Metrics Showing

```bash
# Verify metrics endpoints
curl http://localhost:8000/metrics
curl http://localhost:16000/metrics

# Check Prometheus is scraping
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'

# Restart Prometheus
docker-compose --profile monitoring restart prometheus
```

### Job Never Completes

```bash
# Check worker logs
docker logs triton-worker --tail 100

# Check job status directly
curl http://localhost:8000/jobs/{job_id}

# Check Celery queue
docker exec triton-redis redis-cli LLEN celery

# Restart worker
docker-compose restart worker
```

## 📚 Next Steps

1. **Create Custom Dashboards** - Build Grafana dashboards for your metrics
2. **Set Up Alerts** - Configure alerts for critical metrics
3. **Load Testing** - Run multiple concurrent tests
4. **Performance Tuning** - Use metrics to identify bottlenecks
5. **Production Monitoring** - Deploy monitoring stack to production

## 🎓 Resources

- **Monitoring README**: `monitoring/README.md` - Complete Grafana/Prometheus/Loki guide
- **Metrics Guide**: `monitoring/FASTAPI_METRICS_GUIDE.md` - How to add custom metrics
- **Quick Start**: `monitoring/QUICKSTART.md` - 5-minute setup guide

---

**Everything is ready to test and monitor!** 🎉

Just run:
```bash
docker-compose --profile monitoring up -d
python tests/integration/test_workflow.py --verbose
```
