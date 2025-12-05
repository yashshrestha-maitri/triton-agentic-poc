# Triton Agentic Monitoring Stack

Complete observability stack with **Grafana** + **Prometheus** (metrics) + **Loki** (logs) for monitoring all Triton services.

## Quick Start

### 1. Start the Monitoring Stack

```bash
# Start all services including monitoring
docker-compose --profile monitoring up -d

# Or start main services first, then monitoring
docker-compose up -d
docker-compose --profile monitoring up -d
```

### 2. Access the Dashboards

- **Grafana UI**: http://localhost:3000
  - Username: `admin`
  - Password: `admin` (change on first login)
- **Prometheus UI**: http://localhost:9090
- **Loki API**: http://localhost:3100

### 3. Stop Monitoring

```bash
docker-compose --profile monitoring down
```

## What's Being Monitored

### Metrics (Prometheus)
- **Triton API**: Request rates, latency, error rates, endpoint performance
- **Celery Worker**: Task queue depth, processing time, success/failure rates
- **PostgreSQL**: Connections, queries, cache hit ratio, transaction rates
- **Redis**: Memory usage, commands/sec, key count, evictions
- **Containers**: CPU, memory, network usage (if node-exporter enabled)

### Logs (Loki)
- **All Docker Containers**: Real-time log aggregation
- **Structured Logs**: JSON parsing with automatic field extraction
- **Log Levels**: Automatic detection (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Searchable**: Full-text search with LogQL
- **Correlat**ed**: View logs alongside metrics on same dashboard

## Using Grafana

### Explore Metrics

1. Go to **Explore** (compass icon)
2. Select **Prometheus** datasource
3. Try these queries:

```promql
# Request rate per service
rate(http_requests_total[5m])

# Average response time
avg(http_request_duration_seconds) by (service)

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# Celery queue depth
celery_queue_length

# Database connections
pg_stat_database_numbackends
```

### Explore Logs

1. Go to **Explore**
2. Select **Loki** datasource
3. Try these queries:

```logql
# All logs from triton-api
{service="triton-api"}

# Only ERROR logs
{service="triton-api"} |= "ERROR"

# Logs containing specific text
{service="triton-worker"} |~ "Template generation"

# Multiple services
{service=~"triton-api|celery-worker"}

# Filter by log level
{service="triton-api"} | json | level="ERROR"

# Search for job failures
{service="triton-worker"} |~ "failed|error" | json

# Task execution logs
{service="triton-worker"} |~ "Task.*generate_templates"
```

### LogQL Advanced Queries

```logql
# Count errors per minute
sum(count_over_time({service="triton-api"} |= "ERROR" [1m])) by (service)

# Top 10 error messages
topk(10, sum by (message) (count_over_time({level="ERROR"} [1h])))

# Logs with specific JSON field
{service="triton-api"} | json | job_id!=""

# Time-based filtering (last hour errors)
{service="triton-worker"} |= "ERROR" [1h]
```

## Creating Custom Dashboards

### Example: System Overview Dashboard

1. Click **+** → **Dashboard**
2. Add panels with these queries:

**API Request Rate:**
```promql
sum(rate(http_requests_total{service="triton-api"}[5m])) by (method, endpoint)
```

**Active Celery Tasks:**
```promql
celery_active_tasks
```

**Database Query Time:**
```promql
rate(pg_stat_statements_mean_exec_time_seconds[5m])
```

**Error Logs Count:**
```logql
sum(count_over_time({service=~".*"} |= "ERROR" [5m])) by (service)
```

### Example: Celery Worker Dashboard

```promql
# Tasks per second
rate(celery_tasks_total[1m])

# Task duration (95th percentile)
histogram_quantile(0.95, rate(celery_task_duration_seconds_bucket[5m]))

# Task success rate
sum(rate(celery_tasks_total{state="SUCCESS"}[5m])) /
sum(rate(celery_tasks_total[5m])) * 100

# Worker status
celery_worker_up
```

## Alerts Configuration

Create alert rules in Prometheus (`monitoring/alerts/rules.yml`):

```yaml
groups:
  - name: triton_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) /
          sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "{{ $value }}% of requests are failing"

      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Celery queue backlog"
          description: "{{ $value }} tasks waiting in queue"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
```

## Monitoring Best Practices

### 1. Use Labels Effectively

```python
# In FastAPI - add custom labels
from prometheus_client import Counter

api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status', 'client_type']
)
```

### 2. Set Up Retention

- **Prometheus**: Keeps metrics for 15 days by default
- **Loki**: Configured for 30 days retention
- Adjust in config files if needed

### 3. Dashboard Organization

- Create separate dashboards for:
  - System Overview (all services)
  - API Performance
  - Celery Workers
  - Database Performance
  - Error Investigation

### 4. Use Variables

Create dashboard variables for:
- Service selection: `{service="$service"}`
- Time range: `[$__interval]`
- Environment: `{environment="$env"}`

## Troubleshooting

### No Metrics Showing

```bash
# Check if exporters are running
docker ps | grep exporter

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check if metrics endpoint is accessible
curl http://localhost:8000/metrics
```

### No Logs Showing

```bash
# Check Promtail logs
docker logs triton-promtail

# Check Loki is receiving logs
curl http://localhost:3100/ready

# Verify Promtail can access Docker socket
docker exec triton-promtail ls -la /var/run/docker.sock
```

### Dashboard Not Loading

```bash
# Check Grafana logs
docker logs triton-grafana

# Verify datasources are configured
curl http://localhost:3000/api/datasources

# Check dashboard provisioning
docker exec triton-grafana ls -la /etc/grafana/provisioning
```

## Advanced Features

### Distributed Tracing (Optional)

Add Jaeger or Tempo for distributed tracing:
```yaml
# docker-compose.yml
tempo:
  image: grafana/tempo:latest
  ports:
    - "3200:3200"
    - "4317:4317"  # OTLP gRPC
```

### Long-term Storage (Optional)

Configure Prometheus remote write to external storage:
```yaml
# prometheus.yml
remote_write:
  - url: "http://cortex:9009/api/prom/push"
```

### Alert Notifications (Optional)

Set up Alertmanager for notifications:
```yaml
# alertmanager.yml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#alerts'
```

## Next Steps

1. **Add Metrics to Mare-API**: Follow same instrumentation pattern
2. **Create Custom Dashboards**: Based on your specific needs
3. **Set Up Alerts**: For critical metrics
4. **Enable Authentication**: Secure Grafana with OAuth or LDAP
5. **Export Dashboards**: Share dashboard JSON files with team

## Resources

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL Documentation](https://grafana.com/docs/loki/latest/logql/)
- [FastAPI Prometheus Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
