from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Campaign, CampaignLog
from schemas import AgentRequest
from agent import run_agent
from typing import List

router = APIRouter()

def summarize_logs(logs):
    stats = {"queued": 0, "sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "failed": 0}
    for log in logs:
        if log.status == "queued":
            stats["queued"] += 1
        if log.sent_at:
            stats["sent"] += 1
        if log.status == "failed":
            stats["failed"] += 1
        if log.delivered_at:
            stats["delivered"] += 1
        if log.opened_at:
            stats["opened"] += 1
        if log.clicked_at:
            stats["clicked"] += 1
    return stats

@router.post("/chat")
def chat(request: AgentRequest, db: Session = Depends(get_db)):
    response = run_agent(request.message, db)
    return {"response": response}

@router.get("/")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    result = []
    for c in campaigns:
        logs = db.query(CampaignLog).filter(CampaignLog.campaign_id == c.id).all()
        result.append({
            "id": c.id,
            "name": c.name,
            "prompt": c.prompt,
            "status": c.status,
            "created_at": c.created_at,
            "total_messages": len(logs),
            "stats": summarize_logs(logs)
        })
    return result

@router.get("/{campaign_id}/logs")
def get_logs(campaign_id: int, db: Session = Depends(get_db)):
    logs = db.query(CampaignLog).filter(CampaignLog.campaign_id == campaign_id).all()
    return [{"id": l.id, "customer_id": l.customer_id, "message": l.message,
             "channel": l.channel, "status": l.status, "sent_at": l.sent_at,
             "delivered_at": l.delivered_at, "opened_at": l.opened_at} for l in logs]
