"""Placeholder API so the load-test harness has something to measure.

The endpoints return fixed data. Phase 1 replaces them with the real ones,
keeping the same paths so the k6 scenarios carry over.
"""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Vouch (placeholder)")


class ReferralRequest(BaseModel):
    to_user_id: int
    company_id: int
    message: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/search")
def search(company: str, limit: int = 20) -> dict[str, Any]:
    return {"company": company, "results": [], "limit": limit, "placeholder": True}


@app.get("/profiles/{user_id}")
def profile(user_id: int) -> dict[str, Any]:
    return {"id": user_id, "name": "Placeholder Person", "jobs": [], "placeholder": True}


@app.post("/referral-requests", status_code=201)
def send_referral_request(request: ReferralRequest) -> dict[str, Any]:
    return {"id": 1, "status": "pending", **request.model_dump(), "placeholder": True}
