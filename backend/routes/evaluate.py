from fastapi import APIRouter, HTTPException
from store import STORE

router = APIRouter()

@router.post("/evaluate")
def evaluate():
    cfg = STORE.get("config")
    consolidated = STORE.get("consolidated", [])
    if not cfg:
        raise HTTPException(status_code=400, detail="Call /inputs first")

    conv_rate = 0.02
    suggestions = []
    for k in consolidated:
        low_cpc = k["top_of_page_bid_low_micros"] / 1e6
        high_cpc = k["top_of_page_bid_high_micros"] / 1e6
        target_cpa = max(1.0, 100.0 / (1 + (k["avg_monthly_searches"] / 1000)))
        target_cpc = target_cpa * conv_rate
        suggestions.append({
            "keyword": k["keyword"],
            "avg_searches": k["avg_monthly_searches"],
            "competition": k["competition"],
            "suggested_cpc_low": round(low_cpc, 2),
            "suggested_cpc_high": round(high_cpc, 2),
            "computed_target_cpc": round(target_cpc, 2)
        })

    suggestions = sorted(suggestions, key=lambda x: -x["avg_searches"])
    return {"suggestions": suggestions, "total_keywords": len(suggestions)}
