"""
Care Home Matcher
Matches care homes between CQC and Staging databases using multiple fields

Since staging table doesn't have cqc_location_id, we use:
- Name + Postcode (primary)
- Name + City + Address (secondary)
- Telephone (tertiary)
- Fuzzy name matching for variations
"""
import re
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


def normalize_text(text: Optional[str]) -> Optional[str]:
    """Нормализовать текст для сравнения"""
    if not text:
        return None
    # Убрать лишние пробелы, привести к нижнему регистру
    normalized = re.sub(r'\s+', ' ', str(text).strip().lower())
    # Убрать специальные символы для более точного сравнения
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return normalized if normalized else None


def normalize_postcode(postcode: Optional[str]) -> Optional[str]:
    """Нормализовать почтовый индекс для сравнения"""
    if not postcode:
        return None
    # Убрать все пробелы и привести к верхнему регистру
    normalized = re.sub(r'\s+', '', str(postcode).strip().upper())
    return normalized if normalized else None


def normalize_telephone(phone: Optional[str]) -> Optional[str]:
    """Нормализовать телефонный номер для сравнения"""
    if not phone:
        return None
    # Убрать все нецифровые символы
    normalized = re.sub(r'\D', '', str(phone).strip())
    return normalized if normalized else None


def calculate_name_similarity(name1: Optional[str], name2: Optional[str]) -> float:
    """
    Вычислить схожесть названий (простой алгоритм).
    
    Returns:
        float: 0.0 - 1.0 (1.0 = полное совпадение)
    """
    if not name1 or not name2:
        return 0.0
    
    norm1 = normalize_text(name1)
    norm2 = normalize_text(name2)
    
    if not norm1 or not norm2:
        return 0.0
    
    # Точное совпадение
    if norm1 == norm2:
        return 1.0
    
    # Одно название содержит другое
    if norm1 in norm2 or norm2 in norm1:
        return 0.8
    
    # Простое сравнение по словам
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def create_matching_keys(cqc_home: Dict[str, Any]) -> Dict[str, str]:
    """
    Создать ключи для сопоставления из CQC данных.
    
    Returns:
        Dict с различными ключами для поиска
    """
    name = normalize_text(cqc_home.get('name'))
    postcode = normalize_postcode(cqc_home.get('postcode'))
    city = normalize_text(cqc_home.get('city'))
    telephone = normalize_telephone(cqc_home.get('telephone'))
    
    keys = {}
    
    # Primary key: name + postcode (most reliable)
    if name and postcode:
        keys['name_postcode'] = f"{name}|{postcode}"
    
    # Secondary key: name + city
    if name and city:
        keys['name_city'] = f"{name}|{city}"
    
    # Tertiary key: telephone (if available)
    if telephone:
        keys['telephone'] = telephone
    
    # Store normalized values for fuzzy matching
    keys['_name'] = name
    keys['_postcode'] = postcode
    keys['_city'] = city
    keys['_telephone'] = telephone
    
    return keys


def create_staging_keys(staging_row: Dict[str, Any]) -> Dict[str, str]:
    """
    Создать ключи для сопоставления из Staging данных.
    
    Returns:
        Dict с различными ключами для поиска
    """
    name = normalize_text(staging_row.get('parsed_name'))
    postcode = normalize_postcode(staging_row.get('parsed_postcode'))
    city = normalize_text(staging_row.get('parsed_city'))
    address = normalize_text(staging_row.get('parsed_address_line_1'))
    telephone = normalize_telephone(staging_row.get('parsed_telephone'))
    
    keys = {}
    
    # Primary key: name + postcode
    if name and postcode:
        keys['name_postcode'] = f"{name}|{postcode}"
    
    # Secondary key: name + city
    if name and city:
        keys['name_city'] = f"{name}|{city}"
    
    # Extended key: name + city + address
    if name and city and address:
        keys['name_city_address'] = f"{name}|{city}|{address}"
    
    # Tertiary key: telephone
    if telephone:
        keys['telephone'] = telephone
    
    # Store normalized values for fuzzy matching
    keys['_name'] = name
    keys['_postcode'] = postcode
    keys['_city'] = city
    keys['_address'] = address
    keys['_telephone'] = telephone
    
    return keys


def match_cqc_to_staging(
    cqc_home: Dict[str, Any],
    staging_index: Dict[str, Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Найти соответствующий дом в Staging для CQC дома.
    
    Использует многоуровневую стратегию:
    1. Точное совпадение по name + postcode
    2. Точное совпадение по name + city
    3. Нечеткое совпадение по name (similarity > 0.8) + postcode
    4. Совпадение по telephone
    
    Args:
        cqc_home: Дом из CQC
        staging_index: Индекс Staging данных (ключи создаются в load_staging_data)
        
    Returns:
        Dict с данными Staging или None
    """
    cqc_keys = create_matching_keys(cqc_home)
    
    if not cqc_keys:
        return None
    
    # ─────────────────────────────────────────────────────
    # Strategy 1: Exact match on name + postcode (most reliable)
    # ─────────────────────────────────────────────────────
    if 'name_postcode' in cqc_keys:
        key = cqc_keys['name_postcode']
        if key in staging_index:
            logger.debug(f"Matched by name+postcode: {key}")
            return staging_index[key]
    
    # ─────────────────────────────────────────────────────
    # Strategy 2: Exact match on name + city
    # ─────────────────────────────────────────────────────
    if 'name_city' in cqc_keys:
        key = cqc_keys['name_city']
        if key in staging_index:
            logger.debug(f"Matched by name+city: {key}")
            return staging_index[key]
    
    # ─────────────────────────────────────────────────────
    # Strategy 3: Fuzzy match on name (similarity > 0.8) + exact postcode
    # ─────────────────────────────────────────────────────
    cqc_name = cqc_keys.get('_name')
    cqc_postcode = cqc_keys.get('_postcode')
    
    if cqc_name and cqc_postcode:
        best_match = None
        best_similarity = 0.0
        
        for staging_key, staging_data in staging_index.items():
            # staging_data is the full staging record with _matching_keys
            staging_keys = staging_data.get('_matching_keys', {})
            staging_postcode = staging_keys.get('_postcode')
            
            if staging_postcode == cqc_postcode:
                staging_name = staging_keys.get('_name')
                if staging_name:
                    similarity = calculate_name_similarity(cqc_name, staging_name)
                    if similarity > best_similarity and similarity >= 0.8:
                        best_similarity = similarity
                        best_match = staging_data
        
        if best_match:
            logger.debug(f"Matched by fuzzy name+postcode (similarity: {best_similarity:.2f})")
            return best_match
    
    # ─────────────────────────────────────────────────────
    # Strategy 4: Match by telephone (if available)
    # ─────────────────────────────────────────────────────
    if 'telephone' in cqc_keys:
        key = cqc_keys['telephone']
        if key in staging_index:
            logger.debug(f"Matched by telephone: {key}")
            return staging_index[key]
    
    return None


def build_staging_index_with_keys(
    staging_data_list: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Построить индекс Staging данных с ключами для сопоставления.
    
    Создает несколько индексов:
    - name_postcode -> staging_data
    - name_city -> staging_data
    - name_city_address -> staging_data
    - telephone -> staging_data
    
    Args:
        staging_data_list: Список записей из Staging CSV (в формате БД с _original_staging_row)
        
    Returns:
        Dict с индексами для быстрого поиска
    """
    index: Dict[str, Dict[str, Any]] = {}
    
    for staging_data in staging_data_list:
        # Get original staging row for matching
        original_row = staging_data.get('_original_staging_row', staging_data)
        keys = create_staging_keys(original_row)
        
        # Store matching keys in the data for fuzzy matching
        staging_data['_matching_keys'] = keys
        
        # Add to index by all possible keys
        for key_type, key_value in keys.items():
            if key_type.startswith('_'):
                continue  # Skip internal keys
            
            if key_value:
                # If key already exists, prefer the one with more data
                if key_value in index:
                    existing = index[key_value]
                    # Compare data quality (more fields = better)
                    existing_fields = sum(1 for v in existing.values() if v is not None)
                    new_fields = sum(1 for v in staging_data.values() if v is not None)
                    
                    if new_fields > existing_fields:
                        index[key_value] = staging_data
                else:
                    index[key_value] = staging_data
    
    logger.info(f"Built staging index with {len(index)} keys from {len(staging_data_list)} records")
    return index

