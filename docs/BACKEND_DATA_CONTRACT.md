
# 📘 **Backend Data Contract — SIH DBT Workflow System**

This document defines the **API shapes**, **data models**, **workflow rules**, and **backend architecture guidelines** for Copilot and developers.

All backend and frontend code MUST follow this specification.

---

# 1) System Overview

This system digitizes the DBT workflow under PoA/PCR Acts.

A case flows through multiple officers:

1. **Investigation Officer (IO)** — submits FIR-linked victim data
2. **Tribal Officer (TO)** — verifies victim & enters benefit amount
3. **District Magistrate (DM)** — approves or sends back for correction
4. **State Nodal Officer (SNO)** — sanctions funds
5. **PFMS Officer** — transfers DBT amount to victim
6. **Investigation Officer** — submits chargesheet
7. **DM** — closes the case after judgment
8. **System** — releases remaining funds

Every action generates a **timeline event**.

---

# 2) Role Names (Canonical)

Copilot MUST use the exact string values below:

```
"Investigation Officer"
"Tribal Officer"
"District Magistrate"
"State Nodal Officer"
"PFMS Officer"
```

No abbreviations, no alternate spellings.

---

# 3) Database Model (Source of Truth)

The ATROCITY MySQL table stores the **full case record**.

Copilot MUST treat the following structure as the ONLY correct DB schema.

### **AtrocityDBModel (matches SQL table 1:1)**

```python
Case_No: int
FIR_NO: str | None
Victim_Name: str | None
Father_Name: str | None
Victim_DOB: str | None
Gender: str | None
Victim_Mobile_No: str | None
Aadhar_No: int | None
Caste: str | None
Caste_Certificate_No: str | None
Applied_Acts: str | None
Case_Description: str | None
Victim_Image_No: str | None
Location: str | None
Date_of_Incident: str | None

Medical_Report_Image: str | None
Passbook_Image: str | None

Bank_Account_No: str | None
IFSC_Code: str | None
Holder_Name: str | None

Stage: int | None
Fund_Type: str | None
Fund_Ammount: str | None
Pending_At: str | None
Approved_By: str | None

Limit_Delayed: int | None
Reason_for_Delay: str | None

Applicant_Name: str | None
Applicant_Relation: str | None
Applicant_Mobile_No: str | None
Applicant_Email: str | None

Bank_Name: str | None
created_at: str | None
```

This model MUST be used for:

* DB queries
* API responses
* Frontend state
* Workflow actions

---

# 4) Form Template (NOT DB MODEL)

AtrocityBase is a **form input schema only**, used when IO submits data.

Copilot MUST NOT use this structure for database models or response models.

```
AtrocityBase = FIR submission form only.
NOT used for DB. 
NOT used for frontend detail screens. 
```

---

# 5) Combined Output Model (Used in Frontend)

### **AtrocityFullRecord**

This is what **case detail API** returns.

```json
{
  "data": { ...AtrocityDBModel... },
  "documents": {
    "victimImage": "url/path",
    "medicalReport": "url/path",
    "passbook": "url/path"
  },
  "events": [
    {
      "event_id": 12,
      "case_no": 3,
      "performed_by": "Officer Singh",
      "performed_by_role": "Tribal Officer",
      "event_type": "TO_APPROVED",
      "event_data": { ... optional ... },
      "created_at": "2025-01-10T10:32:00"
    }
  ]
}
```

This wrapper ensures **FastAPI does NOT remove extra fields**.

---

# 6) Event Model (Timeline)

### **CaseEvent Table (required)**

Each important workflow action generates an event:

```python
event_id: int
case_no: int
performed_by: str
performed_by_role: str
event_type: str
event_data: dict | None
created_at: str
```

Examples of `event_type`:

```
"FIR_SUBMITTED"
"TO_APPROVED"
"DM_APPROVED"
"SNO_APPROVED"
"DM_CORRECTION"
"PFMS_FIRST_TRANCHE"
"CHARGESHEET_SUBMITTED"
"PFMS_SECOND_TRANCHE"
"DM_JUDGMENT_RECORDED"
"PFMS_FINAL_TRANCHE"
```

---

# 7) API Endpoints (Correct and Updated)

### **1. Get all cases**

```
GET /dbt/case/get-fir-form-data
response → list[AtrocityDBModel]
```

### **2. Get full case details**

```
GET /dbt/case/get-fir-form-data/fir/{fir_no}
response → AtrocityFullRecord
```

Returned data includes:

* Full DB row
* Documents object
* Timeline events

---

# 8) Workflow Endpoints (Payload Specification)

### Approve

```python
{
  "actor": "Officer Name",
  "role": "District Magistrate",
  "next_stage": 3,
  "comment": "Approved",
  "payload": { ...optional }
}
```

### Correction

```python
{
  "actor": "District Magistrate",
  "role": "District Magistrate",
  "comment": "Amount incorrect",
  "corrections_required": ["Fund_Ammount"]
}
```

**Correction Flow Rules:**
- Only the District Magistrate can request corrections.
- Correction ALWAYS moves case from stage 2 → stage 1.
- Tribal Officer fixes and re-approves.
- Case NEVER returns to Investigation Officer for corrections.

### Fund Release

```python
{
  "actor": "PFMS Officer",
  "role": "PFMS Officer",
  "amount": 50000,
  "percent_of_total": 25,
  "fund_type": "Immediate Relief",
  "txn_id": "PFMS12345"
}
```

**Fund Tranche Transitions:**
- Stage 4 → PFMS releases First Tranche (25%) → moves to Stage 5
- Stage 5 → IO submits chargesheet → moves to Stage 6
- Stage 6 → PFMS releases Second Tranche (25-50%) → moves to Stage 7
- Stage 7 → DM records judgment → PFMS releases Final Tranche → Stage 8

**Important:** All tranche releases are stored ONLY in CASE_EVENTS. The `Fund_Ammount` field in ATROCITY stores the TOTAL APPROVED amount and never changes.

### Chargesheet

```python
{
  "actor": "IO Sharma",
  "role": "Investigation Officer",
  "chargesheet_no": "CS-2025-44",
  "chargesheet_date": "2025-02-10",
  "court_name": "Jabalpur District Court",
  "severity": "Severe"
}
```

### Case completion

```python
{
  "actor": "District Magistrate",
  "role": "District Magistrate",
  "judgment_ref": "CJ-8844",
  "judgment_date": "2025-05-12",
  "verdict": "Guilty",
  "notes": "Case closed"
}
```

---

# 9) Case Stages (Canonical)

Copilot MUST use these exact stage numbers and transitions:

```
0 = FIR Submitted (IO) → Pending at Tribal Officer
1 = Verification Pending (Tribal Officer) → Pending at District Magistrate
2 = DM Approval Pending → Pending at State Nodal Officer
3 = SNO Fund Sanction Pending → Pending at PFMS Officer
4 = First Tranche Release Pending (PFMS) → Pending at Investigation Officer
5 = Chargesheet Submission Pending (IO) → Pending at PFMS Officer
6 = Second Tranche Release Pending (PFMS) → Pending at District Magistrate
7 = Judgment Pending (DM) → Pending at PFMS Officer
8 = Final Tranche Release → Case Closed
```

### Stage Transitions:
- Stage 0 → 1: IO submits FIR (auto)
- Stage 1 → 2: Tribal Officer approves
- Stage 2 → 3: District Magistrate approves
- Stage 2 → 1: District Magistrate requests correction (back to TO)
- Stage 3 → 4: State Nodal Officer approves
- Stage 4 → 5: PFMS releases First Tranche (25%)
- Stage 5 → 6: Investigation Officer submits chargesheet
- Stage 6 → 7: PFMS releases Second Tranche (25-50%)
- Stage 7 → 8: District Magistrate records judgment, PFMS releases Final Tranche

---

# 10) Document Handling Rules

Documents are **not stored** inside the main DB row.
Instead:

* store them in a folder or doc table
* return them under `documents` key in AtrocityFullRecord

---

# 11) Copilot Guidance (This Ensures Stable Autocomplete)

### Copilot MUST follow:

* Use `AtrocityDBModel` for all backend → frontend responses
* Use `AtrocityFullRecord` for case details
* Use `AtrocityBase` only for IO form submissions
* Generate React types using `AtrocityDBModel` and `AtrocityFullRecord`
* Use canonical role names exactly
* Do NOT infer schema from mockData.ts
* Do NOT use AtrocityBase as DB model
* When generating endpoints, always return the wrapper model
* DB first → wrapper → frontend
* Timeline must always attach to case detail
* **JWT role MUST match payload.role exactly** — if mismatch, return 403 Forbidden
* Do NOT introduce any new fields in ATROCITY table
* Store total approved fund ONLY in `Fund_Ammount`
* Store all tranche releases ONLY inside `CASE_EVENTS`

---

# 12) Example Case Detail Response

```json
{
  "data": {
    "Case_No": 5,
    "Victim_Name": "Anita",
    "FIR_NO": "FIR-005",
    "Stage": 3,
    "Pending_At": "State Nodal Officer",
    "Fund_Ammount": "200000",
    "Bank_Name": "State Bank Of India"
  },
  "documents": {
    "victimImage": "/uploads/docs/5/victim.jpg",
    "medicalReport": "/uploads/docs/5/med.pdf",
    "passbook": "/uploads/docs/5/pass.png"
  },
  "events": [
    {
      "event_type": "FIR_SUBMITTED",
      "performed_by": "IO Sharma",
      "performed_by_role": "Investigation Officer",
      "created_at": "2025-01-10T15:45:20"
    }
  ]
}
```

---

