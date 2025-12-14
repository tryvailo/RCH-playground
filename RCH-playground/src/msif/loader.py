import pandas as pd
import requests
from pathlib import Path
from typing import Dict, Optional
import logging
from fastapi import HTTPException

# URLs актуальны на 19.11.2025
MSIF_URLS = {
    "2025-2026": "https://assets.publishing.service.gov.uk/media/68a3021cf49bec79d23d2940/market-sustainability-and-improvement-fund-fees-2025-to-2026.xlsx",
    "2024-2025": "https://assets.publishing.service.gov.uk/media/6703d7cc3b919067bb482d39/market-sustainability-and-improvement-fund-fees-2024-to-2025.xlsx"
}

# Use absolute path to avoid issues with working directory
import os
DATA_DIR = Path(os.getcwd()) / "data" / "msif"
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError) as e:
    # If we can't create directory, use a fallback location in user's home
    DATA_DIR = Path.home() / ".cache" / "rch-playground" / "msif"
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _download(year_key: str = "2025-2026") -> Path:
    url = MSIF_URLS[year_key]
    path = DATA_DIR / f"msif_{year_key}.xlsx"
    if path.exists():
        return path
    r = requests.get(url)
    r.raise_for_status()
    path.write_bytes(r.content)
    logging.info(f"Downloaded MSIF {year_key} to {path}")
    return path


_MSIF_CACHE: Optional[Dict] = None


def get_msif_data() -> Dict[str, Dict[str, float]]:
    """Load MSIF data with caching"""
    global _MSIF_CACHE
    if _MSIF_CACHE is None:
        try:
            df = pd.read_excel(_download("2025-2026"), sheet_name=0, skiprows=2)
            logging.info("Loaded MSIF 2025-2026 data")
        except Exception as e:
            logging.warning(f"Failed to load 2025-2026, trying 2024-2025: {e}")
            df = pd.read_excel(_download("2024-2025"), sheet_name=0, skiprows=2)
            logging.info("Loaded MSIF 2024-2025 data")
        
        df = df.dropna(subset=["Local authority"])
        df.columns = [c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]
        
        result = {}
        for _, row in df.iterrows():
            la = str(row["local_authority"]).strip()
            # Remove " Council" suffix if present
            if la.endswith(" Council"):
                la = la[:-8]
            
            result[la] = {
                "residential": float(row.get("65+_residential_care_home_fees", 0.0) or 0.0),
                "nursing": float(row.get("65+_nursing_care_home_fees", 0.0) or 0.0),
                "residential_dementia": float(row.get("65+_residential_dementia_care_home_fees", 0.0) or 0.0),
                "nursing_dementia": float(row.get("65+_nursing_dementia_care_home_fees", 0.0) or 0.0),
            }
        
        _MSIF_CACHE = result
        logging.info(f"Loaded MSIF data for {len(result)} local authorities")
    
    return _MSIF_CACHE


def get_fair_cost(local_authority: str, care_type: str = "nursing") -> float:
    """
    Get MSIF fair cost lower bound for a local authority and care type
    
    Args:
        local_authority: Local authority name (e.g., "Camden", "Westminster")
        care_type: "residential", "nursing", "residential_dementia", "nursing_dementia"
    
    Returns:
        Fair cost lower bound in GBP per week
    
    Raises:
        HTTPException: If local authority not found
    """
    data = get_msif_data()
    
    # Try exact match first
    if local_authority in data:
        la_key = local_authority
    else:
        # Try case-insensitive partial match
        la_key = next((k for k in data if local_authority.lower() in k.lower() or k.lower() in local_authority.lower()), None)
    
    if not la_key:
        raise HTTPException(
            status_code=404,
            detail=f"MSIF data not found for {local_authority}. Available authorities: {list(data.keys())[:10]}..."
        )
    
    key_map = {
        "residential": "residential",
        "nursing": "nursing",
        "residential_dementia": "residential_dementia",
        "nursing_dementia": "nursing_dementia",
    }
    
    care_key = key_map.get(care_type, "nursing")
    cost = data[la_key].get(care_key, 0.0)
    
    if cost == 0.0:
        raise HTTPException(
            status_code=404,
            detail=f"MSIF data not available for {care_type} care in {local_authority}"
        )
    
    return cost


def get_fair_cost_lower_bound(local_authority: str, care_type: str = "nursing") -> Optional[float]:
    """
    Alias for get_fair_cost (for backward compatibility)
    Returns None instead of raising exception if not found
    """
    try:
        return get_fair_cost(local_authority, care_type)
    except HTTPException:
        return None


def calculate_fair_cost_gap(market_price: float, local_authority: str, care_type: str = "nursing") -> Dict:
    """
    Calculate Fair Cost Gap breakdown
    
    Returns:
        Dict with gap_weekly, gap_annual, gap_5year, etc.
    """
    msif_lower = get_fair_cost(local_authority, care_type)
    gap_week = market_price - msif_lower
    
    return {
        "msif_lower_bound": msif_lower,
        "market_price": market_price,
        "gap_weekly": round(gap_week, 2),
        "gap_annual": round(gap_week * 52, 0),
        "gap_5year": round(gap_week * 52 * 5, 0),
        "gap_percent": round((gap_week / msif_lower) * 100, 1) if msif_lower > 0 else 0.0
    }

