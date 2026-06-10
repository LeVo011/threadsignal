from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import CampaignLog
from schemas import ReceiptCallback
from datetime import datetime

router = APIRouter()

@router.post("/callback")
def receive_callback(data: ReceiptCallback, db: Session = Depends(get_db)):
    log = db.query(CampaignLog).filter(CampaignLog.id == data.log_id).first()
    if not log:
        return {"error": "log not found"}
    log.status = data.status
    if data.status == "delivered": log.delivered_at = data.timestamp
    if data.status == "opened": log.opened_at = data.timestamp
    if data.status == "clicked": log.clicked_at = data.timestamp
    db.commit()
    return {"ok": True}