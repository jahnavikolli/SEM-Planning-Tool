from fastapi import APIRouter
from models import Inputs
from store import STORE

router = APIRouter()

@router.post("/inputs")
def post_inputs(payload: Inputs):
    STORE["config"] = payload.model_dump()
    return {"status": "ok", "config": STORE["config"]}
