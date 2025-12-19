# Triton Agentic Monitoring Setup

This guide explains how to monitor Celery workers, tasks, and jobs using **Flower** and **Grafana**.

## Quick Start

### Option 1: Start Everything with Monitoring
```bash
# Start all services including Flower, Grafana, Prometheus
docker-compose --profile with-flower --profile monitoring up -d

# Check status
docker-compose ps
```

### Option 2: Start Services Separately
```bash
# Start core services (API, Worker, Database)
docker-compose up -d

# Add Flower (Celery monitoring)
docker-compose --profile with-flower up -d

# Add Grafana stack (comprehensive monitoring)
docker-compose --profile monitoring up -d
```

---

## Monitoring Tools Overview

### 🌸 Flower - Celery-Specific Monitoring

**Purpose:** Real-time Celery task and worker monitoring

**Access:** http://localhost:5555

**What You Can See:**
- ✅ Active workers and their status
- ✅ Task history (success/failure/retry)
- ✅ Task execution details (runtime, arguments, exceptions)
- ✅ Worker pool status (threads/processes)
- ✅ Task routing and queues
- ✅ Real-time task events
- ✅ Broker (Redis) statistics

**Best For:**
- Debugging specific task failures
- Checking task arguments and return values
- Monitoring worker health
- Viewing task execution timeline

---

### 📊 Grafana - Comprehensive Monitoring

**Purpose:** Metrics visualization, alerting, and historical analysis

**Access:** http://localhost:3000

**Default Credentials:**
- Username: `admin`
- Password: `admin` (change on first login)

**What You Can See:**
- ✅ Celery metrics (tasks/sec, success rate, execution time)
- ✅ PostgreSQL database metrics (connections, queries, locks)
- ✅ Redis broker metrics (memory, connections, commands/sec)
- ✅ System metrics (CPU, memory, disk if configured)
- ✅ Application logs (via Loki)
- ✅ Custom dashboards and alerts

**Pre-configured Dashboard:**
- **Celery Task Monitoring** - Located at: `/monitoring/grafana/dashboards/celery-monitoring.json`

**Best For:**
- Historical analysis and trends
- Performance optimization
- Capacity planning
- Alerting on anomalies
- Executive reporting

---

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| **Flower** | 5555 | Celery web UI |
| **Grafana** | 3000 | Dashboards and visualization |
| **Prometheus** | 9090 | Metrics database |
| **Loki** | 3100 | Log aggregation |
| **Celery Exporter** | 9808 | Celery metrics for Prometheus |
| **PostgreSQL Exporter** | 9187 | Database metrics |
| **Redis Exporter** | 9121 | Broker metrics |

---

## Flower Quick Guide

### Dashboard Overview

1. **Workers Tab** - View all active workers
   - Worker hostname and status
   - Active/completed tasks count
   - Resource usage

2. **Tasks Tab** - Browse task history
   - Task name and UUID
   - State (SUCCESS, FAILURE, PENDING, etc.)
   - Runtime and timestamp
   - Click task to see details (args, kwargs, exception)

3. **Monitor Tab** - Real-time task stream
   - Live task events as they happen
   - Task start/completion/failure events

4. **Broker Tab** - Redis statistics
   - Queue lengths
   - Message counts
   - Connection info

### Useful Flower Actions

**Check Task Details:**
1. Go to "Tasks" tab
2. Click on any task ID
3. View: Arguments, Return value, Exception traceback, Runtime

**Find Failed Tasks:**
1. Go to "Tasks" tab
2. Filter by State: "FAILURE"
3. Click task to see exception

**Monitor Worker Health:**
1. Go to "Workers" tab
2. Check status indicator (green = online, red = offline)
3. View active/completed task counts

---

## Grafana Quick Guide

### First-Time Setup

1. Open http://localhost:3000
2. Login with `admin` / `admin`
3. Set new password (or skip)
4. Go to **Dashboards** → **Browse**
5. Select **"Celery Task Monitoring"**

### Celery Dashboard Panels

The pre-configured dashboard shows:

**Top Row (Stats):**
- Active Workers count
- Tasks/second rate (5-minute average)
- Active Tasks count
- Success Rate percentage (5-minute average)

**Charts:**
- **Task Success/Failure Rate** - Line chart showing task outcomes over time
- **Task Execution Time** - p50 and p95 percentiles by task name
- **Tasks by State** - Stacked area chart (PENDING, STARTED, SUCCESS, FAILURE, RETRY)
- **Queue Length** - Monitor queue backlogs
- **Worker Status** - Table showing which workers are online/offline

### Customize Time Range

- Top-right corner: Click time picker
- Options: Last 5m, 15m, 1h, 6h, 24h, 7d
- Or set custom absolute range

### Create Alerts (Optional)

1. Edit panel → Alert tab
2. Set condition (e.g., "Success rate < 0.90")
3. Configure notification channel (Slack, email, etc.)

---

## Prometheus Metrics Available

### Celery Metrics (from celery-exporter)

```promql
# Active workers
celery_workers

# Tasks received (rate)
rate(celery_task_received_total[5m])

# Task success/failure
rate(celery_task_succeeded_total[5m])
rate(celery_task_failed_total[5m])

# Task execution time (histogram)
celery_task_runtime_seconds_bucket

# Active tasks
celery_task_active

# Queue length
celery_queue_length

# Worker uptime
celery_worker_up
```

### PostgreSQL Metrics

```promql
# Active connections
pg_stat_database_numbackends

# Queries per second
rate(pg_stat_database_xact_commit[5m])

# Database size
pg_database_size_bytes
```

### Redis Metrics

```promql
# Memory usage
redis_memory_used_bytes

# Connected clients
redis_connected_clients

# Commands per second
rate(redis_commands_processed_total[5m])
```

---

## Troubleshooting

### Flower Not Showing Tasks

**Issue:** No tasks appearing in Flower UI

**Solution:**
```bash
# Restart Flower service
docker-compose restart flower

# Check Flower logs
docker-compose logs flower
```

### Grafana Dashboard Empty

**Issue:** Celery dashboard shows "No data"

**Solution:**
1. Check Prometheus is scraping celery-exporter:
   ```bash
   # Open Prometheus: http://localhost:9090
   # Go to Status → Targets
   # Verify "celery" target is UP
   ```

2. Generate some tasks to populate metrics:
   ```bash
   # Run test script
   cd /home/yashrajshres/triton-agentic
   bash test_triton_flow.sh
   ```

3. Wait 15-30 seconds for metrics to appear

### Celery Exporter Connection Issues

**Issue:** Celery exporter can't connect to Redis

**Solution:**
```bash
# Check Redis is running
docker-compose ps redis

# Check celery-exporter logs
docker-compose logs celery-exporter

# Verify REDIS_PASSWORD environment variable
docker-compose config | grep REDIS_PASSWORD
```

---

## Best Practices

### For Development

- ✅ Use **Flower** for debugging individual tasks
- ✅ Use **Grafana** for performance trends
- ✅ Set refresh to 10s in Grafana for near real-time
- ✅ Check Flower when tasks fail to see exceptions

### For Production

- ✅ Enable Grafana alerting (Slack/PagerDuty)
- ✅ Set up retention policies for Prometheus (default: 15 days)
- ✅ Use HTTPS for Grafana (configure reverse proxy)
- ✅ Restrict Flower access (add authentication)
- ✅ Monitor queue length alerts (prevent backlog)

---

## Recommended Monitoring Workflow

### When Starting Template Generation Job

1. **Before:** Check Flower → Workers tab
   - Verify workers are online
   - Check current load

2. **During:** Monitor in real-time
   - **Flower:** Tasks tab to see task progress
   - **Grafana:** Watch "Active Tasks" panel

3. **After:** Analyze results
   - **Flower:** Check failed tasks for errors
   - **Grafana:** Review execution time trends

### Daily Health Check

1. Open **Grafana** → Celery Dashboard
2. Check:
   - ✅ Active Workers = Expected count
   - ✅ Success Rate > 95%
   - ✅ Queue Length < 100
   - ✅ No workers offline in status table

---

## Stopping Monitoring Services

```bash
# Stop Flower only
docker-compose stop flower

# Stop Grafana stack only
docker-compose stop grafana prometheus loki promtail celery-exporter postgres-exporter redis-exporter

# Stop everything
docker-compose down
```

---

## Advanced: Custom Grafana Dashboards

### Import Community Dashboards

1. Go to http://localhost:3000
2. Navigate to **Dashboards** → **New** → **Import**
3. Enter dashboard ID:
   - **PostgreSQL:** 9628
   - **Redis:** 11835
   - **FastAPI:** 16123
4. Select "prometheus" as data source
5. Click **Import**

### Create Custom Panel

1. Open dashboard → **Add** → **Visualization**
2. Select data source: **prometheus**
3. Enter PromQL query (e.g., `rate(celery_task_received_total[5m])`)
4. Configure visualization type (Graph, Stat, Table)
5. Click **Apply**

---

## Summary: Which Tool When?

| Task | Use Flower | Use Grafana |
|------|-----------|-------------|
| Debug specific task failure | ✅ | ❌ |
| View task exception traceback | ✅ | ❌ |
| Check worker is online | ✅ | ✅ |
| Analyze performance trends | ❌ | ✅ |
| Set up alerts | ❌ | ✅ |
| View historical metrics | ❌ | ✅ |
| Monitor database/Redis | ❌ | ✅ |
| Real-time task stream | ✅ | ❌ |
| Executive dashboard | ❌ | ✅ |

**Answer to "Which is better?"**
- Neither! Use **both together** for complete monitoring coverage.
- **Flower** = Celery-specific, detailed task debugging
- **Grafana** = Comprehensive, metrics-driven, production monitoring
