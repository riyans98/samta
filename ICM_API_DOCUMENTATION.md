# ICM API Documentation

This document provides comprehensive documentation for the new ICM (Inter-Caste Marriage) API endpoints.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Citizen Endpoints](#citizen-endpoints)
4. [Officer Endpoints](#officer-endpoints)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Workflow States](#workflow-states)

---

## Overview

The ICM API manages Inter-Caste Marriage applications from submission through approval and fund disbursement. The system supports:

- **Citizens**: Submit and track applications
- **Officers (ADM, TO, DM, SNO, PFMS)**: Review and approve applications
- **Complete Audit Trail**: All actions tracked in timeline
- **Multi-Stage Workflow**: Applications progress through defined stages

**Base URL:** `/icm`

---

## Authentication

All ICM endpoints require JWT authentication via `Authorization` header:

```
Authorization: Bearer <JWT_TOKEN>
```

**Token Claims Required:**
- `sub` - Login ID
- `role` - User role (citizen, Tribal Officer, etc.)
- `citizen_id` - Citizen ID (for citizens)
- `aadhaar_number` - Aadhaar number
- `state_ut` - State/UT
- `district` - District (optional, for district-level officers)

---

## Citizen Endpoints

### 1. Submit ICM Application

**Endpoint:** `POST /icm/applications`

**Description:** Submit a new Inter-Caste Marriage application. Automatically assigns to ADM for initial review.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "groom_name": "Rajesh Kumar",
  "groom_age": 28,
  "groom_father_name": "Ram Kumar",
  "groom_dob": "1996-05-15",
  "groom_aadhaar": 123456789012,
  "groom_caste_cert_id": "CERT-001",
  
  "bride_name": "Priya Singh",
  "bride_age": 26,
  "bride_father_name": "Singh Sahab",
  "bride_dob": "1998-07-20",
  "bride_aadhaar": 987654321098,
  "bride_caste_cert_id": "CERT-002",
  
  "marriage_date": "2025-02-14",
  "joint_account_number": "1234567890123456",
  "joint_ifsc": "SBIN0001234"
}
```

**Response (201 Created):**
```json
{
  "icm_id": 1,
  "status": "created",
  "current_stage": 0,
  "pending_at": "ADM",
  "message": "ICM application created successfully"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid JWT or missing citizen_id
- `500 Internal Server Error` - Database error

**Timeline Event Created:** `APPLICATION_CREATED`

---

### 2. Get Citizen's Applications

**Endpoint:** `GET /icm/applications`

**Description:** Retrieve all applications submitted by the authenticated citizen.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Query Parameters:** None

**Response (200 OK):**
```json
[
  {
    "icm_id": 1,
    "citizen_id": 10,
    "applicant_aadhaar": 123456789012,
    "groom_name": "Rajesh Kumar",
    "bride_name": "Priya Singh",
    "marriage_date": "2025-02-14",
    "current_stage": 1,
    "pending_at": "TO",
    "application_status": "Under Review",
    "state_ut": "Delhi",
    "district": "Delhi",
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-16T14:45:00"
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid JWT or missing citizen_id

---

### 3. Get Application Details

**Endpoint:** `GET /icm/applications/{icm_id}`

**Description:** Get complete details of a specific application including timeline.

**Path Parameters:**
- `icm_id` (integer, required) - Application ID

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**
```json
{
  "application": {
    "icm_id": 1,
    "citizen_id": 10,
    "groom_name": "Rajesh Kumar",
    "bride_name": "Priya Singh",
    "marriage_date": "2025-02-14",
    "current_stage": 1,
    "pending_at": "TO",
    "application_status": "Under Review",
    "joint_account_number": "1234567890123456",
    "state_ut": "Delhi",
    "district": "Delhi"
  },
  "timeline": [
    {
      "event_id": 1,
      "icm_id": 1,
      "event_type": "APPLICATION_CREATED",
      "event_role": "CITIZEN",
      "event_stage": 0,
      "comment": "Application created",
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid JWT
- `404 Not Found` - Application not found

---

### 4. Get Application Timeline

**Endpoint:** `GET /icm/applications/{icm_id}/timeline`

**Description:** Get complete timeline/events for an application.

**Path Parameters:**
- `icm_id` (integer, required) - Application ID

**Response (200 OK):**
```json
{
  "icm_id": 1,
  "current_stage": 2,
  "status": "Under Review",
  "timeline": [
    {
      "event_id": 1,
      "event_type": "APPLICATION_CREATED",
      "event_role": "CITIZEN",
      "event_stage": 0,
      "comment": "Application created",
      "created_at": "2025-01-15T10:30:00"
    },
    {
      "event_id": 2,
      "event_type": "ADM_APPROVED",
      "event_role": "ADM",
      "event_stage": 0,
      "comment": "Initial review completed",
      "created_at": "2025-01-16T09:15:00"
    }
  ]
}
```

---

### 4. Resubmit Application with Corrections

**Endpoint:** `PUT /icm/applications/{icm_id}`

**Description:** Applicant resubmits a corrected application after receiving correction feedback. Allows updating corrected data and/or documents. Only applications in "Correction Required" status can be resubmitted.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
```

**Request Body (Form Data - Partial Update):**
Only provide fields that need correction. All fields are optional.

```
groom_name: Rajesh Kumar (corrected)
groom_age: 29
bride_name: Priya Singh (corrected)
marriage_date: 2025-03-14
marriage_certificate: <file>
groom_signature: <file>
bride_signature: <file>
```

**Available Fields for Correction:**
- Groom details: `groom_name`, `groom_age`, `groom_father_name`, `groom_dob`, `groom_aadhaar`, `groom_pre_address`, `groom_current_address`, `groom_permanent_address`, `groom_caste_cert_id`, `groom_education`, `groom_training`, `groom_income`, `groom_livelihood`, `groom_future_plan`, `groom_first_marriage`
- Bride details: `bride_name`, `bride_age`, `bride_father_name`, `bride_dob`, `bride_aadhaar`, `bride_pre_address`, `bride_current_address`, `bride_permanent_address`, `bride_caste_cert_id`, `bride_education`, `bride_training`, `bride_income`, `bride_livelihood`, `bride_future_plan`, `bride_first_marriage`
- Marriage details: `marriage_date`, `marriage_certificate_number`, `previous_benefit_taken`
- Witness details: `witness_name`, `witness_aadhaar`, `witness_address`, `witness_verified`
- Bank details: `joint_account_number`, `joint_ifsc`, `joint_account_bank_name`
- Documents: `marriage_certificate`, `groom_signature`, `bride_signature`, `witness_signature`

**Response (200 OK):**
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

**Error Responses:**
- `401 Unauthorized` - Invalid JWT or missing citizen_id
- `403 Forbidden` - Not the application owner, or invalid role
- `404 Not Found` - Application not found
- `400 Bad Request` - Application not in "Correction Required" status
- `500 Internal Server Error` - Database error

**Workflow Changes:**
- Application stage resets to 0 (Submitted)
- Application status changes to "Resubmitted"
- Pending at: "Tribal Officer" (for review)
- New timeline event: `CORRECTION_RESUBMITTED`

**Timeline Event Created:** `CORRECTION_RESUBMITTED`

**Notes:**
- Only the original applicant (citizen) can resubmit corrections
- Application must be in "Correction Required" status
- Partial updates supported - only provide corrected fields
- All file updates are optional
- New files will overwrite previous versions
- New events are created for audit trail

---

## Officer Endpoints

### 1. Approve Application

**Endpoint:** `POST /icm/applications/{icm_id}/approve`

**Description:** Approve an application and move it to the next stage.
````

**Path Parameters:**
- `icm_id` (integer, required) - Application ID

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "comment": "Application meets all eligibility criteria"
}
```

**Response (200 OK):**
```json
{
  "icm_id": 1,
  "previous_stage": 0,
  "new_stage": 1,
  "pending_at": "TO",
  "approved_by": "ADM",
  "message": "Application approved and moved to stage 1"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid JWT or missing role
- `403 Forbidden` - User is not an officer
- `404 Not Found` - Application not found
- `500 Internal Server Error` - Update failed

**Allowed Roles:** ADM, TO, DM, SNO, PFMS, Tribal Officer, District Collector/DM/SJO, State Nodal Officer, PFMS Officer

**Timeline Event Created:** `{ROLE}_APPROVED`

---

### 2. Reject Application

**Endpoint:** `POST /icm/applications/{icm_id}/reject`

**Description:** Reject an application with reason.

**Path Parameters:**
- `icm_id` (integer, required) - Application ID

**Request Body:**
```json
{
  "reason": "Documents incomplete. Please resubmit with all required certificates."
}
```

**Response (200 OK):**
```json
{
  "icm_id": 1,
  "status": "Rejected",
  "reason": "Documents incomplete. Please resubmit with all required certificates.",
  "rejected_by": "TO"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid JWT
- `403 Forbidden` - User is not an officer
- `404 Not Found` - Application not found

**Timeline Event Created:** `APPLICATION_REJECTED`

---

### 3. Request Corrections

**Endpoint:** `POST /icm/applications/{icm_id}/request-correction`

**Description:** Request corrections and send application back to citizen.

**Path Parameters:**
- `icm_id` (integer, required) - Application ID

**Request Body:**
```json
{
  "corrections_required": [
    "Update groom's current address",
    "Provide valid marriage certificate",
    "Verify bank account with passbook copy"
  ],
  "comment": "Please provide the above documents within 7 days"
}
```

**Response (200 OK):**
```json
{
  "icm_id": 1,
  "status": "Correction Required",
  "corrections_required": [
    "Update groom's current address",
    "Provide valid marriage certificate",
    "Verify bank account with passbook copy"
  ],
  "pending_at": "CITIZEN",
  "requested_by": "TO"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid JWT
- `403 Forbidden` - User is not an officer
- `404 Not Found` - Application not found

**Timeline Event Created:** `CORRECTION_REQUESTED`

---

### 4. Get Filtered Applications

**Endpoint:** `GET /icm/applications?state_ut=X&district=Y&pending_at=Z`

**Description:** Get applications filtered by jurisdiction and status (Admin/Officers only).

**Query Parameters:**
- `state_ut` (string, required) - State/UT
- `district` (string, optional) - District name
- `pending_at` (string, optional) - Pending with role (ADM, TO, DM, SNO, PFMS, CITIZEN)

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**
```json
[
  {
    "icm_id": 1,
    "groom_name": "Rajesh Kumar",
    "bride_name": "Priya Singh",
    "current_stage": 1,
    "pending_at": "TO",
    "application_status": "Under Review",
    "state_ut": "Delhi",
    "district": "Delhi"
  },
  {
    "icm_id": 2,
    "groom_name": "Arun Singh",
    "bride_name": "Meera Sharma",
    "current_stage": 2,
    "pending_at": "DM",
    "application_status": "Under Review",
    "state_ut": "Delhi",
    "district": "Delhi"
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid JWT
- `403 Forbidden` - User is not an officer

---

## Data Models

### ICMApplication
```json
{
  "icm_id": 1,
  "citizen_id": 10,
  "applicant_aadhaar": 123456789012,
  
  "groom_name": "string",
  "groom_age": 28,
  "groom_father_name": "string",
  "groom_dob": "date",
  "groom_aadhaar": 123456789012,
  "groom_caste_cert_id": "string",
  "groom_education": "string",
  "groom_income": "string",
  "groom_first_marriage": true,
  
  "bride_name": "string",
  "bride_age": 26,
  "bride_father_name": "string",
  "bride_dob": "date",
  "bride_aadhaar": 987654321098,
  "bride_caste_cert_id": "string",
  "bride_education": "string",
  "bride_income": "string",
  "bride_first_marriage": true,
  
  "marriage_date": "date",
  "marriage_certificate_number": "string",
  
  "joint_account_number": "string",
  "joint_ifsc": "string",
  "joint_account_bank_name": "string",
  
  "current_stage": 0,
  "pending_at": "ADM",
  "application_status": "Pending",
  
  "state_ut": "Delhi",
  "district": "Delhi",
  
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### ICMEvent
```json
{
  "event_id": 1,
  "icm_id": 1,
  "event_type": "APPLICATION_CREATED",
  "event_role": "CITIZEN",
  "event_stage": 0,
  "comment": "Application created",
  "event_data": {
    "actor": "citizen123",
    "comment": "Initial submission"
  },
  "created_at": "datetime"
}
```

---

## Workflow States

### Application Stages
```
Stage 0: Submitted (CITIZEN submits)
    ↓ [ADM reviews]
Stage 1: Tribal Officer Review
    ↓ [TO reviews]
Stage 2: District Magistrate Review
    ↓ [DM reviews]
Stage 3: State Nodal Officer Review
    ↓ [SNO reviews]
Stage 4: PFMS Fund Release
    ↓ [PFMS releases funds]
Stage 5: Completed (Approved/Rejected)
```

### Application Statuses
- `Pending` - Awaiting review
- `Under Review` - Being processed by officer
- `Correction Required` - Sent back to citizen for fixes
- `Approved` - Application approved
- `Rejected` - Application rejected

### Pending At Values
- `ADM` - Administrative review
- `TO` - Tribal Officer review
- `DM` - District Magistrate review
- `SNO` - State Nodal Officer review
- `PFMS` - PFMS fund release
- `CITIZEN` - Waiting for citizen to submit corrections

### Event Types
- `APPLICATION_CREATED` - Initial submission
- `ADM_APPROVED` - ADM approved
- `TO_APPROVED` - TO approved
- `DM_APPROVED` - DM approved
- `SNO_APPROVED` - SNO approved
- `PFMS_APPROVED` - PFMS approved
- `APPLICATION_REJECTED` - Application rejected
- `CORRECTION_REQUESTED` - Corrections requested

---

## Error Handling

All endpoints follow standard HTTP status codes:

| Status Code | Meaning | Common Causes |
|------------|---------|---------------|
| 200 | Success | Request processed successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Database or server error |

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Usage Examples

### Submit Application (Python)
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
data = {
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

response = requests.post(
    "http://localhost:8000/icm/applications",
    headers=headers,
    json=data
)
print(response.json())
```

### Approve Application (cURL)
```bash
curl -X POST "http://localhost:8000/icm/applications/1/approve" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Application meets all criteria"
  }'
```

### Get Applications (Python)
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/icm/applications",
    headers=headers
)
applications = response.json()
for app in applications:
    print(f"Application {app['icm_id']}: {app['groom_name']} & {app['bride_name']}")
```

---

## Notes

1. **Application ID**: Generated automatically when submitted; used for all subsequent operations
2. **Audit Trail**: All actions create events for complete history
3. **Jurisdiction**: Applications filtered by user's state/district
4. **Stage Lock**: Applications can only progress forward, not backward (unless corrections requested)
5. **Event Data**: Stored as JSON for flexible tracking of additional details

---

**Last Updated:** December 5, 2025

