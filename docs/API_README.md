# Triton Template Generation API

REST API for generating and managing dashboard templates using AI agents.

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (copy from .env.example):
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the API

Start the development server:
```bash
# Option 1: Using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python app.py
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Health Check

#### `GET /`
Root endpoint - API health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-24T12:00:00Z",
  "version": "1.0.0"
}
```

#### `GET /health`
Health check endpoint for monitoring systems.

---

### Template Endpoints

#### `POST /templates/generate`
Generate new dashboard templates based on client value proposition.

**Request Body:**
```json
{
  "client_name": "Livongo Health",
  "industry": "Diabetes Management",
  "target_audiences": ["Health Plan", "Broker", "Medical Management"],
  "value_proposition": {
    "executive_value_proposition": {
      "core_value_statement": "AI-powered diabetes management platform",
      "primary_impact_areas": ["Clinical Outcomes", "Cost Reduction"]
    }
  },
  "max_templates": 10
}
```

**Response:** `TemplateGenerationResult` with all generated templates

**Status Codes:**
- `201` - Templates generated successfully
- `422` - Validation error
- `500` - Generation failed

---

#### `GET /templates/`
List all generated templates (with pagination and filtering).

**Query Parameters:**
- `limit` (int, default=100): Maximum number of templates to return
- `skip` (int, default=0): Number of templates to skip
- `category` (string, optional): Filter by category
- `audience` (string, optional): Filter by target audience

**Example:**
```bash
GET /templates/?limit=50&category=roi-focused&audience=Health%20Plan
```

**Response:**
```json
{
  "total": 150,
  "templates": [
    {
      "id": "uuid-123",
      "name": "ROI Executive Dashboard",
      "description": "C-suite focused financial impact dashboard",
      "category": "roi-focused",
      "targetAudience": "Health Plan",
      "widget_count": 8,
      "source_file": "templates_Livongo_Health_20250124_120000.json"
    }
  ]
}
```

---

#### `GET /templates/{template_id}`
Get a specific template by ID.

**Path Parameters:**
- `template_id` (string): Unique template identifier

**Response:** Complete `DashboardTemplate` object

**Status Codes:**
- `200` - Success
- `404` - Template not found

---

#### `DELETE /templates/{template_id}`
Delete a specific template.

**Path Parameters:**
- `template_id` (string): Unique template identifier

**Response:**
```json
{
  "message": "Template 'uuid-123' deleted successfully",
  "data": {
    "template_id": "uuid-123"
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - Template not found

---

#### `GET /templates/categories/list`
Get list of all available template categories.

**Response:**
```json
[
  "roi-focused",
  "clinical-outcomes",
  "operational-efficiency",
  "competitive-positioning",
  "comprehensive"
]
```

---

#### `GET /templates/audiences/list`
Get list of all target audiences found in generated templates.

**Response:**
```json
[
  "Broker",
  "Health Plan",
  "Medical Management",
  "PBM",
  "TPA"
]
```

---

### Result Endpoints

#### `GET /results/`
List all template generation results.

**Query Parameters:**
- `limit` (int, default=100): Maximum number of results to return
- `skip` (int, default=0): Number of results to skip

**Response:**
```json
[
  {
    "filename": "templates_Livongo_Health_20250124_120000.json",
    "client_name": "Livongo Health",
    "industry": "Diabetes Management",
    "generated_at": "2025-01-24T12:00:00Z",
    "total_templates": 7,
    "validation_passed": true,
    "generation_time_seconds": 45.2,
    "file_size_bytes": 125840
  }
]
```

---

#### `GET /results/{filename}`
Get a specific generation result by filename.

**Path Parameters:**
- `filename` (string): Result file name

**Response:** Complete `TemplateGenerationResult` object

---

#### `GET /results/{filename}/download`
Download a generation result file.

**Path Parameters:**
- `filename` (string): Result file name

**Response:** JSON file download

---

#### `DELETE /results/{filename}`
Delete a generation result file.

**Path Parameters:**
- `filename` (string): Result file name

**Response:**
```json
{
  "message": "Result file 'templates_Livongo_Health_20250124_120000.json' deleted successfully",
  "data": {
    "filename": "templates_Livongo_Health_20250124_120000.json"
  }
}
```

---

#### `GET /results/stats/summary`
Get overall statistics about template generation results.

**Response:**
```json
{
  "total_result_files": 15,
  "total_templates": 105,
  "total_storage_bytes": 2048576,
  "clients": ["Livongo Health", "Another Client"],
  "industries": ["Diabetes Management", "Healthcare"],
  "categories": {
    "roi-focused": 25,
    "clinical-outcomes": 20,
    "operational-efficiency": 15,
    "competitive-positioning": 20,
    "comprehensive": 25
  },
  "audiences": {
    "Health Plan": 30,
    "Broker": 25,
    "Medical Management": 25,
    "PBM": 15,
    "TPA": 10
  },
  "avg_generation_time_seconds": 42.5
}
```

---

## Usage Examples

### Using cURL

**Generate templates:**
```bash
curl -X POST "http://localhost:8000/templates/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Livongo Health",
    "industry": "Diabetes Management",
    "target_audiences": ["Health Plan", "Broker"],
    "value_proposition": {
      "executive_value_proposition": {
        "core_value_statement": "AI-powered diabetes management"
      }
    },
    "max_templates": 7
  }'
```

**List templates:**
```bash
curl "http://localhost:8000/templates/?limit=10&category=roi-focused"
```

**Get a specific template:**
```bash
curl "http://localhost:8000/templates/uuid-123"
```

**Get statistics:**
```bash
curl "http://localhost:8000/results/stats/summary"
```

### Using Python

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000"

# Generate templates
response = requests.post(
    f"{BASE_URL}/templates/generate",
    json={
        "client_name": "Livongo Health",
        "industry": "Diabetes Management",
        "target_audiences": ["Health Plan", "Broker"],
        "value_proposition": {
            "executive_value_proposition": {
                "core_value_statement": "AI-powered diabetes management"
            }
        },
        "max_templates": 7
    }
)

if response.status_code == 201:
    result = response.json()
    print(f"Generated {len(result['templates'])} templates")
    print(f"Generation time: {result['metadata']['generation_time_seconds']}s")

# List templates
response = requests.get(
    f"{BASE_URL}/templates/",
    params={"limit": 50, "category": "roi-focused"}
)

templates = response.json()
print(f"Found {templates['total']} templates")

# Get statistics
response = requests.get(f"{BASE_URL}/results/stats/summary")
stats = response.json()
print(f"Total templates: {stats['total_templates']}")
print(f"Categories: {stats['categories']}")
```

### Using JavaScript/Fetch

```javascript
// Generate templates
const response = await fetch('http://localhost:8000/templates/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    client_name: 'Livongo Health',
    industry: 'Diabetes Management',
    target_audiences: ['Health Plan', 'Broker'],
    value_proposition: {
      executive_value_proposition: {
        core_value_statement: 'AI-powered diabetes management'
      }
    },
    max_templates: 7
  })
});

const result = await response.json();
console.log(`Generated ${result.templates.length} templates`);

// List templates
const listResponse = await fetch('http://localhost:8000/templates/?limit=50');
const templates = await listResponse.json();
console.log(`Found ${templates.total} templates`);
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Error Type",
  "detail": "Detailed error message or validation errors",
  "status_code": 400
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Resource created
- `404` - Resource not found
- `422` - Validation error
- `500` - Internal server error

## Production Deployment

### Environment Variables

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key (optional)
- `GOOGLE_API_KEY` - Google API key (optional)
- `GROQ_API_KEY` - Groq API key (optional)

### Security Considerations

For production deployment:

1. **Enable authentication**: Add API key or OAuth2 authentication
2. **Configure CORS**: Update `allow_origins` in `app.py` to specific domains
3. **Add rate limiting**: Use middleware like `slowapi`
4. **Enable HTTPS**: Use reverse proxy (nginx, traefik)
5. **Set up monitoring**: Add logging and error tracking (Sentry, DataDog)
6. **Use a production ASGI server**: Deploy with gunicorn + uvicorn workers

**Example production deployment:**
```bash
gunicorn app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## Testing

Test the API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Interactive documentation
open http://localhost:8000/docs
```

## Support

For issues or questions:
- Check the interactive API documentation at `/docs`
- Review the main project README.md
- File an issue in the project repository
