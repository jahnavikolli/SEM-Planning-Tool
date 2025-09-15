import time
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from config import GOOGLE_ADS

# ----------------
# Mock function (keep this for local debugging)
# ----------------
def mock_generate_keyword_ideas(seed_keywords, competitor_url=None):
    """Mock: generate fake keyword ideas for debugging."""
    ideas = []
    ts = int(time.time())
    for seed in seed_keywords:
        for i in range(1, 4):
            kw = f"{seed} variation {i}"
            ideas.append({
                "keyword": kw,
                "avg_monthly_searches": max(100, (hash(kw) % 5000)),
                "top_of_page_bid_low_micros": 1000000 + (hash(kw) % 1000000),
                "top_of_page_bid_high_micros": 2000000 + (hash(kw) % 2000000),
                "competition": round(((hash(kw) % 100) / 100), 2),
                "seed": seed,
                "source": "mock",
                "timestamp": ts
            })
    return ideas


# ----------------
# Real Google Ads function (new addition)
# ----------------
def google_ads_generate_keyword_ideas(seed_keywords, url_seed=None, locations=None, language_code="en"):
    """Fetch keyword ideas from Google Ads API."""

    try:
        #client = GoogleAdsClient.load_from_env()  # loads from .env
        client = GoogleAdsClient.load_from_dict(GOOGLE_ADS)

        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

        # Build location criteria IDs
        location_rns = []
        if locations:
            geo_service = client.get_service("GeoTargetConstantService")
            for loc in locations:
                geo_request = geo_service.suggest_geo_target_constants(
                    locale="en", country_code="US", location_names=[loc]
                )
                if geo_request.geo_target_constant_suggestions:
                    location_rns.append(geo_request.geo_target_constant_suggestions[0].geo_target_constant)

        # Build request
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

        if seed_keywords:
            request.keyword_seed.keywords.extend(seed_keywords)
        if url_seed:
            request.url_seed.url = url_seed
        if location_rns:
            request.geo_target_constants.extend(location_rns)
        request.language = f"languageConstants/{language_code}"  # Example: "1000" = English

        # Send request
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

        ideas = []
        ts = int(time.time())
        for result in response:
            ideas.append({
                "keyword": result.text,
                "avg_monthly_searches": result.keyword_idea_metrics.avg_monthly_searches,
                "competition": result.keyword_idea_metrics.competition.name,
                "top_of_page_bid_low_micros": result.keyword_idea_metrics.low_top_of_page_bid_micros,
                "top_of_page_bid_high_micros": result.keyword_idea_metrics.high_top_of_page_bid_micros,
                "seed": ",".join(seed_keywords),
                "source": "google_ads",
                "timestamp": ts
            })

        return ideas

    except GoogleAdsException as ex:
        print(f"Google Ads API Error: {ex}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
