# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings 
from app.routers import auth, admin, dbt, test, icm, govt_lookup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.routers.dbt import check_and_send_notifications
# --- D. FastAPI Setup ---

app = FastAPI(
    title="PCR/PoA DBT System API", 
    description="Backend for Direct Benefit Transfer under The Protection of Civil Rights (PCR) Act, 1955 and The Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989.",
    version="1.0.0"
) 

scheduler = BackgroundScheduler()

# CORS Middleware (Crucial for frontend web apps)
origins = ["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Middleware ko hata diya gaya hai. 
# Ab har protected endpoint par `Depends(verify_jwt_token)` use hoga.

# Routers ko include karna
app.include_router(auth.router, tags=["Authentication"])
app.include_router(admin.router, tags=["Admin"])
# New DBT Router for case submission
app.include_router(dbt.router) # Prefix defined in dbt.py
app.include_router(icm.router) # ICM applications
app.include_router(govt_lookup.router) # Government records lookup
app.include_router(test.test_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the PCR/PoA DBT System Backend. Use /docs for API documentation."}


def alertScheduler(): 
    check_and_send_notifications()

@app.on_event("startup")
def stat_scheduler():

    scheduler.add_job(alertScheduler, 'interval', seconds=10)
    scheduler.start()