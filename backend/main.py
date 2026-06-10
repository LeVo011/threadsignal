from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import customers, campaigns, receipts
from seed import seed

Base.metadata.create_all(bind=engine)
seed()

app = FastAPI(title="ThreadSignal CRM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])

@app.get("/")
def root():
    return {"status": "ThreadSignal CRM running"}