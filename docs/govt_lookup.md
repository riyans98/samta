## Government Records Lookup APIs

These endpoints validate and retrieve government records needed during ICM application submission and officer verification.

### Base URL
```
/govt
```

### Authentication
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 1. Get Aadhaar Record

### `GET /govt/aadhaar/{aadhaar_number}`

**Description:** Get Aadhaar record details by Aadhaar number.

**Access:** Citizens & Officers

**Used for:**
- Validating Aadhaar existence during ICM application
- Verifying groom/bride Aadhaar before officer approval
- Cross-referencing with other documents

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `aadhaar_number` | string | 12-digit Aadhaar number |

#### Success Response (200 OK)
```json
{
  "aadhaar_id": 123456789012,
  "full_name": "Rajesh Kumar",
  "father_name": "Ramesh Kumar",
  "dob": "1996-05-15",
  "gender": "Male",
  "address_line1": "123 Main Street",
  "address_line2": "Near City Center",
  "district": "Central Delhi",
  "state": "Delhi",
  "pincode": "110001",
  "mobile": "9876543210",
  "email": "rajesh@example.com",
  "enrollment_date": "2015-06-20",
  "mobile_verified": true,
  "email_verified": true,
  "status": "active"
}
```

#### Error Response (404 Not Found)
```json
{
  "detail": "Aadhaar record not found for ID: 123456789012"
}
```

---

## 2. Get Caste Certificate by ID

### `GET /govt/caste-certificate/{certificate_id}`

**Description:** Get Caste Certificate details by certificate ID.

**Access:** Citizens & Officers

**Used for:**
- Validating caste certificate during ICM application
- Verifying SC/ST eligibility for incentive scheme
- Ensuring at least one spouse has valid certificate

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `certificate_id` | string | Certificate ID |

#### Success Response (200 OK)
```json
{
  "certificate_id": "CERT123456",
  "aadhaar_number": 123456789012,
  "person_name": "Rajesh Kumar",
  "caste_category": "SC",
  "caste_name": "Dalit",
  "issue_date": "2020-03-15",
  "issuing_authority": "District Magistrate, Delhi",
  "verification_date": "2020-03-20",
  "certificate_status": "active",
  "remarks": "Certificate verified and valid"
}
```

#### Error Response (404 Not Found)
```json
{
  "detail": "Caste certificate not found for ID: CERT123456"
}
```

---

## 3. Get Caste Certificates by Aadhaar

### `GET /govt/caste-certificates/aadhaar/{aadhaar_number}`

**Description:** Get all Caste Certificates for a person by their Aadhaar number.

**Access:** Citizens & Officers

**Returns:** Array of all certificates linked to this Aadhaar.

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `aadhaar_number` | integer | Aadhaar number |

#### Success Response (200 OK)
```json
[
  {
    "certificate_id": "CERT123456",
    "aadhaar_number": 123456789012,
    "person_name": "Rajesh Kumar",
    "caste_category": "SC",
    "issue_date": "2020-03-15",
    "certificate_status": "active"
  },
  {
    "certificate_id": "CERT789012",
    "aadhaar_number": 123456789012,
    "person_name": "Rajesh Kumar",
    "caste_category": "SC",
    "issue_date": "2018-01-10",
    "certificate_status": "expired"
  }
]
```

#### Empty Response (200 OK)
```json
[]
```

---

## 4. Get Caste Certificates by Name

### `GET /govt/caste-certificates/name/{person_name}`

**Description:** Get Caste Certificates by person name (supports partial matches).

**Access:** Citizens & Officers

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `person_name` | string | Person's name or partial name |

#### Success Response (200 OK)
Returns array of certificates matching the name search.

---

## 5. Get Caste Certificates by Category

### `GET /govt/caste-certificates/category/{category}`

**Description:** Get Caste Certificates by caste category.

**Access:** Citizens & Officers

**Category Values:** `SC`, `ST`, `OBC`, `General`

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | SC, ST, OBC, or General |

#### Success Response (200 OK)
```json
[
  {
    "certificate_id": "CERT123456",
    "person_name": "Rajesh Kumar",
    "caste_category": "SC",
    "certificate_status": "active"
  },
  {
    "certificate_id": "CERT789012",
    "person_name": "Priya Sharma",
    "caste_category": "SC",
    "certificate_status": "active"
  }
]
```

#### Error Response (400 Bad Request)
```json
{
  "detail": "Invalid category. Use: SC, ST, OBC, or General"
}
```

---

## 6. Get Bank KYC by Account Number

### `GET /govt/bank-kyc/account/{account_number}`

**Description:** Get NPCI Bank KYC records by joint account number.

**Access:** Citizens & Officers

**Validates:**
- Account exists and is JOINT type
- Account holder names and Aadhaar numbers
- Matching groom/bride Aadhaar with account holders

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `account_number` | string | Bank account number |

#### Success Response (200 OK)
```json
[
  {
    "kyc_id": "KYC123456",
    "account_number": "1234567890123456",
    "account_type": "JOINT",
    "primary_holder_name": "Rajesh Kumar",
    "primary_aadhaar": 123456789012,
    "primary_caste_category": "SC",
    "secondary_holder_name": "Priya Sharma",
    "secondary_aadhaar": 987654321098,
    "secondary_caste_category": "ST",
    "bank_name": "State Bank of India",
    "ifsc_code": "SBIN0001234",
    "kyc_status": "verified",
    "kyc_completed_on": "2024-01-15",
    "remarks": "KYC verification completed successfully"
  }
]
```

#### Empty Response (200 OK)
```json
[]
```

---

## 7. Get Bank KYC by Primary Aadhaar

### `GET /govt/bank-kyc/primary-aadhaar/{primary_aadhaar}`

**Description:** Get all joint accounts where given Aadhaar is the primary account holder.

**Access:** Citizens & Officers

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `primary_aadhaar` | integer | Primary account holder's Aadhaar |

#### Success Response (200 OK)
Returns array of KYC records where this Aadhaar is primary holder.

---

## 8. Get Bank KYC by Secondary Aadhaar

### `GET /govt/bank-kyc/secondary-aadhaar/{secondary_aadhaar}`

**Description:** Get all joint accounts where given Aadhaar is the secondary account holder.

**Access:** Citizens & Officers

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `secondary_aadhaar` | integer | Secondary account holder's Aadhaar |

#### Success Response (200 OK)
Returns array of KYC records where this Aadhaar is secondary holder.

---

## 9. Get Bank KYC by Bank Name

### `GET /govt/bank-kyc/bank/{bank_name}`

**Description:** Get NPCI Bank KYC records by bank name.

**Access:** Citizens & Officers

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `bank_name` | string | Bank name |

#### Success Response (200 OK)
Returns array of KYC records for accounts in that bank.

---

## 10. Get Bank KYC by Status

### `GET /govt/bank-kyc/status/{kyc_status}`

**Description:** Get NPCI Bank KYC records by KYC verification status.

**Access:** Citizens & Officers

**Status Values:** `verified`, `pending`, `rejected`

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `kyc_status` | string | verified, pending, or rejected |

#### Success Response (200 OK)
```json
[
  {
    "kyc_id": "KYC123456",
    "account_number": "1234567890123456",
    "account_type": "JOINT",
    "kyc_status": "verified",
    "primary_holder_name": "Rajesh Kumar",
    "secondary_holder_name": "Priya Sharma"
  }
]
```

#### Error Response (400 Bad Request)
```json
{
  "detail": "Invalid status. Use: verified, pending, or rejected"
}
```

---

## 11. Get Bank KYC by ID

### `GET /govt/bank-kyc/{kyc_id}`

**Description:** Get specific NPCI Bank KYC record by ID.

**Access:** Citizens & Officers

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `kyc_id` | string | KYC ID |

#### Success Response (200 OK)
Returns complete KYC record with all account and holder details.

---
