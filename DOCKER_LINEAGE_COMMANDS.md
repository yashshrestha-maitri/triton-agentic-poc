# Docker Lineage Commands - Quick Reference

**Quick setup for users without PostgreSQL installed locally**

---

## 🚀 One-Command Setup

```bash
# Run this to set up everything
./scripts/setup_lineage_docker.sh
```

This will:
1. Start PostgreSQL container if not running
2. Run schema migration
3. Load mock data
4. Verify setup

---

## 📊 Query Commands (Using Docker)

### Basic Queries

```bash
# Count lineage records
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT COUNT(*) FROM extraction_lineage;"

# View all lineage records
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT extraction_id, source_document_url, verification_status FROM extraction_lineage;"

# Find extractions from specific document
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM extraction_lineage WHERE source_document_hash = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2';"
```

### Impact Analysis

```bash
# Find all affected dashboards for a document
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM find_affected_dashboards('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2');"
```

### Agent Performance

```bash
# Analyze agent performance
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT extraction_agent, verification_status, COUNT(*), AVG(extraction_confidence_final)
      FROM extraction_lineage
      GROUP BY extraction_agent, verification_status;"
```

### Flagged Extractions

```bash
# Find extractions needing manual review
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM extraction_lineage WHERE verification_status = 'flagged';"
```

---

## 🔧 Interactive PostgreSQL Shell

```bash
# Enter interactive psql shell
docker exec -it triton-postgres psql -U triton -d triton_db

# Once inside, you can run any SQL:
# SELECT * FROM extraction_lineage;
# \dt                    -- List all tables
# \d extraction_lineage  -- Describe table
# \q                     -- Quit
```

---

## 🐳 Docker Management Commands

### Start/Stop PostgreSQL

```bash
# Start PostgreSQL only
docker-compose up -d postgres

# Stop PostgreSQL
docker-compose stop postgres

# Restart PostgreSQL
docker-compose restart postgres

# View PostgreSQL logs
docker logs triton-postgres -f
```

### Database Backup & Restore

```bash
# Backup database
docker exec triton-postgres pg_dump -U triton triton_db > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251217.sql | docker exec -i triton-postgres psql -U triton -d triton_db
```

### Reset Database (WARNING: Deletes all data!)

```bash
# Drop and recreate database
docker exec triton-postgres psql -U triton -c "DROP DATABASE IF EXISTS triton_db;"
docker exec triton-postgres psql -U triton -c "CREATE DATABASE triton_db;"

# Then re-run setup
./scripts/setup_lineage_docker.sh
```

---

## 🎯 Common Workflows

### Workflow 1: Fresh Setup

```bash
# 1. Start PostgreSQL
docker-compose up -d postgres

# 2. Wait for PostgreSQL to be ready (10 seconds)
sleep 10

# 3. Run lineage setup
./scripts/setup_lineage_docker.sh

# 4. Verify
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT COUNT(*) FROM extraction_lineage;"
# Should output: 5
```

### Workflow 2: Query Lineage Data

```bash
# Get specific extraction
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM extraction_lineage WHERE extraction_id = '33333333-3333-3333-3333-333333333333';"

# See what ROI models use this extraction
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT unnest(used_in_roi_models) FROM extraction_lineage WHERE extraction_id = '33333333-3333-3333-3333-333333333333';"
```

### Workflow 3: Complete Audit Trail

```bash
# Show complete chain: Document → Extraction → ROI → Dashboard
docker exec triton-postgres psql -U triton -d triton_db <<'EOF'
SELECT
    el.extraction_id,
    el.source_document_url,
    el.extraction_agent,
    el.verification_status,
    rm.name AS roi_model_name,
    dt.name AS dashboard_name,
    dt.target_audience
FROM extraction_lineage el
LEFT JOIN LATERAL unnest(el.used_in_roi_models) AS roi_id ON TRUE
LEFT JOIN roi_models rm ON rm.id = roi_id
LEFT JOIN LATERAL unnest(el.used_in_dashboards) AS dash_id ON TRUE
LEFT JOIN dashboard_templates dt ON dt.id = dash_id
WHERE el.extraction_id = '33333333-3333-3333-3333-333333333333';
EOF
```

---

## 🧪 Testing the Setup

### Test 1: Basic Connectivity

```bash
docker exec triton-postgres psql -U triton -d triton_db -c "SELECT version();"
```

**Expected Output:** PostgreSQL version information

### Test 2: Table Exists

```bash
docker exec triton-postgres psql -U triton -d triton_db -c "\dt extraction_lineage"
```

**Expected Output:** Table schema information

### Test 3: Mock Data Loaded

```bash
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT COUNT(*) FROM extraction_lineage;"
```

**Expected Output:** `5`

### Test 4: Functions Work

```bash
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM find_affected_dashboards('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2') LIMIT 1;"
```

**Expected Output:** Rows showing extraction_id, roi_model_id, dashboard_id

---

## 📝 Pro Tips

### 1. Use Aliases (Add to ~/.bashrc)

```bash
alias pgexec='docker exec triton-postgres psql -U triton -d triton_db'
alias pgshell='docker exec -it triton-postgres psql -U triton -d triton_db'
alias pglogs='docker logs triton-postgres -f'

# Then you can use:
pgexec -c "SELECT * FROM extraction_lineage;"
pgshell  # Interactive shell
```

### 2. Format Output Nicely

```bash
# Add -x for expanded display
docker exec triton-postgres psql -U triton -d triton_db -x \
  -c "SELECT * FROM extraction_lineage WHERE extraction_id = '33333333-3333-3333-3333-333333333333';"

# Add -A for unaligned output
docker exec triton-postgres psql -U triton -d triton_db -A -t \
  -c "SELECT COUNT(*) FROM extraction_lineage;"
```

### 3. Save Query Results

```bash
# Save to file
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT * FROM extraction_lineage;" > lineage_export.txt

# Save as CSV
docker exec triton-postgres psql -U triton -d triton_db \
  -c "COPY (SELECT * FROM extraction_lineage) TO STDOUT CSV HEADER;" > lineage.csv
```

---

## ⚠️ Troubleshooting

### Issue 1: "Container not found"

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait 10 seconds
sleep 10

# Retry setup
./scripts/setup_lineage_docker.sh
```

### Issue 2: "Connection refused"

```bash
# Check if container is running
docker ps | grep postgres

# Check logs
docker logs triton-postgres --tail 50

# Restart container
docker-compose restart postgres
```

### Issue 3: "Database does not exist"

```bash
# The container should auto-create triton_db
# If not, create manually:
docker exec triton-postgres psql -U triton -c "CREATE DATABASE triton_db;"

# Then run setup
./scripts/setup_lineage_docker.sh
```

### Issue 4: "Permission denied"

```bash
# Make scripts executable
chmod +x scripts/setup_lineage_docker.sh
```

---

## 📚 Related Documentation

- **Full Guide:** `docs/operations/DATA_LINEAGE_API_GUIDE.md`
- **Quick Reference:** `docs/DATA_LINEAGE_QUICK_REFERENCE.md`
- **Implementation Plan:** `docs/EXTRACTION_HALLUCINATION_AND_LINEAGE_PLAN.md`

---

## 🎉 You're All Set!

Your lineage tracking system is now ready. Start querying!

```bash
# Quick test
docker exec triton-postgres psql -U triton -d triton_db \
  -c "SELECT extraction_id, verification_status, array_length(used_in_dashboards, 1) AS dashboard_count FROM extraction_lineage;"
```
