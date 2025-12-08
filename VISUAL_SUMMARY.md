# ICM PUT Endpoint - Visual Summary

## Endpoint Overview

```
┌────────────────────────────────────────────────────────────────┐
│                   PUT Endpoint Summary                         │
├────────────────────────────────────────────────────────────────┤
│ HTTP Method:  PUT                                              │
│ Route:        /icm/applications/{icm_id}                       │
│ Content-Type: multipart/form-data                              │
│ Auth:         JWT Bearer Token                                 │
│ Access:       Citizen (Application Owner Only)                 │
│ Status Req:   "Correction Required"                            │
└────────────────────────────────────────────────────────────────┘
```

## Request Structure

```
PUT /icm/applications/1

┌─────────────────────────────────────┐
│ Headers                             │
├─────────────────────────────────────┤
│ Authorization: Bearer <JWT_TOKEN>   │
│ Content-Type: multipart/form-data   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Form Data (All Optional)            │
├─────────────────────────────────────┤
│ • Groom Details (15 fields)         │
│ • Bride Details (15 fields)         │
│ • Marriage Details (3 fields)       │
│ • Witness Details (4 fields)        │
│ • Bank Details (3 fields)           │
│ • Document Files (4 files)          │
└─────────────────────────────────────┘
```

## Response Structure

```
HTTP 200 OK

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

## Application State Transition

```
Before Correction Request:
┌─────────────────────────┐
│ Status: "Under Review"  │
│ Stage: 1, 2, or 3       │
│ Pending At: Officer     │
└─────────────────────────┘
         ↓ (Officer requests corrections)
         
After Correction Request:
┌──────────────────────────────┐
│ Status: "Correction Required"│
│ Stage: 0 (reset)            │
│ Pending At: "Citizen"        │
└──────────────────────────────┘
         ↓ (Citizen resubmits with PUT)
         
After Resubmission:
┌──────────────────────────┐
│ Status: "Resubmitted"    │
│ Stage: 0                 │
│ Pending At: "TO"         │
│ Event: CORRECTION_RESUBMITTED │
└──────────────────────────┘
         ↓ (Officer reviews again)
         
Back to Review:
┌─────────────────────────┐
│ Status: "Under Review"  │
│ Stage: 1+ (continues)   │
│ Pending At: Officer     │
└─────────────────────────┘
```

## Data Flow

```
┌─────────────────────────────────────┐
│  Citizen Submits PUT Request        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  JWT Token Validation               │
│  - Extract citizen_id               │
│  - Verify signature                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Application Lookup                 │
│  - Fetch by icm_id                  │
│  - Check if exists                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Ownership Verification             │
│  - Compare citizen_id with app owner│
│  - Return 403 if not owner          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Status Validation                  │
│  - Check status = "Correction Req"  │
│  - Return 400 if wrong status       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Prepare Corrected Data             │
│  - Filter non-None values only      │
│  - Build update payload             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Update Application Data            │
│  - Update corrected fields          │
│  - Reset stage to 0                 │
│  - Update status to "Resubmitted"   │
│  - Set pending_at to "Tribal Off."  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Process File Uploads               │
│  - Save new files to storage        │
│  - Update file paths in app         │
│  - Replace old files               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Create Audit Event                 │
│  - Type: CORRECTION_RESUBMITTED     │
│  - Record files updated             │
│  - Record fields updated            │
│  - Record timestamp                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Return Success Response            │
│  - HTTP 200 OK                      │
│  - Include update details           │
└─────────────────────────────────────┘
```

## Error Handling Tree

```
        ┌─── PUT Request ───┐
        │                   │
     JWT Token Valid?       NO → 401 Unauthorized
        │ YES
        │
  citizen_id Present?       NO → 401 Unauthorized
        │ YES
        │
  Application Exists?       NO → 404 Not Found
        │ YES
        │
  Is Application Owner?     NO → 403 Forbidden
        │ YES
        │
  Status = "Correction Req"? NO → 400 Bad Request
        │ YES
        │
  File Upload Valid?        NO → 500 Internal Server Error
        │ YES
        │
  Database Update OK?       NO → 500 Internal Server Error
        │ YES
        │
   ✓ 200 Success Response
```

## File Fields Reference

```
Document Type       Form Field Name         Database Column
─────────────────────────────────────────────────────────
Marriage Cert       marriage_certificate    marriage_certificate_file
Groom Signature     groom_signature         groom_signature_file
Bride Signature     bride_signature         bride_signature_file
Witness Signature   witness_signature       witness_signature_file
```

## Partial Update Examples

```
Example 1: Update Single Field
┌─────────────────────┐
│ Form Data:          │
│ groom_name = "John" │
└─────────────────────┘
Result: Only groom_name updated, all other fields unchanged

Example 2: Update Multiple Fields
┌──────────────────────┐
│ Form Data:           │
│ groom_age = 30       │
│ bride_name = "Jane"  │
│ marriage_date = date │
└──────────────────────┘
Result: 3 fields updated, others unchanged

Example 3: Update with Files
┌──────────────────────────┐
│ Form Data:               │
│ groom_age = 30           │
│ groom_signature = [file] │
│ bride_signature = [file] │
└──────────────────────────┘
Result: Data + files updated, other fields unchanged

Example 4: Update Only Files
┌──────────────────────────┐
│ Form Data:               │
│ marriage_certificate = [file] │
│ witness_signature = [file]    │
└──────────────────────────┘
Result: Only files updated, data fields unchanged
```

## Timeline Event Structure

```
┌────────────────────────────────────────────┐
│ Event Type: CORRECTION_RESUBMITTED         │
├────────────────────────────────────────────┤
│ event_id: auto-generated                   │
│ icm_id: 1                                  │
│ event_type: "CORRECTION_RESUBMITTED"       │
│ event_role: "Citizen"                      │
│ event_stage: 0                             │
│ comment: "Corrected application..."        │
│                                            │
│ event_data:                                │
│ {                                          │
│   "action": "resubmitted_corrections",     │
│   "applicant_aadhaar": 123456789012,       │
│   "previous_stage": 2,                     │
│   "files_updated": [                       │
│     "groom_signature_file",                │
│     "bride_signature_file"                 │
│   ],                                       │
│   "data_fields_updated": [                 │
│     "groom_name",                          │
│     "groom_age",                           │
│     "marriage_date"                        │
│   ]                                        │
│ }                                          │
│                                            │
│ created_at: "2025-01-16T14:30:00"          │
└────────────────────────────────────────────┘
```

## Validation Rules

```
┌─────────────────────────────────────────────────┐
│ Validation Rule                    Consequence  │
├─────────────────────────────────────────────────┤
│ JWT token required                 401          │
│ citizen_id in token               401          │
│ Application must exist            404          │
│ Must be application owner         403          │
│ Status must be "Correction Req"   400          │
│ File uploads must be valid        500          │
│ Database operations must succeed  500          │
│ All fields optional (no false req) 200         │
│ Partial updates supported         200         │
└─────────────────────────────────────────────────┘
```

## HTTP Status Codes

```
200 OK
    ✓ Corrections resubmitted successfully
    ✓ All validations passed
    ✓ Data and files updated
    ✓ Audit event created

400 Bad Request
    ✗ Application not in "Correction Required" status
    ✗ Invalid date format
    ✗ Invalid field values

401 Unauthorized
    ✗ JWT token invalid or expired
    ✗ citizen_id missing from token
    ✗ No authentication provided

403 Forbidden
    ✗ Not the application owner
    ✗ User role not permitted

404 Not Found
    ✗ Application doesn't exist
    ✗ Application ID invalid

500 Internal Server Error
    ✗ Database error during update
    ✗ File upload error
    ✗ File storage error
    ✗ Unexpected server error
```

## Feature Comparison: POST vs PUT

```
Aspect              POST Submit         PUT Corrections
────────────────────────────────────────────────
Endpoint            /icm/applications   /icm/applications/{id}
Purpose             New application     Update with corrections
Required Fields     All required        All optional
Partial Update      Not supported       Supported
File Requirement    All required        All optional
Stage Reset         No (starts at 0)    Yes (resets to 0)
Status Change       Pending             Resubmitted
Duplicate Check     Yes                 No
Aadhaar Validation  Yes                 No
Applicant Check     Yes                 Yes
Ownership Check     Not needed          Required
Event Type          APPLICATION_SUBMITTED  CORRECTION_RESUBMITTED
```

## Integration Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Router Layer                          │
├──────────────────────────────────────────────────────────┤
│  PUT /icm/applications/{icm_id}                          │
│  ├─ Extract parameters from request                      │
│  ├─ Validate JWT                                         │
│  ├─ Filter non-None fields                              │
│  └─ Call service layer                                   │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│                    Service Layer                         │
├──────────────────────────────────────────────────────────┤
│  resubmit_corrected_application()                        │
│  ├─ Lookup application                                   │
│  ├─ Verify ownership                                     │
│  ├─ Validate status                                      │
│  ├─ Update data                                          │
│  ├─ Save files                                           │
│  └─ Create event                                         │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│                    Data Layer                            │
├──────────────────────────────────────────────────────────┤
│  Database Tables:                                        │
│  ├─ icm_applications (update data & file paths)          │
│  ├─ icm_events (insert new event)                        │
│  └─ File storage (save/update files)                     │
└──────────────────────────────────────────────────────────┘
```

---

**Visual Summary Complete**  
Ready for implementation and testing!
