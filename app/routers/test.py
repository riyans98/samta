from fastapi import APIRouter, HTTPException, status
from app.db.govt_session import get_aadhaar_by_number, get_fir_by_number
from app.schemas.govt_record_schemas import AadhaarRecord, FIRRecord

test_router = APIRouter(prefix="/test", tags=["Test"])


@test_router.get("/aadhaar/{aadhaar_number}", response_model=AadhaarRecord)
async def get_aadhaar_api(aadhaar_number: str):
    adhaarData = get_aadhaar_by_number(aadhaar_number)
    if adhaarData:
        return adhaarData
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aadhaar not found")

@test_router.get("/fir/{fir_number}", response_model=FIRRecord)
async def get_fir_api(fir_number: str):
    firData = get_fir_by_number(fir_number)
    if firData:
        return firData
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aadhaar not found")