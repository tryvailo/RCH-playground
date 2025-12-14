import pandas as pd
import requests
from pathlib import Path
from typing import Dict, Optional
import logging

# URLs (актуальны на 19.11.2025)
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


def download_msif_file(year_key: str = "2025-2026") -> Path:
    url = MSIF_URLS[year_key]
    file_path = DATA_DIR / f"msif_fees_{year_key}.xlsx"
    
    if file_path.exists():
        logging.info(f"MSIF файл уже существует: {file_path}")
        return file_path
    
    logging.info(f"Скачиваем MSIF {year_key}...")
    response = requests.get(url)
    response.raise_for_status()
    
    with open(file_path, "wb") as f:
        f.write(response.content)
    
    logging.info(f"Скачано: {file_path}")
    return file_path


def load_msif_data(year_key: str = "2025-2026") -> Dict[str, Dict[str, float]]:
    """
    Возвращает dict:
    {
        "Camden": {
            "residential_median": 842.0,
            "nursing_median": 1048.0,
            "residential_dementia_uplift": 123.0,
            ...
        },
        ...
    }
    """
    file_path = download_msif_file(year_key)
    
    # MSIF XLS имеет несколько листов, основной — "Fees paid 2025 to 2026"
    df = pd.read_excel(file_path, sheet_name=None)  # все листы
    
    # Находим нужный лист (обычно "Fees paid 2025 to 2026" или похожий)
    sheet_name = [k for k in df.keys() if "fees paid" in k.lower()][0]
    df = df[sheet_name]
    
    # Находим колонку с названием local authority (до нормализации)
    la_col_original = None
    for col in df.columns:
        if "local" in str(col).lower() and "authority" in str(col).lower():
            la_col_original = col
            break
    
    if la_col_original is None:
        # Fallback: используем первую колонку
        la_col_original = df.columns[0]
    
    # Очищаем данные (до нормализации колонок)
    df = df.dropna(subset=[la_col_original])  # главная колонка
    df = df[~df[la_col_original].astype(str).str.contains("England", na=False, case=False)]  # убираем summary строки
    
    # Нормализуем названия колонок (могут отличаться)
    df.columns = [c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]
    
    # Ключевые колонки (пример из файла 2025–2026)
    key_mapping = {
        "65+_residential_care_home_fees": "residential_median",
        "65+_nursing_care_home_fees": "nursing_median",
        "65+_residential_dementia_care_home_fees": "residential_dementia_median",
        "65+_nursing_dementia_care_home_fees": "nursing_dementia_median",
    }
    
    result = {}
    # Находим нормализованное имя колонки для local authority
    la_col_normalized = None
    for col in df.columns:
        if "local" in col.lower() and "authority" in col.lower():
            la_col_normalized = col
            break
    
    if la_col_normalized is None:
        la_col_normalized = df.columns[0]
    
    for _, row in df.iterrows():
        la = str(row[la_col_normalized]).strip()
        if not la or la == "nan":
            continue
        result[la] = {}
        for old_col, new_col in key_mapping.items():
            # Ищем колонку в разных вариантах названий
            col_found = None
            for col in df.columns:
                if old_col.lower() in col.lower() or col.lower() in old_col.lower():
                    col_found = col
                    break
            
            if col_found and col_found in row and pd.notna(row[col_found]):
                try:
                    result[la][new_col] = float(row[col_found])
                except (ValueError, TypeError):
                    continue
    
    logging.info(f"Загружено MSIF данные для {len(result)} local authorities")
    return result


# Глобальный кэш (загружается один раз)
_MSIF_DATA = None


def get_msif_data() -> Dict[str, Dict[str, float]]:
    global _MSIF_DATA
    if _MSIF_DATA is None:
        try:
            _MSIF_DATA = load_msif_data("2025-2026")
        except:
            logging.warning("2025-2026 не загрузился, пробуем 2024-2025")
            _MSIF_DATA = load_msif_data("2024-2025")
    return _MSIF_DATA


def get_fair_cost_lower_bound(local_authority: str, care_type: str) -> Optional[float]:
    """
    care_type: "residential", "nursing", "residential_dementia", "nursing_dementia"
    """
    data = get_msif_data()
    la_data = data.get(local_authority) or data.get(local_authority.replace(" Council", ""))
    
    if not la_data:
        return None
    
    key_map = {
        "residential": "residential_median",
        "nursing": "nursing_median",
        "residential_dementia": "residential_dementia_median",
        "nursing_dementia": "nursing_dementia_median",
    }
    
    key = key_map.get(care_type)
    return la_data.get(key)


# Пример использования в PricingService
def calculate_fair_cost_gap(market_price: float, local_authority: str, care_type: str) -> Dict:
    msif_lower = get_fair_cost_lower_bound(local_authority, care_type)
    if not msif_lower:
        return {"error": "MSIF data not found for this area"}
    
    gap_week = market_price - msif_lower
    return {
        "msif_lower_bound": msif_lower,
        "market_price": market_price,
        "gap_weekly": round(gap_week, 2),
        "gap_annual": round(gap_week * 52, 0),
        "gap_5year": round(gap_week * 52 * 5, 0),
        "gap_percent": round((gap_week / msif_lower) * 100, 1)
    }


# Тест
if __name__ == "__main__":
    data = get_msif_data()
    print("Camden nursing:", get_fair_cost_lower_bound("Camden", "nursing"))  # → ~£1,048
    print(calculate_fair_cost_gap(1912, "Camden", "nursing_dementia"))

