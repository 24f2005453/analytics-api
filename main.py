import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Header, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="IITM TDS Assignment - Analytics Endpoint")

# --- CORS CONFIGURATION ---
# Allows cross-origin requests from the grader's browser page directly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ASSIGNED CONFIGURATION ---
ASSIGNED_API_KEY = "ak_382j7s7scuz2b8d47zm4blh0"
STUDENT_EMAIL = "your_logged_in_email@example.com"  # ⚠️ REPLACE THIS with your actual IITM logged-in email

# --- MODELS ---
class Event(BaseModel):
    user: str
    amount: float
    ts: int

class AnalyticsRequest(BaseModel):
    events: List[Event]

# --- ENDPOINT ---

@app.post("/analytics")
async def post_analytics(
    request_data: AnalyticsRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    # 1. Authenticate via Header
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing API Key"
        )
    if x_api_key != ASSIGNED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid API Key"
        )

    events = request_data.events

    # 2. Aggregation Logic
    total_events = len(events)
    
    # Track unique users across all events
    unique_users_set = set(e.user for e in events)
    unique_users = len(unique_users_set)

    # Initialize revenue tracking and user-specific positive spends
    revenue = 0.0
    user_positive_revenue: Dict[str, float] = {}

    for e in events:
        if e.amount > 0:
            revenue += e.amount
            user_positive_revenue[e.user] = user_positive_revenue.get(e.user, 0.0) + e.amount

    # Find the top user based on highest positive-amount total
    top_user = ""
    if user_positive_revenue:
        top_user = max(user_positive_revenue, key=user_positive_revenue.get)
    else:
        # Fallback if no events contain positive amounts
        top_user = ""

    # 3. Formulate Response payload exactly per specification
    return {
        "email": STUDENT_EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": round(revenue, 2),  # Rounds safely for potential float precision issues
        "top_user": top_user
    }
