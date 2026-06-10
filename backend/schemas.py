from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    city: str
    total_spent: float
    last_order_date: Optional[datetime]
    class Config:
        from_attributes = True

class CampaignOut(BaseModel):
    id: int
    name: str
    prompt: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class CampaignLogOut(BaseModel):
    id: int
    campaign_id: int
    customer_id: int
    message: str
    channel: str
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    class Config:
        from_attributes = True

class AgentRequest(BaseModel):
    message: str

class ReceiptCallback(BaseModel):
    log_id: int
    status: str
    timestamp: datetime