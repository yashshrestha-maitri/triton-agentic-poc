# Grafana Monitoring Stack - Quick Start

Get your complete observability stack running in 5 minutes!

## 🚀 Start Monitoring Stack

```bash
# Navigate to triton-agentic directory
cd /home/yashrajshres/triton-agentic

# Start all services including monitoring
docker-compose --profile monitoring up -d

# Watch logs to ensure everything starts
docker-compose --profile monitoring logs -f
```

## 📊 Access Dashboards

Once all services are healthy:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | None |
| **Loki** | http://localhost:3100 | None |

## ✅ Verify Setup

```bash
# Check all containers are running
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "triton|grafana|prometheus|loki"

# Expected output:
# triton-grafana     Up (healthy)
# triton-prometheus  Up
# triton-loki        Up
# triton-promtail    Up
# triton-postgres-exporter  Up
# triton-redis-exporter     Up
# triton-api         Up (healthy)
# triton-worker      Up (healthy)

# Test Prometheus is scraping
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'

# Test Loki is ready
curl http://localhost:3100/ready

# Test metrics endpoint
curl http://localhost:8000/metrics | head -20
```

## 📈 First Steps in Grafana

### 1. Log In
- Go to http://localhost:3000
- Username: `admin`
- Password: `admin`
- Change password when prompted (or skip)

### 2. Explore Metrics
- Click **Explore** (compass icon on left)
- Select **Prometheus** from datasource dropdown
- Try these queries:

```promql
# PostgreSQL connections
pg_stat_database_numbackends

# Redis memory usage
redis_memory_used_bytes / 1024 / 1024

# Container stats
up{job=~".*"}
```

### 3. Explore Logs
- Click **Explore**
- Select **Loki** from datasource dropdown
- Try these queries:

```logql
# All logs from triton-api
{service="triton-api"}

# Error logs only
{service=~".*"} |= "ERROR"

# Celery task logs
{service="triton-worker"} |~ "Task.*generate_templates"
```

### 4. Create Your First Dashboard
1. Click **+** → **Dashboard**
2. Click **Add visualization**
3. Select **Prometheus**
4. In query, enter: `up{job!=""}`
5. Run query and see results
6. Click **Apply** to add panel
7. Click **Save** (disk icon) to save dashboard

## 🎯 Pre-Built Queries

### System Health
```promql
# All services status (1 = up, 0 = down)
up

# Database connections
pg_stat_database_numbackends

# Redis commands per second
rate(redis_commands_processed_total[1m])
```

### Application Metrics (After adding instrumentation)
```promql
# Request rate
rate(http_requests_total[5m])

# Average response time
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100
```

### Log Queries
```logql
# Count errors per minute
sum(count_over_time({service=~".*"} |= "ERROR" [1m])) by (service)

# Show failed jobs
{service="triton-worker"} |~ "failed|Failed" | json

# API errors with context
{service="triton-api"} |= "ERROR" | line_format "{{.message}}"
```

## 🛑 Stop Monitoring

```bash
# Stop monitoring stack only (keeps main services running)
docker-compose --profile monitoring down

# Stop everything
docker-compose --profile monitoring down
docker-compose down
```

## 🔧 Configuration Files

All configuration is in `monitoring/` directory:

```
monitoring/
├── prometheus.yml              # Prometheus scrape config
├── loki-config.yml             # Loki storage config
├── promtail-config.yml         # Log collection config
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/        # Auto-configured datasources
│   │   └── dashboards/         # Dashboard loading config
│   └── dashboards/             # Dashboard JSON files (add your own)
├── README.md                   # Full documentation
├── FASTAPI_METRICS_GUIDE.md   # How to add metrics to APIs
└── QUICKSTART.md               # This file
```

## 📝 Adding Metrics to Your APIs

See [FASTAPI_METRICS_GUIDE.md](./FASTAPI_METRICS_GUIDE.md) for complete instructions.

Quick version:

```python
# In app.py
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app, endpoint="/metrics")
```

Then metrics will be available at:
- Triton API: http://localhost:8000/metrics
- Mare-API: http://localhost:16000/metrics

## 🆘 Troubleshooting

### "No data" in Grafana

**Check datasources:**
```bash
curl http://localhost:3000/api/datasources
```

**Verify Prometheus can reach services:**
```bash
docker exec triton-prometheus wget -O- http://triton-api:8000/metrics
```

### Logs not showing

**Check Promtail:**
```bash
docker logs triton-promtail
```

**Verify Docker socket access:**
```bash
docker exec triton-promtail ls -la /var/run/docker.sock
```

### High memory usage

**Prometheus retention:**
Edit `monitoring/prometheus.yml` and add:
```yaml
global:
  evaluation_interval: 30s  # Increase interval
storage:
  tsdb:
    retention.time: 7d  # Reduce from 15d to 7d
```

**Loki retention:**
Edit `monitoring/loki-config.yml`:
```yaml
limits_config:
  retention_period: 168h  # 7 days instead of 30
```

## 🎓 Learn More

- **Full Documentation**: [README.md](./README.md)
- **Metrics Guide**: [FASTAPI_METRICS_GUIDE.md](./FASTAPI_METRICS_GUIDE.md)
- **Grafana Docs**: https://grafana.com/docs/grafana/latest/
- **PromQL Tutorial**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **LogQL Tutorial**: https://grafana.com/docs/loki/latest/logql/

## 🎉 Next Steps

1. ✅ **You're monitoring!** - Stack is running
2. 📊 **Create dashboards** - Build custom views
3. 🚨 **Set up alerts** - Get notified of issues
4. 📈 **Add custom metrics** - Instrument your code
5. 🔒 **Secure Grafana** - Set strong password, enable auth

Enjoy your complete observability stack! 🎯
