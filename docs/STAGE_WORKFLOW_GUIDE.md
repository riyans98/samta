# DBT Atrocity Case Workflow - Stage Management Guide

## Overview
This document details the 9-stage workflow (0-8) for atrocity case processing, including:
- **Stage conditions** - Preconditions and required state
- **Actor roles** - Who can perform actions at each stage
- **Jurisdiction enforcement** - Geographic boundary checks
- **API endpoints** - How to move between stages
- **Database events** - Events recorded in CASE_EVENTS table

---

## Stage 0: FIR Submitted (Investigation Officer)

### Stage Information
- **Current Stage**: 0
- **Next Stage**: 1 (Tribal Officer)
- **Pending At**: "Tribal Officer"
- **Actor Role**: Investigation Officer (IO)

### Preconditions
- [ ] FIR form complete with all required fields
- [ ] Victim Aadhaar number verified in government database
- [ ] FIR number exists in government FIR database
- [ ] All required documents uploaded:
  - FIR Document
  - Victim Photo
  - Caste Certificate
  - Medical Certificate (optional)
  - Postmortem Report (optional)
- [ ] Bank details captured (Account No, Bank Name, IFSC Code, Holder Name)
- [ ] IO authenticated with valid JWT token

### Jurisdiction Enforcement
```
JWT Role: Investigation Officer
JWT Jurisdiction Fields:
  - state_ut: Must match case location
  - district: Must match case location
  - vishesh_p_s_name: Officer's assigned police station
```
IO can only submit FIR for cases in their `vishesh_p_s_name` (police station).

### Data Captured
```
From FIR Form:
  - FIR_NO, Case_Description
  - Victim Details (Name, DOB, Gender, Mobile, Aadhaar, Caste)
  - Applicant Details (Name, Relation, Contact, Email)
  - Bank Account Details (Account No, IFSC, Holder Name, Bank)
  - Applied Acts, Location, Date of Incident

From JWT Token (IO's Jurisdiction):
  - State_UT
  - District
  - Vishesh_P_S_Name
```

### Database Updates
```sql
-- Create new ATROCITY record
INSERT INTO ATROCITY (
  FIR_NO, Case_Description, Victim_Name, Father_Name, Victim_DOB, Gender,
  Victim_Mobile_No, Aadhar_No, Caste, Bank_Account_No, IFSC_Code,
  Holder_Name, Bank_Name, Applicant_Name, Applicant_Relation,
  Applicant_Mobile_No, Applicant_Email, Applied_Acts, Location,
  Date_of_Incident, Stage, Pending_At, State_UT, District, Vishesh_P_S_Name
) VALUES (...)

-- Insert FIR_SUBMITTED event
INSERT INTO CASE_EVENTS (
  CASE_NO, Performed_By, Performed_By_Role, Event_Type, Event_Data, Timestamp
) VALUES (
  {case_no}, {io_login_id}, 'Investigation Officer', 'FIR_SUBMITTED', {...}, NOW()
)
```

### API Endpoint

**POST** `/dbt/case/submit_fir`

**Query Parameters:**
- `isDrafted` (optional, default=false): If true, case goes to IO draft status; if false, moves to Tribal Officer

**Form Data:**
```json
{
  "firNumber": "FIR-2025-001",
  "caste": "Scheduled Tribe",
  "aadhaar": "123456789012",
  "email": "victim@email.com",
  "accountNumber": "1234567890",
  "ifscCode": "BANK0001234",
  "holderName": "Victim Name",
  "bankName": "State Bank of India",
  "firDocument": "[FILE]",
  "photo": "[FILE]",
  "casteCertificate": "[FILE]",
  "medicalCertificate": "[FILE (optional)]",
  "postmortem": "[FILE (optional)]"
}
```

**Headers:**
```
Authorization: Bearer {JWT_TOKEN}
```

**Success Response (201):**
```json
{
  "case_no": 1001,
  "fir_no": "FIR-2025-001",
  "stage": 0 or 1,
  "pending_at": "Investigation Officer" or "Tribal Officer",
  "message": "FIR submitted successfully"
}
```

**Error Responses:**
- `400`: Validation error (missing fields, invalid data)
- `401`: Invalid or expired JWT token
- `403`: Jurisdiction violation (IO not assigned to this police station)
- `404`: Aadhaar or FIR number not found in government database
- `500`: Server/database error

---

## Stage 1: Tribal Officer Verification

### Stage Information
- **Current Stage**: 1
- **Next Stage**: 2 (District Magistrate)
- **Pending At**: "District Magistrate"
- **Actor Role**: Tribal Officer (TO)

### Preconditions
- [ ] Case at Stage 1 with pending_at = "Tribal Officer"
- [ ] FIR_SUBMITTED event exists in CASE_EVENTS
- [ ] TO verified all required documents
- [ ] TO determined total approved fund amount (Fund_Ammount set)
- [ ] Tribal Officer authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: Tribal Officer
JWT Jurisdiction Fields:
  - state_ut: Must match case.State_UT
  - district: Must match case.District
```
TO can only approve cases in their assigned district & state.

### Data Captured (in Event)
```json
{
  "comment": "All proofs verified. Eligible for benefits.",
  "next_stage": 2,
  "total_approved_fund": 500000,
  "beneficiary_category": "ST",
  "additional_notes": "..."
}
```

### Database Updates
```sql
-- Insert TO_APPROVED event
INSERT INTO CASE_EVENTS (
  CASE_NO, Performed_By, Performed_By_Role, Event_Type, Event_Data, Timestamp
) VALUES (
  {case_no}, {to_login_id}, 'Tribal Officer', 'TO_APPROVED', {...}, NOW()
)

-- Update ATROCITY case
UPDATE ATROCITY SET
  Stage = 2,
  Pending_At = 'District Magistrate',
  Fund_Ammount = {total_approved_fund},  -- SET ONCE BY TO
  Approved_By = {to_login_id}
WHERE CASE_NO = {case_no}
```

### API Endpoint

**POST** `/dbt/case/{case_no}/approve`

**Path Parameters:**
- `case_no` (integer): The case number

**Request Body (JSON):**
```json
{
  "role": "Tribal Officer",
  "actor": "to_officer_123",
  "comment": "All proofs verified. Eligible for benefits.",
  "next_stage": 2,
  "payload": {
    "total_approved_fund": 500000,
    "beneficiary_category": "ST",
    "remarks": "..."
  }
}
```

**Headers:**
```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Success Response (200):**
```json
{
  "message": "Case 1001 approved successfully",
  "new_stage": 2,
  "pending_at": "District Magistrate",
  "event_type": "TO_APPROVED"
}
```

**Error Responses:**
- `400`: Invalid stage or payload
- `401`: Invalid/expired JWT
- `403`: Role mismatch or jurisdiction violation
- `404`: Case not found
- `500`: Server error

---

## Stage 2: District Magistrate Approval

### Stage Information
- **Current Stage**: 2
- **Next Stage (Approve)**: 3 (State Nodal Officer)
- **Next Stage (Correction)**: 1 (Tribal Officer - special case)
- **Pending At (Approve)**: "State Nodal Officer"
- **Pending At (Correction)**: "Tribal Officer"
- **Actor Role**: District Magistrate (DM)

### Preconditions
- [ ] Case at Stage 2 with pending_at = "District Magistrate"
- [ ] TO_APPROVED event exists in CASE_EVENTS
- [ ] Fund_Ammount is set in ATROCITY
- [ ] DM authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: District Magistrate
JWT Jurisdiction Fields:
  - state_ut: Must match case.State_UT
  - district: Must match case.District
```
DM can only process cases in their assigned district & state.

### Two Actions at Stage 2

#### Action A: Approve Case (→ Stage 3)
**Data Captured:**
```json
{
  "comment": "Application approved by DM. Forwarding to SNO.",
  "next_stage": 3
}
```

**Database Updates:**
```sql
INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {dm_login_id}, 'District Magistrate', 'DM_APPROVED', {...}, NOW()
)

UPDATE ATROCITY SET
  Stage = 3,
  Pending_At = 'State Nodal Officer',
  Approved_By = {dm_login_id}
WHERE CASE_NO = {case_no}
```

#### Action B: Request Correction (→ Stage 1)
**Only DM can request corrections at Stage 2**
**Data Captured:**
```json
{
  "comment": "More documentation needed for verification.",
  "corrections_required": ["Updated Medical Report", "Bank Statement"]
}
```

**Database Updates:**
```sql
INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {dm_login_id}, 'District Magistrate', 'DM_CORRECTION', {...}, NOW()
)

UPDATE ATROCITY SET
  Stage = 1,
  Pending_At = 'Tribal Officer'
WHERE CASE_NO = {case_no}
```

### API Endpoints

#### 1. Approve Case

**POST** `/dbt/case/{case_no}/approve`

**Request Body:**
```json
{
  "role": "District Magistrate",
  "actor": "dm_officer_456",
  "comment": "Application approved. Forwarding to SNO.",
  "next_stage": 3,
  "payload": {}
}
```

**Success Response:**
```json
{
  "message": "Case 1001 approved successfully",
  "new_stage": 3,
  "pending_at": "State Nodal Officer",
  "event_type": "DM_APPROVED"
}
```

#### 2. Request Correction

**POST** `/dbt/case/{case_no}/correction`

**Request Body:**
```json
{
  "role": "District Magistrate",
  "actor": "dm_officer_456",
  "comment": "Medical report outdated. Please resubmit.",
  "corrections_required": ["Updated Medical Report", "Additional Bank Statement"]
}
```

**Success Response:**
```json
{
  "message": "Correction requested for case 1001",
  "new_stage": 1,
  "pending_at": "Tribal Officer",
  "corrections_required": ["Updated Medical Report", "Additional Bank Statement"]
}
```

**Error Responses (both endpoints):**
- `400`: Invalid stage or corrections
- `401`: Invalid/expired JWT
- `403`: Only DM can request corrections; role/jurisdiction violation
- `404`: Case not found

---

## Stage 3: State Nodal Officer Fund Sanction

### Stage Information
- **Current Stage**: 3
- **Next Stage**: 4 (PFMS Officer)
- **Pending At**: "PFMS Officer"
- **Actor Role**: State Nodal Officer (SNO)

### Preconditions
- [ ] Case at Stage 3 with pending_at = "State Nodal Officer"
- [ ] DM_APPROVED event exists in CASE_EVENTS
- [ ] Fund_Ammount is set (total approved amount)
- [ ] SNO authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: State Nodal Officer
JWT Jurisdiction Field:
  - state_ut: Must match case.State_UT
```
SNO can only process cases in their assigned state. No district-level restriction.

### Data Captured
```json
{
  "comment": "Funds sanctioned by SNO. Proceeding to PFMS.",
  "next_stage": 4,
  "sanction_order_no": "SAN/2025/001",
  "sanction_date": "2025-01-15"
}
```

### Database Updates
```sql
INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {sno_login_id}, 'State Nodal Officer', 'SNO_APPROVED', {...}, NOW()
)

UPDATE ATROCITY SET
  Stage = 4,
  Pending_At = 'PFMS Officer',
  Approved_By = {sno_login_id}
WHERE CASE_NO = {case_no}
```

### API Endpoint

**POST** `/dbt/case/{case_no}/approve`

**Request Body:**
```json
{
  "role": "State Nodal Officer",
  "actor": "sno_officer_789",
  "comment": "Funds sanctioned. Proceeding to PFMS.",
  "next_stage": 4,
  "payload": {
    "sanction_order_no": "SAN/2025/001",
    "sanction_date": "2025-01-15"
  }
}
```

**Success Response:**
```json
{
  "message": "Case 1001 approved successfully",
  "new_stage": 4,
  "pending_at": "PFMS Officer",
  "event_type": "SNO_APPROVED"
}
```

---

## Stage 4: PFMS First Tranche Release (25%)

### Stage Information
- **Current Stage**: 4
- **Next Stage**: 5 (Investigation Officer)
- **Pending At**: "Investigation Officer"
- **Actor Role**: PFMS Officer

### Preconditions
- [ ] Case at Stage 4 with pending_at = "PFMS Officer"
- [ ] SNO_APPROVED event exists in CASE_EVENTS
- [ ] Fund_Ammount is set in ATROCITY (total approved)
- [ ] Bank account details valid in ATROCITY record
- [ ] PFMS Officer authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: PFMS Officer
JWT Jurisdiction Field:
  - state_ut: Must match case.State_UT
```
PFMS can only release funds for cases in their assigned state.

### Fund Details
- **Tranche Percentage**: 25% of Fund_Ammount
- **Calculation**: (Fund_Ammount * 0.25)
- **Fund Type**: "Initial/First Tranche"

### Data Captured
```json
{
  "amount": 125000,
  "percent_of_total": 25,
  "fund_type": "Initial Tranche",
  "txn_id": "TXN20250115001",
  "bank_acknowledgement": "ACK-2025-001",
  "remarks": "First tranche released successfully"
}
```

### Database Updates
```sql
-- Note: Fund_Ammount in ATROCITY is UNCHANGED
-- Only CASE_EVENTS tracks tranche releases

INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {pfms_login_id}, 'PFMS Officer', 'PFMS_FIRST_TRANCHE', 
  {
    amount, percent_of_total, fund_type, txn_id, 
    bank_acknowledgement, tranche_label
  }, 
  NOW()
)

UPDATE ATROCITY SET
  Stage = 5,
  Pending_At = 'Investigation Officer'
WHERE CASE_NO = {case_no}
```

### API Endpoint

**POST** `/dbt/case/{case_no}/fund-release`

**Request Body:**
```json
{
  "role": "PFMS Officer",
  "actor": "pfms_officer_001",
  "amount": 125000,
  "percent_of_total": 25,
  "fund_type": "Initial Tranche",
  "txn_id": "TXN20250115001",
  "bank_acknowledgement": "ACK-2025-001"
}
```

**Success Response:**
```json
{
  "message": "First Tranche (25%) released for case 1001",
  "amount": 125000,
  "percent_of_total": 25,
  "txn_id": "TXN20250115001",
  "new_stage": 5,
  "pending_at": "Investigation Officer"
}
```

**Error Responses:**
- `400`: Invalid stage or fund amount
- `401`: Invalid/expired JWT
- `403`: Only PFMS can release funds; jurisdiction violation
- `404`: Case not found

---

## Stage 5: Chargesheet Submission (Investigation Officer)

### Stage Information
- **Current Stage**: 5
- **Next Stage**: 6 (PFMS Officer - Second Tranche)
- **Pending At**: "PFMS Officer"
- **Actor Role**: Investigation Officer (IO)

### Preconditions
- [ ] Case at Stage 5 with pending_at = "Investigation Officer"
- [ ] PFMS_FIRST_TRANCHE event exists in CASE_EVENTS
- [ ] First 25% tranche released
- [ ] Chargesheet filed in court
- [ ] IO authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: Investigation Officer
JWT Jurisdiction Field:
  - vishesh_p_s_name: Must match case.Vishesh_P_S_Name
```
IO can only submit chargesheet for their assigned police station.

### Data Captured
```json
{
  "chargesheet_no": "CS-2025-001",
  "chargesheet_date": "2025-01-20",
  "court_name": "District Court, Ranchi",
  "severity": "heinous"
}
```

### Database Updates
```sql
INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {io_login_id}, 'Investigation Officer', 'CHARGESHEET_SUBMITTED',
  {chargesheet_no, chargesheet_date, court_name, severity},
  NOW()
)

UPDATE ATROCITY SET
  Stage = 6,
  Pending_At = 'PFMS Officer'
WHERE CASE_NO = {case_no}
```

### API Endpoint

**POST** `/dbt/case/{case_no}/chargesheet`

**Request Body:**
```json
{
  "role": "Investigation Officer",
  "actor": "io_officer_123",
  "chargesheet_no": "CS-2025-001",
  "chargesheet_date": "2025-01-20",
  "court_name": "District Court, Ranchi",
  "severity": "heinous"
}
```

**Success Response:**
```json
{
  "message": "Chargesheet submitted for case 1001",
  "chargesheet_no": "CS-2025-001",
  "new_stage": 6,
  "pending_at": "PFMS Officer"
}
```

**Error Responses:**
- `400`: Invalid stage or chargesheet data
- `401`: Invalid/expired JWT
- `403`: Only IO can submit chargesheet; jurisdiction violation
- `404`: Case not found

---

## Stage 6: PFMS Second Tranche Release (25-50%)

### Stage Information
- **Current Stage**: 6
- **Next Stage**: 7 (District Magistrate - Judgment)
- **Pending At**: "District Magistrate"
- **Actor Role**: PFMS Officer

### Preconditions
- [ ] Case at Stage 6 with pending_at = "PFMS Officer"
- [ ] CHARGESHEET_SUBMITTED event exists in CASE_EVENTS
- [ ] Chargesheet filed in court
- [ ] PFMS Officer authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: PFMS Officer
JWT Jurisdiction Field:
  - state_ut: Must match case.State_UT
```
PFMS can only release funds for cases in their assigned state.

### Fund Details
- **Tranche Percentage**: 25-50% of Fund_Ammount (flexible based on progress)
- **Typical Range**: 25-50% of total
- **Calculation**: (Fund_Ammount * 0.25) to (Fund_Ammount * 0.50)
- **Fund Type**: "Interim Tranche" or "Second Tranche"

### Data Captured
```json
{
  "amount": 200000,
  "percent_of_total": 40,
  "fund_type": "Second Tranche",
  "txn_id": "TXN20250120001",
  "bank_acknowledgement": "ACK-2025-002",
  "remarks": "Second tranche released after chargesheet submission"
}
```

### Database Updates
```sql
INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {pfms_login_id}, 'PFMS Officer', 'PFMS_SECOND_TRANCHE',
  {amount, percent_of_total, fund_type, txn_id, bank_acknowledgement, tranche_label},
  NOW()
)

UPDATE ATROCITY SET
  Stage = 7,
  Pending_At = 'District Magistrate'
WHERE CASE_NO = {case_no}
```

### API Endpoint

**POST** `/dbt/case/{case_no}/fund-release`

**Request Body:**
```json
{
  "role": "PFMS Officer",
  "actor": "pfms_officer_001",
  "amount": 200000,
  "percent_of_total": 40,
  "fund_type": "Second Tranche",
  "txn_id": "TXN20250120001",
  "bank_acknowledgement": "ACK-2025-002"
}
```

**Success Response:**
```json
{
  "message": "Second Tranche (25-50%) released for case 1001",
  "amount": 200000,
  "percent_of_total": 40,
  "txn_id": "TXN20250120001",
  "new_stage": 7,
  "pending_at": "District Magistrate"
}
```

---

## Stage 7: District Magistrate Judgment Recording

### Stage Information
- **Current Stage**: 7
- **Next Stage**: 8 (PFMS - Final Tranche, after DM records judgment)
- **Pending At (After Judgment)**: "PFMS Officer"
- **Actor Role**: District Magistrate (DM)

### Preconditions
- [ ] Case at Stage 7 with pending_at = "District Magistrate"
- [ ] PFMS_SECOND_TRANCHE event exists in CASE_EVENTS
- [ ] Court has issued judgment
- [ ] Second tranche released
- [ ] DM authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: District Magistrate
JWT Jurisdiction Fields:
  - state_ut: Must match case.State_UT
  - district: Must match case.District
```
DM can only record judgment for cases in their assigned district & state.

### Data Captured
```json
{
  "judgment_ref": "JDG/2025/001",
  "judgment_date": "2025-02-01",
  "verdict": "Convicted",
  "notes": "Accused convicted under SC/ST Act. Compensation awarded."
}
```

### Database Updates
```sql
INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {dm_login_id}, 'District Magistrate', 'DM_JUDGMENT_RECORDED',
  {judgment_ref, judgment_date, verdict, notes},
  NOW()
)

UPDATE ATROCITY SET
  Pending_At = 'PFMS Officer',
  Approved_By = {dm_login_id}
WHERE CASE_NO = {case_no}
-- Note: Stage remains 7 until final tranche released
```

### API Endpoint

**POST** `/dbt/case/{case_no}/complete`

**Request Body:**
```json
{
  "role": "District Magistrate",
  "actor": "dm_officer_456",
  "judgment_ref": "JDG/2025/001",
  "judgment_date": "2025-02-01",
  "verdict": "Convicted",
  "notes": "Accused convicted under SC/ST Act. Full compensation awarded."
}
```

**Success Response:**
```json
{
  "message": "Judgment recorded for case 1001",
  "judgment_ref": "JDG/2025/001",
  "verdict": "Convicted",
  "stage": 7,
  "pending_at": "PFMS Officer",
  "note": "Awaiting final tranche release"
}
```

**Error Responses:**
- `400`: Invalid stage (requires Stage 7)
- `401`: Invalid/expired JWT
- `403`: Only DM can record judgment; role/jurisdiction violation
- `404`: Case not found

---

## Stage 8: PFMS Final Tranche Release (Remaining)

### Stage Information
- **Current Stage**: 8 (Final)
- **Next Stage**: None (Case Closed)
- **Pending At**: "" (Empty - Case Closed)
- **Actor Role**: PFMS Officer

### Preconditions
- [ ] Case at Stage 7 with pending_at = "PFMS Officer"
- [ ] DM_JUDGMENT_RECORDED event exists in CASE_EVENTS
- [ ] Judgment recorded and verdict known
- [ ] Final tranche amount approved
- [ ] PFMS Officer authenticated with valid JWT

### Jurisdiction Enforcement
```
JWT Role: PFMS Officer
JWT Jurisdiction Field:
  - state_ut: Must match case.State_UT
```
PFMS can only release funds for cases in their assigned state.

### Fund Details
- **Tranche Percentage**: Remaining balance to 100%
- **Typical Range**: 50% of Fund_Ammount (if prior tranches totaled 50%)
- **Calculation**: Fund_Ammount - sum(prior tranches)
- **Fund Type**: "Final Tranche"

### Data Captured
```json
{
  "amount": 175000,
  "percent_of_total": 100,
  "fund_type": "Final Tranche",
  "txn_id": "TXN20250210001",
  "bank_acknowledgement": "ACK-2025-003",
  "remarks": "Final tranche released. Case closed."
}
```

### Database Updates
```sql
INSERT INTO CASE_EVENTS (...) VALUES (
  {case_no}, {pfms_login_id}, 'PFMS Officer', 'PFMS_FINAL_TRANCHE',
  {amount, percent_of_total, fund_type, txn_id, bank_acknowledgement, tranche_label},
  NOW()
)

UPDATE ATROCITY SET
  Stage = 8,
  Pending_At = '',
  Status = 'CLOSED'  -- If status column exists
WHERE CASE_NO = {case_no}
```

### API Endpoint

**POST** `/dbt/case/{case_no}/fund-release`

**Request Body:**
```json
{
  "role": "PFMS Officer",
  "actor": "pfms_officer_001",
  "amount": 175000,
  "percent_of_total": 100,
  "fund_type": "Final Tranche",
  "txn_id": "TXN20250210001",
  "bank_acknowledgement": "ACK-2025-003"
}
```

**Success Response:**
```json
{
  "message": "Final Tranche released for case 1001",
  "amount": 175000,
  "percent_of_total": 100,
  "txn_id": "TXN20250210001",
  "new_stage": 8,
  "pending_at": "",
  "note": "Case closed successfully"
}
```

---

## Stage Transition Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                    ATROCITY CASE WORKFLOW                       │
└─────────────────────────────────────────────────────────────────┘

Stage 0: FIR Submitted (IO)
  └──> Submit_FIR API
      └─────> Stage 1: Tribal Officer Verification

Stage 1: Tribal Officer Verification (TO)
  └──> /approve API
      └─────> Stage 2: District Magistrate Approval

Stage 2: District Magistrate Approval (DM)
  ├──> /approve API
  │    └─────> Stage 3: State Nodal Officer Sanction
  │
  └──> /correction API (DM Only)
       └─────> Stage 1: Tribal Officer (Back)

Stage 3: SNO Fund Sanction (SNO)
  └──> /approve API
      └─────> Stage 4: PFMS First Tranche (25%)

Stage 4: PFMS First Tranche Release (PFMS)
  └──> /fund-release API
      └─────> Stage 5: Chargesheet Submission

Stage 5: Chargesheet Submission (IO)
  └──> /chargesheet API
      └─────> Stage 6: PFMS Second Tranche (25-50%)

Stage 6: PFMS Second Tranche Release (PFMS)
  └──> /fund-release API
      └─────> Stage 7: Judgment Recording

Stage 7: Judgment Recording (DM)
  └──> /complete API
      │ (Records DM_JUDGMENT_RECORDED event)
      │ (Remains Stage 7, Pending PFMS)
      │
      └──> /fund-release API (PFMS Final Tranche)
           └─────> Stage 8: CASE CLOSED

Stage 8: Case Closed
  └──> [END]
```

---

## Summary Table: Stage, Role, and API Mapping

| Stage | Description | Actor Role | API Endpoint | Event Type | Next Stage |
|-------|-------------|-----------|--------------|-----------|-----------|
| 0 | FIR Submitted | Investigation Officer | POST /submit_fir | FIR_SUBMITTED | 1 |
| 1 | TO Verification | Tribal Officer | POST /{case_no}/approve | TO_APPROVED | 2 |
| 2 | DM Approval | District Magistrate | POST /{case_no}/approve | DM_APPROVED | 3 |
| 2 | DM Correction | District Magistrate | POST /{case_no}/correction | DM_CORRECTION | 1 |
| 3 | SNO Sanction | State Nodal Officer | POST /{case_no}/approve | SNO_APPROVED | 4 |
| 4 | First Tranche | PFMS Officer | POST /{case_no}/fund-release | PFMS_FIRST_TRANCHE | 5 |
| 5 | Chargesheet | Investigation Officer | POST /{case_no}/chargesheet | CHARGESHEET_SUBMITTED | 6 |
| 6 | Second Tranche | PFMS Officer | POST /{case_no}/fund-release | PFMS_SECOND_TRANCHE | 7 |
| 7 | Judgment | District Magistrate | POST /{case_no}/complete | DM_JUDGMENT_RECORDED | 7 (pending) |
| 7 | Final Tranche | PFMS Officer | POST /{case_no}/fund-release | PFMS_FINAL_TRANCHE | 8 |
| 8 | Case Closed | - | - | - | - |

---

## Jurisdiction Validation Rules

### Investigation Officer (IO)
```
Query Table: Vishesh_Thana_Officers
JWT Fields: state_ut, district, vishesh_p_s_name
Can Access: Cases where Vishesh_P_S_Name = jwt.vishesh_p_s_name
Actions:
  - Stage 0: Submit FIR
  - Stage 5: Submit Chargesheet
```

### Tribal Officer (TO)
```
Query Table: District_lvl_Officers (with role = 'Tribal Officer')
JWT Fields: state_ut, district
Can Access: Cases where State_UT = jwt.state_ut AND District = jwt.district
Actions:
  - Stage 1: Approve/Verify case
```

### District Magistrate (DM)
```
Query Table: District_lvl_Officers (with role = 'District Collector/DM/SJO')
JWT Fields: state_ut, district
Can Access: Cases where State_UT = jwt.state_ut AND District = jwt.district
Actions:
  - Stage 2: Approve case or Request correction
  - Stage 7: Record judgment
```

### State Nodal Officer (SNO)
```
Query Table: State_Nodal_Officers
JWT Fields: state_ut
Can Access: Cases where State_UT = jwt.state_ut
Actions:
  - Stage 3: Sanction funds
```

### PFMS Officer
```
Query Table: PFMS_Officers (if exists) OR derived from state
JWT Fields: state_ut
Can Access: Cases where State_UT = jwt.state_ut AND Stage in [4, 6, 7]
Actions:
  - Stage 4: Release first tranche (25%)
  - Stage 6: Release second tranche (25-50%)
  - Stage 7→8: Release final tranche
```

---

## Fund Management

### Fund_Ammount Field (ATROCITY Table)
- **Set by**: Tribal Officer at Stage 1
- **Value**: Total approved amount for the case
- **Immutable**: Cannot be changed after set by TO
- **Purpose**: Reference for all tranche calculations

### Fund Tracking (CASE_EVENTS Table)
- **First Tranche**: 25% recorded in event at Stage 4→5
- **Second Tranche**: 25-50% recorded in event at Stage 6→7
- **Final Tranche**: Remainder recorded in event at Stage 7→8
- **Total Releases**: Sum of all tranches = Fund_Ammount (ideally)

### Example
```
Total Fund_Ammount: 500,000

Stage 4: Release 125,000 (25%)  → Event: PFMS_FIRST_TRANCHE
Stage 6: Release 200,000 (40%)  → Event: PFMS_SECOND_TRANCHE
Stage 8: Release 175,000 (35%)  → Event: PFMS_FINAL_TRANCHE

Total Released: 500,000 ✓
```

---

## Error Handling

### Common HTTP Status Codes

| Status | Scenario | Reason |
|--------|----------|--------|
| 201 | FIR Submitted | Case created successfully |
| 200 | Action Successful | Approval/Fund release/Chargesheet recorded |
| 400 | Bad Request | Invalid payload, wrong stage for action |
| 401 | Unauthorized | Missing/invalid/expired JWT token |
| 403 | Forbidden | Role mismatch, jurisdiction violation, action not allowed for role |
| 404 | Not Found | Case not found, Aadhaar/FIR not in government database |
| 500 | Server Error | Database/system error |

### Common Error Messages

```
"Invalid Login ID or Password for the selected role."
  → Authentication failed in login

"Role mismatch: JWT role 'X' does not match payload role 'Y'"
  → JWT and request payload roles don't match

"Only [ROLE_NAME] can [ACTION]"
  → Action restricted to specific role

"Case is at stage X, but [ACTION] requires stage Y"
  → Stage validation failed

"User's jurisdiction does not include this case"
  → Geographic/jurisdiction validation failed

"Invalid token payload" / "Invalid or expired token"
  → JWT token issue
```

---

## Quick Reference: Who Can Do What

| Role | Stage 0 | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 | Stage 6 | Stage 7 | Stage 8 |
|------|--------|--------|--------|--------|--------|--------|--------|---------|---------|
| **IO** | Submit FIR | - | - | - | - | Submit CS | - | - | - |
| **TO** | - | Approve | - | - | - | - | - | - | - |
| **DM** | - | - | Approve / Correct | - | - | - | - | Judge | - |
| **SNO** | - | - | - | Approve | - | - | - | - | - |
| **PFMS** | - | - | - | - | Release (25%) | - | Release (25-50%) | Release Remaining | - |

---

## Testing Checklist

### FIR Submission (Stage 0→1)
- [ ] Valid JWT token for Investigation Officer
- [ ] Aadhaar exists in government database
- [ ] FIR exists in government FIR database
- [ ] All required documents uploaded
- [ ] Case created with Stage=1, Pending_At="Tribal Officer"
- [ ] FIR_SUBMITTED event recorded

### TO Approval (Stage 1→2)
- [ ] Valid JWT token for Tribal Officer in same state/district
- [ ] Case at Stage 1
- [ ] Fund_Ammount set
- [ ] TO_APPROVED event recorded
- [ ] Case moved to Stage 2, Pending_At="District Magistrate"

### DM Approval (Stage 2→3)
- [ ] Valid JWT token for DM in same state/district
- [ ] Case at Stage 2
- [ ] DM_APPROVED event recorded
- [ ] Case moved to Stage 3, Pending_At="State Nodal Officer"

### DM Correction (Stage 2→1)
- [ ] Only DM can request
- [ ] Case moves back to Stage 1
- [ ] DM_CORRECTION event recorded

### SNO Sanction (Stage 3→4)
- [ ] Valid JWT token for SNO in same state
- [ ] Case at Stage 3
- [ ] SNO_APPROVED event recorded
- [ ] Case moved to Stage 4, Pending_At="PFMS Officer"

### Fund Release (Stages 4, 6, 7)
- [ ] Valid JWT token for PFMS in same state
- [ ] Correct amount calculated (% of Fund_Ammount)
- [ ] Transaction ID and bank acknowledgement recorded
- [ ] Event recorded (PFMS_FIRST/SECOND/FINAL_TRANCHE)
- [ ] Case stage incremented appropriately

### Chargesheet (Stage 5→6)
- [ ] Valid JWT token for IO in same police station
- [ ] Case at Stage 5
- [ ] Chargesheet details recorded
- [ ] CHARGESHEET_SUBMITTED event recorded
- [ ] Case moved to Stage 6

### Judgment (Stage 7)
- [ ] Valid JWT token for DM in same state/district
- [ ] Case at Stage 7
- [ ] DM_JUDGMENT_RECORDED event recorded
- [ ] Case remains at Stage 7, pending PFMS

---

## Conclusion

This workflow enforces:
1. **Strict Role-Based Access** - Each role can only perform designated actions
2. **Geographic Jurisdiction** - Officers restricted to their assigned areas
3. **Sequential Processing** - Cases must follow the stage progression
4. **Complete Audit Trail** - All actions recorded in CASE_EVENTS
5. **Fund Tracking** - All financial transactions documented separately from case data

For implementation, always:
- ✅ Validate JWT token first
- ✅ Check role matches payload
- ✅ Verify jurisdiction access
- ✅ Validate case stage
- ✅ Record event before updating case
- ✅ Return clear success/error messages
