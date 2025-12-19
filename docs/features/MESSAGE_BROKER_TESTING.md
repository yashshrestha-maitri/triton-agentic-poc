# Message Broker Testing Guide

Complete testing guide for the Redis Pub/Sub event system that eliminates HTTP polling.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EVENT FLOW                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Celery Worker               Redis Pub/Sub           Mare-API      │
│  (triton-agentic)                                                   │
│                                                                     │
│  ┌──────────┐               ┌──────────┐           ┌──────────┐   │
│  │  Job     │               │          │           │ Event    │   │
│  │  Starts  │──publish─────►│  Channel │──────────►│ Subscriber│  │
│  └──────────┘               │  triton: │           └──────────┘   │
│                             │  jobs:all│                 │         │
│  ┌──────────┐               │          │                 ▼         │
│  │  Job     │──publish─────►│          │           ┌──────────┐   │
│  │Completes │               └──────────┘           │ Cache in │   │
│  └──────────┘                                      │  Redis   │   │
│                                                     └──────────┘   │
│                                                           │         │
│                                                           ▼         │
│  ┌──────────┐                                      ┌──────────┐   │
│  │  Client  │◄─────────────instant response────────│  GET     │   │
│  │  Request │                (no polling!)         │ /jobs/id │   │
│  └──────────┘                                      └──────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Ensure Services are Running

```bash
# Check all services
docker ps

# Expected services:
# - triton-api (port 8000)
# - triton-worker
# - triton-redis (port 6379)
# - mare-api (port 16000)
# - postgres (mare-api database)
# - redis (mare-api cache)

# If not running, start triton-agentic
cd /home/yashrajshres/triton-agentic
docker-compose up -d

# Start mare-api
cd /home/yashrajshres/mare-api
docker-compose up -d
```

### 2. Verify Redis Connectivity

```bash
# Test triton-redis
docker exec -it triton-redis redis-cli ping
# Expected: PONG

# Test mare-api redis
docker exec -it redis redis-cli ping
# Expected: PONG
```

---

## Test 1: Monitor Redis Events (Real-Time)

This test shows events being published as they happen.

### Terminal 1: Subscribe to Events

```bash
# Subscribe to all job events in triton-redis
docker exec -it triton-redis redis-cli

# In redis-cli:
SUBSCRIBE triton:jobs:all

# You should see:
# Reading messages... (press Ctrl-C to quit)
# 1) "subscribe"
# 2) "triton:jobs:all"
# 3) (integer) 1
```

### Terminal 2: Trigger Template Generation

```bash
# Get a client ID first
curl http://localhost:8000/clients/ | jq '.clients[0].id'

# Or create new client
CLIENT_RESPONSE=$(curl -s -X POST http://localhost:8000/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Client - Message Broker",
    "industry": "Healthcare"
  }')

CLIENT_ID=$(echo $CLIENT_RESPONSE | jq -r '.id')
echo "Client ID: $CLIENT_ID"

# Create value proposition
VP_RESPONSE=$(curl -s -X POST "http://localhost:8000/clients/$CLIENT_ID/value-propositions" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "We reduce hospital readmissions by 30% through AI-powered care coordination",
    "is_active": true
  }')

VP_ID=$(echo $VP_RESPONSE | jq -r '.id')
echo "Value Prop ID: $VP_ID"

# Submit generation job via mare-api
JOB_RESPONSE=$(curl -s -X POST "http://localhost:16000/v1/triton/clients/$CLIENT_ID/generate-templates" \
  -H "Content-Type: application/json")

JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"
```

### Expected Output in Terminal 1

You should see events appear in real-time:

```
# Event 1: Job Started
1) "message"
2) "triton:jobs:all"
3) {"event_type":"job:started","timestamp":"2024-12-01T10:00:00.000Z","job_id":"abc-123-...","client_id":"xyz-456-...","status":"running","started_at":"2024-12-01T10:00:00.000Z"}

# Event 2: Job Completed (2-5 minutes later)
1) "message"
2) "triton:jobs:all"
3) {"event_type":"job:completed","timestamp":"2024-12-01T10:03:30.000Z","job_id":"abc-123-...","client_id":"xyz-456-...","status":"completed","template_ids":["t1","t2","t3","t4","t5","t6","t7"],"template_count":7,"generation_duration_ms":210000,"completed_at":"2024-12-01T10:03:30.000Z"}
```

✅ **PASS**: You see job:started and job:completed events

---

## Test 2: Verify Event Caching

This test verifies that completed jobs are cached in Redis for instant retrieval.

```bash
# Wait for job to complete (check Terminal 1 for job:completed event)

# Check if result was cached in mare-api Redis
docker exec -it redis redis-cli

# In redis-cli:
KEYS triton:job:result:*

# Expected output:
# 1) "triton:job:result:abc-123-uuid"

# Get cached value
GET triton:job:result:YOUR_JOB_ID

# Should return JSON with job status
```

✅ **PASS**: Cached result found in Redis

---

## Test 3: Cache-First Lookup (No HTTP Request)

This test verifies that mare-api checks cache before making HTTP requests.

### Enable Debug Logging

```bash
# In triton-api logs
docker logs triton-api -f | grep "Cache"

# In mare-api logs
docker logs mare-api -f | grep -E "cache|Cache"
```

### Test Cache Hit

```bash
# Get job status (should use cache)
curl -s "http://localhost:16000/v1/triton/jobs/$JOB_ID" | jq '.'

# Expected in logs:
# mare-api: "Cache hit for job abc-123-uuid"

# Response is INSTANT (< 50ms) because no HTTP request to triton-api
time curl -s "http://localhost:16000/v1/triton/jobs/$JOB_ID" > /dev/null

# Expected: real 0m0.030s (very fast!)
```

✅ **PASS**: Response < 100ms, logs show cache hit

---

## Test 4: Server-Sent Events (SSE) - Real-Time Updates

This test uses SSE to receive push notifications instead of polling.

### Test with curl (Terminal 1)

```bash
# Subscribe to job events via SSE
curl -N "http://localhost:16000/v1/triton/jobs/$JOB_ID/subscribe"

# Connection stays open, events streamed as they happen:
# data: {"event_type":"job:started","timestamp":"...","job_id":"...","status":"running"}

# (2-5 minutes later)
# data: {"event_type":"job:completed","timestamp":"...","job_id":"...","status":"completed","template_ids":[...],"template_count":7}

# : Connection closing - job completed
# (connection closes automatically)
```

### Test with JavaScript (Browser/Node.js)

```javascript
// Save this as test-sse.html and open in browser
const jobId = 'YOUR_JOB_ID';
const eventSource = new EventSource(`http://localhost:16000/v1/triton/jobs/${jobId}/subscribe`);

eventSource.onopen = () => {
    console.log('✅ SSE connection opened');
};

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Event received:', data);

    if (data.status === 'running') {
        console.log('⏳ Job is running...');
    }

    if (data.status === 'completed') {
        console.log(`✅ Job completed! Generated ${data.template_count} templates`);
        console.log('Template IDs:', data.template_ids);
        eventSource.close();
    }

    if (data.status === 'failed') {
        console.error('❌ Job failed:', data.error_message);
        eventSource.close();
    }
};

eventSource.onerror = (error) => {
    console.error('❌ SSE error:', error);
    eventSource.close();
};
```

✅ **PASS**: Events received in real-time, connection closes after completion

---

## Test 5: Performance Comparison (Before vs After)

### BEFORE (HTTP Polling)

```bash
# Simulate old polling behavior
JOB_ID="YOUR_JOB_ID"

echo "Polling every 2 seconds..."
COUNTER=0
START_TIME=$(date +%s)

while true; do
    RESPONSE=$(curl -s "http://localhost:8000/jobs/$JOB_ID")
    STATUS=$(echo $RESPONSE | jq -r '.status')
    COUNTER=$((COUNTER + 1))

    echo "[$COUNTER] Status: $STATUS"

    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
        break
    fi

    sleep 2
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HTTP_REQUESTS=$COUNTER

echo ""
echo "📊 HTTP Polling Stats:"
echo "   Total HTTP requests: $HTTP_REQUESTS"
echo "   Duration: ${DURATION}s"
echo "   Avg requests/minute: $((HTTP_REQUESTS * 60 / DURATION))"
```

### AFTER (Message Broker)

```bash
# Using SSE (no polling)
JOB_ID="YOUR_JOB_ID"
START_TIME=$(date +%s)

curl -N "http://localhost:16000/v1/triton/jobs/$JOB_ID/subscribe" 2>&1 | \
while read line; do
    if [[ $line == data:* ]]; then
        DATA=$(echo $line | sed 's/^data: //')
        STATUS=$(echo $DATA | jq -r '.status')

        if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
            break
        fi
    fi
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "📊 Message Broker Stats:"
echo "   Total HTTP requests: 1 (SSE connection)"
echo "   Duration: ${DURATION}s"
echo "   Events: Push-based (0 polling overhead)"
```

### Expected Results

```
HTTP Polling:
   Total HTTP requests: 90-150
   Duration: 180-300s
   Avg requests/minute: 30

Message Broker (SSE):
   Total HTTP requests: 1
   Duration: 180-300s
   Events: Push-based (0 polling overhead)

📈 IMPROVEMENT: 99% reduction in HTTP requests!
```

✅ **PASS**: < 5 HTTP requests vs 90+ with polling

---

## Test 6: Multiple Subscribers

Test that multiple clients can subscribe to the same job.

### Terminal 1: SSE Client 1

```bash
curl -N "http://localhost:16000/v1/triton/jobs/$JOB_ID/subscribe"
```

### Terminal 2: SSE Client 2

```bash
curl -N "http://localhost:16000/v1/triton/jobs/$JOB_ID/subscribe"
```

### Terminal 3: Cache Lookup

```bash
curl -s "http://localhost:16000/v1/triton/jobs/$JOB_ID" | jq '.status'
```

**Expected**: All three receive updates simultaneously

✅ **PASS**: All clients get real-time updates

---

## Test 7: Error Handling

### Test Job Failure Event

```bash
# Trigger a job that will fail (invalid client ID)
curl -X POST "http://localhost:16000/v1/triton/clients/00000000-0000-0000-0000-000000000000/generate-templates"

# Subscribe to events
docker exec -it triton-redis redis-cli SUBSCRIBE triton:jobs:all

# Expected: job:failed event published
```

✅ **PASS**: job:failed event published and cached

---

## Troubleshooting

### Issue: No events received

**Check 1: Is subscriber running?**
```bash
docker logs mare-api | grep "subscriber"

# Expected: "Triton event subscriber started successfully"
```

**Check 2: Is publisher connected?**
```bash
docker logs triton-worker | grep "Event publisher"

# Expected: "Event publisher connected to Redis"
```

**Check 3: Redis connectivity**
```bash
# From triton-worker
docker exec -it triton-worker redis-cli -h redis ping

# From mare-api
docker exec -it mare-api redis-cli -h redis ping
```

### Issue: Cache misses

**Check cache TTL:**
```bash
docker exec -it redis redis-cli

TTL triton:job:result:YOUR_JOB_ID

# Expected: positive number (seconds remaining)
# If -2: Key doesn't exist
# If -1: Key has no expiry
```

### Issue: SSE connection drops

**Check logs:**
```bash
docker logs mare-api | grep "SSE"

# Look for connection errors
```

**Increase timeout:**
```bash
# Add to mare-api .env
REQUEST_TIMEOUT=600  # 10 minutes
```

---

## Success Criteria

✅ **All tests passing:**

1. ✅ Events visible in Redis Pub/Sub
2. ✅ Job results cached in Redis
3. ✅ Cache-first lookup (< 100ms response)
4. ✅ SSE real-time updates working
5. ✅ 99% reduction in HTTP requests
6. ✅ Multiple subscribers work
7. ✅ Error events handled correctly

---

## Next Steps

### Production Deployment

1. **Enable Redis persistence:**
   ```yaml
   # docker-compose.yml
   redis:
     command: redis-server --appendonly yes --save 60 1000
   ```

2. **Monitor event lag:**
   ```bash
   # Add Prometheus metrics
   triton_event_publish_duration_seconds
   triton_event_subscriber_lag_seconds
   ```

3. **Scale subscribers:**
   - Run multiple mare-api instances
   - All subscribe to same Redis channels
   - Load balancer distributes SSE connections

4. **Add event replay:**
   ```python
   # Store last N events for late subscribers
   redis.lpush("triton:events:history", event_json)
   redis.ltrim("triton:events:history", 0, 100)
   ```

### Monitoring

**Grafana Dashboard Metrics:**
- Event publish rate (events/minute)
- Cache hit rate (%)
- SSE connection count
- Average event delivery time (ms)

**Alert Thresholds:**
- Cache hit rate < 80% → Investigate TTL
- Event delivery > 5s → Redis lag
- SSE connections > 1000 → Scale subscribers

---

## Summary

**Before (HTTP Polling):**
- 30 requests/minute per client
- 2-second delays
- High API load
- Database queries every poll

**After (Message Broker):**
- 1 request total (SSE connection)
- Instant updates (< 100ms)
- Minimal API load
- Cache-first lookups

**Result: 99% reduction in HTTP overhead! 🎉**
