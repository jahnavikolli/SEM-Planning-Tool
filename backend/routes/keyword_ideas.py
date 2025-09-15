from fastapi import APIRouter, HTTPException
from models import KeywordIdeaRequest
from store import STORE
from utils import mock_generate_keyword_ideas, google_ads_generate_keyword_ideas

router = APIRouter()

@router.post("/keyword_ideas")
def keyword_ideas(req: KeywordIdeaRequest):
    cfg = STORE.get("config")
    if cfg is None:
        raise HTTPException(status_code=400, detail="Call /inputs first")
    seeds = STORE.get("seed_keywords")
    if not seeds:
        raise HTTPException(status_code=400, detail="Call /seed_keywords first")

    if req.use_google_api:
        ideas = google_ads_generate_keyword_ideas(
            seeds, cfg.get("competitor_url"), req.locations or cfg.get("locations"), req.language_code
        )
    else:
        ideas = mock_generate_keyword_ideas(seeds, cfg.get("competitor_url"))

    STORE["keyword_ideas"] = ideas
    return {"num_ideas": len(ideas), "sample": ideas[:5]}
