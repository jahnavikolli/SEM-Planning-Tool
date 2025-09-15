from fastapi import APIRouter
from models import ConsolidateRequest
from store import STORE

router = APIRouter()

@router.post("/consolidate")
def consolidate(req: ConsolidateRequest):
    ideas = STORE.get("keyword_ideas", [])
    seen = {}
    for it in ideas:
        kw = it["keyword"].lower()
        if kw not in seen or it["avg_monthly_searches"] > seen[kw]["avg_monthly_searches"]:
            seen[kw] = it
    consolidated = [v for v in seen.values() if v["avg_monthly_searches"] >= req.min_search_volume]
    STORE["consolidated"] = consolidated
    return {"consolidated_count": len(consolidated), "sample": consolidated[:10]}
