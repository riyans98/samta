
---

# BACKEND COPILOT TASK: FINALIZE ICM FILES + FLOW

## High-level summary

1. Make the **apply** endpoint accept multipart data (JSON + files) and persist files: `marriage_certificate`, `joint_photo`, `groom_signature`, `bride_signature`, `witness_signature`, `joint_passbook`.
2. Store files in structured folders under `/uploads/icm/` and save relative URLs in the `icm_applications` record.
3. Add/ensure `append_icm_event(...)` is called for all state changes (submit, approve, correction, reject, pfms release).
4. Implement a **declaration HTML** route (`GET /icm/{icm_id}/declaration`) that renders a server-side HTML template (no PDF saved) and is printable via browser.
5. Implement full role-based approval endpoints with jurisdiction checks and stage transitions, creating events for each action.
6. Implement small validation rules (duplicate couple check, aadhaar existence, stage checks, PFMS amount check).
7. Keep witness OTP simulated: accept witness_aadhaar and `witness_verified` flag from frontend (backend must not send OTP in prototype).

---

## 1) Files & paths to add / update

**Files to create/update:**

* `intercaste_marriage/storage.py` — helper functions for file saving & URL generation.
* `intercaste_marriage/services.py` — business logic (create application, save files, approve, correction, append_event, pfms_release).
* `intercaste_marriage/templates/declaration.html` — HTML template for the declaration form (Form B).
* update `app/routers/icm.py` if necessary to accept files for apply and add declaration route `GET /icm/{icm_id}/declaration`.
* optionally `intercaste_marriage/utils.py` — small helpers: validate_ifsc_format, validate_aadhaar_exists, unique_couple_check.

---

## 2) Storage design (exact rules)

**Base upload dir (configurable)**:

```
UPLOAD_ROOT = /var/www/uploads/icm   # or config.UPLOAD_ROOT
BASE_URL = https://<your-host>/uploads/icm  # or use StaticFiles mount
```

**Subfolders (create if missing):**

```
marriage_certs/
joint_photos/
signatures/groom/
signatures/bride/
signatures/witness/
passbook/
declaration_template/  # store generated HTML copies if you want optional cache
```

**Filenames**: sanitize + deterministic:

```
icm_{icm_id}_{field}_{uuid4().hex}.{ext}
examples:
icm_123_marriage_cert_e6f3b2.pdf
icm_123_groom_signature_8a1f3.png
```

**Saving helper API (storage.py)**:

```py
def save_icm_file(icm_id: int, file: UploadFile, subdir: str) -> str:
    # create dir if missing
    # compute filename = f"icm_{icm_id}_{subdir}_{uuid4().hex}.{ext}"
    # save to disk
    # return relative_url (e.g., f"/uploads/icm/{subdir}/{filename}")
```

**Serve files**: Use FastAPI `StaticFiles` mount or return `FileResponse` for authenticated endpoints. For prototype, returning relative URL that is publicly accessible is OK if you mount static folder; otherwise return `FileResponse` via an authenticated route.

---

## 3) Apply endpoint changes (multipart)

**Current route** `POST /icm/applications` (you already have a JSON version). Replace/overload it with a multipart version that accepts files.

**New route signature** (FastAPI):

```py
from fastapi import File, UploadFile, Form

@router.post("/applications", status_code=201)
async def submit_icm_application(
    groom_name: str = Form(...),
    groom_aadhaar: int = Form(...),
    bride_name: str = Form(...),
    bride_aadhaar: int = Form(...),
    marriage_date: str = Form(...),
    joint_account_number: str = Form(...),
    # optional fields as Form(...)
    marriage_certificate: UploadFile = File(...),
    joint_photo: UploadFile = File(...),
    groom_signature: UploadFile = File(...),
    bride_signature: UploadFile = File(...),
    witness_signature: Optional[UploadFile] = File(None),
    joint_passbook: Optional[UploadFile] = File(None),
    token_payload: dict = Depends(verify_jwt_token)
):
    ...
```

**Behaviour**:

* Validate logged-in citizen (citizen_id), ensure applicant_aadhaar equals token aadhaar OR allow citizens to apply for couple using either spouse (decide policy; choose: allow any logged-in citizen to apply if one of groom/bride matches token.aadhaar).
* Validate that `groom_aadhaar` and `bride_aadhaar` exist in `aadhaar_records` (call `validate_aadhaar_exists`).
* Check duplicate couple:

  ```py
  if exists icm_applications where (groom==g_aadhaar and bride==b_aadhaar) OR (groom==b_aadhaar and bride==g_aadhaar) and status not in ('Rejected','Completed'):
      raise HTTPException(409, "Application already exists for this couple")
  ```
* Create DB row with fields except file paths.
* Save files via `save_icm_file(icm_id, uploadfile, subdir)` and update DB record with returned file URLs.
* If witness provided: do NOT perform real OTP. Set `witness_verified = False` until frontend simulates OTP; store witness_aadhaar and optionally witness_name resolved from `aadhaar_records` if present.
* Insert event `APPLICATION_SUBMITTED` (role=CITIZEN, stage=0) with `event_data` including file paths and metadata.

Return created `icm_id`, `current_stage`, `pending_at`.

---

## 4) Declaration HTML (printable) route

**Endpoint**:

```
GET /icm/{icm_id}/declaration
```

**Behaviour**:

* Verify requestor has access (owner or officer in jurisdiction).
* Load `icm_application` record.
* Render server-side HTML from template `templates/declaration.html` filling fields:

  * Groom full name & address
  * Bride full name & address
  * Date
  * Witness area blank (signature block)
  * "Declaration text" exactly as in Form B (you can copy text from the scanned form)
* Return `HTMLResponse(content=rendered_html)` so browser shows it and user can print (Ctrl+P). No PDF file to be stored.
* Optionally add header/footers, `icm_id` and `generated_at` in footer.
* For front-end convenience, also return `Content-Disposition: inline; filename="declaration_icm_{icm_id}.html"`

**Template notes**: Keep simple bootstrap CSS for print formatting.

---

## 5) Approval & event tracking implementation (services.py)

**Key functions to ensure exist or create/update:**

* `append_icm_event(icm_id, event_type, event_role, event_stage, comment=None, event_data=None)` — insert into `icm_events`.
* `create_icm_application(app_data)` — create DB row and return icm record.
* `approve_icm_application(icm_id, actor, role, comment=None)` — central function that:

  * loads application
  * checks role is allowed to act at current stage (map below)
  * check jurisdiction of actor (token role state/district) -> if mismatch raise 403
  * update `current_stage`, `pending_at`, `application_status` per transition table below
  * call `append_icm_event(...)`
  * return updated record
* `reject_icm_application(icm_id, actor, role, reason)` — sets `application_status='Rejected'`, `pending_at=NULL`, append event DM_REJECTED (role=DM).
* `request_icm_correction(icm_id, actor, role, corrections_required, comment)` — sets `current_stage=0`, `pending_at='CITIZEN'`, append `*_CORRECTION` event.

**Stage mapping (use exact names in code):**

```
0 -> Submitted (pending_at='ADM')
1 -> Under ADM Review
2 -> Under TO Review
3 -> Under DM Review
4 -> Under SNO Review
5 -> Under PFMS (fund release)
6 -> Completed (application_status='Completed')
```

(You can keep stage numbers flexible; above is canonical. Ensure approve transitions increment stage appropriately.)

**Role->Stage allowed actions (enforce in approve_icm_application):**

* ADM: can act when current_stage == 0; on approve => set current_stage = 2 (TO)
* TO: can act when current_stage == 2; on approve => set current_stage = 3 (DM)
* DM: can act when current_stage == 3; on approve => set current_stage = 4 (SNO) or reject => set application_status='Rejected'
* SNO: can act when current_stage == 4; on approve => set current_stage = 5 (PFMS)
* PFMS: can act when current_stage == 5; on fund release => set current_stage = 6, application_status='Completed'
* Officers may request corrections: allowed roles call `request_icm_correction` which sets `current_stage=0` and `pending_at='CITIZEN'`.

**Event types**:
Use consistent strings:
`APPLICATION_SUBMITTED`, `ADM_APPROVED`, `ADM_CORRECTION`, `TO_APPROVED`, `TO_CORRECTION`, `DM_APPROVED`, `DM_REJECTED`, `SNO_APPROVED`, `PFMS_FUND_RELEASED`, `APPLICATION_COMPLETED`.

**PFMS fund release**: `pfms_release(icm_id, actor, role, amount, txn_id, bank_ref)`:

* Validate current stage==5
* Validate amount equals configured grant (default 250000) OR allow configurable amount
* Append `PFMS_FUND_RELEASED` event with `event_data={'amount': amount, 'txn_id': txn_id, 'bank_ref': bank_ref}`
* Set `current_stage=6` and `application_status='Completed'` and `pending_at='COMPLETED'`

---

## 6) Jurisdiction checks (server-side required)

**Rule enforcement** (extract user fields from JWT):

* ADM/TO/DM: `application.district == user.district and application.state_ut == user.state_ut`
* SNO: `application.state_ut == user.state_ut`
* PFMS: `application.state_ut == user.state_ut` (or global if PFMS is pan-state)
* Citizen: allow only if `token.aadhaar == groom_aadhaar or token.aadhaar == bride_aadhaar or token.citizen_id == application.citizen_id`

If mismatch return `HTTP 403` and JSON `{"detail": "Access denied: jurisdiction mismatch"}`.

---

## 7) Witness OTP simulation

**Frontend will show OTP UI but backend should not send SMS** (prototype). Back-end behaviour:

* Accept `witness_aadhaar` (optional) and `witness_verified` boolean in apply and in a `PATCH /icm/{icm_id}/witness-verify` if you want to allow marking verified.
* For prototype: when frontend sends `witness_verified = true`, accept it but log a warning `logger.info("Prototype: witness verified flag set without OTP")`.
* For production later: add SMS gateway integration and verification flow.

---

## 8) Validation & anti-fraud checks

At minimum validate on apply:

* Aadhaar existence for groom and bride:

  * call existing `aadhaar_records` table
* Caste certificate presence (if required by scheme) via `caste_certificate_data` table and ensure at least one spouse has SC/ST category
* joint account validation: check `npci_bank_kyc` simulated table:

  * must be `account_type == 'JOINT'`
  * primary and secondary Aadhaar must match groom & bride Aadhaar (or names fuzzy match)
* duplicate couple: enforce unique couple check (see earlier)
* file types allowed: `['image/png','image/jpeg','application/pdf']` for certs; signatures best as image; apply file size limit (e.g., 10MB)

If any validation fails return `400` with helpful message; if duplicate then `409`.

---

## 9) Events & timeline retrieval

You already have `get_icm_events_by_application` — ensure:

* Events are returned ascending by `created_at`.
* Each event has: `event_id`, `event_type`, `event_role`, `event_stage`, `comment`, `event_data`, `created_at`.

When any state change occurs, call `append_icm_event` with meaningful `event_data` for fund release, corrections_required array, or file updates.

---

## 10) Declaration HTML template (exact details)

Create `intercaste_marriage/templates/declaration.html` — include placeholders:

```
{{ groom_name }}, {{ groom_current_address }}, {{ bride_name }}, {{ bride_current_address }}, {{ marriage_date }}, {{ icm_id }}, {{ generated_at }}
```

Include the declaration paragraphs from the form and signature blocks (groom, bride, witness). Add print CSS:

```html
@media print {
  /* hide nav, buttons */
}
```

Expose route `GET /icm/{icm_id}/declaration` rendering this template.

---

## 11) Routes to add/update (explicit list)

* `POST /icm/applications` — multipart/form-data apply (see section 3)
* `GET /icm/applications` — citizen list (already exists)
* `GET /icm/applications/{icm_id}` — details + timeline (already exists)
* `GET /icm/{icm_id}/declaration` — new HTML render route (print)
* `POST /icm/applications/{icm_id}/approve` — already exists; ensure it calls `approve_icm_application` with role mapping & events
* `POST /icm/applications/{icm_id}/request-correction` — already exists; ensure behavior resets to citizen
* `POST /icm/applications/{icm_id}/reject` — ensure DM only
* `POST /icm/applications/{icm_id}/pfms/release` — new or adjust existing PFMS action endpoint to accept amount & txn_id and append event
* `GET /icm/applications/{icm_id}/timeline` — already exists; ensure sorted ascending

---

## 12) Error codes & messages (be explicit)

* 201 Created — new application created
* 200 OK — successful approve/correction/reject/release
* 400 Bad Request — validation errors (list all missing / invalid fields)
* 401 Unauthorized — invalid token
* 403 Forbidden — jurisdiction or role mismatch
* 404 Not Found — icm_id not found
* 409 Conflict — duplicate couple / already completed
* 500 Server Error — unexpected

---

## 13) Tests to add/maintain (minimal)

* `test_icm_apply_with_files` — ensure files are stored and DB updated, APPLICATION_SUBMITTED event created.
* `test_duplicate_icm_returns_409`
* `test_officer_approve_jurisdiction_enforced`
* `test_pfms_release_creates_event_and_marks_complete`
* `test_declaration_route_renders_html_and_returns_200`

---

## 14) Logging & Security notes (must include)

* Log every action: `logger.info(f"ICM action: {action}, icm_id={icm_id}, user={actor}, role={role}")`
* Save file paths as relative path and return URLs via `url_for` or static mount.
* Sanitize and limit file uploads.
* Do not send OTP from backend in prototype.

---

## 15) Example pseudo-workflow in code (service snippet)

```py
def create_icm_application(data, files, citizen_id):
    # 1. insert row with provided data (without file paths)
    icm = insert_icm_row(data)
    icm_id = icm.icm_id

    # 2. save files and update icm record
    if files.get('marriage_certificate'):
        url = save_icm_file(icm_id, files['marriage_certificate'], 'marriage_certs')
        update_icm_field(icm_id, marriage_certificate_file=url)
    ...
    # 3. append event
    append_icm_event(icm_id, 'APPLICATION_SUBMITTED', 'CITIZEN', 0, comment=None,
                     event_data={'files':[...], 'applicant_aadhaar': data['applicant_aadhaar']})
    return get_icm_application_by_id(icm_id)
```

---

## Final notes for Copilot

* Use existing functions where available (`create_icm_application`, `get_user_icm_applications`) and extend them to handle file saving & events.
* Keep field names identical to `icm_schemas.py` and DB column names.
* Implement jurisdiction checks centrally in a helper `assert_jurisdiction(user, icm_record)` to avoid duplication.
* Keep declaration as HTML render (no PDF stored).
* Witness OTP is simulated; log this clearly.

---
