# API Documentation - New Endpoints

This document provides comprehensive documentation for all new API endpoints created during this development session.

---

## Table of Contents

1. [Government Database APIs](#government-database-apis)
2. [Citizen Authentication & Profile APIs](#citizen-authentication--profile-apis)
3. [DBT Case Management APIs](#dbt-case-management-apis)

---

## Government Database APIs

These APIs provide access to government records from the GOVT database (Aadhaar, FIR, Caste Certificates, and NPCI Bank KYC records).

### Base Database: GOVT_DB

Located in: `app/db/govt_session.py`

---

## Caste Certificate APIs

### 1. Get Caste Certificate by ID

**Function:** `get_caste_certificate_by_id(certificate_id: str)`

**Description:** Fetches a single caste certificate record by certificate ID.

**Parameters:**
- `certificate_id` (str, required): The unique certificate ID

**Returns:** `Optional[CasteCertificate]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_caste_certificate_by_id

cert = get_caste_certificate_by_id("CERT-2025-001")
```

---

### 2. Get Caste Certificates by Aadhaar

**Function:** `get_caste_certificates_by_aadhaar(aadhaar_number: int)`

**Description:** Fetches all caste certificates associated with a given Aadhaar number.

**Parameters:**
- `aadhaar_number` (int, required): The Aadhaar number

**Returns:** `List[CasteCertificate]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_caste_certificates_by_aadhaar

certificates = get_caste_certificates_by_aadhaar(123456789012)
```

---

### 3. Get Caste Certificates by Person Name

**Function:** `get_caste_certificates_by_person_name(person_name: str)`

**Description:** Fetches caste certificates by person name with partial match support.

**Parameters:**
- `person_name` (str, required): Person's name (supports partial matches)

**Returns:** `List[CasteCertificate]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_caste_certificates_by_person_name

certificates = get_caste_certificates_by_person_name("Rajesh")
```

---

### 4. Get Caste Certificates by Category

**Function:** `get_caste_certificates_by_category(caste_category: str)`

**Description:** Fetches caste certificates filtered by caste category.

**Parameters:**
- `caste_category` (str, required): Category code (SC, ST, OBC, General)

**Returns:** `List[CasteCertificate]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_caste_certificates_by_category

certificates = get_caste_certificates_by_category("SC")
```

---

### 5. Get Caste Certificates by Status

**Function:** `get_caste_certificates_by_status(status_filter: str)`

**Description:** Fetches caste certificates filtered by certificate status.

**Parameters:**
- `status_filter` (str, required): Status (active, pending, expired, etc.)

**Returns:** `List[CasteCertificate]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_caste_certificates_by_status

certificates = get_caste_certificates_by_status("active")
```

---

### 6. Get All Caste Certificates with Filters

**Function:** `get_all_caste_certificates(filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0)`

**Description:** Fetches all caste certificates with optional filters and pagination support.

**Parameters:**
- `filters` (Dict[str, Any], optional): Filter dictionary with keys:
  - `caste_category` (str): Category filter
  - `certificate_status` (str): Status filter
  - `aadhaar_number` (int): Aadhaar filter
  - `issuing_authority` (str): Authority filter
- `limit` (int, default=100): Maximum records to return
- `offset` (int, default=0): Number of records to skip for pagination

**Returns:** `List[CasteCertificate]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_all_caste_certificates

# Fetch with pagination
certificates = get_all_caste_certificates(limit=50, offset=0)

# Fetch with filters
filters = {
    "caste_category": "ST",
    "certificate_status": "active"
}
certificates = get_all_caste_certificates(filters=filters, limit=25)
```

---

## NPCI Bank KYC APIs

### 1. Get NPCI Bank KYC by ID

**Function:** `get_npci_kyc_by_id(kyc_id: str)`

**Description:** Fetches a single NPCI Bank KYC record by KYC ID.

**Parameters:**
- `kyc_id` (str, required): The unique KYC ID

**Returns:** `Optional[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_id

kyc = get_npci_kyc_by_id("KYC-2025-001")
```

---

### 2. Get NPCI Bank KYC by Account Number

**Function:** `get_npci_kyc_by_account_number(account_number: str)`

**Description:** Fetches NPCI Bank KYC records by bank account number.

**Parameters:**
- `account_number` (str, required): Bank account number

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_account_number

kyc_records = get_npci_kyc_by_account_number("1234567890123456")
```

---

### 3. Get NPCI Bank KYC by Primary Aadhaar

**Function:** `get_npci_kyc_by_primary_aadhaar(primary_aadhaar: int)`

**Description:** Fetches NPCI Bank KYC records by primary account holder's Aadhaar number.

**Parameters:**
- `primary_aadhaar` (int, required): Primary holder's Aadhaar number

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_primary_aadhaar

kyc_records = get_npci_kyc_by_primary_aadhaar(123456789012)
```

---

### 4. Get NPCI Bank KYC by Secondary Aadhaar

**Function:** `get_npci_kyc_by_secondary_aadhaar(secondary_aadhaar: int)`

**Description:** Fetches NPCI Bank KYC records by secondary account holder's Aadhaar number.

**Parameters:**
- `secondary_aadhaar` (int, required): Secondary holder's Aadhaar number

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_secondary_aadhaar

kyc_records = get_npci_kyc_by_secondary_aadhaar(123456789012)
```

---

### 5. Get NPCI Bank KYC by Bank Name

**Function:** `get_npci_kyc_by_bank_name(bank_name: str)`

**Description:** Fetches NPCI Bank KYC records by bank name.

**Parameters:**
- `bank_name` (str, required): Name of the bank

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_bank_name

kyc_records = get_npci_kyc_by_bank_name("State Bank of India")
```

---

### 6. Get NPCI Bank KYC by Status

**Function:** `get_npci_kyc_by_status(kyc_status: str)`

**Description:** Fetches NPCI Bank KYC records by KYC verification status.

**Parameters:**
- `kyc_status` (str, required): Status (verified, pending, rejected)

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_status

kyc_records = get_npci_kyc_by_status("verified")
```

---

### 7. Get NPCI Bank KYC by IFSC Code

**Function:** `get_npci_kyc_by_ifsc_code(ifsc_code: str)`

**Description:** Fetches NPCI Bank KYC records by IFSC code.

**Parameters:**
- `ifsc_code` (str, required): Bank IFSC code

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_ifsc_code

kyc_records = get_npci_kyc_by_ifsc_code("SBIN0001234")
```

---

### 8. Get NPCI Bank KYC by Primary Holder Name

**Function:** `get_npci_kyc_by_primary_holder_name(holder_name: str)`

**Description:** Fetches NPCI Bank KYC records by primary account holder name with partial match support.

**Parameters:**
- `holder_name` (str, required): Primary holder's name (supports partial matches)

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_npci_kyc_by_primary_holder_name

kyc_records = get_npci_kyc_by_primary_holder_name("Rajesh")
```

---

### 9. Get All NPCI Bank KYC with Filters

**Function:** `get_all_npci_kyc(filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0)`

**Description:** Fetches all NPCI Bank KYC records with optional filters and pagination support.

**Parameters:**
- `filters` (Dict[str, Any], optional): Filter dictionary with keys:
  - `bank_name` (str): Bank name filter
  - `kyc_status` (str): KYC status filter
  - `primary_aadhaar` (int): Primary Aadhaar filter
  - `account_type` (str): Account type filter (JOINT, SAVINGS, etc.)
  - `primary_caste_category` (str): Caste category filter
- `limit` (int, default=100): Maximum records to return
- `offset` (int, default=0): Number of records to skip for pagination

**Returns:** `List[NPCIBankKYC]`

**Example Usage (Python):**
```python
from app.db.govt_session import get_all_npci_kyc

# Fetch with pagination
kyc_records = get_all_npci_kyc(limit=50, offset=0)

# Fetch with filters
filters = {
    "bank_name": "ICICI Bank",
    "kyc_status": "verified",
    "account_type": "SAVINGS"
}
kyc_records = get_all_npci_kyc(filters=filters, limit=25)
```

---

## Citizen Authentication & Profile APIs

These APIs handle citizen user authentication, profile management, and access to enriched Aadhaar data.

Located in: `app/routers/auth.py`

### Base URL: `/` (No prefix)

---

### 1. Citizen Login

**Endpoint:** `POST /citizen/login`

**Description:** Authenticates a citizen user using login credentials and returns JWT token with user profile.

**Request Body:**
```json
{
  "login_id": "citizen_user123",
  "password": "plain_text_password"
}
```

**Response (200 OK):**
```json
{
  "citizen_id": 1,
  "login_id": "citizen_user123",
  "aadhaar_number": 123456789012,
  "caste_certificate_id": "CERT-2025-001",
  "full_name": "John Doe",
  "mobile_number": "9876543210",
  "email": "john@example.com",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-20T14:45:00",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid Login ID or Password
- `500 Internal Server Error`: Database connection failed

**Security:** None required for login (credentials provided in body)

**Example Usage (cURL):**
```bash
curl -X POST "http://localhost:8000/citizen/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login_id": "citizen_user123",
    "password": "mypassword"
  }'
```

---

### 2. Get Citizen Profile with Aadhaar Data

**Endpoint:** `GET /citizen/profile`

**Description:** Fetches authenticated citizen's profile enriched with Aadhaar data from government database.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**
```json
{
  "citizen_id": 1,
  "login_id": "citizen_user123",
  "aadhaar_number": 123456789012,
  "caste_certificate_id": "CERT-2025-001",
  "full_name": "John Doe",
  "mobile_number": "9876543210",
  "email": "john@example.com",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-20T14:45:00",
  "aadhaar_data": {
    "aadhaar_id": 123456789012,
    "full_name": "John Doe",
    "father_name": "Ram Doe",
    "dob": "1990-05-15",
    "gender": "Male",
    "address_line1": "123 Main Street",
    "address_line2": "Apt 4B",
    "district": "Delhi",
    "state": "Delhi",
    "pincode": "110001",
    "mobile": "9876543210",
    "email": "john@example.com",
    "enrollment_date": "2015-07-20",
    "last_update": "2024-12-01T12:00:00",
    "mobile_verified": true,
    "email_verified": true,
    "status": "active"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired JWT token / missing citizen_id or aadhaar_number in token
- `404 Not Found`: Citizen user not found
- `500 Internal Server Error`: Database query failed

**Security:** Requires valid JWT token (citizen must be authenticated)

**Example Usage (cURL):**
```bash
curl -X GET "http://localhost:8000/citizen/profile" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## DBT Case Management APIs

These APIs provide access to atrocity case data for citizens.

Located in: `app/routers/dbt.py`

### Base URL: `/dbt/case`

---

### 1. Get Atrocity Cases by Aadhaar Number

**Endpoint:** `GET /dbt/case/get-fir-form-data/aadhaar/{aadhaar_number}`

**Description:** Fetches all atrocity cases (FIR records) associated with a given Aadhaar number. Citizens can only access their own cases.

**Path Parameters:**
- `aadhaar_number` (int, required): The Aadhaar number to search for

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK):**
```json
[
  {
    "Case_No": 1,
    "FIR_NO": "FIR-2025-001",
    "Victim_Name": "John Doe",
    "Father_Name": "Ram Doe",
    "Victim_DOB": "1990-05-15",
    "Gender": "Male",
    "Victim_Mobile_No": "9876543210",
    "Aadhar_No": 123456789012,
    "Caste": "SC",
    "Caste_Certificate_No": "CERT-2025-001",
    "Applied_Acts": "PCR Act 1955",
    "Case_Description": "Case description here",
    "Victim_Image_No": "FIR-2025-001_photo.jpg",
    "Location": "Delhi",
    "Date_of_Incident": "2025-01-10",
    "Medical_Report_Image": "FIR-2025-001_medical.pdf",
    "Passbook_Image": "FIR-2025-001_passbook.jpg",
    "Bank_Account_No": "1234567890123456",
    "IFSC_Code": "SBIN0001234",
    "Holder_Name": "John Doe",
    "Stage": 2,
    "Fund_Type": "Direct Benefit Transfer",
    "Fund_Ammount": "50000",
    "Pending_At": "District Collector/DM/SJO",
    "Approved_By": "Tribal Officer",
    "Limit_Delayed": 0,
    "Reason_for_Delay": null,
    "Applicant_Name": "John Doe",
    "Applicant_Relation": "Self",
    "Applicant_Mobile_No": "9876543210",
    "Applicant_Email": "john@example.com",
    "Bank_Name": "State Bank of India",
    "created_at": "2025-01-10T15:30:00",
    "State_UT": "Delhi",
    "District": "Delhi",
    "Vishesh_P_S_Name": "Delhi Central PS"
  }
]
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired JWT token
- `403 Forbidden`: Citizen attempting to access another user's Aadhaar data
- `500 Internal Server Error`: Database query failed

**Notes:**
- Citizens can only access cases for their own Aadhaar number (validated via JWT token)
- Returns empty array if no cases found for the Aadhaar number
- Returns full case details including all workflow status information

**Security:** Requires valid JWT token with `aadhaar_number` claim

**Example Usage (cURL):**
```bash
curl -X GET "http://localhost:8000/dbt/case/get-fir-form-data/aadhaar/123456789012" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example Usage (Python):**
```python
import requests

headers = {"Authorization": f"Bearer {jwt_token}"}
response = requests.get(
    "http://localhost:8000/dbt/case/get-fir-form-data/aadhaar/123456789012",
    headers=headers
)
cases = response.json()
```

---

## Response Models

### CasteCertificate
```python
{
  "certificate_id": str,
  "aadhaar_number": int,
  "person_name": str,
  "caste_category": str,  # SC, ST, OBC, General
  "caste_name": Optional[str],
  "issue_date": Optional[date],
  "issuing_authority": Optional[str],
  "verification_date": Optional[date],
  "certificate_status": Optional[str],  # active, pending, expired, etc.
  "remarks": Optional[str]
}
```

### NPCIBankKYC
```python
{
  "kyc_id": str,
  "account_number": str,
  "account_type": Optional[str],  # JOINT, SAVINGS, etc.
  "primary_holder_name": str,
  "primary_aadhaar": int,
  "primary_caste_category": Optional[str],
  "secondary_holder_name": Optional[str],
  "secondary_aadhaar": Optional[int],
  "secondary_caste_category": Optional[str],
  "bank_name": Optional[str],
  "ifsc_code": Optional[str],
  "kyc_status": Optional[str],  # verified, pending, rejected
  "kyc_completed_on": Optional[date],
  "remarks": Optional[str]
}
```

### CitizenUserResponse
```python
{
  "citizen_id": int,
  "login_id": str,
  "aadhaar_number": int,
  "caste_certificate_id": Optional[str],
  "full_name": str,
  "mobile_number": str,
  "email": Optional[EmailStr],
  "created_at": Optional[datetime],
  "updated_at": Optional[datetime]
}
```

### AadhaarDataResponse
```python
{
  "aadhaar_id": int,
  "full_name": str,
  "father_name": str,
  "dob": date,
  "gender": str,
  "address_line1": str,
  "address_line2": Optional[str],
  "district": str,
  "state": str,
  "pincode": str,
  "mobile": str,
  "email": Optional[EmailStr],
  "enrollment_date": date,
  "last_update": Optional[datetime],
  "mobile_verified": bool,
  "email_verified": bool,
  "status": str
}
```

### CitizenDataWithAadhaar
```python
{
  "citizen_id": int,
  "login_id": str,
  "aadhaar_number": int,
  "caste_certificate_id": Optional[str],
  "full_name": str,
  "mobile_number": str,
  "email": Optional[EmailStr],
  "created_at": Optional[datetime],
  "updated_at": Optional[datetime],
  "aadhaar_data": Optional[AadhaarDataResponse]
}
```

---

## Error Handling

All APIs follow standard HTTP status codes:

| Status Code | Meaning |
|------------|---------|
| 200 | Success - Request processed successfully |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid parameters or request body |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - User lacks permissions for the resource |
| 404 | Not Found - Requested resource does not exist |
| 500 | Internal Server Error - Database or server error |

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Authentication

JWT tokens are required for protected endpoints. Token structure includes:

```python
{
  "sub": "login_id",           # Subject (user identifier)
  "role": "citizen",            # User role
  "citizen_id": 1,              # Citizen ID
  "aadhaar_number": 123456789012,  # Aadhaar number
  "exp": 1704067200            # Expiration timestamp
}
```

**Token Expiration:** Configured via `settings.ACCESS_TOKEN_EXPIRE_MINUTES`

---

## Implementation Files

| Component | File Location |
|-----------|---------------|
| Caste Certificate & NPCI KYC Functions | `app/db/govt_session.py` |
| Citizen Profile & Authentication APIs | `app/routers/auth.py` |
| Atrocity Cases by Aadhaar API | `app/routers/dbt.py` |
| Response Schemas | `app/schemas/auth_schemas.py` |
| Database Models | `app/schemas/dbt_schemas.py` |

---

## Notes

1. **Password Security:** Citizen passwords are hashed using bcrypt before storage. The `hash_password()` function is used during registration.

2. **Data Validation:** All Pydantic models validate input data before processing.

3. **Error Handling:** All database operations include try-catch blocks with appropriate HTTP exception handling.

4. **Connection Management:** Database connections are properly closed in finally blocks to prevent connection leaks.

5. **Pagination:** All "get all" endpoints support pagination with `limit` and `offset` parameters.

6. **Partial Matching:** Name-based searches support partial matches using LIKE queries.

---

## Testing

Example test cases for the new endpoints:

```python
# Test Citizen Login
def test_citizen_login():
    response = client.post("/citizen/login", json={
        "login_id": "test_user",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# Test Citizen Profile
def test_citizen_profile():
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/citizen/profile", headers=headers)
    assert response.status_code == 200
    assert "aadhaar_data" in response.json()

# Test Cases by Aadhaar
def test_cases_by_aadhaar():
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/dbt/case/get-fir-form-data/aadhaar/123456789012",
        headers=headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

**Last Updated:** December 5, 2025

