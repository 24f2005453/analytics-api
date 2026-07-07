from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from collections import defaultdict

EMAIL = "24f2005453@ds.study.iitm.ac.in"
API_KEY = "ak_382j7s7scuz2b8d47zm4blh0"

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@app.get("/")
def home():
    return {"message": "Analytics API Running"}


@app.post("/analytics")
def analytics(
    request: AnalyticsRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    total_events = len(request.events)

    unique_users = len(set(event.user for event in request.events))

    revenue = 0.0
    user_totals = defaultdict(float)

    for event in request.events:
        if event.amount > 0:
            revenue += event.amount
            user_totals[event.user] += event.amount

    top_user = ""

    if user_totals:
        top_user = max(user_totals, key=user_totals.get)

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user
    }
