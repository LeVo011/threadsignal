from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Customer
from schemas import CustomerOut
from typing import List

router = APIRouter()

@router.get("/", response_model=List[CustomerOut])
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=60)
    inactive = [c for c in customers if c.last_order_date and c.last_order_date <= cutoff]
    high_value = [c for c in customers if c.total_spent >= 3000]
    return {
        "total_customers": len(customers),
        "inactive_60d": len(inactive),
        "high_value": len(high_value),
        "total_revenue": sum(c.total_spent for c in customers)
    }