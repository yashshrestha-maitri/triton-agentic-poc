# Complete API Endpoints List - Triton Agentic & Mare API

**Version:** 1.0.0
**Last Updated:** 2025-12-18
**Total Endpoints:** 122 (Triton: 48 | Mare: 74)

---

## Table of Contents

1. [Triton Agentic API (48 endpoints)](#triton-agentic-api-48-endpoints)
2. [Mare API (74 endpoints)](#mare-api-74-endpoints)

---

## Triton Agentic API (48 endpoints)

**Base URL:** `http://localhost:8000`

### 1. CLIENTS Module (7 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| POST | `/clients` | `create_client` | Create new client |
| GET | `/clients` | `list_clients` | List all clients (paginated) |
| GET | `/clients/{client_id}` | `get_client` | Get specific client |
| GET | `/clients/{client_id}/with-value-props` | `get_client_with_value_props` | Get client with value propositions |
| POST | `/clients/{client_id}/value-propositions` | `create_value_proposition` | Create value proposition |
| GET | `/clients/{client_id}/value-propositions` | `list_value_propositions` | List client value propositions |
| PATCH | `/clients/{client_id}/value-propositions/{vp_id}` | `update_value_proposition` | Update value proposition |

### 2. JOBS Module (4 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| POST | `/jobs` | `create_generation_job` | Create template generation job |
| GET | `/jobs` | `list_jobs` | List generation jobs |
| GET | `/jobs/{job_id}` | `get_job_status` | Get job status |
| DELETE | `/jobs/{job_id}` | `cancel_job` | Cancel job |

### 3. TEMPLATES Module (4 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/templates` | `list_templates` | List dashboard templates |
| GET | `/templates/{template_id}` | `get_template` | Get specific template |
| GET | `/templates/categories/list` | `list_categories` | List template categories |
| GET | `/templates/audiences/list` | `list_audiences` | List target audiences |

### 4. RESEARCH Module (6 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| POST | `/research/web-search` | `initiate_web_search` | Start web search research (async) |
| POST | `/research/document-analysis` | `initiate_document_analysis` | Start document analysis (async) |
| GET | `/research/{job_id}` | `get_research_job_status` | Get research job status |
| GET | `/research` | `list_research_jobs` | List research jobs |
| GET | `/research/stats/summary` | `get_research_stats` | Get research statistics |
| POST | `/research/validate` | `validate_research_result` | Validate research output |

### 5. ROI MODELS Module (6 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| POST | `/api/roi-models/generate` | `generate_roi_model` | Generate ROI model (async) |
| GET | `/api/roi-models/{job_id}/status` | `get_job_status` | Get ROI generation job status |
| GET | `/api/roi-models` | `list_jobs` | List ROI model jobs |
| DELETE | `/api/roi-models/{job_id}` | `delete_job` | Delete job record |
| GET | `/api/roi-models/results/files` | `list_saved_models` | List saved ROI model files |
| GET | `/api/roi-models/results/files/{filename}` | `get_saved_model` | Download ROI model file |

### 6. PROSPECT DATA Module (6 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| POST | `/prospect-data/generate` | `generate_dashboard_data` | Generate dashboard data (sync/batch) |
| POST | `/prospect-data/generate-async` | `generate_dashboard_data_async` | Generate data async (Celery) |
| GET | `/prospect-data/jobs/{job_id}` | `get_prospect_data_job_status` | Get generation job status |
| GET | `/prospect-data/{prospect_id}` | `get_prospect_dashboard_data` | Get all data for prospect |
| GET | `/prospect-data/{prospect_id}/{template_id}` | `get_specific_dashboard_data` | Get specific prospect-template data |
| DELETE | `/prospect-data/{prospect_id}/{template_id}` | `delete_dashboard_data` | Delete prospect data |

### 7. LINEAGE Module (9 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/lineage/{extraction_id}` | `get_lineage` | Get lineage for extraction |
| GET | `/lineage/document/{document_hash}` | `find_extractions_by_document` | Find extractions from document |
| GET | `/lineage/audit-trail/{extraction_id}` | `get_audit_trail` | Get complete audit trail |
| POST | `/lineage/impact-analysis` | `impact_analysis` | Analyze impact of changes |
| GET | `/lineage/flagged` | `get_flagged_extractions` | Get flagged extractions |
| PUT | `/lineage/{extraction_id}/verify` | `verify_extraction` | Mark extraction as verified |
| PUT | `/lineage/{extraction_id}/flag` | `flag_extraction` | Flag extraction for review |
| GET | `/lineage/stats/summary` | `get_lineage_stats` | Get lineage statistics |
| GET | `/lineage/health` | `health_check` | Lineage API health check |

### 8. SYSTEM Module (2 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/health` | `health_check` | API health check |
| GET | `/metrics` | `prometheus_metrics` | Prometheus metrics |

---

## Mare API (74 endpoints)

**Base URL:** `http://localhost:PORT` (configured in settings)

### 1. AUTH Module (9 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/auth/user` | `get_auth_user_info` | Get current user info |
| GET | `/auth/user/url` | `get_auth_user_url` | Get user auth URL |
| GET | `/auth/branding` | `get_branding_info_for_user` | Get branding for user |
| GET | `/auth/profile-branding` | `get_profile_and_branding_info_for_user` | Get profile + branding |
| GET | `/auth/branding/{url}` | `get_branding_info_for_url` | Get branding by URL |
| POST | `/auth/signin` | `signin_user` | Sign in user |
| POST | `/auth/signup` | `signup_user` | Sign up new user |
| POST | `/auth/password-reset` | `send_password_reset_email` | Request password reset |
| POST | `/auth/verify-otp` | `verify_otp_code` | Verify OTP code |

### 2. USERS Module (2 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/users` | `get_users` | List all users |
| PUT | `/users/{user_id}/active` | `update_user_active_status` | Update user active status |

### 3. CLIENTS Module (7 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/clients/all` | `get_all_clients` | Get all clients (admin) |
| GET | `/clients` | `list_clients` | List clients (filtered by access) |
| GET | `/clients/{client_id}` | `get_client_by_id` | Get specific client |
| POST | `/clients` | `create_client` | Create new client |
| PATCH | `/clients/{client_id}` | `update_client` | Update client |
| DELETE | `/clients/{client_id}` | `delete_client` | Delete client |
| GET | `/clients/{client_id}/filters` | `get_filter_user_and_prospect` | Get client filters |

### 4. CUSTOMER PROFILES Module (7 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/customer-profiles` | `get_customer_profiles` | List customer profiles |
| POST | `/customer-profiles` | `create_customer_profile` | Create customer profile |
| PATCH | `/customer-profiles/{id}` | `update_customer_profile` | Update customer profile |
| DELETE | `/customer-profiles/{id}` | `delete_customer_profile` | Delete customer profile |
| POST | `/customer-profiles/validate/name` | `validate_customer_profile_name` | Validate profile name |
| POST | `/customer-profiles/validate/url` | `validate_customer_profile_url` | Validate profile URL |
| POST | `/customer-profiles/upload-url` | `generate_presigned_upload_url_for_customer_logos` | Generate logo upload URL |

### 5. PROSPECTS Module (13 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/prospects` | `get_user_prospects` | List user's prospects |
| GET | `/prospects/{prospect_id}` | `get_prospect_details` | Get prospect details |
| POST | `/prospects` | `create_prospect` | Create new prospect |
| PATCH | `/prospects/{prospect_id}` | `update_prospect` | Update prospect |
| DELETE | `/prospects/{prospect_id}` | `delete_prospect` | Delete prospect |
| POST | `/prospects/validate/name` | `validate_prospect_name` | Validate unique prospect name |
| POST | `/prospects/{prospect_id}/process` | `start_prospect_processing` | Start ETL processing |
| GET | `/prospects/{prospect_id}/progress` | `get_prospect_progress` | Get processing progress |
| GET | `/prospects/{prospect_id}/report` | `get_prospect_report_data` | Get report data |
| PATCH | `/prospects/{prospect_id}/status` | `update_prospect_status` | Update prospect status |
| GET | `/prospects/{prospect_id}/members` | `get_prospect_members` | Get prospect members |
| DELETE | `/prospects/{prospect_id}/members/{member_id}` | `delete_prospect_member` | Remove prospect member |
| POST | `/prospects/{prospect_id}/grade` | `calculate_prospect_data_grade` | Calculate data grade |

### 6. PROSPECT FILES Module (10 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/prospect-files` | `get_prospect_files` | List prospect files |
| GET | `/prospect-files/{file_id}` | `get_prospect_file_details` | Get file details |
| POST | `/prospect-files` | `create_prospect_file` | Upload prospect file |
| DELETE | `/prospect-files/{file_id}` | `delete_prospect_file` | Delete prospect file |
| POST | `/prospect-files/upload-url` | `generate_presigned_upload_url` | Generate S3 upload URL |
| POST | `/prospect-files/validate/types` | `validate_prospect_file_types` | Validate file types |
| GET | `/prospect-files/non-graded/count` | `get_non_graded_prospect_files_count` | Get ungraded file count |
| GET | `/prospect-files/count` | `get_prospect_file_count` | Get total file count |
| DELETE | `/prospect-files/{file_id}/mapper-records` | `delete_data_mapper_records_for_file` | Delete data mapper records |
| POST | `/prospect-files/validate/processable` | `validate_prospect_is_processable` | Check if processable |

### 7. PROSPECT REPORTS Module (5 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/prospect-reports` | `get_prospect_reports_data` | List all prospect reports |
| GET | `/prospect-reports/{report_id}` | `get_sales_report_details` | Get report details |
| POST | `/prospect-reports` | `create_sales_report` | Create sales report |
| PATCH | `/prospect-reports/{report_id}` | `update_sales_report` | Update sales report |
| DELETE | `/prospect-reports/{report_id}` | `delete_sales_report` | Delete sales report |

### 8. SALES REPORTS Module (5 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/sales-reports/prospect/{prospect_id}` | `get_sales_reports_for_prospect` | Get prospect sales reports |
| POST | `/sales-reports/upload-url` | `generate_presigned_upload_url_for_sales_report` | Generate upload URL |
| GET | `/sales-reports/{report_id}/download` | `get_sales_report_download_url` | Get download URL |
| PATCH | `/sales-reports/bulk/status` | `bulk_update_sales_reports_status` | Bulk update report status |
| DELETE | `/sales-reports/bulk` | `bulk_delete_sales_reports` | Bulk delete reports |

### 9. INVITATIONS Module (6 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/invitations` | `list_invitations` | List all invitations |
| POST | `/invitations` | `send_invitation` | Send invitation |
| POST | `/invitations/{id}/resend` | `resend_invitation` | Resend invitation |
| DELETE | `/invitations/{id}` | `delete_invitation` | Delete invitation |
| POST | `/invitations/{token}/accept` | `accept_invitation` | Accept invitation (public) |
| POST | `/invitations/search-emails` | `search_emails_for_invitation` | Search emails for invitation |

### 10. PROSPECT INVITATIONS Module (3 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/prospect-invitations/prospect/{id}` | `get_prospect_invitations` | Get prospect invitations |
| POST | `/prospect-invitations` | `send_prospect_invitation` | Send prospect invitation |
| POST | `/prospect-invitations/{id}/resend` | `resend_prospect_invitation` | Resend prospect invitation |

### 11. TOKENS Module (5 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/tokens` | `get_tokens` | List API tokens |
| POST | `/tokens` | `create_token` | Create new API token |
| DELETE | `/tokens/{token_id}` | `delete_token` | Delete API token |
| POST | `/tokens/redeem` | `redeem_token` | Redeem token (public) |
| POST | `/tokens/register` | `register_with_token` | Register with token (public) |

### 12. APP PROFILE Module (3 endpoints)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| PUT | `/app-profile` | `update_app_profile` | Update application profile |
| GET | `/app-profile/version` | `get_app_version` | Get app version (public) |
| POST | `/app-profile/upload-url` | `generate_presigned_upload_url_for_app_logos` | Generate app logo upload URL |

### 13. PROSPECT FILE TYPES Module (1 endpoint)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/prospect-file-types` | `get_prospect_file_types` | Get configured file types |

### 14. BASE Module (1 endpoint)

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| GET | `/healthcheck` | `healthcheck` | Health check endpoint |

### 15. PASSWORD AUTH Module (Optional - 3+ endpoints)

**Note:** This module is conditionally loaded when `PASSWORD_AUTH=true` in settings.

| Method | Path | Function Name | Description |
|--------|------|---------------|-------------|
| POST | `/password-auth/login` | `login_with_password` | Login with password |
| POST | `/password-auth/register` | `register_with_password` | Register with password |
| POST | `/password-auth/change-password` | `change_password` | Change user password |

---

## Summary Statistics

### By System

| System | Total Endpoints | Modules | HTTP Methods Used |
|--------|----------------|---------|-------------------|
| **Triton Agentic** | 48 | 8 | GET, POST, PUT, PATCH, DELETE |
| **Mare API** | 74 | 14-15 | GET, POST, PUT, PATCH, DELETE |
| **TOTAL** | **122** | **22-23** | 5 methods |

### By HTTP Method

| Method | Triton Count | Mare Count | Total |
|--------|--------------|------------|-------|
| GET | 28 | 41 | 69 |
| POST | 10 | 23 | 33 |
| PUT | 2 | 2 | 4 |
| PATCH | 1 | 6 | 7 |
| DELETE | 4 | 5 | 9 |
| **TOTAL** | **45** | **77** | **122** |

### By Category

| Category | Endpoints | Systems |
|----------|-----------|---------|
| **Data Management** | 35 | Prospects, Files, Templates |
| **Authentication & Auth** | 17 | Auth, Users, Tokens, Invitations |
| **Client Management** | 14 | Clients, Customer Profiles |
| **AI/ML Operations** | 18 | Research, ROI Models, Template Generation |
| **Reports & Analytics** | 13 | Reports, Sales Reports, Lineage |
| **Jobs & Processing** | 15 | Jobs, Async Processing, Status Tracking |
| **System & Monitoring** | 10 | Health, Metrics, Validation |

---

## Quick Reference

### Triton Agentic - Most Used Endpoints

```bash
# Generate templates
POST /templates/generate

# Research company
POST /research/web-search

# Generate ROI model
POST /api/roi-models/generate

# Generate prospect data
POST /prospect-data/generate

# Check lineage
GET /lineage/{extraction_id}
```

### Mare API - Most Used Endpoints

```bash
# Authentication
POST /auth/signin
GET /auth/user

# Manage prospects
GET /prospects
POST /prospects
POST /prospects/{id}/process

# Upload files
POST /prospect-files
POST /prospect-files/upload-url

# Manage clients
GET /clients
POST /clients

# Reports
GET /prospect-reports
POST /prospect-reports
```

---

## Testing Endpoints

### Triton Agentic
```bash
# Health check
curl http://localhost:8000/health

# List templates
curl http://localhost:8000/templates/

# Get research stats
curl http://localhost:8000/research/stats/summary
```

### Mare API
```bash
# Health check
curl http://localhost:PORT/healthcheck

# Get app version (public)
curl http://localhost:PORT/app-profile/version

# List clients (requires auth)
curl -H "Authorization: Bearer $TOKEN" http://localhost:PORT/clients
```

---

## API Documentation URLs

### Triton Agentic
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

### Mare API
- **Swagger UI:** `http://localhost:PORT/docs`
- **ReDoc:** `http://localhost:PORT/redoc`
- **OpenAPI JSON:** `http://localhost:PORT/openapi.json`

---

## Related Documentation

- **User Role Matrix:** [COMPLETE_USER_ROLE_MATRIX.md](./COMPLETE_USER_ROLE_MATRIX.md)
- **Triton API Guide:** [API_README.md](./API_README.md)
- **Research API Guide:** [../architecture-current/RESEARCH_API_GUIDE.md](../architecture-current/RESEARCH_API_GUIDE.md)
- **Lineage API Guide:** [DATA_LINEAGE_API_GUIDE.md](./DATA_LINEAGE_API_GUIDE.md)

---

**Last Updated:** 2025-12-18
**Total Endpoints:** 122 (Triton: 48 | Mare: 74)
