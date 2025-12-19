#!/bin/bash

# ============================================================================
# Data Lineage Setup Script (Docker Version)
# ============================================================================
# Purpose: Sets up extraction lineage tracking system using Docker PostgreSQL
# Usage: ./scripts/setup_lineage_docker.sh
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="triton-postgres"
DATABASE_NAME="${POSTGRES_DB:-triton_db}"
POSTGRES_USER="${POSTGRES_USER:-triton}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-triton_password}"
MIGRATIONS_DIR="$(dirname "$0")/../database/migrations"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Data Lineage Setup Script (Docker)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Container:${NC} $CONTAINER_NAME"
echo -e "${GREEN}Database:${NC} $DATABASE_NAME"
echo -e "${GREEN}User:${NC} $POSTGRES_USER"
echo -e "${GREEN}Migrations:${NC} $MIGRATIONS_DIR"
echo ""

# Check if Docker is running
echo -e "${YELLOW}[1/6] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Check if PostgreSQL container exists
echo -e "${YELLOW}[2/6] Checking PostgreSQL container...${NC}"
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}PostgreSQL container not found. Starting services...${NC}"
    docker-compose up -d postgres
    echo "Waiting for PostgreSQL to be healthy (30 seconds)..."
    sleep 30
fi

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}PostgreSQL container exists but not running. Starting...${NC}"
    docker-compose start postgres
    echo "Waiting for PostgreSQL to be ready (10 seconds)..."
    sleep 10
fi
echo -e "${GREEN}✓ PostgreSQL container is running${NC}"
echo ""

# Test connection
echo -e "${YELLOW}[3/6] Testing PostgreSQL connection...${NC}"
if ! docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DATABASE_NAME" -c '\q' 2>/dev/null; then
    echo -e "${RED}ERROR: Cannot connect to PostgreSQL${NC}"
    echo "Container logs:"
    docker logs "$CONTAINER_NAME" --tail 20
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
echo ""

# Check if migrations directory exists
echo -e "${YELLOW}[4/6] Checking migrations directory...${NC}"
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo -e "${RED}ERROR: Migrations directory not found: $MIGRATIONS_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Migrations directory found${NC}"
echo ""

# Run schema migration
echo -e "${YELLOW}[5/6] Running schema migration (001_add_extraction_lineage.sql)...${NC}"
MIGRATION_FILE="$MIGRATIONS_DIR/001_add_extraction_lineage.sql"
if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}ERROR: Migration file not found: $MIGRATION_FILE${NC}"
    exit 1
fi

docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DATABASE_NAME" < "$MIGRATION_FILE"
echo -e "${GREEN}✓ Schema migration completed${NC}"
echo ""

# Load mock data
echo -e "${YELLOW}[6/6] Loading mock data (002_mock_lineage_data.sql)...${NC}"
MOCK_DATA_FILE="$MIGRATIONS_DIR/002_mock_lineage_data.sql"
if [ ! -f "$MOCK_DATA_FILE" ]; then
    echo -e "${RED}ERROR: Mock data file not found: $MOCK_DATA_FILE${NC}"
    exit 1
fi

docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DATABASE_NAME" < "$MOCK_DATA_FILE"
echo -e "${GREEN}✓ Mock data loaded${NC}"
echo ""

# Verification
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check extraction_lineage table
LINEAGE_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM extraction_lineage;" | tr -d ' ')
echo -e "${GREEN}Lineage records:${NC} $LINEAGE_COUNT (expected: 5)"

# Check roi_models table
ROI_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM roi_models;" | tr -d ' ')
echo -e "${GREEN}ROI models:${NC} $ROI_COUNT (expected: 2)"

# Check dashboard_templates table
DASHBOARD_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM dashboard_templates WHERE id IN ('99999999-9999-9999-9999-999999999999', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');" | tr -d ' ')
echo -e "${GREEN}Dashboards:${NC} $DASHBOARD_COUNT (expected: 3)"

# Check indexes
INDEX_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$DATABASE_NAME" -t -c "SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'extraction_lineage';" | tr -d ' ')
echo -e "${GREEN}Indexes:${NC} $INDEX_COUNT (expected: 7)"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo ""
echo "1. Query lineage data (using Docker):"
echo "   docker exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $DATABASE_NAME -c 'SELECT * FROM extraction_lineage;'"
echo ""
echo "2. Test impact analysis:"
echo "   docker exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $DATABASE_NAME -c \\"
echo "     \"SELECT * FROM find_affected_dashboards('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2');\""
echo ""
echo "3. Interactive PostgreSQL shell:"
echo "   docker exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $DATABASE_NAME"
echo ""
echo "4. View complete audit trail:"
echo "   See: docs/operations/DATA_LINEAGE_API_GUIDE.md"
echo ""
echo "5. Test with curl (once API is running):"
echo "   curl http://localhost:8000/lineage/33333333-3333-3333-3333-333333333333"
echo ""
echo -e "${YELLOW}Documentation: docs/operations/DATA_LINEAGE_API_GUIDE.md${NC}"
echo ""
