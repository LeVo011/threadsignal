from datetime import datetime
import asyncio
import os
import random
from typing import List

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

CRM_RECEIPT_URL = os.getenv("CRM_RECEIPT_URL", "http://localhost:8000")

app = FastAPI(title="ThreadSignal Channel Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageItem(BaseModel):
    log_id: int
    customer_id: int
    message: str
    channel: str


class SendRequest(BaseModel):
    campaign_id: int
    messages: List[MessageItem]


async def post_receipt(client: httpx.AsyncClient, log_id: int, status: str):
    await client.post(
        f"{CRM_RECEIPT_URL}/receipts/callback",
        json={
            "log_id": log_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        },
        timeout=5,
    )


async def simulate_delivery(log_id: int):
    async with httpx.AsyncClient() as client:
        await post_receipt(client, log_id, "sent")

        await asyncio.sleep(random.uniform(1, 3))
        status = random.choices(["delivered", "failed"], weights=[90, 10])[0]
        await post_receipt(client, log_id, status)

        if status != "delivered":
            return

        await asyncio.sleep(random.uniform(2, 5))
        if random.random() < 0.6:
            await post_receipt(client, log_id, "opened")

        if random.random() < 0.3:
            await asyncio.sleep(random.uniform(1, 3))
            await post_receipt(client, log_id, "clicked")


@app.post("/send")
async def send_messages(request: SendRequest):
    for msg in request.messages:
        asyncio.create_task(simulate_delivery(msg.log_id))
    return {"accepted": len(request.messages)}


@app.get("/")
def root():
    return {"status": "Channel service running"}
