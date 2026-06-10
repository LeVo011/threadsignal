from groq import Groq
from sqlalchemy.orm import Session
from models import Customer, Campaign, CampaignLog
from datetime import datetime, timedelta
import httpx, json, os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
CHANNEL_SERVICE_URL = os.getenv("CHANNEL_SERVICE_URL", "http://localhost:8001")

tools = [
    {
        "type": "function",
        "function": {
            "name": "segment_customers",
            "description": "Segments customers based on spend, inactivity, city etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_spent": {"type": "number", "description": "Minimum total spent"},
                    "max_spent": {"type": "number", "description": "Maximum total spent"},
                    "inactive_days": {"type": "number", "description": "Haven't ordered in this many days"},
                    "city": {"type": "string", "description": "Filter by city"},
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "draft_messages",
            "description": "Drafts personalized WhatsApp messages for each customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_goal": {"type": "string", "description": "Campaign objective"},
                    "customer_ids": {"type": "array", "items": {"type": "integer"}, "description": "List of customer IDs"}
                },
                "required": ["campaign_goal", "customer_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_campaign",
            "description": "Executes campaign by sending messages via channel service",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string"},
                    "customer_ids": {"type": "array", "items": {"type": "integer"}},
                    "messages": {"type": "object", "description": "Dict of customer_id (string) to message (string)"}
                },
                "required": ["campaign_name", "customer_ids", "messages"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_campaign_insights",
            "description": "Returns performance stats for a campaign",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "integer", "description": "Campaign ID"}
                },
                "required": ["campaign_id"]
            }
        }
    }
]

def segment_customers(db: Session, min_spent=None, max_spent=None, inactive_days=None, city=None):
    query = db.query(Customer)
    if min_spent and str(min_spent).strip(): query = query.filter(Customer.total_spent >= float(min_spent))
    if max_spent and str(max_spent).strip(): query = query.filter(Customer.total_spent <= float(max_spent))
    if city and str(city).strip(): query = query.filter(Customer.city == city)
    if inactive_days and str(inactive_days).strip():
        cutoff = datetime.utcnow() - timedelta(days=int(float(inactive_days)))
        query = query.filter(Customer.last_order_date <= cutoff)
    customers = query.all()
    return [{"id": c.id, "name": c.name, "email": c.email, "city": c.city, "total_spent": c.total_spent} for c in customers]


def draft_messages(db: Session, campaign_goal: str, customer_ids: list):
    customers = db.query(Customer).filter(Customer.id.in_([int(x) for x in customer_ids])).all()
    messages = {}
    for c in customers:
        prompt = f"""You are a copywriter for a D2C fashion brand called ThreadSignal.
Write a short personalized WhatsApp message (max 2 sentences) for this customer.
Customer: {c.name}, City: {c.city}, Total spent: ₹{c.total_spent}
Goal: {campaign_goal}
Be warm, personal, with a subtle call to action. No excessive emojis."""
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120
        )
        messages[str(c.id)] = response.choices[0].message.content.strip()
    return messages


def execute_campaign(db: Session, campaign_name: str, customer_ids: list, messages: dict):
    campaign = Campaign(
        name=campaign_name,
        prompt=campaign_name,
        segment_query=str(customer_ids),
        status="running"
    )
    db.add(campaign)
    db.flush()

    logs_to_send = []
    for cid in customer_ids:
        msg = messages.get(str(cid), messages.get(cid, "Special offer just for you!"))
        log = CampaignLog(
            campaign_id=campaign.id,
            customer_id=int(cid),
            message=msg,
            channel="whatsapp",
            status="queued",
            sent_at=None
        )
        db.add(log)
        db.flush()
        logs_to_send.append({"log_id": log.id, "customer_id": int(cid), "message": msg, "channel": "whatsapp"})

    db.commit()

    try:
        httpx.post(f"{CHANNEL_SERVICE_URL}/send", json={
            "campaign_id": campaign.id,
            "messages": logs_to_send
        }, timeout=5)
    except Exception as e:
        print(f"Channel service error: {e}")

    return {"campaign_id": campaign.id, "total_sent": len(logs_to_send)}


def get_campaign_insights(db: Session, campaign_id: int):
    logs = db.query(CampaignLog).filter(CampaignLog.campaign_id == campaign_id).all()
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
    return {"campaign_id": campaign_id, "total": len(logs), "stats": stats}


def run_agent(user_message: str, db: Session):
    messages = [
        {
            "role": "system",
            "content": """You are ThreadSignal's AI campaign agent for a D2C fashion brand.
Help marketers run campaigns by following this exact order:
1. Call segment_customers — only pass parameters that are explicitly mentioned. Never pass empty strings. Omit unused parameters entirely.
2. Call draft_messages with the customer IDs from step 1
3. Call execute_campaign with the messages from step 2
4. Call get_campaign_insights with the campaign_id from step 3
Always complete all 4 steps. Be concise and conversational in your final summary."""
        },
        {"role": "user", "content": user_message}
    ]

    last_campaign_id = None

    for _ in range(10):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=2000
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    }
                    for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                fn = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"[Agent] Calling: {fn} with {args}")

                if fn == "segment_customers":
                    result = segment_customers(db, **args)
                elif fn == "draft_messages":
                    customer_ids = [int(x) for x in args.get("customer_ids", [])]
                    result = draft_messages(db, args.get("campaign_goal", ""), customer_ids)
                elif fn == "execute_campaign":
                    customer_ids = [int(x) for x in args.get("customer_ids", [])]
                    messages_dict = {str(k): v for k, v in args.get("messages", {}).items()}
                    result = execute_campaign(db, args.get("campaign_name", "Campaign"), customer_ids, messages_dict)
                    if isinstance(result, dict) and "campaign_id" in result:
                        last_campaign_id = result["campaign_id"]
                elif fn == "get_campaign_insights":
                    cid = last_campaign_id or int(args.get("campaign_id", 0))
                    result = get_campaign_insights(db, cid)
                else:
                    result = {"error": "unknown function"}

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result)
                })
        else:
            return msg.content

    return "Campaign completed successfully."
