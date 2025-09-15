from fastapi import APIRouter, HTTPException
from models import SeedRequest
from store import STORE
from urllib.parse import urlparse

router = APIRouter()

@router.post("/seed_keywords")
def generate_seeds(req: SeedRequest):
    cfg = STORE.get("config")
    if cfg is None:
        raise HTTPException(status_code=400, detail="Call /inputs first")

    if req.method == "manual" and req.manual_seeds:
        seeds = req.manual_seeds[:req.num_seeds]
    else:
        domain = urlparse(cfg["brand_url"]).netloc.split(".")[0]
        generic = ["buy", "best", "cheap", "reviews", "near me"]
        seeds = [f"{domain} {g}" for g in generic][:req.num_seeds]

    STORE["seed_keywords"] = seeds
    return {"seeds": seeds}
