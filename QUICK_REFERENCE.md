# ICM PUT Endpoint - Quick Reference Card

## 📍 Endpoint Location
```
PUT /icm/applications/{icm_id}
```

## 🔐 Authentication
```
Authorization: Bearer <JWT_TOKEN>
```

## 📋 Content Type
```
multipart/form-data
```

## ✅ Success Response
```json
{
  "icm_id": 1,
  "status": "resubmitted",
  "message": "Corrected application resubmitted successfully",
  "current_stage": 0,
  "pending_at": "Tribal Officer",
  "application_status": "Resubmitted",
  "files_updated": [...],
  "data_fields_updated": [...]
}
```

## ❌ Error Responses

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Wrong status | "Application must be in 'Correction Required' status..." |
| 401 | No JWT/citizen_id | "Citizen ID missing from token" |
| 403 | Not owner | "You can only resubmit your own applications" |
| 404 | Not found | "ICM Application #X not found" |
| 500 | Server error | "Failed to resubmit corrected application..." |

## 📝 Form Fields (All Optional)

### Groom (15 fields)
```
groom_name, groom_age, groom_father_name, groom_dob, groom_aadhaar,
groom_pre_address, groom_current_address, groom_permanent_address,
groom_caste_cert_id, groom_education, groom_training, groom_income,
groom_livelihood, groom_future_plan, groom_first_marriage
```

### Bride (15 fields)
```
bride_name, bride_age, bride_father_name, bride_dob, bride_aadhaar,
bride_pre_address, bride_current_address, bride_permanent_address,
bride_caste_cert_id, bride_education, bride_training, bride_income,
bride_livelihood, bride_future_plan, bride_first_marriage
```

### Marriage (3 fields)
```
marriage_date, marriage_certificate_number, previous_benefit_taken
```

### Witness (4 fields)
```
witness_name, witness_aadhaar, witness_address, witness_verified
```

### Bank (3 fields)
```
joint_account_number, joint_ifsc, joint_account_bank_name
```

### Files (4 fields)
```
marriage_certificate, groom_signature, bride_signature, witness_signature
```

## 🚀 Quick Examples

### Single Field Update
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "groom_name=Rajesh Kumar"
```

### Multiple Fields
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "groom_age=30" \
  -F "bride_name=Priya" \
  -F "marriage_date=2025-03-14"
```

### With Files
```bash
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "groom_age=30" \
  -F "groom_signature=@signature.jpg" \
  -F "bride_signature=@signature.jpg"
```

## 🔄 Workflow State Changes

| Before | After |
|--------|-------|
| Status: "Correction Required" | Status: "Resubmitted" |
| Stage: 0 | Stage: 0 (reset) |
| Pending At: "Citizen" | Pending At: "Tribal Officer" |

## 📊 Timeline Event

```
event_type: "CORRECTION_RESUBMITTED"
event_role: "Citizen"
event_stage: 0
event_data: {
  action: "resubmitted_corrections",
  files_updated: [...],
  data_fields_updated: [...],
  previous_stage: <number>
}
```

## ⚠️ Important Notes

1. **All fields optional** - Partial updates supported
2. **Ownership required** - Only applicant can resubmit
3. **Status check** - Must be "Correction Required"
4. **Files optional** - Update data without files or vice versa
5. **New files replace old** - Previous versions overwritten
6. **JWT required** - Every request needs authentication
7. **One owner** - Application owner can only resubmit their own

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check JWT token validity, ensure citizen_id in token |
| 403 Forbidden | Ensure you're using applicant's token, not another user |
| 400 Bad Request | Check application status is "Correction Required" |
| 404 Not Found | Verify application ID is correct |
| File error | Check file size/format/permissions |

## 📚 Documentation

- Full Documentation: `ICM_CORRECTIONS_PUT_ENDPOINT.md`
- Examples & Troubleshooting: `ICM_CORRECTIONS_EXAMPLES.md`
- Code Reference: `CODE_REFERENCE.md`
- Visual Diagrams: `VISUAL_SUMMARY.md`
- API Docs: `ICM_API_DOCUMENTATION.md` (section 4)

## 🔍 Verification Checklist

Before using in production:

- [ ] JWT token is valid
- [ ] citizen_id in token
- [ ] Application exists (correct ID)
- [ ] Application status is "Correction Required"
- [ ] You are the application owner
- [ ] Files are valid format/size
- [ ] Form field names are correct
- [ ] Required headers are set

## 📞 HTTP Status Reference

```
200 OK              - Correction resubmitted successfully
400 Bad Request     - Application status or data invalid
401 Unauthorized    - Authentication required/invalid
403 Forbidden       - Authorization failed (not owner)
404 Not Found       - Application doesn't exist
500 Server Error    - Database or file operation failed
```

## 🔑 Key Differences: POST vs PUT

| Feature | POST (Submit) | PUT (Corrections) |
|---------|---------------|------------------|
| Purpose | New application | Corrections |
| Required fields | All | None (all optional) |
| File requirement | All required | Optional |
| Update type | Full | Partial |
| Status change | Pending | Resubmitted |
| Stage | Starts at 0 | Resets to 0 |

## 💡 Pro Tips

1. **Partial updates are powerful** - Only send fields that changed
2. **Test with curl first** - Verify before client integration
3. **Check timeline** - View events to verify resubmission
4. **Keep JWT fresh** - Refresh token if expired
5. **Monitor logs** - Check application logs for issues
6. **Use correct IDs** - Always verify application ID
7. **Date format** - Always use YYYY-MM-DD for dates

## 🎯 Expected Workflow

```
1. Officer requests correction
   → Application status: "Correction Required"

2. Citizen receives correction request
   → Prepares corrected data

3. Citizen calls PUT endpoint
   PUT /icm/applications/1
   → Application status: "Resubmitted"

4. Officer reviews again
   → Continues approval process

5. Final approval and fund release
   → Application status: "Completed"
```

## 📱 Python Quick Example

```python
import requests

response = requests.put(
    "http://localhost:8000/icm/applications/1",
    headers={"Authorization": f"Bearer {token}"},
    data={"groom_name": "New Name", "groom_age": 30},
    files={
        "groom_signature": open("sig.jpg", "rb"),
        "bride_signature": open("sig2.jpg", "rb")
    }
)

if response.status_code == 200:
    print("✓ Success:", response.json())
else:
    print("✗ Error:", response.status_code, response.json())
```

---

**Last Updated:** December 8, 2025  
**Quick Reference Version:** 1.0
