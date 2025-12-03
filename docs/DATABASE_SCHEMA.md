# Database Schema Documentation

## Overview
The DBT system uses multiple credential tables for role-based access control. This document outlines the structure of each table.

---

## Credential Tables

### 1. State_Nodal_Officers
Stores credentials for State-level officers (SNO).

```sql
CREATE TABLE State_Nodal_Officers (
  login_id VARCHAR(255) PRIMARY KEY UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'State Nodal Officer',
  state_ut VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

| Column | Type | Description |
|--------|------|-------------|
| `login_id` | VARCHAR(255) | Unique login identifier (Primary Key) |
| `password` | VARCHAR(255) | Hashed password (bcrypt) |
| `role` | VARCHAR(50) | Role: "State Nodal Officer" |
| `state_ut` | VARCHAR(100) | State/UT assigned |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

**Access Scope**: State-level (can view all cases in their state)

---

### 2. District_lvl_Officers
Stores credentials for multiple officer roles: Tribal Officer, District Collector/DM/SJO, and PFMS Officer.

```sql
CREATE TABLE District_lvl_Officers (
  login_id VARCHAR(255) PRIMARY KEY UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  state_ut VARCHAR(100) NOT NULL,
  district VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

| Column | Type | Description |
|--------|------|-------------|
| `login_id` | VARCHAR(255) | Unique login identifier (Primary Key) |
| `password` | VARCHAR(255) | Hashed password (bcrypt) |
| `role` | VARCHAR(50) | Role: "Tribal Officer", "District Collector/DM/SJO", or "PFMS Officer" |
| `state_ut` | VARCHAR(100) | State/UT assigned |
| `district` | VARCHAR(100) | District assigned |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

**Important**: This table stores three different roles. Login query validates both `login_id` AND `role` to prevent role confusion and unauthorized role escalation.

**Access Scopes**:
- **Tribal Officer**: District-level (stage 1 verification, fund amount decision)
- **District Collector/DM/SJO**: District-level (stage 2 approval, corrections, stage 7 judgment)
- **PFMS Officer**: District-level (fund release at stages 4, 6, 7 within their district)

---

### 3. Vishesh_Thana_Officers
Stores credentials for Investigation Officers (at police station level).

```sql
CREATE TABLE Vishesh_Thana_Officers (
  login_id VARCHAR(255) PRIMARY KEY UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'Investigation Officer',
  state_ut VARCHAR(100) NOT NULL,
  district VARCHAR(100) NOT NULL,
  vishesh_p_s_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

| Column | Type | Description |
|--------|------|-------------|
| `login_id` | VARCHAR(255) | Unique login identifier (Primary Key) |
| `password` | VARCHAR(255) | Hashed password (bcrypt) |
| `role` | VARCHAR(50) | Role: "Investigation Officer" |
| `state_ut` | VARCHAR(100) | State/UT assigned |
| `district` | VARCHAR(100) | District assigned |
| `vishesh_p_s_name` | VARCHAR(255) | Police station name |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

**Access Scope**: Police station-level (can only see FIRs at their assigned PS)

---

## Role-to-Table Mapping

| Role | Table | State-based | District-based | PS-based | Fund Release |
|------|-------|-----------|----------------|----------|--------------|
| **State Nodal Officer** | State_Nodal_Officers | ✅ | ❌ | ❌ | ❌ |
| **PFMS Officer** | District_lvl_Officers | ❌ | ✅ | ❌ | ✅ (stages 4,6,7) |
| **Tribal Officer** | District_lvl_Officers | ❌ | ✅ | ❌ | ❌ |
| **District Collector/DM/SJO** | District_lvl_Officers | ❌ | ✅ | ❌ | ❌ |
| **Investigation Officer** | Vishesh_Thana_Officers | ❌ | ✅ | ✅ | ❌ |

---

## ATROCITY Table (Case Records)

```sql
CREATE TABLE ATROCITY (
  Case_No INT AUTO_INCREMENT PRIMARY KEY,
  FIR_NO VARCHAR(100) UNIQUE NOT NULL,
  Victim_Name VARCHAR(255) NOT NULL,
  Father_Name VARCHAR(255),
  Aadhaar_Number VARCHAR(12),
  Caste VARCHAR(100),
  Stage INT DEFAULT 0,
  Pending_At VARCHAR(100),
  Approved_By VARCHAR(255),
  Fund_Ammount DECIMAL(10, 2),
  State_UT VARCHAR(100) NOT NULL,
  District VARCHAR(100) NOT NULL,
  Vishesh_P_S_Name VARCHAR(100),
  Bank_Name VARCHAR(255),
  Account_Number VARCHAR(50),
  IFSC_Code VARCHAR(20),
  Holder_Name VARCHAR(255),
  Photo_Path VARCHAR(500),
  Caste_Cert_Path VARCHAR(500),
  Medical_Report_Path VARCHAR(500),
  Postmortem_Path VARCHAR(500),
  FIR_Document_Path VARCHAR(500),
  Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_state_district (State_UT, District),
  INDEX idx_stage_pending (Stage, Pending_At)
);
```

---

## CASE_EVENTS Table (Event Timeline)

```sql
CREATE TABLE CASE_EVENTS (
  event_id INT AUTO_INCREMENT PRIMARY KEY,
  case_no INT NOT NULL,
  performed_by VARCHAR(255),
  performed_by_role VARCHAR(50),
  event_type VARCHAR(100),
  event_data JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (case_no) REFERENCES ATROCITY(Case_No) ON DELETE CASCADE,
  INDEX idx_case_events (case_no)
);
```

| Column | Type | Description |
|--------|------|-------------|
| `event_id` | INT | Unique event identifier |
| `case_no` | INT | Reference to ATROCITY case |
| `performed_by` | VARCHAR(255) | Officer name who performed action |
| `performed_by_role` | VARCHAR(50) | Role of the officer |
| `event_type` | VARCHAR(100) | Type of event (FIR_SUBMITTED, TO_APPROVED, etc.) |
| `event_data` | JSON | Additional event details |
| `created_at` | TIMESTAMP | Event timestamp |

---

## Admin API Endpoints for Registration

### Using Admin API Key

All registration endpoints require the `X-API-Key` header with the admin API key.

**Header**: `X-API-Key: <ADMIN_API_KEY>`

#### 1. Register State Nodal Officer
```
POST /state_nodal_officers
```

**Request Body**:
```json
{
  "login_id": "sno_mp_001",
  "password": "SecurePassword123",
  "role": "State Nodal Officer",
  "state_ut": "Madhya Pradesh"
}
```

#### 2. Register District-Level Officers
```
POST /district_lvl_officers
```

Unified endpoint for all three roles: Tribal Officer, District Collector/DM/SJO, and PFMS Officer.

**For Tribal Officer/DM** (requires district):
```json
{
  "login_id": "to_jabalpur_001",
  "password": "SecurePassword123",
  "role": "Tribal Officer",
  "state_ut": "Madhya Pradesh",
  "district": "Jabalpur"
}
```

**For District Collector** (requires district):
```json
{
  "login_id": "dm_jabalpur_001",
  "password": "SecurePassword123",
  "role": "District Collector/DM/SJO",
  "state_ut": "Madhya Pradesh",
  "district": "Jabalpur"
}
```

**For PFMS Officer** (requires district):
```json
{
  "login_id": "pfms_jabalpur_001",
  "password": "SecurePassword123",
  "role": "PFMS Officer",
  "state_ut": "Madhya Pradesh",
  "district": "Jabalpur"
}
```

**Note**: All three roles use the same `/district_lvl_officers` endpoint. The endpoint automatically:
- Validates the role
- Stores in District_lvl_Officers table
- PFMS Officer operates at district level (not state-level)

#### 3. Register Investigation Officer
```
POST /vishesh_thana_officers
```

**Request Body**:
```json
{
  "login_id": "io_ps_jabalpur_001",
  "password": "SecurePassword123",
  "role": "Investigation Officer",
  "state_ut": "Madhya Pradesh",
  "district": "Jabalpur",
  "vishesh_p_s_name": "PS Jabalpur"
}
```

---

## Registration Requirements by Role

| Role | Requires district | Requires vishesh_p_s_name | Table |
|------|-------------------|---------------------------|-------|
| State Nodal Officer | ❌ | ❌ | State_Nodal_Officers |
| PFMS Officer | ✅ | ❌ | District_lvl_Officers |
| Tribal Officer | ✅ | ❌ | District_lvl_Officers |
| District Collector/DM/SJO | ✅ | ❌ | District_lvl_Officers |
| Investigation Officer | ✅ | ✅ | Vishesh_Thana_Officers |

---

## Security Notes

1. **Password Hashing**: All passwords are hashed using bcrypt (salt rounds: 10)
2. **Role Validation**: Login query for District_lvl_Officers validates both login_id AND role to prevent role confusion
3. **JWT Tokens**: Include jurisdiction fields (state_ut, district, vishesh_p_s_name) for access control
4. **Database Indexes**: Created on frequently queried columns (state_ut, district, stage, pending_at) for performance

---

**Last Updated**: December 3, 2025
**Version**: 2.0
