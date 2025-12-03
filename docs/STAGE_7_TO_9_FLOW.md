# Stage 7 to 9 Flow: Judgment & Final Tranche Release

## Overview
This document explains the complete workflow for cases at stages 7, 8, and 9 - from judgment recording to case closure.

---

## Stage Definitions

| Stage | Status | Pending At | Actor | Action |
|-------|--------|-----------|-------|--------|
| **7** | Judgment Pending | District Collector/DM/SJO | DM | Review case, record judgment |
| **8** | Judgment Complete | PFMS Officer for Final Tranche Release | PFMS | Confirm final tranche release |
| **9** | Case Closed | — | — | Case completed |

---

## Complete Workflow

### **Phase 1: DM Records Judgment (Stage 7 → 8)**

#### Trigger
After chargesheet is submitted and second tranche is released, case reaches stage 7.

#### Endpoint
```
POST /dbt/case/{case_no}/complete
```

#### Request Body
```json
{
  "actor": "dm_jabalpur_001",
  "role": "District Collector/DM/SJO",
  "judgment_ref": "JUDGMENT-2025-001",
  "judgment_date": "2025-12-04",
  "verdict": "Guilty - Compensation Awarded",
  "notes": "All evidence reviewed. Victim eligible for full compensation."
}
```

#### What Happens
1. ✅ Validates DM has jurisdiction (state + district match)
2. ✅ Records `DM_JUDGMENT_RECORDED` event in CASE_EVENTS
3. ✅ Stores judgment details (ref, date, verdict, notes) in event_data
4. ✅ **Moves case to Stage 8**
5. ✅ Updates `Pending_At` to "PFMS Officer for Final Tranche Release"

#### Response
```json
{
  "message": "Judgment recorded for case 101",
  "judgment_ref": "JUDGMENT-2025-001",
  "verdict": "Guilty - Compensation Awarded",
  "stage": 8,
  "pending_at": "PFMS Officer for Final Tranche Release",
  "note": "Case complete, awaiting final tranche release confirmation"
}
```

#### Frontend Status Update
- Case moves from "Judgment Pending" → "Awaiting Final Tranche"
- Show judgment details on case page
- Display: "Waiting for PFMS Officer to release final funds"

---

### **Phase 2: PFMS Releases Final Tranche (Stage 8 → 9)**

#### Trigger
After DM records judgment, case is at stage 8. PFMS Officer can now release final funds.

#### Endpoint
```
POST /dbt/case/{case_no}/fund-release
```

#### Request Body
```json
{
  "actor": "pfms_jabalpur_001",
  "role": "PFMS Officer",
  "amount": 150000.00,
  "percent_of_total": 100,
  "fund_type": "Final Compensation Tranche",
  "txn_id": "TXN-2025-789456",
  "bank_acknowledgement": "ACK-2025-001"
}
```

#### What Happens
1. ✅ Validates PFMS has jurisdiction (state + district match)
2. ✅ Validates case is at stage 8
3. ✅ Records `PFMS_FINAL_TRANCHE` event in CASE_EVENTS
4. ✅ Stores fund release details (amount, txn_id, bank ack) in event_data
5. ✅ **Moves case to Stage 9** (case closed)
6. ✅ Sets `Pending_At` to empty (no further pending)

#### Response
```json
{
  "message": "Final Tranche released for case 101",
  "amount": 150000.00,
  "percent_of_total": 100,
  "txn_id": "TXN-2025-789456",
  "new_stage": 9,
  "pending_at": ""
}
```

#### Frontend Status Update
- Case moves from "Awaiting Final Tranche" → "Case Closed"
- Show final tranche transaction details
- Display completion date and total compensation released
- Lock case from further edits

---

## Complete Case Timeline (Example)

```
Stage 0: FIR Submitted by Investigation Officer
   ↓
Stage 1: Tribal Officer Verification (fund amount set: 500,000)
   ↓
Stage 2: DM Approval
   ↓
Stage 3: SNO Fund Sanction
   ↓
Stage 4: First Tranche Release (25% = 125,000) by PFMS
   ↓
Stage 5: Chargesheet Submitted by Investigation Officer
   ↓
Stage 6: Second Tranche Release (25-50% = 187,500) by PFMS
   ↓
Stage 7: Judgment Pending (DM reviews evidence)
   ├─ DM calls /complete with judgment details
   ↓
Stage 8: Judgment Complete (awaiting final tranche)
   ├─ PFMS calls /fund-release with final amount
   ↓
Stage 9: Case Closed ✓
```

---

## Error Cases & Handling

### Error 1: PFMS Tries to Release at Stage 7
**Problem**: PFMS calls `/fund-release` at stage 7
**Response**: 400 Bad Request
```json
{
  "detail": "Case is at stage 7, but this action requires stage [4, 6, 8]"
}
```
**Solution**: DM must call `/complete` first to move to stage 8

### Error 2: DM Tries to Complete at Wrong Stage
**Problem**: DM calls `/complete` but case is at stage 6
**Response**: 400 Bad Request
```json
{
  "detail": "Case is at stage 6, but completion requires stage 7"
}
```
**Solution**: Wait for chargesheet submission and second tranche release first

### Error 3: Wrong Role Tries to Record Judgment
**Problem**: Tribal Officer tries to call `/complete`
**Response**: 403 Forbidden
```json
{
  "detail": "Only District Collector/DM/SJO can complete a case"
}
```
**Solution**: Only DM can record judgment

### Error 4: PFMS Has No Jurisdiction
**Problem**: PFMS Officer from MP tries to release funds for case in Bihar
**Response**: 403 Forbidden
```json
{
  "detail": "Access denied: Case is in state 'Bihar', but you are assigned to 'Madhya Pradesh'"
}
```
**Solution**: Use correct PFMS officer for case's state/district

---

## Frontend Implementation Guide

### Case Status Display
```javascript
const stageStatus = {
  7: "Judgment Pending",
  8: "Awaiting Final Tranche",
  9: "Case Closed"
};

const stagePendingAt = {
  7: "District Collector/DM/SJO",
  8: "PFMS Officer for Final Tranche Release",
  9: ""
};
```

### Action Buttons
```javascript
// Show based on case stage and user role
if (stage === 7 && userRole === "District Collector/DM/SJO") {
  showButton("Record Judgment"); // Opens /complete endpoint form
}

if (stage === 8 && userRole === "PFMS Officer") {
  showButton("Release Final Tranche"); // Opens /fund-release endpoint form
}

if (stage === 9) {
  disableAllButtons("Case Closed");
  showCaseDetails("View-Only Mode");
}
```

### Event Timeline Display
```javascript
// Show events in chronological order
events.forEach(event => {
  if (event.event_type === "DM_JUDGMENT_RECORDED") {
    displayTimeline({
      date: event.created_at,
      actor: event.performed_by,
      action: "Judgment Recorded",
      details: {
        verdict: event.event_data.verdict,
        judgment_ref: event.event_data.judgment_ref,
        notes: event.event_data.notes
      }
    });
  }
  
  if (event.event_type === "PFMS_FINAL_TRANCHE") {
    displayTimeline({
      date: event.created_at,
      actor: event.performed_by,
      action: "Final Tranche Released",
      details: {
        amount: event.event_data.amount,
        txn_id: event.event_data.txn_id,
        bank_ack: event.event_data.bank_acknowledgement
      }
    });
  }
});
```

### Form Validation
```javascript
// /complete endpoint form (DM)
const completeFormSchema = {
  actor: "required | string",
  role: "required | must be 'District Collector/DM/SJO'",
  judgment_ref: "required | string | min 3 chars",
  judgment_date: "required | date format YYYY-MM-DD",
  verdict: "required | string | min 10 chars",
  notes: "optional | string"
};

// /fund-release endpoint form (PFMS at stage 8)
const fundReleaseFormSchema = {
  actor: "required | string",
  role: "required | must be 'PFMS Officer'",
  amount: "required | number | > 0",
  percent_of_total: "required | number | 100 (for final tranche)",
  fund_type: "required | string",
  txn_id: "required | string | unique transaction ID",
  bank_acknowledgement: "required | string"
};
```

---

## Data Persistence

### ATROCITY Table Updates
```
After DM records judgment (/complete):
- Stage: 7 → 8
- Pending_At: "PFMS Officer for Final Tranche Release"
- Approved_By: DM's login_id

After PFMS releases final tranche (/fund-release):
- Stage: 8 → 9
- Pending_At: (empty)
```

### CASE_EVENTS Table Entries
```
Event 1: DM_JUDGMENT_RECORDED
- case_no: 101
- performed_by: "dm_jabalpur_001"
- performed_by_role: "District Collector/DM/SJO"
- event_type: "DM_JUDGMENT_RECORDED"
- event_data: {
    judgment_ref: "JUDGMENT-2025-001",
    judgment_date: "2025-12-04",
    verdict: "Guilty - Compensation Awarded",
    notes: "All evidence reviewed..."
  }
- created_at: timestamp

Event 2: PFMS_FINAL_TRANCHE
- case_no: 101
- performed_by: "pfms_jabalpur_001"
- performed_by_role: "PFMS Officer"
- event_type: "PFMS_FINAL_TRANCHE"
- event_data: {
    amount: 150000.00,
    percent_of_total: 100,
    fund_type: "Final Compensation Tranche",
    txn_id: "TXN-2025-789456",
    bank_acknowledgement: "ACK-2025-001",
    tranche_label: "Final Tranche"
  }
- created_at: timestamp
```

---

## Quick Reference

| What | Who | Endpoint | Stage Change |
|------|-----|----------|--------------|
| Record Judgment | DM | `POST /{case_no}/complete` | 7 → 8 |
| Release Final Funds | PFMS | `POST /{case_no}/fund-release` | 8 → 9 |
| View Case Details | Any | `GET /get-fir-form-data/fir/{fir_no}` | — |
| View Timeline | Any | `GET /{case_no}/events` | — |

---

**Document Version**: 1.0  
**Last Updated**: December 4, 2025  
**Status**: Active
