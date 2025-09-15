from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class Budgets(BaseModel):
    shopping: float
    search: float
    pmax: float

class Inputs(BaseModel):
    brand_url: str
    #brand_url: HttpUrl
    #competitor_url: Optional[HttpUrl] = None
    competitor_url: Optional[str] = None

    locations: List[str]
    budgets: Budgets

class SeedRequest(BaseModel):
    method: str = "auto"  # 'auto' or 'manual'
    manual_seeds: Optional[List[str]] = None
    num_seeds: int = 10

class KeywordIdeaRequest(BaseModel):
    use_google_api: bool = False
    locations: Optional[List[str]] = None
    language_code: Optional[str] = "en"

class ConsolidateRequest(BaseModel):
    min_search_volume: int = 500

class GroupRequest(BaseModel):
    method: str = "semantic"  # 'semantic' or 'rule'
    num_groups: Optional[int] = 6
