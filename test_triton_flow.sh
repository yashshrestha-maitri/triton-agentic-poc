#!/bin/bash

# Test script for Mare-API → Triton-API workflow
# Uses Python for JSON parsing (no jq required)

BASE_URL="http://localhost:16000/v1/triton"
LOG_FILE="test_triton_flow.log"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function to extract JSON field using Python
json_extract() {
    python3 -c "import sys, json; print(json.load(sys.stdin)$1)" 2>/dev/null
}

# Helper function to pretty print JSON
json_pretty() {
    python3 -m json.tool 2>/dev/null || cat
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Mare-API → Triton Workflow Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Start logging
echo "Test started at $(date)" > "$LOG_FILE"

# =============================================================================
# Step 1: Create Client
# =============================================================================
echo -e "${YELLOW}=== Step 1: Create Client ===${NC}"
CLIENT_RESPONSE=$(curl -s -X POST ${BASE_URL}/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HealthCare Analytics Inc",
    "industry": "Healthcare",
    "meta_data": {
      "region": "North America",
      "test_client": true,
      "test_run": true
    }
  }' 2>&1)

echo "$CLIENT_RESPONSE" >> "$LOG_FILE"
echo "$CLIENT_RESPONSE" | json_pretty

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to create client${NC}"
    echo "Response: $CLIENT_RESPONSE"
    exit 1
fi

CLIENT_ID=$(echo "$CLIENT_RESPONSE" | json_extract "['id']")

if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" == "None" ]; then
    echo -e "${RED}✗ Failed to extract client ID${NC}"
    echo "Response: $CLIENT_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Client created successfully${NC}"
echo -e "Client ID: ${GREEN}$CLIENT_ID${NC}"
echo ""

# =============================================================================
# Step 2: Create Value Proposition
# =============================================================================
echo -e "${YELLOW}=== Step 2: Create Value Proposition ===${NC}"
VP_RESPONSE=$(curl -s -X POST ${BASE_URL}/clients/${CLIENT_ID}/value-propositions \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Transform complex healthcare data into intuitive, actionable dashboards that empower clinical teams to make faster, data-driven decisions. Our AI-powered analytics platform reduces reporting time by 70% while improving patient outcome visibility across all care units, emergency departments, and surgical centers.",
    "is_active": true,
    "meta_data": {
      "target_users": ["Clinicians", "Administrators", "C-Suite Executives"],
      "key_metrics": ["Patient Flow", "Resource Utilization", "Quality Metrics", "Financial Performance"],
      "use_cases": ["Real-time Monitoring", "Predictive Analytics", "Operational Efficiency"]
    }
  }' 2>&1)

echo "$VP_RESPONSE" >> "$LOG_FILE"
echo "$VP_RESPONSE" | json_pretty

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to create value proposition${NC}"
    exit 1
fi

VP_ID=$(echo "$VP_RESPONSE" | json_extract "['id']")

if [ -z "$VP_ID" ] || [ "$VP_ID" == "None" ]; then
    echo -e "${RED}✗ Failed to extract value proposition ID${NC}"
    echo "Response: $VP_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Value proposition created successfully${NC}"
echo -e "Value Proposition ID: ${GREEN}$VP_ID${NC}"
echo ""

# =============================================================================
# Step 3: Generate Templates (Submit Job)
# =============================================================================
echo -e "${YELLOW}=== Step 3: Submit Template Generation Job ===${NC}"
JOB_RESPONSE=$(curl -s -X POST ${BASE_URL}/clients/${CLIENT_ID}/generate-templates \
  -H "Content-Type: application/json" 2>&1)

echo "$JOB_RESPONSE" >> "$LOG_FILE"
echo "$JOB_RESPONSE" | json_pretty

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to submit generation job${NC}"
    exit 1
fi

JOB_ID=$(echo "$JOB_RESPONSE" | json_extract "['id']")

if [ -z "$JOB_ID" ] || [ "$JOB_ID" == "None" ]; then
    echo -e "${RED}✗ Failed to extract job ID${NC}"
    echo "Response: $JOB_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Template generation job submitted${NC}"
echo -e "Job ID: ${GREEN}$JOB_ID${NC}"
echo ""

# =============================================================================
# Step 4: Poll Job Status
# =============================================================================
echo -e "${YELLOW}=== Step 4: Poll Job Status ===${NC}"
STATUS="pending"
ATTEMPT=0
MAX_ATTEMPTS=60  # 5 minutes with 5-second intervals

while [[ "$STATUS" != "completed" && "$STATUS" != "failed" && "$STATUS" != "error" && $ATTEMPT -lt $MAX_ATTEMPTS ]]; do
    sleep 5
    ATTEMPT=$((ATTEMPT + 1))

    JOB_STATUS=$(curl -s ${BASE_URL}/jobs/${JOB_ID} 2>&1)
    echo "$JOB_STATUS" >> "$LOG_FILE"

    STATUS=$(echo "$JOB_STATUS" | json_extract "['status']")
    PROGRESS=$(echo "$JOB_STATUS" | json_extract "['progress']" 2>/dev/null || echo "0")

    if [ -z "$STATUS" ] || [ "$STATUS" == "None" ]; then
        echo -e "${RED}✗ Failed to get job status${NC}"
        echo "Response: $JOB_STATUS"
        break
    fi

    echo -e "Attempt $ATTEMPT: Status = ${BLUE}$STATUS${NC}, Progress = ${BLUE}${PROGRESS}%${NC}"

    if [[ "$STATUS" == "processing" ]]; then
        echo "  → Template generation in progress..."
    fi
done

echo ""
echo "$JOB_STATUS" | json_pretty
echo ""

if [[ "$STATUS" == "completed" ]]; then
    echo -e "${GREEN}✓ Template generation completed successfully${NC}"

    TEMPLATE_COUNT=$(echo "$JOB_STATUS" | json_extract "['result']['total_templates']" 2>/dev/null)
    if [ ! -z "$TEMPLATE_COUNT" ] && [ "$TEMPLATE_COUNT" != "None" ]; then
        echo -e "  Generated ${GREEN}$TEMPLATE_COUNT${NC} templates"
    fi
    echo ""

    # =============================================================================
    # Step 5: Retrieve Generated Templates
    # =============================================================================
    echo -e "${YELLOW}=== Step 5: Retrieve Generated Templates ===${NC}"
    TEMPLATES_RESPONSE=$(curl -s "${BASE_URL}/templates?client_id=${CLIENT_ID}" 2>&1)

    echo "$TEMPLATES_RESPONSE" >> "$LOG_FILE"
    echo "$TEMPLATES_RESPONSE" | json_pretty

    TOTAL=$(echo "$TEMPLATES_RESPONSE" | json_extract "['total']" 2>/dev/null)
    if [ ! -z "$TOTAL" ] && [ "$TOTAL" != "None" ]; then
        echo ""
        echo -e "${GREEN}✓ Successfully retrieved $TOTAL templates${NC}"
    fi

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Results:"
    echo "  • Client ID: $CLIENT_ID"
    echo "  • Value Proposition ID: $VP_ID"
    echo "  • Job ID: $JOB_ID"
    echo "  • Templates Generated: $TOTAL"
    echo ""
    echo "Full log saved to: $LOG_FILE"

elif [[ "$STATUS" == "failed" || "$STATUS" == "error" ]]; then
    echo -e "${RED}✗ Template generation failed${NC}"
    ERROR_MSG=$(echo "$JOB_STATUS" | json_extract "['error_message']" 2>/dev/null)
    if [ -z "$ERROR_MSG" ] || [ "$ERROR_MSG" == "None" ]; then
        ERROR_MSG="Unknown error"
    fi
    echo -e "Error: ${RED}$ERROR_MSG${NC}"
    echo ""
    echo "Full log saved to: $LOG_FILE"
    exit 1

else
    echo -e "${YELLOW}⚠ Job status check timed out after $MAX_ATTEMPTS attempts${NC}"
    echo -e "Last known status: ${YELLOW}$STATUS${NC}"
    echo ""
    echo "The job may still be processing. Check manually with:"
    echo "  curl ${BASE_URL}/jobs/${JOB_ID}"
    echo ""
    echo "Full log saved to: $LOG_FILE"
    exit 1
fi
