from fastapi import APIRouter
from models import GroupRequest
from store import STORE

router = APIRouter()

@router.post("/group_adgroups")
def group_adgroups(req: GroupRequest):
    consolidated = STORE.get("consolidated", [])
    groups = {}
    for kw in consolidated:
        toks = kw["keyword"].split()
        key = toks[0]
        groups.setdefault(key, []).append(kw["keyword"])
    ags = [{"adgroup_name": k, "keywords": v} for k, v in groups.items()][:req.num_groups]
    STORE["adgroups"] = ags
    return {"adgroups": ags}

@router.get("/export")
def export():
    return {
        "config": STORE["config"],
        "seed_keywords": STORE["seed_keywords"],
        "consolidated": STORE["consolidated"],
        "adgroups": STORE["adgroups"]
    }
