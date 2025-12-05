# Refactoring Summary - Services & ICM Implementation

## Overview

This refactoring reorganizes the codebase into a proper layered architecture with business logic separated into services, and adds complete ICM (Inter-Caste Marriage) application support.

---

## Architecture Changes

### Before: Monolithic Router
```
routers/
  ├── dbt.py (all functions mixed with routes)
  ├── auth.py
  └── admin.py
```

### After: Layered Architecture
```
routers/
  ├── dbt.py (routes only - simplified)
  ├── icm.py (ICM routes)
  ├── auth.py
  └── admin.py

services/
  ├── dbt_service.py (DBT business logic)
  ├── icm_service.py (ICM business logic)
  └── __init__.py

db/
  ├── session.py (Main DB & DBT tables)
  ├── govt_session.py (Government data)
  ├── icm_session.py (ICM tables - NEW)
  └── __init__.py
```

---

## Files Created/Modified

### 1. New Service Layer Files

#### `app/services/dbt_service.py`
**Business logic for DBT case management**

Functions:
- `filter_cases_by_jurisdiction()` - Filter cases based on user role and location
- `validate_jurisdiction()` - Ensure user can access specific case
- `validate_role_for_action()` - Validate role and stage for workflow actions
- `approve_case_workflow()` - Handle case approval and stage progression
- `request_correction_workflow()` - Request case corrections
- `get_all_cases_for_user()` - Get jurisdiction-filtered cases

**Key Features:**
- Separates business logic from API routing
- Reusable across different API consumers
- Better testing capabilities
- Cleaner code organization

#### `app/services/icm_service.py`
**Business logic for ICM application management**

Functions:
- `get_user_icm_applications()` - Retrieve citizen's applications
- `create_icm_application()` - Create new ICM application
- `approve_icm_application()` - Approve and advance application
- `reject_icm_application()` - Reject application
- `request_icm_correction()` - Request corrections
- `get_icm_applications_by_jurisdiction()` - Filter by jurisdiction

**Key Features:**
- Full application lifecycle management
- Event tracking for audit trail
- Jurisdiction-based filtering
- Status workflow control

### 2. New Database Session File

#### `app/db/icm_session.py`
**Database operations for ICM applications**

Connection Management:
- `get_icm_db_connection()` - Establish ICM database connection (uses `get_dbt_db_connection` pattern)

ICM Application Functions:
- `get_icm_application_by_id()` - Fetch by ID
- `get_icm_applications_by_citizen()` - Fetch by citizen
- `get_all_icm_applications()` - Fetch all with pagination
- `insert_icm_application()` - Create new application
- `update_icm_application()` - Update application fields

ICM Event Functions:
- `get_icm_events_by_application()` - Fetch timeline events
- `insert_icm_event()` - Record application event

Query Functions:
- `get_icm_applications_by_status()` - Filter by status
- `get_icm_applications_by_stage()` - Filter by stage

**Key Features:**
- Proper connection pooling
- Error handling with HTTPException
- JSON event data support
- Pagination support

### 3. New Router File

#### `app/routers/icm.py`
**Complete ICM API endpoints**

**Citizen Endpoints:**
- `POST /icm/applications` - Submit new application
- `GET /icm/applications` - Get citizen's applications
- `GET /icm/applications/{icm_id}` - Get application details
- `GET /icm/applications/{icm_id}/timeline` - Get application timeline

**Officer Endpoints:**
- `POST /icm/applications/{icm_id}/approve` - Approve application
- `POST /icm/applications/{icm_id}/reject` - Reject application
- `POST /icm/applications/{icm_id}/request-correction` - Request corrections
- `GET /icm/applications?state_ut=X&district=Y` - Get filtered applications

**Request Models:**
- `CreateICMApplicationRequest` - Application submission
- `ApproveICMRequest` - Approval with optional comment
- `RejectICMRequest` - Rejection with reason
- `CorrectionRequest` - Correction request with list

**Features:**
- JWT authentication required
- Role-based access control
- Complete CRUD operations
- Event logging for audit trail

### 4. Updated Files

#### `app/routers/dbt.py`
- Imports service functions instead of defining them
- Routes remain (simplified if desired)
- Uses business logic from `dbt_service.py`

#### `main.py`
- Added ICM router import
- Included ICM router in app

#### `app/routers/__init__.py`
- Added ICM router export

#### `app/services/__init__.py`
- Central export point for all services
- Easy importing: `from app.services import filter_cases_by_jurisdiction`

---

## ICM Database Schema (Referenced)

### icm_applications table
```sql
Columns:
- icm_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- citizen_id (INT, FOREIGN KEY)
- applicant_aadhaar (BIGINT)
- groom_name, bride_name (VARCHAR)
- groom_age, bride_age (INT)
- marriage_date (DATE)
- joint_account_number (VARCHAR)
- current_stage (INT, default 0)
- pending_at (VARCHAR)
- application_status (VARCHAR)
- state_ut, district (VARCHAR)
- created_at, updated_at (TIMESTAMP)
```

### icm_events table
```sql
Columns:
- event_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- icm_id (INT, FOREIGN KEY)
- event_type (VARCHAR)
- event_role (VARCHAR)
- event_stage (INT)
- comment (TEXT)
- event_data (JSON)
- created_at (TIMESTAMP)
```

---

## Service Layer Benefits

### 1. Separation of Concerns
- **Routers**: Handle HTTP details only
- **Services**: Contains business logic
- **Database**: Handles data persistence

### 2. Testability
```python
# Test service without HTTP overhead
from app.services.dbt_service import approve_case_workflow

result = approve_case_workflow(
    case_no=1,
    actor="user1",
    role="Tribal Officer",
    # ... other params
)
assert result["new_stage"] == 2
```

### 3. Reusability
```python
# Use service from multiple routers
from app.services import validate_jurisdiction

# Use in dbt.py
validate_jurisdiction(token_payload, case)

# Use in other routers if needed
validate_jurisdiction(token_payload, case)
```

### 4. Maintainability
- Easy to locate business logic
- Changes isolated to service layer
- Routes stay clean and focused

---

## ICM Application Workflow

### Stage Progression
```
Stage 0: Application Created (CITIZEN)
   ↓
Stage 1: ADM Review Pending
   ↓
Stage 2: TO Review Pending (Tribal Officer)
   ↓
Stage 3: DM Review Pending (District Magistrate)
   ↓
Stage 4: SNO Review Pending (State Nodal Officer)
   ↓
Stage 5: PFMS Fund Release Pending (PFMS Officer)
   ↓
Stage 6: CLOSED (Approved/Rejected)
```

### Status Values
- `Pending` - Initial status
- `Under Review` - Being processed by officer
- `Approved` - Application approved
- `Rejected` - Application rejected
- `Correction Required` - Sent back for corrections

### Event Types
- `APPLICATION_CREATED` - Initial creation
- `{ROLE}_APPROVED` - Role approval (ADM_APPROVED, TO_APPROVED, etc.)
- `APPLICATION_REJECTED` - Rejection
- `CORRECTION_REQUESTED` - Correction request
- `FUND_RELEASED` - Fund disbursement

---

## API Usage Examples

### Create ICM Application
```bash
POST /icm/applications
Authorization: Bearer <token>
Content-Type: application/json

{
  "groom_name": "Rajesh Kumar",
  "groom_age": 28,
  "groom_father_name": "Ram Kumar",
  "groom_dob": "1996-05-15",
  "groom_aadhaar": 123456789012,
  "bride_name": "Priya Singh",
  "bride_age": 26,
  "bride_father_name": "Singh",
  "bride_dob": "1998-07-20",
  "bride_aadhaar": 987654321098,
  "marriage_date": "2025-02-14",
  "joint_account_number": "1234567890"
}
```

### Approve Application
```bash
POST /icm/applications/1/approve
Authorization: Bearer <token>
Content-Type: application/json

{
  "comment": "Application meets all criteria"
}
```

### Request Corrections
```bash
POST /icm/applications/1/request-correction
Authorization: Bearer <token>
Content-Type: application/json

{
  "corrections_required": [
    "Update groom's address",
    "Provide marriage certificate",
    "Verify bank account ownership"
  ],
  "comment": "Please provide missing documents"
}
```

---

## Database Connection Pattern

All database sessions follow consistent pattern:

```python
def get_icm_db_connection():
    """Establishes ICM database connection"""
    try:
        connection = mysql.connector.connect(**ICM_DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(...)

# Usage in functions
def get_icm_application_by_id(icm_id: int):
    connection = get_icm_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        # ... query logic
    finally:
        cursor.close()
        connection.close()
```

---

## Configuration Required

Add to `.env`:
```
# ICM Database Configuration
ICM_DB_HOST=localhost
ICM_DB_PORT=3306
ICM_DB_USER=root
ICM_DB_PASSWORD=password
ICM_DB_DATABASE=icm_db
```

Or update `app/core/config.py`:
```python
ICM_DB_DATABASE: str = os.getenv("ICM_DB_DATABASE", "icm_db")
```

---

## Migration Path

### Step 1: Deploy Services Layer
- Add `app/services/` with `dbt_service.py` and `icm_service.py`
- Update imports in existing routers
- No API changes, backward compatible

### Step 2: Add ICM Support
- Deploy `app/db/icm_session.py`
- Deploy `app/routers/icm.py`
- Update `main.py` to register ICM router

### Step 3: Refactor Existing Routers (Optional)
- Clean up `dbt.py` to use services
- Keep API endpoints unchanged
- Improve code organization

---

## Testing Strategy

```python
# test_services.py
from app.services.dbt_service import filter_cases_by_jurisdiction
from app.schemas.dbt_schemas import AtrocityDBModel

def test_filter_cases_by_jurisdiction():
    # Create mock data
    cases = [create_test_case(...)]
    token = {"role": "TO", "state_ut": "Delhi", "district": "Delhi"}
    
    # Call service
    filtered = filter_cases_by_jurisdiction(cases, token)
    
    # Assert
    assert len(filtered) == 1
    assert filtered[0].State_UT == "Delhi"
```

---

## Summary of Changes

| Component | Action | Benefit |
|-----------|--------|---------|
| `dbt_service.py` | Created | Business logic separation |
| `icm_service.py` | Created | ICM application management |
| `icm_session.py` | Created | ICM database operations |
| `icm.py` | Created | Complete ICM API |
| `services/__init__.py` | Created | Centralized service exports |
| `dbt.py` | Updated | Now uses services |
| `main.py` | Updated | ICM router registered |
| `routers/__init__.py` | Updated | Package exports |

---

**Status:** ✅ Complete and Ready for Integration

**Next Steps:**
1. Update configuration with ICM database details
2. Run database migrations for `icm_applications` and `icm_events` tables
3. Test endpoints with sample data
4. Deploy and monitor

