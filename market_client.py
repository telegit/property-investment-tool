"""
Real Estate Market Data API client.
Host: real-estate-market-data.p.rapidapi.com
"""
import os
import requests

RAPIDAPI_HOST = "real-estate-market-data.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}"


def _headers() -> dict:
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise ValueError("RAPIDAPI_KEY not set. Add it to your .env file.")
    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/json",
    }


def get_property_estimate(
    zip_code: str,
    bedrooms: int,
    bathrooms: int,
    sqft: int,
) -> dict:
    """
    Get estimated property value and investment metrics for a zip code + specs.

    Returns dict with keys:
      estimated_value, value_range_low, value_range_high, gross_yield_pct,
      data_source, investment_metrics, assumptions
    """
    params = {
        "zip_code": zip_code,
        "bedrooms": str(bedrooms),
        "bathrooms": str(bathrooms),
        "sqft": str(sqft),
    }
    response = requests.get(
        f"{BASE_URL}/property-estimate",
        headers=_headers(),
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()
