# ICM Corrections PUT Endpoint - Usage Examples

## Quick Start

### Basic Example - Correcting a Single Field

```bash
# Fix groom's age
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -F "groom_age=30"
```

### Correcting Multiple Data Fields

```bash
# Correct groom and bride names
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "groom_name=Raj Kumar Singh" \
  -F "bride_name=Priya Sharma"
```

### Correcting With New Documents

```bash
# Update birth dates and marriage certificate
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "groom_dob=1995-08-20" \
  -F "bride_dob=1998-06-15" \
  -F "marriage_certificate=@/path/to/new_marriage_cert.pdf"
```

### Complete Correction Resubmission

```bash
# Correct groom details, bride details, and all signatures
curl -X PUT http://localhost:8000/icm/applications/1 \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "groom_name=Rajesh Kumar" \
  -F "groom_age=30" \
  -F "groom_current_address=123 Main St, Delhi" \
  -F "bride_name=Priya Singh" \
  -F "bride_age=28" \
  -F "bride_current_address=456 Oak Ave, Delhi" \
  -F "marriage_date=2025-03-14" \
  -F "groom_signature=@/path/to/groom_sign.jpg" \
  -F "bride_signature=@/path/to/bride_sign.jpg" \
  -F "witness_signature=@/path/to/witness_sign.jpg"
```

## Python Client Example

```python
import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIs..."  # Your JWT token
ICM_ID = 1

def resubmit_corrections(icm_id, corrections_data, file_paths=None):
    """
    Resubmit ICM application with corrections
    
    Args:
        icm_id: Application ID
        corrections_data: Dict of field corrections
        file_paths: Dict of file paths to upload
    """
    
    url = f"{API_URL}/icm/applications/{icm_id}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Prepare form data
    files = {}
    
    if file_paths:
        for field_name, file_path in file_paths.items():
            if Path(file_path).exists():
                files[field_name] = open(file_path, 'rb')
    
    try:
        response = requests.put(
            url,
            headers=headers,
            data=corrections_data,
            files=files
        )
        
        if response.status_code == 200:
            print("✓ Corrections resubmitted successfully!")
            print(response.json())
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.json())
            
    finally:
        # Close all file handles
        for f in files.values():
            f.close()

# Example Usage
corrections = {
    "groom_name": "Rajesh Kumar",
    "groom_age": 30,
    "bride_name": "Priya Singh",
    "marriage_date": "2025-03-14"
}

files = {
    "groom_signature": "/path/to/groom_sign.jpg",
    "bride_signature": "/path/to/bride_sign.jpg"
}

resubmit_corrections(ICM_ID, corrections, files)
```

## Response Examples

### Successful Resubmission (200 OK)

```json
{
  "icm_id": 1,
  "status": "resubmitted",
  "message": "Corrected application resubmitted successfully",
  "current_stage": 0,
  "pending_at": "Tribal Officer",
  "application_status": "Resubmitted",
  "files_updated": ["groom_signature_file", "bride_signature_file"],
  "data_fields_updated": ["groom_name", "groom_age", "bride_name", "marriage_date"]
}
```

### Application Not Found (404)

```json
{
  "detail": "ICM Application #999 not found"
}
```

### Not Application Owner (403)

```json
{
  "detail": "You can only resubmit your own applications"
}
```

### Wrong Status (400)

```json
{
  "detail": "Application must be in 'Correction Required' status. Current status: Approved"
}
```

## Workflow Timeline

### Before Correction Request (Officer Requests Corrections)
```
Application Status: "Under Review"
Current Stage: 1
Pending At: "Tribal Officer"
Event: "TO_CORRECTION_REQUESTED"
```

### After Correction Request (Waiting for Citizen to Resubmit)
```
Application Status: "Correction Required"
Current Stage: 0
Pending At: "Citizen"
Event: "TO_CORRECTION" (officer event)
```

### After Citizen Resubmits (Using PUT endpoint)
```
Application Status: "Resubmitted"
Current Stage: 0
Pending At: "Tribal Officer"
Event: "CORRECTION_RESUBMITTED" (citizen event)
```

### Officer Reviews Again
```
Application Status: "Under Review" (if approved/progresses)
Current Stage: 1 (or higher)
Pending At: "District Collector/DM" (or next role)
```

## Field Reference

### Groom Details
- `groom_name` - Full name
- `groom_age` - Age in years
- `groom_father_name` - Father's full name
- `groom_dob` - Date of birth (YYYY-MM-DD)
- `groom_aadhaar` - Aadhaar number
- `groom_caste_cert_id` - Caste certificate ID
- `groom_pre_address` - Previous address
- `groom_current_address` - Current address
- `groom_permanent_address` - Permanent address
- `groom_education` - Education details
- `groom_training` - Training/skills
- `groom_income` - Income level
- `groom_livelihood` - Livelihood details
- `groom_future_plan` - Future plans
- `groom_first_marriage` - Is first marriage? (boolean)

### Bride Details
- Similar fields as groom (replace `groom_` with `bride_`)

### Marriage Details
- `marriage_date` - Date of marriage (YYYY-MM-DD)
- `marriage_certificate_number` - Certificate number
- `previous_benefit_taken` - Any previous benefit? (boolean)

### Witness Details
- `witness_name` - Witness full name
- `witness_aadhaar` - Witness Aadhaar number
- `witness_address` - Witness address
- `witness_verified` - Witness verified? (boolean)

### Bank Details
- `joint_account_number` - Bank account number
- `joint_ifsc` - IFSC code
- `joint_account_bank_name` - Bank name

### Documents
- `marriage_certificate` - Marriage certificate file
- `groom_signature` - Groom's signature image
- `bride_signature` - Bride's signature image
- `witness_signature` - Witness's signature image

## Troubleshooting

### "Citizen ID missing from token"
- Token doesn't have citizen_id claim
- Ensure you're using citizen user's token
- Re-authenticate with citizen credentials

### "You can only resubmit your own applications"
- You're trying to modify another citizen's application
- Use the token of the original applicant

### "Application must be in 'Correction Required' status"
- Application is not in the correct status
- Check application timeline to see current status
- Only applications with "Correction Required" status can be resubmitted

### "ICM Application #X not found"
- Application ID doesn't exist
- Verify the correct application ID
- Check if it's deleted or archived

### File Upload Errors
- Ensure file path is correct
- Check file permissions
- Verify file size is within limits
- Use valid file formats (PDF, JPG, PNG, etc.)

## Important Notes

1. **Partial Updates:** You don't need to send all fields - only the ones being corrected
2. **Files Are Optional:** You can update data without files or files without data
3. **New Files Replace Old:** If you upload new files, they replace the previous versions
4. **Audit Trail:** All changes are logged with timestamp and user info
5. **Workflow Reset:** After resubmission, application goes back to initial review stage
6. **One Owner:** Only the original applicant can resubmit corrections
