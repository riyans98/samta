# Duplicate Row Fix - UPSERT Pattern Implementation

## Problem Identified

**Error**: Multiple endpoints throwing "Duplicate entry" or "duplicate key" errors when re-submitting or updating cases.

**Root Cause**: 
- `submit_fir` endpoint always uses `INSERT INTO ATROCITY` 
- When called multiple times with same FIR_NO, creates duplicate rows
- Subsequent API calls (approval, correction, chargesheet, etc.) should UPDATE existing rows, not INSERT

**Impact**: 
- Can't re-submit/update FIR after draft
- Can't re-attempt approval if request fails
- ATROCITY table has multiple rows for same FIR_NO
- Database integrity issues

---

## Solution Implemented: UPSERT Pattern

Modified `/dbt/case/submit_fir` endpoint to use **UPSERT** (Update if exists, Insert if not):

### Changes in `submit_fir_form` endpoint:

#### 1. Check for Existing FIR (Before Insert/Update)
```python
existing_case = get_fir_data_by_fir_no(firNumber)

if existing_case:
    # UPDATE existing record
    case_no = existing_case.Case_No
    update_atrocity_case(case_no, update_payload)
else:
    # INSERT new record
    response = insert_atrocity_case(db_payload)
    case_no = response.get("Case_No")
```

#### 2. Update Only Safe Fields
When updating existing FIR, only update workflow fields:
- `Stage`: Changes based on isDrafted
- `Pending_At`: Who should act next
- `Approved_By`: IO's login_id (metadata)

**Never re-insert:**
- FIR_NO, Victim details, Bank details (protected)
- These can only be changed via separate endpoint (if needed)

#### 3. Prevent Duplicate Events
```python
timeline = get_timeline(case_no)
fir_submitted_exists = any(event.event_type == "FIR_SUBMITTED" for event in timeline)

if not isDrafted and not fir_submitted_exists:
    # Insert FIR_SUBMITTED event only once
    insert_case_event(...)
```

#### 4. Indicate Update in Response
```json
{
  "case_no": 1001,
  "fir_no": "FIR-2025-001",
  "stage": 1,
  "pending_at": "Tribal Officer",
  "is_update": true,  // NEW: Indicates this was an update, not new insert
  "message": "FIR saved... Case #1001 updated."
}
```

---

## Flow Comparison

### BEFORE (Issue):
```
Call 1: POST /submit_fir?isDrafted=true, FIR-2025-001
  └─> INSERT into ATROCITY (Stage=0, Case_No=1001)

Call 2: POST /submit_fir?isDrafted=false, FIR-2025-001
  └─> INSERT into ATROCITY (Stage=1, Case_No=1002)  ❌ DUPLICATE ROW!
  
Database result:
  | Case_No | FIR_NO | Stage |
  | 1001 | FIR-2025-001 | 0 |
  | 1002 | FIR-2025-001 | 1 |  ← DUPLICATE!
```

### AFTER (Fixed):
```
Call 1: POST /submit_fir?isDrafted=true, FIR-2025-001
  └─> Case doesn't exist → INSERT (Case_No=1001, Stage=0)

Call 2: POST /submit_fir?isDrafted=false, FIR-2025-001
  └─> Case exists → UPDATE (Case_No=1001, Stage=1)  ✓ SAME ROW!
  
Database result:
  | Case_No | FIR_NO | Stage |
  | 1001 | FIR-2025-001 | 1 |  ← UPDATED, NOT DUPLICATED
```

---

## API Response Changes

### Response Structure (Enhanced):
```json
{
  "case_no": 1001,
  "fir_no": "FIR-2025-001",
  "stage": 1,
  "pending_at": "Tribal Officer",
  "is_drafted": false,
  "is_update": true,        // NEW FIELD: Indicates update vs create
  "message": "FIR saved as submitted successfully. Case #1001 updated."
}
```

**New Field Explanation:**
- `is_update: true` = This was an UPDATE (FIR already existed)
- `is_update: false` = This was an INSERT (new FIR)

---

## Testing Scenarios

### ✅ Scenario 1: Draft → Submit (Same FIR)
```
Request 1: POST /dbt/case/submit_fir?isDrafted=true
  Body: { firNumber: "FIR-2025-001", ... }
  
Response 1:
  {
    "case_no": 1001,
    "stage": 0,
    "is_update": false,
    "message": "... Case #1001 created."
  }

Request 2: POST /dbt/case/submit_fir?isDrafted=false
  Body: { firNumber: "FIR-2025-001", ... }  // Same FIR!
  
Response 2:
  {
    "case_no": 1001,  // SAME case_no!
    "stage": 1,
    "is_update": true,  // Now it's an update
    "message": "... Case #1001 updated."
  }

Database: Only 1 row for FIR-2025-001 ✓
```

### ✅ Scenario 2: Retry Submission (Network Failure)
```
Request 1: POST /dbt/case/submit_fir (fails due to network)

Request 2: POST /dbt/case/submit_fir (retry, same data)

Response:
  {
    "case_no": 1001,
    "is_update": true,  // Already exists, updated safely
    "message": "... Case #1001 updated."
  }

No duplicate rows created ✓
```

### ✅ Scenario 3: Multiple FIRs
```
Request 1: FIR-2025-001 → Case_No=1001
Request 2: FIR-2025-002 → Case_No=1002  (new row, different FIR)
Request 3: FIR-2025-001 (retry) → Case_No=1001 (update same)

Database:
  | Case_No | FIR_NO |
  | 1001 | FIR-2025-001 |
  | 1002 | FIR-2025-002 |
  
No duplicates for same FIR ✓
```

---

## Code Implementation Details

### Updated Fields During UPSERT:
```python
update_payload = {
    "Stage": 0 if isDrafted else 1,           # Changes with isDrafted
    "Pending_At": 'Investigation Officer' if isDrafted else 'Tribal Officer',
    "Approved_By": token_payload.get('sub')   # IO's login_id
}
```

### Unchanged Fields (Protected):
- FIR_NO, Victim details, Bank details
- Only INSERT sets these, UPDATE never touches them
- Prevents accidental data overwrites

### Event Deduplication:
```python
timeline = get_timeline(case_no)
fir_submitted_exists = any(event.event_type == "FIR_SUBMITTED" for event in timeline)

# Only insert if doesn't already exist
if not isDrafted and not fir_submitted_exists:
    insert_case_event(...)
```

---

## Files Modified

| File | Change | Lines |
|------|--------|-------|
| `app/routers/dbt.py` | Updated `submit_fir_form` to use UPSERT pattern | 418-462 |

## Database Query Changes

### Before (Always INSERT):
```sql
INSERT INTO ATROCITY (columns...) VALUES (values...)
-- Can create duplicates if called multiple times
```

### After (Check then INSERT or UPDATE):
```sql
-- First: Check if FIR_NO exists
SELECT * FROM ATROCITY WHERE FIR_NO = %s

-- If exists: UPDATE
UPDATE ATROCITY SET Stage=%s, Pending_At=%s WHERE Case_No=%s

-- If not exists: INSERT
INSERT INTO ATROCITY (columns...) VALUES (values...)
```

---

## Event Handling (No Duplicates)

### Before:
```
Submit 1: FIR_SUBMITTED event created (Event_ID=101)
Submit 2: FIR_SUBMITTED event created (Event_ID=102) ❌ DUPLICATE EVENT
```

### After:
```
Submit 1: FIR_SUBMITTED event created (Event_ID=101)
Submit 2: Check timeline → FIR_SUBMITTED exists → Skip ✓ NO DUPLICATE
```

---

## Backward Compatibility

✅ **No Breaking Changes:**
- isDrafted parameter works as before
- Response still includes all original fields
- Only adds `is_update` field (additive, not breaking)
- Existing clients that ignore `is_update` still work

✅ **Graceful Handling:**
- Repeated calls with same FIR: Updates instead of error
- Network retry scenarios: Safe idempotent behavior
- Different FIRs: Still creates new rows as expected

---

## Verification Queries

### Check for Duplicates:
```sql
SELECT FIR_NO, COUNT(*) as count 
FROM ATROCITY 
GROUP BY FIR_NO 
HAVING count > 1;

-- Expected result: EMPTY (no duplicates)
```

### Check Event Deduplication:
```sql
SELECT CASE_NO, Event_Type, COUNT(*) as count 
FROM CASE_EVENTS 
GROUP BY CASE_NO, Event_Type 
HAVING count > 1;

-- Expected result: EMPTY (no duplicate events)
```

### Check Latest Case per FIR:
```sql
SELECT FIR_NO, MAX(Case_No) as latest_case_no, Stage, Pending_At 
FROM ATROCITY 
GROUP BY FIR_NO 
ORDER BY FIR_NO;

-- Shows 1 row per FIR, with latest stage
```

---

## Summary

✅ **Problem Solved**: No more duplicate rows on re-submission  
✅ **Safe Updates**: Only workflow fields updated, data protected  
✅ **Event Deduplication**: FIR_SUBMITTED only recorded once  
✅ **Backward Compatible**: Existing clients work unchanged  
✅ **Idempotent**: Retry-safe, network-resilient  

**Result**: Cases can now be re-submitted, draft→submit, and updated safely without creating duplicate database rows.
