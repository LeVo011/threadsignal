from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import CampaignLog
from schemas import ReceiptCallback

router = APIRouter()
VALID_STATUSES = {"sent", "delivered", "failed", "opened", "clicked"}

@router.post("/callback")
def receive_callback(data: ReceiptCallback, db: Session = Depends(get_db)):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="invalid status")

    log = db.query(CampaignLog).filter(CampaignLog.id == data.log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="log not found")
    log.status = data.status
    if data.status == "sent": log.sent_at = data.timestamp
    if data.status == "delivered": log.delivered_at = data.timestamp
    if data.status == "opened": log.opened_at = data.timestamp
    if data.status == "clicked": log.clicked_at = data.timestamp
    db.commit()
    return {"ok": True}
