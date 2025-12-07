# Inter-Caste Marriage (ICM) API Documentation

## Overview

The ICM module handles Inter-Caste Marriage incentive scheme applications. It supports a multi-stage approval workflow with role-based access control.

### Grant Amount
- **₹2,50,000** (Rs. Two Lakh Fifty Thousand)

### Roles (5 DB Roles)
| Role | Description |
|------|-------------|
| `Citizen` | Applicant (must be groom OR bride) |
| `Tribal Officer` | First level reviewer |
| `District Collector/DM/SJO` | Second level reviewer (can reject) |
| `State Nodal Officer` | Third level reviewer |
| `PFMS Officer` | Final approver - releases funds |

### Stage Flow
```
Stage 0 → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
(Submit)   (TO)      (DM)      (SNO)    (PFMS)   (Complete)
```

| Stage | Status | Pending At | Action By |
|-------|--------|------------|-----------|
| 0 | Submitted | Tribal Officer | Citizen submits |
| 1 | TO Approved | District Collector/DM/SJO | Tribal Officer approves |
| 2 | DM Approved | State Nodal Officer | DM approves |
| 3 | SNO Approved | PFMS Officer | SNO approves |
| 4 | PFMS Released | Completed | PFMS releases funds |
| 5 | Completed | - | Final state |

### Documents (4 Files)
| Document Type | Key | Required |
|--------------|-----|----------|
| Marriage Certificate | `MARRIAGE` | Yes |
| Groom Signature | `GROOM_SIGN` | Yes |
| Bride Signature | `BRIDE_SIGN` | Yes |
| Witness Signature | `WITNESS_SIGN` | No |

### File Naming Convention
```
ICM{icm_id}_{uploader}_{TYPE}.{ext}
Example: ICM123_citizen_MARRIAGE.pdf
```

---

## API Endpoints

### Base URL
```
/icm
```

### Authentication
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 1. Submit ICM Application

### `POST /icm/applications`

**Description:** Submit a new ICM application with documents. Uses multipart/form-data.

**Access:** Citizens only (applicant must be groom or bride)

**Content-Type:** `multipart/form-data`

#### Form Fields

**Groom Details (Required)**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `groom_name` | string | Yes | Full name of groom |
| `groom_age` | integer | Yes | Age of groom |
| `groom_father_name` | string | Yes | Father's name |
| `groom_dob` | string | Yes | Date of birth (YYYY-MM-DD) |
| `groom_aadhaar` | integer | Yes | 12-digit Aadhaar number |
| `groom_current_address` | string | Yes | Current address |
| `groom_pre_address` | string | No | Previous address |
| `groom_permanent_address` | string | No | Permanent address |
| `groom_caste_cert_id` | string | No | Caste certificate ID |
| `groom_education` | string | No | Education details |
| `groom_training` | string | No | Training details |
| `groom_income` | string | No | Income details |
| `groom_livelihood` | string | No | Livelihood details |
| `groom_future_plan` | string | No | Future plans |
| `groom_first_marriage` | boolean | No | Is this first marriage? (default: true) |

**Bride Details (Required)**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bride_name` | string | Yes | Full name of bride |
| `bride_age` | integer | Yes | Age of bride |
| `bride_father_name` | string | Yes | Father's name |
| `bride_dob` | string | Yes | Date of birth (YYYY-MM-DD) |
| `bride_aadhaar` | integer | Yes | 12-digit Aadhaar number |
| `bride_current_address` | string | Yes | Current address |
| `bride_pre_address` | string | No | Previous address |
| `bride_permanent_address` | string | No | Permanent address |
| `bride_caste_cert_id` | string | No | Caste certificate ID |
| `bride_education` | string | No | Education details |
| `bride_training` | string | No | Training details |
| `bride_income` | string | No | Income details |
| `bride_livelihood` | string | No | Livelihood details |
| `bride_future_plan` | string | No | Future plans |
| `bride_first_marriage` | boolean | No | Is this first marriage? (default: true) |

**Marriage Details**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `marriage_date` | string | Yes | Marriage date (YYYY-MM-DD) |
| `marriage_certificate_number` | string | No | Certificate registration number |
| `previous_benefit_taken` | boolean | No | Already received benefit? (default: false) |

**Witness Details (Simulated OTP)**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `witness_name` | string | No | Witness full name |
| `witness_aadhaar` | integer | No | Witness Aadhaar number |
| `witness_address` | string | No | Witness address |
| `witness_verified` | boolean | No | OTP verified flag (simulated) |

**Bank Details**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `joint_account_number` | string | Yes | Joint bank account number |
| `joint_ifsc` | string | No | Bank IFSC code |
| `joint_account_bank_name` | string | No | Bank name |

#### File Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `marriage_certificate` | File | Yes | Marriage certificate (PDF/Image) |
| `groom_signature` | File | Yes | Groom's signature image |
| `bride_signature` | File | Yes | Bride's signature image |
| `witness_signature` | File | No | Witness signature image |

#### Request Example (JavaScript/Fetch)
```javascript
const formData = new FormData();

// Groom details
formData.append('groom_name', 'Rajesh Kumar');
formData.append('groom_age', 28);
formData.append('groom_father_name', 'Ramesh Kumar');
formData.append('groom_dob', '1996-05-15');
formData.append('groom_aadhaar', 123456789012);
formData.append('groom_current_address', '123 Main St, Delhi');

// Bride details
formData.append('bride_name', 'Priya Sharma');
formData.append('bride_age', 25);
formData.append('bride_father_name', 'Suresh Sharma');
formData.append('bride_dob', '1999-03-20');
formData.append('bride_aadhaar', 987654321098);
formData.append('bride_current_address', '456 Park Ave, Delhi');

// Marriage details
formData.append('marriage_date', '2024-12-01');
formData.append('joint_account_number', '1234567890123456');

// Files
formData.append('marriage_certificate', marriageCertFile);
formData.append('groom_signature', groomSigFile);
formData.append('bride_signature', brideSigFile);

const response = await fetch('/icm/applications', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

#### Success Response (201 Created)
```json
{
  "icm_id": 123,
  "current_stage": 0,
  "pending_at": "Tribal Officer",
  "application_status": "Submitted",
  "message": "ICM application submitted successfully",
  "files_saved": ["MARRIAGE", "GROOM_SIGN", "BRIDE_SIGN"]
}
```

#### Error Responses

**400 Bad Request** - Validation errors
```json
{
  "detail": "Applicant must be either groom or bride"
}
```

**409 Conflict** - Duplicate couple
```json
{
  "detail": "An active application already exists for this couple"
}
```

**401 Unauthorized** - Invalid/missing token
```json
{
  "detail": "Citizen ID missing from token"
}
```

---

## 2. Get Citizen's Applications

### `GET /icm/applications`

**Description:** Get list of ICM applications. Citizens see their own; officers see jurisdiction-filtered list.

**Access:** Citizens & Officers

#### Query Parameters (Officers only)
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `state_ut` | string | No | Filter by state (uses token state if not provided) |
| `district` | string | No | Filter by district |
| `pending_at` | string | No | Filter by pending_at role |

#### Request Example
```javascript
// Citizen - get own applications
const response = await fetch('/icm/applications', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Officer - get applications in jurisdiction
const response = await fetch('/icm/applications?state_ut=Delhi&pending_at=Tribal Officer', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

#### Success Response (200 OK)
```json
[
  {
    "icm_id": 123,
    "groom_name": "Rajesh Kumar",
    "bride_name": "Priya Sharma",
    "marriage_date": "2024-12-01",
    "current_stage": 1,
    "pending_at": "Tribal Officer",
    "application_status": "Under Review",
    "state_ut": "Delhi",
    "district": "Central Delhi",
    "created_at": "2024-12-01T10:30:00"
  }
]
```

---

## 3. Get Application Details

### `GET /icm/applications/{icm_id}`

**Description:** Get full details of a specific ICM application with timeline.

**Access:** Owner citizen or officer in jurisdiction

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `icm_id` | integer | Application ID |

#### Success Response (200 OK)
```json
{
  "application": {
    "icm_id": 123,
    "citizen_id": 456,
    "applicant_aadhaar": 123456789012,
    "groom_name": "Rajesh Kumar",
    "groom_age": 28,
    "groom_father_name": "Ramesh Kumar",
    "groom_dob": "1996-05-15",
    "groom_aadhaar": 123456789012,
    "groom_current_address": "123 Main St, Delhi",
    "bride_name": "Priya Sharma",
    "bride_age": 25,
    "bride_father_name": "Suresh Sharma",
    "bride_dob": "1999-03-20",
    "bride_aadhaar": 987654321098,
    "bride_current_address": "456 Park Ave, Delhi",
    "marriage_date": "2024-12-01",
    "joint_account_number": "1234567890123456",
    "current_stage": 1,
    "pending_at": "Tribal Officer",
    "application_status": "Under Review",
    "state_ut": "Delhi",
    "district": "Central Delhi",
    "created_at": "2024-12-01T10:30:00",
    "updated_at": "2024-12-02T14:00:00"
  },
  "timeline": [
    {
      "event_id": 1,
      "icm_id": 123,
      "event_type": "APPLICATION_SUBMITTED",
      "event_role": "Citizen",
      "event_stage": 0,
      "comment": null,
      "event_data": {"files": ["MARRIAGE", "GROOM_SIGN", "BRIDE_SIGN"]},
      "created_at": "2024-12-01T10:30:00"
    },
    {
      "event_id": 2,
      "icm_id": 123,
      "event_type": "ADM_APPROVED",
      "event_role": "ADM",
      "event_stage": 1,
      "comment": "Documents verified",
      "event_data": null,
      "created_at": "2024-12-02T14:00:00"
    }
  ]
}
```

#### Error Response (404 Not Found)
```json
{
  "detail": "ICM Application #123 not found"
}
```

#### Error Response (403 Forbidden)
```json
{
  "detail": "Access denied: jurisdiction mismatch"
}
```

---

## 4. Get Application Timeline

### `GET /icm/applications/{icm_id}/timeline`

**Description:** Get only the timeline/events for an application (sorted chronologically - oldest first).

**Access:** Owner citizen or officer in jurisdiction

#### Success Response (200 OK)
```json
{
  "icm_id": 123,
  "current_stage": 2,
  "status": "Under Review",
  "timeline": [
    {
      "event_id": 1,
      "icm_id": 123,
      "event_type": "APPLICATION_SUBMITTED",
      "event_role": "Citizen",
      "event_stage": 0,
      "comment": null,
      "event_data": null,
      "created_at": "2024-12-01T10:30:00"
    },
    {
      "event_id": 2,
      "icm_id": 123,
      "event_type": "ADM_APPROVED",
      "event_role": "ADM",
      "event_stage": 1,
      "comment": "Verified",
      "event_data": null,
      "created_at": "2024-12-02T14:00:00"
    }
  ]
}
```

---

## 5. Get Application Documents

### `GET /icm/applications/{icm_id}/documents`

**Description:** Get all documents for an application with base64 encoding.

**Access:** Owner citizen or officer in jurisdiction

#### Success Response (200 OK)
```json
{
  "icm_id": 123,
  "documents": {
    "MARRIAGE": [
      {
        "filename": "ICM123_citizen_MARRIAGE.pdf",
        "file_type": "MARRIAGE",
        "content": "JVBERi0xLjQK...(base64 encoded content)",
        "file_size": 125000,
        "mime_type": "application/pdf"
      }
    ],
    "GROOM_SIGN": [
      {
        "filename": "ICM123_citizen_GROOM_SIGN.png",
        "file_type": "GROOM_SIGN",
        "content": "iVBORw0KGgo...(base64 encoded content)",
        "file_size": 15000,
        "mime_type": "image/png"
      }
    ],
    "BRIDE_SIGN": [
      {
        "filename": "ICM123_citizen_BRIDE_SIGN.png",
        "file_type": "BRIDE_SIGN",
        "content": "iVBORw0KGgo...(base64 encoded content)",
        "file_size": 14500,
        "mime_type": "image/png"
      }
    ],
    "WITNESS_SIGN": []
  }
}
```

---

## 6. Get Declaration HTML (Printable)

### `GET /icm/{icm_id}/declaration`

**Description:** Get a printable HTML declaration form. Browser can print via Ctrl+P.

**Access:** Owner citizen or officer in jurisdiction

**Response Type:** `text/html`

#### Response Headers
```
Content-Type: text/html
Content-Disposition: inline; filename="declaration_icm_123.html"
```

#### Response
Returns a fully rendered HTML page with:
- Application details (groom, bride, marriage info)
- Declaration text with legal statements
- Signature blocks for groom, bride, and witness
- Print-friendly CSS
- "Print Declaration" button (hidden when printing)

---

## 7. Approve Application

### `POST /icm/applications/{icm_id}/approve`

**Description:** Approve an ICM application and move to next stage.

**Access:** Officers only (Tribal Officer, DM, SNO, PFMS)

> **Note:** This endpoint handles approvals for stages 0-3. For final PFMS fund release, use `/pfms/release` endpoint instead.

#### Stage Transitions on Approval
| Current Stage | Role | Next Stage | Next Pending At |
|---------------|------|------------|-----------------|
| 0 | Tribal Officer | 1 | District Collector/DM/SJO |
| 1 | District Collector/DM/SJO | 2 | State Nodal Officer |
| 2 | State Nodal Officer | 3 | PFMS Officer |

#### Request Body
```json
{
  "comment": "Documents verified, all in order"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `comment` | string | No | Approval comment |

#### Success Response (200 OK)
```json
{
  "icm_id": 123,
  "current_stage": 2,
  "pending_at": "District Collector/DM/SJO",
  "application_status": "Under Review",
  "message": "Application approved successfully",
  "event_type": "TO_APPROVED"
}
```

#### Error Responses

**403 Forbidden** - Wrong role or jurisdiction
```json
{
  "detail": "Only officers can approve applications"
}
```
```json
{
  "detail": "Access denied: jurisdiction mismatch"
}
```

**400 Bad Request** - Wrong stage for role
```json
{
  "detail": "Cannot approve: application is at stage 2, but your role (Tribal Officer) can only act at stage 0"
}
```

---

## 8. Reject Application

### `POST /icm/applications/{icm_id}/reject`

**Description:** Reject an ICM application. Sets status to "Rejected".

**Access:** All officers (typically DM)

#### Request Body
```json
{
  "reason": "Documents found to be fraudulent"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | string | Yes | Rejection reason |

#### Success Response (200 OK)
```json
{
  "icm_id": 123,
  "application_status": "Rejected",
  "pending_at": null,
  "message": "Application rejected",
  "event_type": "DM_REJECTED"
}
```

---

## 9. Request Correction

### `POST /icm/applications/{icm_id}/request-correction`

**Description:** Request corrections from applicant. Resets application to stage 0.

**Access:** All officers

#### Request Body
```json
{
  "corrections_required": [
    "Marriage certificate unclear - upload higher resolution",
    "Groom signature does not match Aadhaar records"
  ],
  "comment": "Please correct and resubmit"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `corrections_required` | array[string] | Yes | List of corrections needed |
| `comment` | string | No | Additional comment |

#### Success Response (200 OK)
```json
{
  "icm_id": 123,
  "current_stage": 0,
  "pending_at": "Citizen",
  "application_status": "Correction Required",
  "message": "Correction requested",
  "event_type": "TO_CORRECTION",
  "corrections_required": [
    "Marriage certificate unclear - upload higher resolution",
    "Groom signature does not match Aadhaar records"
  ]
}
```

---

## 10. PFMS Fund Release

### `POST /icm/applications/{icm_id}/pfms/release`

**Description:** Release funds and complete the application. Final step in workflow.

**Access:** PFMS Officer only

**Requirements:**
- Application must be at stage 3 (pending PFMS)
- Amount should be ₹2,50,000 (configurable)

#### Request Body
```json
{
  "amount": 250000,
  "txn_id": "PFMS20241205123456",
  "bank_ref": "REF123456789"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | integer | Yes | Amount released (typically 250000) |
| `txn_id` | string | Yes | PFMS transaction ID |
| `bank_ref` | string | No | Bank reference number |

#### Success Response (200 OK)
```json
{
  "icm_id": 123,
  "current_stage": 5,
  "pending_at": "Completed",
  "application_status": "Completed",
  "message": "Funds released successfully",
  "event_type": "PFMS_FUND_RELEASED",
  "fund_details": {
    "amount": 250000,
    "txn_id": "PFMS20241205123456",
    "bank_ref": "REF123456789"
  }
}
```

#### Error Responses

**403 Forbidden** - Not PFMS officer
```json
{
  "detail": "Only PFMS Officer can release funds"
}
```

**400 Bad Request** - Wrong stage
```json
{
  "detail": "Cannot release funds: application must be at stage 3 (pending PFMS)"
}
```

---

## Event Types Reference

| Event Type | Role | Description |
|------------|------|-------------|
| `APPLICATION_SUBMITTED` | Citizen | Initial submission |
| `TO_APPROVED` | Tribal Officer | TO approval |
| `TO_CORRECTION` | Tribal Officer | TO requested correction |
| `DM_APPROVED` | District Collector/DM/SJO | DM approval |
| `DM_REJECTED` | District Collector/DM/SJO | DM rejection |
| `DM_CORRECTION` | District Collector/DM/SJO | DM requested correction |
| `SNO_APPROVED` | State Nodal Officer | SNO approval |
| `SNO_CORRECTION` | State Nodal Officer | SNO requested correction |
| `PFMS_FUND_RELEASED` | PFMS Officer | Funds released |
| `APPLICATION_COMPLETED` | System | Application completed |

---

## Jurisdiction Rules

### District-Level Officers (Tribal Officer, DM)
Must match **both** `state_ut` AND `district` of the application.

### State-Level Officers (SNO, PFMS)
Must match `state_ut` of the application.

### Citizens
Can only access applications where:
- `citizen_id` matches token's citizen_id, OR
- `applicant_aadhaar` matches token's aadhaar (if citizen is groom or bride)

---

## Error Codes Summary

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created (new application) |
| 400 | Bad Request - validation error |
| 401 | Unauthorized - invalid/missing token |
| 403 | Forbidden - jurisdiction/role mismatch |
| 404 | Not Found - application doesn't exist |
| 409 | Conflict - duplicate couple application |
| 500 | Server Error |

---

## Frontend Implementation Notes

### 1. Application Form
- Use `multipart/form-data` for submission
- All 3 signature files + marriage certificate are required
- Date fields should be in `YYYY-MM-DD` format
- Aadhaar fields expect 12-digit integers

### 2. Document Display
- Use base64 content for image previews: `<img src="data:${mime_type};base64,${content}" />`
- For PDFs, use: `<embed src="data:application/pdf;base64,${content}" type="application/pdf" />`

### 3. Timeline Display
- Events are sorted **ascending** (oldest first)
- Show event_type, event_role, comment, and created_at
- Use event_data for additional context (e.g., fund details, corrections list)

### 4. Role-Based UI
- Citizens: Show submit form, their applications, resubmit for corrections
- Officers: Show applications in their jurisdiction, approve/reject/correction buttons based on stage

### 5. Status Indicators
| Status | Color Suggestion |
|--------|------------------|
| Submitted | Blue |
| Under Review | Yellow/Orange |
| Correction Required | Orange |
| Rejected | Red |
| Completed | Green |

### 6. Witness OTP (Simulated)
- Show OTP verification UI
- Set `witness_verified: true` when "verified"
- Backend accepts but doesn't validate OTP (prototype mode)
