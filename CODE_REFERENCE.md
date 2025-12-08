# Code Implementation Reference

## Files Modified Summary

### 1. Service Layer: `app/services/icm_service.py`

#### Added Import
```python
from datetime import datetime
```

#### New Function: `resubmit_corrected_application()`
Location: Lines 720-874

This async function handles the business logic for resubmitting corrected applications:
- Validates application exists
- Verifies applicant ownership
- Checks application status is "Correction Required"
- Updates application with corrected data
- Saves/uploads new files
- Creates audit event
- Returns success response with update details

Key features:
- Partial update support
- File replacement capability
- Comprehensive error handling
- Event tracking for audit trail

---

### 2. Router Layer: `app/routers/icm.py`

#### Added Import
```python
from app.services.icm_service import (
    # ... existing imports ...
    resubmit_corrected_application
)
```

#### New Endpoint: `PUT /icm/applications/{icm_id}`
Location: Lines 233-416

Endpoint function: `resubmit_application_with_corrections()`

Features:
- All form fields optional (true partial update)
- Multipart/form-data support
- JWT authentication required
- Comprehensive docstring
- Detailed error handling
- Logging of actions
- Field filtering (only non-None values sent to service)

Parameters:
- 15 groom fields (optional)
- 15 bride fields (optional)
- 3 marriage fields (optional)
- 4 witness fields (optional)
- 3 bank fields (optional)
- 4 file fields (optional)

---

### 3. Documentation: `ICM_API_DOCUMENTATION.md`

#### Added Section: "4. Resubmit Application with Corrections"
Location: After line 225, before "Officer Endpoints"

Content:
- Endpoint path: `PUT /icm/applications/{icm_id}`
- Description and purpose
- Request format and headers
- Request body examples
- Available fields for correction
- Response format (200 OK)
- Error responses
- Workflow changes
- Timeline events
- Important notes

---

## Usage Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Workflow                       │
└─────────────────────────────────────────────────────────────┘

1. Submit Application
   POST /icm/applications
   ├─ Status: "Pending"
   ├─ Stage: 0
   └─ Pending At: "ADM"
         ↓
2. Officer Reviews & Requests Corrections
   POST /icm/applications/{id}/request-correction
   ├─ Status: "Correction Required"
   ├─ Stage: 0 (reset)
   └─ Pending At: "Citizen"
         ↓
3. Citizen Resubmits Corrections ← NEW ENDPOINT
   PUT /icm/applications/{id}
   ├─ Status: "Resubmitted"
   ├─ Stage: 0
   ├─ Pending At: "Tribal Officer"
   └─ Event: CORRECTION_RESUBMITTED
         ↓
4. Officers Continue Review & Approval
   POST /icm/applications/{id}/approve
   ├─ Status: "Approved" (or continues through stages)
   ├─ Stage: 1, 2, 3 (incremental)
   └─ Pending At: "Next Role"
```

---

## HTTP Request/Response Examples

### cURL Request
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: multipart/form-data" \
  -F "groom_name=Rajesh Kumar" \
  -F "groom_age=30" \
  -F "bride_name=Priya Singh" \
  -F "marriage_date=2025-03-14" \
  -F "groom_signature=@/path/to/groom_signature.jpg" \
  -F "bride_signature=@/path/to/bride_signature.jpg"
```

### Success Response (HTTP 200)
```json
{
  "icm_id": 1,
  "status": "resubmitted",
  "message": "Corrected application resubmitted successfully",
  "current_stage": 0,
  "pending_at": "Tribal Officer",
  "application_status": "Resubmitted",
  "files_updated": ["groom_signature_file", "bride_signature_file"],
  "data_fields_updated": ["groom_name", "groom_age", "bride_name", "marriage_date"]
}
```

### Error Response - Wrong Status (HTTP 400)
```json
{
  "detail": "Application must be in 'Correction Required' status. Current status: Approved"
}
```

### Error Response - Not Owner (HTTP 403)
```json
{
  "detail": "You can only resubmit your own applications"
}
```

### Error Response - Not Found (HTTP 404)
```json
{
  "detail": "ICM Application #999 not found"
}
```

---

## Data Models

### Request Data Structure
```python
{
    "groom_name": "string (optional)",
    "groom_age": "integer (optional)",
    "groom_father_name": "string (optional)",
    "groom_dob": "string YYYY-MM-DD (optional)",
    "groom_aadhaar": "integer (optional)",
    # ... 10 more groom fields
    
    "bride_name": "string (optional)",
    "bride_age": "integer (optional)",
    "bride_father_name": "string (optional)",
    "bride_dob": "string YYYY-MM-DD (optional)",
    "bride_aadhaar": "integer (optional)",
    # ... 10 more bride fields
    
    "marriage_date": "string YYYY-MM-DD (optional)",
    "marriage_certificate_number": "string (optional)",
    "previous_benefit_taken": "boolean (optional)",
    
    "witness_name": "string (optional)",
    "witness_aadhaar": "integer (optional)",
    "witness_address": "string (optional)",
    "witness_verified": "boolean (optional)",
    
    "joint_account_number": "string (optional)",
    "joint_ifsc": "string (optional)",
    "joint_account_bank_name": "string (optional)",
    
    "marriage_certificate": "file (optional)",
    "groom_signature": "file (optional)",
    "bride_signature": "file (optional)",
    "witness_signature": "file (optional)"
}
```

### Response Data Structure
```python
{
    "icm_id": "integer",
    "status": "string - 'resubmitted'",
    "message": "string - success message",
    "current_stage": "integer - 0",
    "pending_at": "string - 'Tribal Officer'",
    "application_status": "string - 'Resubmitted'",
    "files_updated": "list of strings - updated file fields",
    "data_fields_updated": "list of strings - updated data fields"
}
```

---

## Validation Logic

```
Request Validation:
├─ JWT Token Valid? (401 if not)
├─ citizen_id in token? (401 if not)
├─ Application exists? (404 if not)
├─ citizen_id matches app owner? (403 if not)
├─ Application status = "Correction Required"? (400 if not)
└─ File uploads valid? (500 if errors)

Update Logic:
├─ Prepare corrected data (non-None values only)
├─ Update application record
├─ Save/upload any provided files
├─ Create audit event
└─ Return success response
```

---

## Event Structure Created

```json
{
    "event_id": "auto-generated integer",
    "icm_id": "integer - same as application",
    "event_type": "CORRECTION_RESUBMITTED",
    "event_role": "Citizen",
    "event_stage": 0,
    "comment": "Corrected application resubmitted by citizen",
    "event_data": {
        "action": "resubmitted_corrections",
        "applicant_aadhaar": "integer",
        "previous_stage": "integer",
        "files_updated": ["file_field_1", "file_field_2"],
        "data_fields_updated": ["field_1", "field_2", ...]
    },
    "created_at": "ISO datetime string"
}
```

---

## Field Mapping

### Form Field Names → Database Column Names

```
Groom:
- groom_name → groom_name
- groom_age → groom_age
- groom_father_name → groom_father_name
- groom_dob → groom_dob
- groom_aadhaar → groom_aadhaar
- groom_pre_address → groom_pre_address
- groom_current_address → groom_current_address
- groom_permanent_address → groom_permanent_address
- groom_caste_cert_id → groom_caste_cert_id
- groom_education → groom_education
- groom_training → groom_training
- groom_income → groom_income
- groom_livelihood → groom_livelihood
- groom_future_plan → groom_future_plan
- groom_first_marriage → groom_first_marriage

Bride: (same pattern as groom, replace 'groom_' with 'bride_')

Marriage:
- marriage_date → marriage_date
- marriage_certificate_number → marriage_cert_number
- previous_benefit_taken → previous_benefit_taken

Witness:
- witness_name → witness_name
- witness_aadhaar → witness_aadhaar
- witness_address → witness_address
- witness_verified → witness_verified

Bank:
- joint_account_number → joint_account_number
- joint_ifsc → joint_ifsc
- joint_account_bank_name → joint_account_bank_name

Files:
- marriage_certificate → marriage_cert_file
- groom_signature → groom_signature_file
- bride_signature → bride_signature_file
- witness_signature → witness_signature_file
```

---

## Integration Checklist

- [x] Added import in router: `resubmit_corrected_application`
- [x] Added import in service: `from datetime import datetime`
- [x] Function signature matches usage pattern
- [x] Error handling consistent with codebase
- [x] Logging follows project conventions
- [x] JWT verification used
- [x] Database operations follow existing patterns
- [x] File operations use existing utilities
- [x] Event creation matches project style
- [x] Ownership verification implemented
- [x] Status validation implemented
- [x] Partial update support
- [x] Response format matches project style
- [x] Documentation follows project style
- [x] No breaking changes to existing code

---

## Testing Commands

### Setup
```bash
# Get a valid JWT token for a citizen user first
# Set it as environment variable
export JWT_TOKEN="your_token_here"
```

### Test 1: Single Field Update
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "groom_name=John Doe"
```

### Test 2: Multiple Fields + Files
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "groom_age=30" \
  -F "bride_name=Jane Doe" \
  -F "groom_signature=@groom.jpg" \
  -F "bride_signature=@bride.jpg"
```

### Test 3: Error - Wrong Status
```bash
curl -X PUT http://localhost:8000/icm/applications/2 \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "groom_name=Test"
# Should return 400 if application not in "Correction Required" status
```

### Test 4: Error - Not Owner
```bash
curl -X PUT http://localhost:8000/icm/applications/999 \
  -H "Authorization: Bearer $DIFFERENT_USER_TOKEN" \
  -F "groom_name=Test"
# Should return 403 Forbidden
```

---

## Database Schema Reference

The implementation uses existing database tables without modifications:

**Table: icm_applications**
- Columns: All existing columns remain unchanged
- Updates: Data fields and file paths updated only when provided
- No schema changes required

**Table: icm_events**
- New record created for each resubmission
- event_type: "CORRECTION_RESUBMITTED"
- Stores complete event data in JSON format

---

## Performance Considerations

1. **Partial Updates:** Only modified fields sent to database
2. **File Optimization:** Files not re-uploaded if not provided
3. **Query Efficiency:** Single application lookup + single update query
4. **Event Logging:** Async operations don't block response
5. **Error Early:** Validation done before database operations

---

## Security Review

- ✅ JWT authentication required
- ✅ Application ownership verified
- ✅ Status validation (only "Correction Required" allowed)
- ✅ Input validation on all fields
- ✅ File upload validation
- ✅ Audit trail maintained
- ✅ No SQL injection risks (ORM used)
- ✅ No file path traversal risks (controlled file storage)

---

## Rollback Instructions (if needed)

1. Remove endpoint from `app/routers/icm.py` (lines 233-416)
2. Remove import from `app/routers/icm.py`
3. Remove function from `app/services/icm_service.py` (lines 720-874)
4. Remove import from `app/services/icm_service.py`
5. Revert `ICM_API_DOCUMENTATION.md` to previous version
6. Restart application

No database migrations needed (all uses existing tables).

---

**Last Updated:** December 8, 2025  
**Implementation Status:** Complete and Ready for Testing
