# Complete User Role Matrix - Triton Agentic & Mare API

**Version:** 1.0.0
**Last Updated:** 2025-12-18
**Systems Covered:** Triton Agentic Platform + Mare API Platform

---

## Executive Summary

This document provides a comprehensive user role matrix covering **two integrated systems**:
- **Triton Agentic** - Healthcare dashboard template generation platform (48 endpoints)
- **Mare API** - Data mapping and prospect management platform (74 endpoints)

**Total:** 122 API endpoints across 2 platforms, 4 user types, 4 roles, 26 permissions

---

## Table of Contents

1. [User Types & Roles](#user-types--roles)
2. [Mare API System](#mare-api-system)
3. [Triton Agentic System](#triton-agentic-system)
4. [Combined Access Matrix](#combined-access-matrix)
5. [Database Access Controls](#database-access-controls)
6. [Implementation Guide](#implementation-guide)

---

## User Types & Roles

### Mare API User Types

```python
class UserTypeEnum(str, Enum):
    APP_USER = "app_user"           # Internal application users
    CUSTOMER_USER = "customer_user" # External customer users
```

### Mare API Roles

```python
class RolesEnum(str, Enum):
    CUSTOMER = "customer"        # ID: 1 - Customer users (external)
    APP_STAFF = "app_staff"      # ID: 2 - Staff users (internal)
    APP_ADMIN = "app_admin"      # ID: 3 - Admin users (internal)
    APP_PROSPECT = "app_prospect" # ID: 4 - Prospect users (external)
```

### Mare API Permissions (26 Total)

| ID | Permission | Description |
|----|------------|-------------|
| 1 | `update:app_profile` | Update application profile |
| 2 | `create:customer_profile` | Create customer profiles |
| 3 | `update:customer_profile` | Update any customer profile |
| 4 | `update:customer_profile<created>` | Update own created profiles |
| 5 | `delete:customer_profile` | Delete any customer profile |
| 6 | `delete:customer_profile<created>` | Delete own created profiles |
| 7 | `view:customer_profile` | View any customer profile |
| 8 | `view:customer_profile<created>` | View own created profiles |
| 9 | `create:token` | Create API tokens |
| 10 | `create:tokens<created_customer_user>` | Create tokens for own customers |
| 11 | `delete:token` | Delete any token |
| 12 | `delete:token<created>` | Delete own created tokens |
| 13 | `view:token` | View any token |
| 14 | `view:token<created>` | View own created tokens |
| 15 | `view:user` | View user information |
| 16 | `update:user<active>` | Update user active status |
| 17 | `update:user<role>` | Update user roles |
| 18 | `impersonate:user` | Impersonate other users |
| 19 | `view:client` | View any client |
| 20 | `create:client` | Create clients |
| 21 | `update:client` | Update clients |
| 22 | `delete:client` | Delete clients |
| 23 | `view_own:client` | View only own clients |
| 24 | `view:invitation` | View invitations |
| 25 | `send:invitation` | Send invitations |
| 26 | `delete:invitation` | Delete invitations |

### Triton + Mare Unified Role Mapping

| Triton Role | Mare Role | Access Level | Primary Use Case |
|-------------|-----------|--------------|------------------|
| System Administrator | APP_ADMIN | Full system access | Infrastructure, monitoring |
| Platform Owner | APP_ADMIN | Business operations | Client onboarding, oversight |
| Content Manager | APP_STAFF | Content management | Templates, research, ROI models |
| Data Analyst | APP_STAFF | Data & lineage | Compliance, data verification |
| Sales Representative | APP_STAFF | Prospect management | Generate dashboards for demos |
| Client User | CUSTOMER | Own data only | View templates, generate dashboards |
| Research Specialist | APP_STAFF | Research operations | Web search, document analysis |
| Compliance Officer | APP_STAFF | Audit & compliance | Lineage verification |
| Prospect User | APP_PROSPECT | Prospect-specific | View own prospect data |

---

## Mare API System

### Module Overview

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Auth** | 9 | Authentication & authorization |
| **Users** | 2 | User management |
| **Clients** | 7 | Client organization management |
| **Customer Profiles** | 7 | Customer profile CRUD |
| **Prospects** | 13 | Prospect management & processing |
| **Prospect Files** | 10 | File upload & management |
| **Prospect Reports** | 5 | Report generation & download |
| **Sales Reports** | 5 | Sales report management |
| **Invitations** | 6 | User invitation system |
| **Prospect Invitations** | 3 | Prospect-specific invitations |
| **Tokens** | 5 | API token management |
| **App Profile** | 3 | Application profile settings |
| **File Types** | 1 | Prospect file type configuration |
| **Base** | 1 | Health check |
| **Total** | **74** | |

### Mare API Endpoints by Module

#### 1. AUTH Module (9 endpoints)

| Endpoint Function | HTTP | Path | Role Access | Description |
|-------------------|------|------|-------------|-------------|
| `get_auth_user_info` | GET | `/auth/user` | All authenticated | Get current user info |
| `get_auth_user_url` | GET | `/auth/user/url` | All authenticated | Get user auth URL |
| `get_branding_info_for_user` | GET | `/auth/branding` | All authenticated | Get branding for user |
| `get_profile_and_branding_info_for_user` | GET | `/auth/profile-branding` | All authenticated | Get profile + branding |
| `get_branding_info_for_url` | GET | `/auth/branding/{url}` | Public | Get branding by URL |
| `signin_user` | POST | `/auth/signin` | Public | Sign in user |
| `signup_user` | POST | `/auth/signup` | Public | Sign up new user |
| `send_password_reset_email` | POST | `/auth/password-reset` | Public | Request password reset |
| `verify_otp_code` | POST | `/auth/verify-otp` | Public | Verify OTP code |

#### 2. USERS Module (2 endpoints)

| Endpoint Function | HTTP | Path | Role Access | Permission Required |
|-------------------|------|------|-------------|---------------------|
| `get_users` | GET | `/users` | APP_ADMIN, APP_STAFF | `view:user` |
| `update_user_active_status` | PUT | `/users/{user_id}/active` | APP_ADMIN | `update:user<active>` |

#### 3. CLIENTS Module (7 endpoints)

| Endpoint Function | HTTP | Path | Role Access | Permission Required |
|-------------------|------|------|-------------|---------------------|
| `get_all_clients` | GET | `/clients/all` | APP_ADMIN, APP_STAFF | `view:client` |
| `list_clients` | GET | `/clients` | ALL | `view:client` or `view_own:client` |
| `get_client_by_id` | GET | `/clients/{client_id}` | ALL | `view:client` or `view_own:client` |
| `create_client` | POST | `/clients` | APP_ADMIN, APP_STAFF | `create:client` |
| `update_client` | PATCH | `/clients/{client_id}` | APP_ADMIN, APP_STAFF | `update:client` |
| `delete_client` | DELETE | `/clients/{client_id}` | APP_ADMIN | `delete:client` |
| `get_filter_user_and_prospect` | GET | `/clients/{client_id}/filters` | APP_ADMIN, APP_STAFF | `view:client` |

#### 4. CUSTOMER PROFILES Module (7 endpoints)

| Endpoint Function | HTTP | Path | Permission Required |
|-------------------|------|------|---------------------|
| `get_customer_profiles` | GET | `/customer-profiles` | `view:customer_profile` |
| `create_customer_profile` | POST | `/customer-profiles` | `create:customer_profile` |
| `update_customer_profile` | PATCH | `/customer-profiles/{id}` | `update:customer_profile` |
| `delete_customer_profile` | DELETE | `/customer-profiles/{id}` | `delete:customer_profile` |
| `validate_customer_profile_name` | POST | `/customer-profiles/validate/name` | Public |
| `validate_customer_profile_url` | POST | `/customer-profiles/validate/url` | Public |
| `generate_presigned_upload_url_for_customer_logos` | POST | `/customer-profiles/upload-url` | `create:customer_profile` |

#### 5. PROSPECTS Module (13 endpoints)

| Endpoint Function | HTTP | Path | Description |
|-------------------|------|------|-------------|
| `get_user_prospects` | GET | `/prospects` | List user's prospects |
| `get_prospect_details` | GET | `/prospects/{prospect_id}` | Get prospect details |
| `create_prospect` | POST | `/prospects` | Create new prospect |
| `update_prospect` | PATCH | `/prospects/{prospect_id}` | Update prospect |
| `delete_prospect` | DELETE | `/prospects/{prospect_id}` | Delete prospect |
| `validate_prospect_name` | POST | `/prospects/validate/name` | Validate unique name |
| `start_prospect_processing` | POST | `/prospects/{prospect_id}/process` | Start ETL processing |
| `get_prospect_progress` | GET | `/prospects/{prospect_id}/progress` | Get processing progress |
| `get_prospect_report_data` | GET | `/prospects/{prospect_id}/report` | Get report data |
| `update_prospect_status` | PATCH | `/prospects/{prospect_id}/status` | Update status |
| `get_prospect_members` | GET | `/prospects/{prospect_id}/members` | Get members |
| `delete_prospect_member` | DELETE | `/prospects/{prospect_id}/members/{member_id}` | Remove member |
| `calculate_prospect_data_grade` | POST | `/prospects/{prospect_id}/grade` | Calculate data grade |

#### 6. PROSPECT FILES Module (10 endpoints)

| Endpoint Function | HTTP | Path | Description |
|-------------------|------|------|-------------|
| `get_prospect_files` | GET | `/prospect-files` | List files |
| `get_prospect_file_details` | GET | `/prospect-files/{file_id}` | Get file details |
| `create_prospect_file` | POST | `/prospect-files` | Upload file |
| `delete_prospect_file` | DELETE | `/prospect-files/{file_id}` | Delete file |
| `generate_presigned_upload_url` | POST | `/prospect-files/upload-url` | Generate upload URL |
| `validate_prospect_file_types` | POST | `/prospect-files/validate/types` | Validate file types |
| `get_non_graded_prospect_files_count` | GET | `/prospect-files/non-graded/count` | Get ungraded count |
| `get_prospect_file_count` | GET | `/prospect-files/count` | Get total file count |
| `delete_data_mapper_records_for_file` | DELETE | `/prospect-files/{file_id}/mapper-records` | Delete mapper data |
| `validate_prospect_is_processable` | POST | `/prospect-files/validate/processable` | Check if processable |

#### 7. PROSPECT REPORTS Module (5 endpoints)

| Endpoint Function | HTTP | Path | Description |
|-------------------|------|------|-------------|
| `get_prospect_reports_data` | GET | `/prospect-reports` | List all reports |
| `get_sales_report_details` | GET | `/prospect-reports/{report_id}` | Get report details |
| `create_sales_report` | POST | `/prospect-reports` | Create report |
| `update_sales_report` | PATCH | `/prospect-reports/{report_id}` | Update report |
| `delete_sales_report` | DELETE | `/prospect-reports/{report_id}` | Delete report |

#### 8. SALES REPORTS Module (5 endpoints)

| Endpoint Function | HTTP | Path | Description |
|-------------------|------|------|-------------|
| `get_sales_reports_for_prospect` | GET | `/sales-reports/prospect/{prospect_id}` | Get prospect reports |
| `generate_presigned_upload_url_for_sales_report` | POST | `/sales-reports/upload-url` | Generate upload URL |
| `get_sales_report_download_url` | GET | `/sales-reports/{report_id}/download` | Get download URL |
| `bulk_update_sales_reports_status` | PATCH | `/sales-reports/bulk/status` | Bulk status update |
| `bulk_delete_sales_reports` | DELETE | `/sales-reports/bulk` | Bulk delete |

#### 9. INVITATIONS Module (6 endpoints)

| Endpoint Function | HTTP | Path | Permission Required |
|-------------------|------|------|---------------------|
| `list_invitations` | GET | `/invitations` | `view:invitation` |
| `send_invitation` | POST | `/invitations` | `send:invitation` |
| `resend_invitation` | POST | `/invitations/{id}/resend` | `send:invitation` |
| `delete_invitation` | DELETE | `/invitations/{id}` | `delete:invitation` |
| `accept_invitation` | POST | `/invitations/{token}/accept` | Public |
| `search_emails_for_invitation` | POST | `/invitations/search-emails` | `send:invitation` |

#### 10. PROSPECT INVITATIONS Module (3 endpoints)

| Endpoint Function | HTTP | Path | Description |
|-------------------|------|------|-------------|
| `get_prospect_invitations` | GET | `/prospect-invitations/prospect/{id}` | Get prospect invitations |
| `send_prospect_invitation` | POST | `/prospect-invitations` | Send prospect invitation |
| `resend_prospect_invitation` | POST | `/prospect-invitations/{id}/resend` | Resend invitation |

#### 11. TOKENS Module (5 endpoints)

| Endpoint Function | HTTP | Path | Permission Required |
|-------------------|------|------|---------------------|
| `get_tokens` | GET | `/tokens` | `view:token` |
| `create_token` | POST | `/tokens` | `create:token` |
| `delete_token` | DELETE | `/tokens/{token_id}` | `delete:token` |
| `redeem_token` | POST | `/tokens/redeem` | Public |
| `register_with_token` | POST | `/tokens/register` | Public |

#### 12. APP PROFILE Module (3 endpoints)

| Endpoint Function | HTTP | Path | Permission Required |
|-------------------|------|------|---------------------|
| `update_app_profile` | PUT | `/app-profile` | `update:app_profile` |
| `get_app_version` | GET | `/app-profile/version` | Public |
| `generate_presigned_upload_url_for_app_logos` | POST | `/app-profile/upload-url` | `update:app_profile` |

#### 13. FILE TYPES Module (1 endpoint)

| Endpoint Function | HTTP | Path | Description |
|-------------------|------|------|-------------|
| `get_prospect_file_types` | GET | `/prospect-file-types` | Get configured file types |

#### 14. BASE Module (1 endpoint)

| Endpoint Function | HTTP | Path | Description |
|-------------------|------|------|-------------|
| `healthcheck` | GET | `/healthcheck` | Health check endpoint |

---

## Triton Agentic System

*(Reference from previous section - 48 endpoints across 8 modules)*

### Module Overview

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Clients** | 7 | Client & value proposition management |
| **Jobs** | 4 | Template generation job tracking |
| **Templates** | 4 | Dashboard template CRUD |
| **Research** | 6 | AI research agents (web + documents) |
| **ROI Models** | 6 | ROI model generation (B1-B13) |
| **Prospect Data** | 6 | Prospect-specific dashboard data |
| **Lineage** | 9 | Data lineage & audit trails |
| **System** | 2 | Health checks |
| **Total** | **48** | |

---

## Combined Access Matrix

Legend: ✅ = Full Access | 📖 = Read Only | 🔒 = No Access | 🔑 = With Permission | ⚠️ = Own Data Only

### Mare API Access Matrix

| Module / Function | APP_ADMIN | APP_STAFF | CUSTOMER | APP_PROSPECT |
|-------------------|-----------|-----------|----------|--------------|
| **AUTH** |
| Authentication endpoints | ✅ | ✅ | ✅ | ✅ |
| Get user info | ✅ | ✅ | ✅ | ✅ |
| **USERS** |
| `get_users` | ✅ | ✅ | 🔒 | 🔒 |
| `update_user_active_status` | ✅ | 🔒 | 🔒 | 🔒 |
| **CLIENTS** |
| `get_all_clients` | ✅ | ✅ | 🔒 | 🔒 |
| `list_clients` | ✅ | ✅ | ⚠️ | 🔒 |
| `get_client_by_id` | ✅ | ✅ | ⚠️ | 🔒 |
| `create_client` | ✅ | 🔑 | 🔒 | 🔒 |
| `update_client` | ✅ | 🔑 | 🔒 | 🔒 |
| `delete_client` | ✅ | 🔒 | 🔒 | 🔒 |
| **CUSTOMER PROFILES** |
| `get_customer_profiles` | ✅ | 🔑 | 🔑 | 🔒 |
| `create_customer_profile` | ✅ | 🔑 | 🔒 | 🔒 |
| `update_customer_profile` | ✅ | 🔑 | 🔑 | 🔒 |
| `delete_customer_profile` | ✅ | 🔑 | 🔒 | 🔒 |
| **PROSPECTS** |
| `get_user_prospects` | ✅ | ✅ | ⚠️ | ⚠️ |
| `get_prospect_details` | ✅ | ✅ | ⚠️ | ⚠️ |
| `create_prospect` | ✅ | ✅ | ⚠️ | 🔒 |
| `update_prospect` | ✅ | ✅ | ⚠️ | 🔒 |
| `delete_prospect` | ✅ | ✅ | ⚠️ | 🔒 |
| `start_prospect_processing` | ✅ | ✅ | ⚠️ | 🔒 |
| `get_prospect_progress` | ✅ | ✅ | ⚠️ | ⚠️ |
| **PROSPECT FILES** |
| `get_prospect_files` | ✅ | ✅ | ⚠️ | ⚠️ |
| `create_prospect_file` | ✅ | ✅ | ⚠️ | ⚠️ |
| `delete_prospect_file` | ✅ | ✅ | ⚠️ | 🔒 |
| **REPORTS** |
| `get_prospect_reports_data` | ✅ | ✅ | ⚠️ | ⚠️ |
| `create_sales_report` | ✅ | ✅ | 🔒 | 🔒 |
| `update_sales_report` | ✅ | ✅ | 🔒 | 🔒 |
| `delete_sales_report` | ✅ | 🔒 | 🔒 | 🔒 |
| **INVITATIONS** |
| `list_invitations` | ✅ | 🔑 | 🔒 | 🔒 |
| `send_invitation` | ✅ | 🔑 | 🔒 | 🔒 |
| `delete_invitation` | ✅ | 🔑 | 🔒 | 🔒 |
| **TOKENS** |
| `get_tokens` | ✅ | 🔑 | 🔑 | 🔒 |
| `create_token` | ✅ | 🔑 | 🔒 | 🔒 |
| `delete_token` | ✅ | 🔑 | 🔑 | 🔒 |
| **APP PROFILE** |
| `update_app_profile` | ✅ | 🔒 | 🔒 | 🔒 |

### Triton + Mare Integration Access Matrix

| Unified Role | Mare Role | Triton Clients | Triton Research | Triton ROI Models | Triton Lineage | Mare Clients | Mare Prospects |
|--------------|-----------|----------------|-----------------|-------------------|----------------|--------------|----------------|
| System Administrator | APP_ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Platform Owner | APP_ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Content Manager | APP_STAFF | ✅ | ✅ | ✅ | 📖 | 🔑 | ✅ |
| Data Analyst | APP_STAFF | 📖 | 📖 | 📖 | ✅ | 📖 | 📖 |
| Sales Representative | APP_STAFF | 📖 | 🔒 | 📖 | 🔒 | ⚠️ | ✅ |
| Research Specialist | APP_STAFF | 📖 | ✅ | 📖 | 📖 | 📖 | 📖 |
| Compliance Officer | APP_STAFF | 📖 | 📖 | 📖 | ✅ | 📖 | 📖 |
| Client User | CUSTOMER | ⚠️ | 🔒 | ⚠️ | 🔒 | ⚠️ | ⚠️ |
| Prospect User | APP_PROSPECT | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | ⚠️ |

---

## Database Access Controls

### Mare API Database Tables

| Table | Owner Columns | Access Control |
|-------|---------------|----------------|
| `users` | `id`, `email` | User can view/update own record |
| `roles` | - | Admin only |
| `permissions` | - | Admin only |
| `role_permission_assoc` | - | Admin only |
| `clients` | `creator_id` | CUSTOMER sees only `user_client_assoc` linked |
| `customer_profiles` | `creator_id` | Creator has special permissions |
| `prospects` | `user_id` | User owns prospects they created |
| `prospect_files` | `user_id` | User owns files they uploaded |
| `prospect_members` | `user_id` | Members can access prospect |
| `prospect_reports` | `uploader_id` | Report uploader tracking |
| `tokens` | `creator_id` | Creator can delete own tokens |
| `invitations` | `sender_id` | Sender can resend/delete |
| `user_client_assoc` | - | Links users to clients they can access |
| `prospect_client_assoc` | - | Links prospects to clients |

### Triton Agentic Database Tables

| Table | Owner Columns | Access Control |
|-------|---------------|----------------|
| `clients` | `id` | Client users filtered by `client_id` |
| `value_propositions` | `client_id` | Linked to client |
| `generation_jobs` | `client_id` | Linked to client |
| `dashboard_templates` | `client_id`, `job_id` | Linked to client |
| `prospects` | `client_id` | Linked to client |
| `prospect_dashboard_data` | `prospect_id`, `template_id` | Prospect-specific |
| `extraction_lineage` | - | Read by analysts/compliance |

### Row-Level Security (RLS) Implementation

**For CUSTOMER Users (Mare API):**
```sql
-- Clients table RLS
CREATE POLICY customer_client_access ON clients
FOR SELECT
TO customer_user
USING (id IN (
    SELECT client_id FROM user_client_assoc
    WHERE user_id = current_user_id()
));

-- Prospects table RLS
CREATE POLICY customer_prospect_access ON prospects
FOR ALL
TO customer_user
USING (user_id = current_user_id() OR
       id IN (SELECT prospect_id FROM prospect_members WHERE user_id = current_user_id()));
```

**For CLIENT Users (Triton):**
```sql
-- Templates table RLS
CREATE POLICY client_template_access ON dashboard_templates
FOR SELECT
TO client_user
USING (client_id = current_client_id());

-- Prospect data RLS
CREATE POLICY client_prospect_data_access ON prospect_dashboard_data
FOR SELECT
TO client_user
USING (prospect_id IN (
    SELECT id FROM prospects WHERE client_id = current_client_id()
));
```

---

## Implementation Guide

### 1. FastAPI Permission Dependency (Mare API Pattern)

```python
from fastapi import Depends, HTTPException, status
from src.core.models import PermissionsEnum, User
from src.auth import get_current_user

async def require_permission(permission: PermissionsEnum):
    """Dependency to require specific permission."""
    async def permission_checker(current_user: User = Depends(get_current_user)):
        # Check if user's role has the required permission
        user_permissions = [p.name for p in current_user.role.permissions]

        if permission.value not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required"
            )

        return current_user

    return permission_checker

# Usage in router
@router.post("/clients")
async def create_client(
    current_user: User = Depends(require_permission(PermissionsEnum.CREATE_CLIENT))
):
    ...
```

### 2. Row-Level Access Filter (Triton Pattern)

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

async def get_client_filter(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Optional[UUID]:
    """Return client_id filter for CUSTOMER role users."""
    if current_user.role.name == "CUSTOMER":
        # Customer can only see their own client's data
        return current_user.client_id

    # Admin/Staff can see all
    return None

# Usage in query
@router.get("/templates")
async def list_templates(
    client_filter: Optional[UUID] = Depends(get_client_filter),
    db: Session = Depends(get_db)
):
    query = db.query(DashboardTemplate)

    if client_filter:
        query = query.filter(DashboardTemplate.client_id == client_filter)

    return query.all()
```

### 3. Prospect Access Control (Mare Pattern)

```python
async def verify_prospect_access(
    prospect_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Prospect:
    """Verify user has access to prospect."""

    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()

    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    # Admin/Staff have access to all
    if current_user.role.name in ["APP_ADMIN", "APP_STAFF"]:
        return prospect

    # Check if user owns prospect or is a member
    is_owner = prospect.user_id == current_user.id
    is_member = db.query(ProspectMember).filter(
        ProspectMember.prospect_id == prospect_id,
        ProspectMember.user_id == current_user.id
    ).first() is not None

    if not (is_owner or is_member):
        raise HTTPException(status_code=403, detail="Access denied")

    return prospect

# Usage
@router.get("/prospects/{prospect_id}")
async def get_prospect(
    prospect: Prospect = Depends(verify_prospect_access)
):
    return prospect
```

### 4. API Key Scoped Access

```python
from typing import List

class APIKeyScopes:
    """API key scope definitions."""
    READ_TEMPLATES = "read:templates"
    WRITE_PROSPECTS = "write:prospects"
    READ_LINEAGE = "read:lineage"

async def require_scopes(required_scopes: List[str]):
    """Dependency to check API key scopes."""
    async def scope_checker(api_key: str = Depends(get_api_key)):
        key_record = await get_key_from_db(api_key)

        if not key_record:
            raise HTTPException(status_code=401, detail="Invalid API key")

        missing_scopes = set(required_scopes) - set(key_record.scopes)

        if missing_scopes:
            raise HTTPException(
                status_code=403,
                detail=f"Missing scopes: {missing_scopes}"
            )

        return key_record

    return scope_checker

# Usage
@router.get("/templates")
async def list_templates(
    api_key: APIKey = Depends(require_scopes([APIKeyScopes.READ_TEMPLATES]))
):
    ...
```

---

## Security Best Practices

### 1. Authentication
- JWT tokens with 1-hour expiration
- Refresh tokens for long sessions
- Token revocation list for logout

### 2. Authorization
- Permission-based access control (PBAC) for Mare API
- Role-based access control (RBAC) for Triton
- Row-level security (RLS) for multi-tenant data

### 3. Audit Logging
```python
async def log_access(
    user_id: int,
    action: str,
    resource: str,
    resource_id: str,
    success: bool
):
    """Log all access attempts."""
    await db.execute(
        """
        INSERT INTO audit_log (user_id, action, resource, resource_id, success, timestamp)
        VALUES ($1, $2, $3, $4, $5, NOW())
        """,
        user_id, action, resource, resource_id, success
    )
```

### 4. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Role-based limits
@router.get("/prospects")
@limiter.limit("100/hour")  # Customer limit
async def list_prospects(...):
    ...

# Admin gets higher limits
@limiter.exempt  # No limit for admin
async def admin_list_all_prospects(...):
    ...
```

---

## Migration & Rollout Plan

### Phase 1: Mare API Permission System
1. Audit existing endpoints and add permission checks
2. Create role-permission seed data
3. Update all routers with `require_permission()` dependencies

### Phase 2: Triton Role Integration
1. Add role field to Triton users table
2. Map Triton roles to Mare roles
3. Implement unified authentication

### Phase 3: Row-Level Security
1. Implement RLS policies in PostgreSQL
2. Add client_id filtering to all queries
3. Test multi-tenant data isolation

### Phase 4: API Key Management
1. Implement scoped API keys
2. Add key rotation mechanism
3. Provide self-service key management UI

---

## Related Documentation

- **Mare API README:** `/home/yashrajshres/mare-api/README.md`
- **Triton API Guide:** `docs/operations/API_README.md`
- **Research API:** `docs/architecture-current/RESEARCH_API_GUIDE.md`
- **Lineage API:** `LINEAGE_API_QUICK_REFERENCE.md`

---

**Document End**

**Total System Stats:**
- **Systems:** 2 (Triton Agentic + Mare API)
- **Endpoints:** 122 (48 Triton + 74 Mare)
- **User Types:** 2 (APP_USER, CUSTOMER_USER)
- **Roles:** 4 (CUSTOMER, APP_STAFF, APP_ADMIN, APP_PROSPECT)
- **Permissions:** 26 (Mare API granular permissions)
- **Database Tables:** 28+ (combined)
