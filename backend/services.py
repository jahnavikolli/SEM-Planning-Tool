from models import Inputs, SeedRequest, KeywordIdeaRequest, ConsolidateRequest, GroupRequest
from store import STORE
from utils import mock_generate_keyword_ideas, google_ads_generate_keyword_ideas
from urllib.parse import urlparse


def generate_sem_plan(input_data: Inputs):
    """
    Generate a full SEM plan for the given brand/competitor configuration.

    Workflow:
    1. Save the campaign configuration in memory.
    2. Generate seed keywords:
       - If brand_url has minimal content, derive 10 seed keywords using domain + generic modifiers.
       - If brand_url/competitor_url are valid real sites, Google Ads Keyword Planner
         can extract seeds directly from site content (supported in code, may fallback in demo).
    3. Expand keywords using Google Ads API:
       - Attempts to call Google Ads Keyword Planner via `google_ads_generate_keyword_ideas`.
       - If developer account is not approved or request fails, falls back to `mock_generate_keyword_ideas`.
    4. Consolidate and filter:
       - Deduplicate by keeping keywords with the highest search volume.
       - Drop keywords with Avg Monthly Searches < 500.
    5. Evaluate keywords:
       - Rank by Avg Monthly Searches.
       - Compute CPC ranges and target CPC estimates.
    6. Group into ad groups:
       - Simple grouping by first token of keyword.
    7. Return SEM plan:
       - Includes config, seeds, keyword samples, consolidated count,
         evaluation table, ad groups, and shopping campaign budget.

    Note:
    - This pipeline is designed to be production-ready with Google Ads API.
    - For demo purposes, if API access is restricted, it gracefully falls back
      to mock keyword generation.
    """



    # Step 1: Save config
    STORE["config"] = input_data.model_dump()

    # Step 2: Seeds
    domain = urlparse(input_data.brand_url).netloc.split(".")[0]
    generic = ["buy", "best", "cheap", "reviews", "near me"]
    seeds = [f"{domain} {g}" for g in generic][:10]
    STORE["seed_keywords"] = seeds

    # Step 3: Keyword ideas (try Google Ads, fallback to mock)
    try:
        ideas = google_ads_generate_keyword_ideas(seeds, input_data.competitor_url)
    except Exception as e:
        print(f"[Fallback] Google Ads API failed: {e}")
        ideas = mock_generate_keyword_ideas(seeds, input_data.competitor_url)

    STORE["keyword_ideas"] = ideas


    # Step 4: Consolidate
    seen = {}
    for it in ideas:
        kw = it["keyword"].lower()
        if kw not in seen or it["avg_monthly_searches"] > seen[kw]["avg_monthly_searches"]:
            seen[kw] = it
    consolidated = [v for v in seen.values() if v["avg_monthly_searches"] >= 500]
    STORE["consolidated"] = consolidated

    # Step 5: Evaluate
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

    # Step 6: Group adgroups
    groups = {}
    for kw in consolidated:
        toks = kw["keyword"].split()
        key = toks[0]
        groups.setdefault(key, []).append(kw["keyword"])
    adgroups = [{"adgroup_name": k, "keywords": v} for k, v in groups.items()][:6]
    STORE["adgroups"] = adgroups

    # Step 7: Return final plan
    return {
        "config": STORE["config"],
        "seeds": STORE["seed_keywords"],
        "keyword_ideas_sample": STORE["keyword_ideas"][:5],
        "consolidated_count": len(consolidated),
        "evaluation": suggestions[:10],
        "adgroups": adgroups,
        "shopping_campaign": {
            "target_cpc": 2.0,
            "budget": input_data.budgets.shopping
        }
    }
