# PFMS Officer Setup Guide - Unified Endpoint

## Overview
PFMS Officer is a state-level role for managing fund releases. All three roles (Tribal Officer, District Collector/DM/SJO, and PFMS Officer) now use the **same `/district_lvl_officers` endpoint** for registration.

## Key Change: Unified Registration Endpoint

**Old Approach** (Separate Endpoints):
- `/pfms_officers` → PFMS Officer only
- `/district_lvl_officers` → Tribal Officer, District Collector/DM only

**New Approach** (Unified):
- `/district_lvl_officers` → All three roles (Tribal Officer, District Collector/DM/SJO, PFMS Officer)

The endpoint validates the role and:
- Sets `district=NULL` for PFMS Officer (state-level access)
- Requires `district` for Tribal Officer/District Collector/DM (district-level access)

## Registration Examples

### Register PFMS Officer
```bash
curl -X POST http://localhost:8000/district_lvl_officers \
  -H "X-API-Key: your-admin-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "login_id": "pfms_mp_001",
    "password": "SecurePassword123",
    "role": "PFMS Officer",
    "state_ut": "Madhya Pradesh"
  }'
```
**Note**: No `district` field (will be set to NULL for state-level access)

### Register Tribal Officer
```bash
curl -X POST http://localhost:8000/district_lvl_officers \
  -H "X-API-Key: your-admin-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "login_id": "to_jabalpur_001",
    "password": "SecurePassword123",
    "role": "Tribal Officer",
    "state_ut": "Madhya Pradesh",
    "district": "Jabalpur"
  }'
```
**Note**: `district` field is REQUIRED

### Register District Collector/DM
```bash
curl -X POST http://localhost:8000/district_lvl_officers \
  -H "X-API-Key: your-admin-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "login_id": "dm_jabalpur_001",
    "password": "SecurePassword123",
    "role": "District Collector/DM/SJO",
    "state_ut": "Madhya Pradesh",
    "district": "Jabalpur"
  }'
```
**Note**: `district` field is REQUIRED

## Database Storage

All three roles stored in same `District_lvl_Officers` table:

| login_id | password | role | state_ut | district |
|----------|----------|------|----------|----------|
| to_jabalpur_001 | $2b$10$... | Tribal Officer | MP | Jabalpur |
| dm_jabalpur_001 | $2b$10$... | District Collector/DM/SJO | MP | Jabalpur |
| pfms_mp_001 | $2b$10$... | PFMS Officer | MP | **NULL** |

**Key**: PFMS Officer has NULL district (state-level), others have district values (district-level)
