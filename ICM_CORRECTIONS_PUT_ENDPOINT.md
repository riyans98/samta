# ICM Application Corrections PUT Endpoint

## Overview

A new PUT endpoint has been implemented to allow applicants (citizens) to resubmit their ICM applications with corrections after receiving feedback from officers requesting changes.

## Endpoint Details

### Route
```
PUT /icm/applications/{icm_id}
```

### Purpose
Allow applicants to resubmit corrected ICM applications when they are in "Correction Required" status.

### Access Control
- **Allowed Roles:** Citizens only
- **Applicant Ownership:** Only the original application owner (citizen_id) can resubmit corrections
- **Status Requirement:** Application must be in "Correction Required" status

## Request Format

### Content-Type
```
multipart/form-data
```

### Parameters (All Optional - Partial Updates Supported)

#### Groom Details (optional)
- `groom_name`: string
- `groom_age`: integer
- `groom_father_name`: string
- `groom_dob`: string (YYYY-MM-DD)
- `groom_aadhaar`: integer
- `groom_pre_address`: string
- `groom_current_address`: string
- `groom_permanent_address`: string
- `groom_caste_cert_id`: string
- `groom_education`: string
- `groom_training`: string
- `groom_income`: string
- `groom_livelihood`: string
- `groom_future_plan`: string
- `groom_first_marriage`: boolean

#### Bride Details (optional)
- `bride_name`: string
- `bride_age`: integer
- `bride_father_name`: string
- `bride_dob`: string (YYYY-MM-DD)
- `bride_aadhaar`: integer
- `bride_pre_address`: string
- `bride_current_address`: string
- `bride_permanent_address`: string
- `bride_caste_cert_id`: string
- `bride_education`: string
- `bride_training`: string
- `bride_income`: string
- `bride_livelihood`: string
- `bride_future_plan`: string
- `bride_first_marriage`: boolean

#### Marriage Details (optional)
- `marriage_date`: string (YYYY-MM-DD)
- `marriage_certificate_number`: string
- `previous_benefit_taken`: boolean

#### Witness Details (optional)
- `witness_name`: string
- `witness_aadhaar`: integer
- `witness_address`: string
- `witness_verified`: boolean

#### Bank Details (optional)
- `joint_account_number`: string
- `joint_ifsc`: string
- `joint_account_bank_name`: string

#### Document Files (optional)
- `marriage_certificate`: file (MARRIAGE)
- `groom_signature`: file (GROOM_SIGN)
- `bride_signature`: file (BRIDE_SIGN)
- `witness_signature`: file (WITNESS_SIGN)

## Response Format

### Success Response (HTTP 200 OK)

```json
{
  "icm_id": 1,
  "status": "resubmitted",
  "message": "Corrected application resubmitted successfully",
  "current_stage": 0,
  "pending_at": "Tribal Officer",
  "application_status": "Resubmitted",
  "files_updated": ["marriage_certificate_file", "groom_signature_file"],
  "data_fields_updated": ["groom_name", "groom_age", "marriage_date"]
}
```

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Citizen ID missing from token"
}
```

#### 403 Forbidden
```json
{
  "detail": "You can only resubmit your own applications"
}
```

#### 404 Not Found
```json
{
  "detail": "ICM Application #123 not found"
}
```

#### 400 Bad Request
```json
{
  "detail": "Application must be in 'Correction Required' status. Current status: Pending"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Failed to resubmit corrected application: [error details]"
}
```

## Workflow Impact

### Before Resubmission
- **Current Stage:** Variable (1, 2, or 3)
- **Application Status:** "Correction Required"
- **Pending At:** "Citizen"

### After Resubmission
- **Current Stage:** 0 (Submitted)
- **Application Status:** "Resubmitted"
- **Pending At:** "Tribal Officer"

### Timeline Event
- **Event Type:** `CORRECTION_RESUBMITTED`
- **Event Role:** `Citizen`
- **Includes:** 
  - List of updated files
  - List of updated data fields
  - Previous stage information

## Key Features

1. **Partial Updates:** Only corrected fields need to be provided
2. **File Replacement:** New files replace previous versions
3. **Audit Trail:** All resubmissions tracked in application timeline
4. **Validation:** 
   - Application must exist
   - Applicant must be owner
   - Status must be "Correction Required"
5. **Workflow Reset:** Application returns to stage 0 for fresh review

## Implementation Details

### Service Function
**Location:** `app/services/icm_service.py`
**Function:** `resubmit_corrected_application()`

```python
async def resubmit_corrected_application(
    icm_id: int,
    application_data: Dict[str, Any],
    files: Dict[str, Optional[UploadFile]],
    token_payload: Dict[str, Any]
) -> Dict[str, Any]:
```

### Router Endpoint
**Location:** `app/routers/icm.py`
**Function:** `resubmit_application_with_corrections()`

### Database Operations
- Updates application data with corrected values
- Saves new/updated files
- Creates audit event in timeline
- Updates application status and stage

## Testing Scenarios

### Scenario 1: Correcting Groom's Name and Age
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -F "groom_name=Raj Kumar" \
  -F "groom_age=30"
```

### Scenario 2: Resubmitting with New Documents
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -F "marriage_date=2025-03-15" \
  -F "marriage_certificate=@/path/to/marriage_cert.pdf" \
  -F "groom_signature=@/path/to/groom_sign.jpg"
```

### Scenario 3: Multiple Field Corrections
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -F "bride_name=Priya" \
  -F "bride_age=27" \
  -F "joint_account_number=1234567890" \
  -F "joint_ifsc=SBIN0001234" \
  -F "bride_signature=@/path/to/bride_sign.jpg"
```

## Error Handling

The endpoint includes comprehensive error handling:

1. **JWT Validation:** Checks token validity and extracts citizen_id
2. **Application Lookup:** Validates application exists
3. **Ownership Check:** Ensures only owner can resubmit
4. **Status Check:** Verifies application is in "Correction Required" status
5. **Update Operations:** Handles database update errors
6. **File Operations:** Manages file upload and storage errors

## Security Considerations

1. **JWT Required:** All requests require valid JWT authentication
2. **Ownership Verification:** Only application owner can resubmit
3. **Status Validation:** Application must be in correct status
4. **Audit Logging:** All resubmissions logged with user and timestamp
5. **File Validation:** Files validated during upload process

## Related Endpoints

- **POST `/icm/applications`** - Initial application submission
- **POST `/icm/applications/{icm_id}/request-correction`** - Officer requests corrections
- **GET `/icm/applications/{icm_id}`** - View application details and timeline
- **POST `/icm/applications/{icm_id}/approve`** - Officer approves application
- **POST `/icm/applications/{icm_id}/reject`** - Officer rejects application

## Integration Notes

- Import added: `resubmit_corrected_application` in `app/routers/icm.py`
- New service function in `app/services/icm_service.py`
- Follows existing code patterns and error handling
- Compatible with existing database schema
- Uses existing file storage mechanisms

## Future Enhancements

Potential improvements for future versions:
1. Add email notifications when corrections are resubmitted
2. Track correction history (show what was corrected)
3. Add optional comment field for applicant to explain corrections
4. Implement deadline tracking for corrections
5. Add bulk correction capability for multiple applications
