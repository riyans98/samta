# 📡 DBT Backend API Endpoints Documentation

**Latest Updates** (December 3, 2025):
- ✅ UPSERT pattern implemented in `/submit_fir` - prevents duplicate rows
- ✅ Event deduplication - prevents duplicate FIR_SUBMITTED events
- ✅ New response field: `is_update` indicates if case was created or updated
- ✅ Idempotent behavior - safe retries without errors
- ✅ Added login endpoint documentation

This document lists all available API endpoints for the SIH DBT Workflow System backend.

**Base URL (DBT Endpoints)**: `/dbt/case`
**Base URL (Auth Endpoints)**: `/` (root)

---

## Authentication

All endpoints (except those explicitly marked) require **JWT Bearer token** authentication.

**Header Format**:
```
Authorization: Bearer <JWT_TOKEN>
```

JWT token is obtained from the `/login` endpoint (in auth router).

### JWT Token Payload
The JWT token now includes jurisdiction fields for access control:
```json
{
  "sub": "officer_login_id",
  "role": "District Collector/DM/SJO",
  "state_ut": "Madhya Pradesh",
  "district": "Jabalpur",         // Only for district-level officers
  "vishesh_p_s_name": "PS Jabalpur" // Only for Investigation Officers
}
```

---

## Jurisdiction-Based Access Control

Officers can **only view and act on cases within their assigned jurisdiction**.

| Role | Access Scope | Rule |
|------|--------------|------|
| **Investigation Officer** | Police Station | `case.Vishesh_P_S_Name == user.vishesh_p_s_name` |
| **Tribal Officer** | District | `case.District == user.district AND case.State_UT == user.state_ut` |
| **District Magistrate** | District | `case.District == user.district AND case.State_UT == user.state_ut` |
| **State Nodal Officer** | State | `case.State_UT == user.state_ut` |
| **PFMS Officer** | State + Stage | `case.State_UT == user.state_ut AND case.Stage ∈ {4, 6, 7}` |

**Error Response (403 Forbidden)**:
```json
{
  "detail": "Access denied: Case is in Bhopal, Madhya Pradesh, but you are assigned to Jabalpur, Madhya Pradesh"
}
```

---

## 1. Case Submission & Retrieval (Pre-existing)

### 1.1 Submit FIR Form (with UPSERT Pattern)
**Endpoint**: `POST /submit_fir`

**Authentication**: Required (JWT)

**Description**: Investigation Officer submits a new FIR or updates existing draft. Uses UPSERT pattern:
- If FIR doesn't exist → Creates new case (INSERT)
- If FIR exists → Updates existing case (UPDATE) - prevents duplicate rows

**Query Parameters**:
- `isDrafted` (boolean, default=false) — If true, case stays at Stage 0 (IO draft); if false, moves to Stage 1 (Tribal Officer)

**Form Data (multipart/form-data)**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `firNumber` | string | ✅ | FIR number (e.g., FIR-2025-001) |
| `caste` | string | ✅ | Victim's caste |
| `aadhaar` | string | ✅ | Victim's Aadhaar number |
| `email` | string | ❌ | Applicant's email |
| `photo` | file | ✅ | Victim's photograph (PDF/JPG/PNG) |
| `casteCertificate` | file | ✅ | Caste certificate (PDF/JPG/PNG) |
| `medicalCertificate` | file | ❌ | Medical report (PDF/JPG/PNG) |
| `postmortem` | file | ❌ | Postmortem report (PDF/JPG/PNG) |
| `accountNumber` | string | ✅ | Victim's bank account number |
| `ifscCode` | string | ❌ | Bank IFSC code |
| `holderName` | string | ❌ | Bank account holder name |
| `bankName` | string | ✅ | Bank name |
| `firDocument` | file | ✅ | FIR document (PDF/JPG/PNG) |

**Response** (201 Created - New Case):
```json
{
  "case_no": 5,
  "fir_no": "FIR-2025-001",
  "stage": 1,
  "pending_at": "Tribal Officer",
  "is_drafted": false,
  "is_update": false,
  "message": "FIR saved as submitted successfully. Case #5 created."
}
```

**Response** (201 Created - Existing Case Updated):
```json
{
  "case_no": 5,
  "fir_no": "FIR-2025-001",
  "stage": 1,
  "pending_at": "Tribal Officer",
  "is_drafted": false,
  "is_update": true,
  "message": "FIR saved as submitted successfully. Case #5 updated."
}
```

**Response Fields**:
- `case_no` — Case number (same if update, new if create)
- `fir_no` — FIR number
- `stage` — Current workflow stage (0 for draft, 1 for submit)
- `pending_at` — Who the case is pending with
- `is_drafted` — Whether case is still a draft
- `is_update` — **NEW**: true if existing case was updated, false if new case created
- `message` — Status message

**UPSERT Behavior**:
- **First submission**: Creates new row (is_update=false)
- **Re-submission with same FIR**: Updates existing row (is_update=true), prevents duplicates
- **Same request on retry**: Idempotent - same result both times, no error
- **Event deduplication**: FIR_SUBMITTED event only inserted once, even if submitted multiple times

**Error Responses**:
- `400` — Validation error or invalid file type
- `401` — Missing or invalid JWT token
- `403` — Jurisdiction violation (IO not assigned to this police station)
- `404` — Aadhaar or FIR data not found
- `500` — Database or server error

---

### 1.2 Get All Cases
**Endpoint**: `GET /get-fir-form-data`

**Authentication**: Required (JWT)

**Description**: Retrieve all FIR cases filtered by user's jurisdiction, with optional additional filters.

**Jurisdiction Filtering**: Results are automatically filtered based on the authenticated user's role and assigned location (state, district, or police station).

**Query Parameters**:
- `pending_at` (string, optional) — Filter by who case is pending with (e.g., "Tribal Officer")
- `approved_by` (string, optional) — Filter by who approved it
- `stage` (integer 0-8, optional) — Filter by workflow stage

**Response** (200 OK):
```json
[
  {
    "Case_No": 1,
    "FIR_NO": "FIR-001",
    "Victim_Name": "Anita",
    "Father_Name": "Ram Kumar",
    "Stage": 2,
    "Pending_At": "District Magistrate",
    "Fund_Ammount": "200000",
    "State_UT": "Madhya Pradesh",
    "District": "Jabalpur",
    "Vishesh_P_S_Name": "PS Jabalpur",
    ...
  }
]
```

**Error Responses**:
- `401` — Missing or invalid JWT token
- `500` — Database query error

---

### 1.3 Get Full Case Details with Timeline
**Endpoint**: `GET /get-fir-form-data/fir/{fir_no}`

**Authentication**: Required (JWT)

**Description**: Retrieve complete case record with documents and event timeline. Returns 403 if user lacks jurisdiction access.

**Jurisdiction Check**: User must have jurisdiction access to the case (see Jurisdiction-Based Access Control section).

**Path Parameters**:
- `fir_no` (string) — FIR number (e.g., FIR-2025-001)

**Response** (200 OK):
```json
{
  "data": {
    "Case_No": 5,
    "FIR_NO": "FIR-005",
    "Victim_Name": "Anita",
    "Father_Name": "Kumar",
    "Stage": 3,
    "Pending_At": "State Nodal Officer",
    "Fund_Ammount": "200000",
    "Bank_Name": "State Bank Of India",
    "State_UT": "Madhya Pradesh",
    "District": "Jabalpur",
    "Vishesh_P_S_Name": "PS Jabalpur",
    ...
  },
  "documents": {
    "FIR": [
      {
        "filename": "FIRFIR-005_user123_FIR.pdf",
        "file_type": "FIR",
        "content": "base64_encoded_content...",
        "file_size": 245632,
        "mime_type": "application/pdf"
      }
    ],
    "PHOTO": [...],
    "CASTE": [...],
    "MEDICAL": [...],
    "POSTMORTEM": [...],
    "OTHER": [...]
  },
  "events": [
    {
      "event_id": 1,
      "case_no": 5,
      "performed_by": "IO Sharma",
      "performed_by_role": "Investigation Officer",
      "event_type": "FIR_SUBMITTED",
      "event_data": null,
      "created_at": "2025-01-10T10:30:00"
    }
  ]
}
```

**Error Responses**:
- `404` — FIR not found
- `500` — Database error

---

## Authentication Endpoints

### Login
**Endpoint**: `POST /login`

**Description**: Authenticate user and obtain JWT token with jurisdiction fields.

**Request Body** (JSON):
```json
{
  "login_id": "officer_123",
  "password": "password123",
  "role": "Investigation Officer"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "login_id": "officer_123",
  "role": "Investigation Officer",
  "state_ut": "Jharkhand",
  "district": "Ranchi",
  "vishesh_p_s_name": "Ranchi_PS"
}
```

**Error Responses**:
- `401` — Invalid login ID or password for selected role
- `400` — Invalid role selected
- `500` — Server error

---

## 2. Workflow Actions (New Endpoints)

### 2.1 Approve Case
**Endpoint**: `POST /{case_no}/approve`

**Authentication**: Required (JWT)

**Description**: Approve a case and move it to the next stage.

**Path Parameters**:
- `case_no` (integer) — Case number

**Request Body** (JSON):
```json
{
  "actor": "Officer Singh",
  "role": "District Magistrate",
  "next_stage": 3,
  "comment": "Approved - Amount verified",
  "payload": {
    "optional_key": "optional_value"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `actor` | string | ✅ | Officer name performing the action |
| `role` | string (enum) | ✅ | Officer role: "Investigation Officer", "Tribal Officer", "District Magistrate", "State Nodal Officer", "PFMS Officer" |
| `next_stage` | integer | ✅ | Target stage number (e.g., 3) |
| `comment` | string | ❌ | Approval comment |
| `payload` | object | ❌ | Additional metadata (stored in event_data) |

**Approve Logic**:
- Stage 0: IO submits FIR → auto Stage 1
- Stage 1 (TO approve) → Stage 2
- Stage 2 (DM approve) → Stage 3
- Stage 3 (SNO approve) → Stage 4

**Response** (200 OK):
```json
{
  "message": "Case 5 approved successfully",
  "new_stage": 3,
  "pending_at": "State Nodal Officer",
  "event_type": "DM_APPROVED"
}
```

**Error Responses**:
- `400` — Case at wrong stage, or validation error
- `401` — Invalid JWT token
- `403` — Role mismatch (JWT role ≠ payload role)
- `404` — Case not found
- `500` — Database error

---

### 2.2 Request Correction
**Endpoint**: `POST /{case_no}/correction`

**Authentication**: Required (JWT)

**Description**: Request correction on a case. Only District Magistrate at stage 2 can do this.

**Path Parameters**:
- `case_no` (integer) — Case number

**Request Body** (JSON):
```json
{
  "actor": "DM Verma",
  "role": "District Magistrate",
  "comment": "Amount needs revision - reevaluate medical proof",
  "corrections_required": [
    "Fund_Ammount",
    "Medical_Report_Image"
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `actor` | string | ✅ | Officer name |
| `role` | string (enum) | ✅ | Must be "District Magistrate" |
| `comment` | string | ❌ | Reason for correction |
| `corrections_required` | array[string] | ❌ | List of fields needing correction |

**Transition**: Stage 2 → Stage 1 (case returns to Tribal Officer)

**Response** (200 OK):
```json
{
  "message": "Correction requested for case 5",
  "new_stage": 1,
  "pending_at": "Tribal Officer",
  "corrections_required": ["Fund_Ammount", "Medical_Report_Image"]
}
```

**Error Responses**:
- `400` — Case not at stage 2
- `401` — Invalid JWT token
- `403` — Only DM can request corrections, or role mismatch
- `404` — Case not found
- `500` — Database error

---

### 2.3 Release Funds (Tranche)
**Endpoint**: `POST /{case_no}/fund-release`

**Authentication**: Required (JWT)

**Description**: Release funds to victim (first, second, or final tranche). PFMS Officer only.

**Path Parameters**:
- `case_no` (integer) — Case number

**Request Body** (JSON):
```json
{
  "actor": "PFMS Officer Sharma",
  "role": "PFMS Officer",
  "amount": 50000,
  "percent_of_total": 25,
  "fund_type": "Immediate Relief",
  "txn_id": "PFMS20250110001",
  "bank_acknowledgement": "ACK-2025-001"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `actor` | string | ✅ | Officer name |
| `role` | string (enum) | ✅ | Must be "PFMS Officer" |
| `amount` | float | ✅ | Amount to release |
| `percent_of_total` | float | ✅ | Percentage of total approved fund (25, 50, etc.) |
| `fund_type` | string | ❌ | Type of fund (e.g., "Immediate Relief", "Additional Relief") |
| `txn_id` | string | ❌ | Transaction ID for bank transfer |
| `bank_acknowledgement` | string | ❌ | Bank acknowledgement reference |

**Fund Release Logic**:
- Stage 4 → Release First 25% tranche → moves to Stage 5
- Stage 6 → Release Second tranche (25–50%) → moves to Stage 7
- Stage 7 → Release Final tranche → moves to Stage 8 (case closed)

**Note**: Fund amounts are tracked **only in CASE_EVENTS**, not in ATROCITY table. `Fund_Ammount` in ATROCITY remains the total approved amount.

**Response** (200 OK):
```json
{
  "message": "First Tranche (25%) released for case 5",
  "amount": 50000,
  "percent_of_total": 25,
  "txn_id": "PFMS20250110001",
  "new_stage": 5,
  "pending_at": "Investigation Officer"
}
```

**Error Responses**:
- `400` — Case at wrong stage for fund release
- `401` — Invalid JWT token
- `403` — Only PFMS Officer can release funds, or role mismatch
- `404` — Case not found
- `500` — Database error

---

### 2.4 Submit Chargesheet
**Endpoint**: `POST /{case_no}/chargesheet`

**Authentication**: Required (JWT)

**Description**: Submit chargesheet after investigation. Investigation Officer only at stage 5.

**Path Parameters**:
- `case_no` (integer) — Case number

**Request Body** (JSON):
```json
{
  "actor": "IO Sharma",
  "role": "Investigation Officer",
  "chargesheet_no": "CS-2025-44",
  "chargesheet_date": "2025-02-10",
  "court_name": "Jabalpur District Court",
  "severity": "Severe"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `actor` | string | ✅ | Officer name |
| `role` | string (enum) | ✅ | Must be "Investigation Officer" |
| `chargesheet_no` | string | ✅ | Chargesheet case number |
| `chargesheet_date` | string | ✅ | Date of chargesheet (YYYY-MM-DD format) |
| `court_name` | string | ✅ | Court name where filed |
| `severity` | string | ❌ | Case severity (e.g., "Minor", "Moderate", "Severe") |

**Transition**: Stage 5 → Stage 6 (pending second tranche at PFMS Officer)

**Response** (200 OK):
```json
{
  "message": "Chargesheet submitted for case 5",
  "chargesheet_no": "CS-2025-44",
  "new_stage": 6,
  "pending_at": "PFMS Officer"
}
```

**Error Responses**:
- `400` — Case not at stage 5
- `401` — Invalid JWT token
- `403` — Only Investigation Officer can submit chargesheet, or role mismatch
- `404` — Case not found
- `500` — Database error

---

### 2.5 Complete Case (Record Judgment)
**Endpoint**: `POST /{case_no}/complete`

**Authentication**: Required (JWT)

**Description**: Record judgment and complete a case. District Magistrate only at stage 7.

**Path Parameters**:
- `case_no` (integer) — Case number

**Request Body** (JSON):
```json
{
  "actor": "DM Verma",
  "role": "District Magistrate",
  "judgment_ref": "CJ-8844",
  "judgment_date": "2025-05-12",
  "verdict": "Guilty",
  "notes": "Case closed - offender convicted under PoA Act Section 3(1)"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `actor` | string | ✅ | Officer name |
| `role` | string (enum) | ✅ | Must be "District Magistrate" |
| `judgment_ref` | string | ✅ | Court judgment reference number |
| `judgment_date` | string | ✅ | Date of judgment (YYYY-MM-DD format) |
| `verdict` | string | ✅ | Verdict (e.g., "Guilty", "Not Guilty", "Acquitted") |
| `notes` | string | ❌ | Additional judgment notes |

**Note**: Judgment is recorded at stage 7, case remains at stage 7 (pending final tranche). Final fund release is a separate call.

**Response** (200 OK):
```json
{
  "message": "Judgment recorded for case 5",
  "judgment_ref": "CJ-8844",
  "verdict": "Guilty",
  "stage": 7,
  "pending_at": "PFMS Officer",
  "note": "Awaiting final tranche release"
}
```

**Error Responses**:
- `400` — Case not at stage 7
- `401` — Invalid JWT token
- `403` — Only DM can complete case, or role mismatch
- `404` — Case not found
- `500` — Database error

---

### 2.6 Get Case Events (Timeline)
**Endpoint**: `GET /{case_no}/events`

**Authentication**: Required (JWT, any authenticated user)

**Description**: Retrieve all timeline events for a case.

**Path Parameters**:
- `case_no` (integer) — Case number

**Response** (200 OK):
```json
[
  {
    "event_id": 1,
    "case_no": 5,
    "performed_by": "IO Sharma",
    "performed_by_role": "Investigation Officer",
    "event_type": "FIR_SUBMITTED",
    "event_data": null,
    "created_at": "2025-01-10T10:30:00"
  },
  {
    "event_id": 2,
    "case_no": 5,
    "performed_by": "Officer Singh",
    "performed_by_role": "Tribal Officer",
    "event_type": "TO_APPROVED",
    "event_data": {
      "comment": "Verified - eligible for relief",
      "next_stage": 2
    },
    "created_at": "2025-01-12T14:15:30"
  },
  {
    "event_id": 3,
    "case_no": 5,
    "performed_by": "PFMS Officer Sharma",
    "performed_by_role": "PFMS Officer",
    "event_type": "PFMS_FIRST_TRANCHE",
    "event_data": {
      "amount": 50000,
      "percent_of_total": 25,
      "fund_type": "Immediate Relief",
      "txn_id": "PFMS20250115001",
      "tranche_label": "First Tranche (25%)"
    },
    "created_at": "2025-01-15T11:00:00"
  }
]
```

**Error Responses**:
- `401` — Invalid JWT token
- `404` — Case not found
- `500` — Database error

---

## 3. Event Types Reference

All events are logged with one of these `event_type` values:

| Event Type | Description | Triggered By |
|------------|-------------|--------------|
| `FIR_SUBMITTED` | Case filed by Investigation Officer | submit_fir endpoint |
| `TO_APPROVED` | Tribal Officer verified & approved | approve endpoint (stage 1) |
| `TO_CORRECTION` | Tribal Officer rejected & sent for correction | correction endpoint |
| `DM_APPROVED` | District Magistrate approved | approve endpoint (stage 2) |
| `DM_CORRECTION` | District Magistrate requested correction | correction endpoint |
| `SNO_APPROVED` | State Nodal Officer approved funds | approve endpoint (stage 3) |
| `PFMS_FIRST_TRANCHE` | PFMS Officer released first 25% tranche | fund-release endpoint (stage 4) |
| `CHARGESHEET_SUBMITTED` | Investigation Officer submitted chargesheet | chargesheet endpoint |
| `PFMS_SECOND_TRANCHE` | PFMS Officer released second 25-50% tranche | fund-release endpoint (stage 6) |
| `DM_JUDGMENT_RECORDED` | District Magistrate recorded judgment | complete endpoint |
| `PFMS_FINAL_TRANCHE` | PFMS Officer released final tranche | fund-release endpoint (stage 7→8) |

---

## 4. Workflow Stage Reference

| Stage | Name | Pending At | Action at This Stage |
|-------|------|-----------|----------------------|
| 0 | FIR Submitted | Tribal Officer | TO verifies case |
| 1 | TO Verified | District Magistrate | DM reviews & approves |
| 2 | DM Approved | State Nodal Officer | SNO sanctions funds |
| 3 | SNO Approved | PFMS Officer | PFMS releases first 25% |
| 4 | First Tranche Released | Investigation Officer | IO submits chargesheet |
| 5 | Chargesheet Submitted | PFMS Officer | PFMS releases second tranche |
| 6 | Second Tranche Released | District Magistrate | DM records judgment |
| 7 | Judgment Recorded | PFMS Officer | PFMS releases final tranche |
| 8 | Case Closed | — | Case complete |

---

## 5. Role-Stage Matrix

| Role | Can Act At Stage | Actions |
|------|------------------|---------|
| **Investigation Officer** | 0, 5 | File FIR (stage 0), Submit chargesheet (stage 5) |
| **Tribal Officer** | 1 | Verify & approve (→ stage 2) or request correction |
| **District Magistrate** | 2, 7 | Approve (→ stage 3), request correction (→ stage 1), or complete case (→ stage 7/8) |
| **State Nodal Officer** | 3 | Sanction funds (→ stage 4) |
| **PFMS Officer** | 4, 6, 7 | Release first tranche (stage 4), second tranche (stage 6), or final tranche (stage 7) |

---

## 6. Fund Release Tranches

All tranche tracking is done via `CASE_EVENTS` only. The `Fund_Ammount` field in ATROCITY table stores the **total approved amount** and never changes.

### Tranche Details

| Tranche | Stage | Amount | Trigger | Next Stage |
|---------|-------|--------|---------|-----------|
| **First (25%)** | 4 | 25% of total | PFMS transfers | 5 |
| **Second (25-50%)** | 6 | 25-50% of total | PFMS transfers (after chargesheet) | 7 |
| **Final** | 7 | Remaining amount | PFMS transfers (after judgment) | 8 |

Each fund release creates an event with the following types:
- `PFMS_FIRST_TRANCHE` — First 25% release (stage 4→5)
- `PFMS_SECOND_TRANCHE` — Second 25-50% release (stage 6→7)
- `PFMS_FINAL_TRANCHE` — Final release (stage 7→8)

Event data includes:
- `amount` — Exact amount transferred
- `percent_of_total` — Percentage of originally approved amount
- `fund_type` — Type of relief
- `txn_id` — Bank transaction ID
- `tranche_label` — Human-readable label

---

## 7. Error Handling

### Common Error Responses

**401 Unauthorized** (Missing or invalid JWT):
```json
{
  "detail": "Invalid or expired token."
}
```

**403 Forbidden** (Role mismatch):
```json
{
  "detail": "Role mismatch: JWT role 'Tribal Officer' does not match payload role 'District Magistrate'"
}
```

**400 Bad Request** (Wrong stage for action):
```json
{
  "detail": "Case is at stage 4, but this action requires stage [1, 2, 3]"
}
```

**404 Not Found**:
```json
{
  "detail": "Case not found"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Database connection failed: ..."
}
```

---

## 8. Implementation Notes

- **JWT Authentication**: All workflow endpoints require valid JWT with matching role
- **Stage Validation**: Action is only allowed if case is at the expected stage
- **Role Validation**: JWT role must exactly match the role in request payload
- **Event Auditing**: Every action is recorded with timestamp, actor, and event_data
- **Fund Tracking**: All tranche amounts tracked in CASE_EVENTS, ATROCITY.Fund_Ammount unchanged
- **Correction Flow**: Only the District Magistrate can request correction. Correction ALWAYS moves the case from stage 2 → stage 1. Tribal Officer handles the correction. Case NEVER returns to Investigation Officer for fund-related corrections.

---

**Last Updated**: December 3, 2025
**API Version**: 1.1
**Document Version**: 1.1

### Recent Changes (v1.1)
- ✅ UPSERT pattern for `/submit_fir` to prevent duplicate rows
- ✅ Event deduplication in CASE_EVENTS table
- ✅ New `is_update` response field for clarity
- ✅ Added login endpoint (from auth router)
- ✅ Comprehensive testing guide for duplicate row scenarios
- ✅ Idempotent behavior documented


