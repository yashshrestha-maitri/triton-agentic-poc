1# Adding Prometheus Metrics to FastAPI Applications

This guide shows how to instrument your FastAPI applications (Triton API and Mare-API) with Prometheus metrics.

## Installation

Already added to `requirements.txt`:
```
prometheus-fastapi-instrumentator>=6.1.0
prometheus-client>=0.19.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## For Triton API

### 1. Update `app.py`

Add this code to your main FastAPI application file:

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Triton Agentic API")

# ... your existing middleware and routes ...

# =============================================================================
# Prometheus Metrics Instrumentation
# =============================================================================

# Initialize instrumentator
instrumentator = Instrumentator(
    should_group_status_codes=False,  # Keep individual status codes
    should_ignore_untemplated=True,   # Ignore 404s from invalid paths
    should_respect_env_var=True,      # Can disable via env var
    should_instrument_requests_inprogress=True,  # Track concurrent requests
    excluded_handlers=["/metrics"],    # Don't track metrics endpoint itself
    env_var_name="ENABLE_METRICS",    # Enable/disable via env
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)

# Add default metrics (request count, duration, size)
instrumentator.instrument(app)

# Expose metrics endpoint
instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)

# =============================================================================
# Custom Metrics (Optional)
# =============================================================================

from prometheus_client import Counter, Histogram, Gauge

# Custom counters
template_generation_counter = Counter(
    'triton_template_generations_total',
    'Total template generation requests',
    ['client_id', 'status']
)

agent_execution_duration = Histogram(
    'triton_agent_execution_seconds',
    'Agent execution duration',
    ['agent_name', 'success'],
    buckets=(1, 5, 10, 30, 60, 120, 300)  # seconds
)

active_jobs = Gauge(
    'triton_active_jobs',
    'Number of currently active generation jobs'
)

# Use these in your routes:
# template_generation_counter.labels(client_id="123", status="success").inc()
# with agent_execution_duration.labels(agent_name="template_generator", success="true").time():
#     # ... agent execution code ...
```

### 2. Update Routes to Add Custom Metrics

Example for `api/routes/jobs.py`:

```python
from prometheus_client import Counter, Histogram
import time

# Define metrics at module level
job_creation_counter = Counter(
    'triton_jobs_created_total',
    'Total generation jobs created',
    ['client_id']
)

job_completion_duration = Histogram(
    'triton_job_completion_seconds',
    'Time from job creation to completion',
    ['status'],
    buckets=(10, 30, 60, 120, 300, 600)
)

@router.post("/", response_model=JobStatusResponse)
def create_generation_job(request: JobCreateRequest, db: Session = Depends(get_db)):
    # ... existing code ...

    # Increment counter
    job_creation_counter.labels(client_id=str(request.client_id)).inc()

    # ... rest of the code ...
    return JobStatusResponse.model_validate(job)

@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

    # Track completion time
    if job.status in ["completed", "failed"] and job.generation_duration_ms:
        job_completion_duration.labels(status=job.status).observe(
            job.generation_duration_ms / 1000.0
        )

    return JobStatusResponse.model_validate(job)
```

### 3. Update Worker to Export Metrics

For Celery workers, add metrics to `tasks/template_generation.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, push_to_gateway
import time

# Define worker metrics
task_execution_counter = Counter(
    'celery_tasks_executed_total',
    'Total tasks executed',
    ['task_name', 'status']
)

task_duration_histogram = Histogram(
    'celery_task_duration_seconds',
    'Task execution duration',
    ['task_name'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600)
)

active_tasks_gauge = Gauge(
    'celery_active_tasks',
    'Currently executing tasks',
    ['task_name']
)

@celery_app.task(bind=True)
def generate_templates_task(self, job_id: str, client_id: str, ...):
    task_name = "generate_templates"

    # Track active tasks
    active_tasks_gauge.labels(task_name=task_name).inc()

    start_time = time.time()
    try:
        # ... existing task code ...

        # Record success
        duration = time.time() - start_time
        task_duration_histogram.labels(task_name=task_name).observe(duration)
        task_execution_counter.labels(task_name=task_name, status="success").inc()

    except Exception as e:
        # Record failure
        task_execution_counter.labels(task_name=task_name, status="failure").inc()
        raise
    finally:
        active_tasks_gauge.labels(task_name=task_name).dec()
```

## For Mare-API

Add the same instrumentation to Mare-API's main application file:

```python
# In mare-api/src/main.py
from prometheus_fastapi_instrumentator import Instrumentator

# After creating the FastAPI app
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics"],
)

instrumentator.instrument(app)
instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)
```

## Environment Configuration

Add to `.env`:

```bash
# Monitoring
ENABLE_METRICS=true
```

## Verify Metrics Endpoint

After adding instrumentation, restart services and check:

```bash
# Triton API metrics
curl http://localhost:8000/metrics

# Mare-API metrics
curl http://localhost:16000/metrics

# Should see output like:
# http_requests_total{method="GET",path="/health",status="200"} 42.0
# http_request_duration_seconds_bucket{le="0.1",method="GET"} 38.0
```

## Available Default Metrics

The instrumentator automatically provides:

### Request Metrics
- `http_requests_total` - Total HTTP requests by method, path, status
- `http_request_duration_seconds` - Request latency histogram
- `http_request_size_bytes` - Request body size
- `http_response_size_bytes` - Response body size
- `http_requests_inprogress` - Currently processing requests

### Labels
- `method` - HTTP method (GET, POST, etc.)
- `handler` - Route path (/jobs/, /clients/, etc.)
- `status` - HTTP status code (200, 404, 500, etc.)

## Custom Metrics Best Practices

### 1. Metric Types

**Counter** - Monotonically increasing (requests, errors):
```python
api_errors = Counter('api_errors_total', 'Total API errors', ['endpoint'])
api_errors.labels(endpoint='/jobs').inc()
```

**Gauge** - Can go up and down (connections, queue length):
```python
queue_size = Gauge('job_queue_size', 'Current job queue size')
queue_size.set(42)
```

**Histogram** - Distribution of values (latency, size):
```python
response_time = Histogram('response_time_seconds', 'Response time', buckets=(0.1, 0.5, 1, 5))
response_time.observe(1.23)
```

**Summary** - Like histogram but calculates quantiles:
```python
request_latency = Summary('request_latency_seconds', 'Request latency')
request_latency.observe(0.42)
```

### 2. Naming Conventions

Follow Prometheus naming best practices:
- Use `_total` suffix for counters
- Use `_seconds` for durations
- Use `_bytes` for sizes
- Use snake_case
- Include application prefix (triton_, mare_)

### 3. Cardinality

**Avoid high-cardinality labels** (like user_id, job_id):
```python
# BAD - creates a metric per job
Counter('jobs_total', 'Jobs', ['job_id'])  # DON'T DO THIS

# GOOD - aggregates by status
Counter('jobs_total', 'Jobs', ['status'])  # DO THIS
```

### 4. Context Managers

Use context managers for automatic timing:
```python
with agent_execution_duration.labels(agent_name="template_gen").time():
    result = agent.run(prompt)
```

## Testing

### 1. Generate Some Load

```bash
# Create some requests
for i in {1..100}; do
    curl -s http://localhost:8000/health > /dev/null
    curl -s http://localhost:8000/clients/ > /dev/null
done
```

### 2. Check Metrics

```bash
curl http://localhost:8000/metrics | grep http_requests_total
```

### 3. Query in Prometheus

```promql
# Total requests per second
rate(http_requests_total[1m])

# Average response time
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) by (handler)
```

## Troubleshooting

### Metrics Endpoint Returns 404

Make sure you called `instrumentator.expose()` after `instrumentator.instrument()`.

### No Metrics Showing in Prometheus

1. Check Prometheus config includes the service
2. Verify Prometheus can reach the metrics endpoint:
   ```bash
   docker exec triton-prometheus wget -O- http://triton-api:8000/metrics
   ```
3. Check Prometheus targets page: http://localhost:9090/targets

### Worker Metrics Not Appearing

Workers need to either:
1. Expose an HTTP endpoint (requires extra setup)
2. Push metrics to Prometheus Push Gateway
3. Use Celery exporter (recommended)

For Celery, use the redis exporter and query Celery metrics from Redis.

## Next Steps

1. **Add metrics to all critical endpoints**
2. **Create Grafana dashboards** using these metrics
3. **Set up alerting rules** for important thresholds
4. **Monitor metric cardinality** to avoid explosion
5. **Document custom metrics** for your team

## Resources

- [FastAPI Instrumentator Docs](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [Prometheus Client Python](https://github.com/prometheus/client_python)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
