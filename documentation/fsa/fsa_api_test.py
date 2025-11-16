#!/usr/bin/env python3
"""
FSA FHRS API Testing Script для RightCareHome
Тестовые запросы для получения данных о домах престарелых (care homes)
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

# Базовый URL API
BASE_URL = "https://api.ratings.food.gov.uk"

# Обязательные заголовки
HEADERS = {
    "x-api-version": "2",  # КРИТИЧНО: без этого API не вернёт данные
    "Accept": "application/json",
    "Accept-Language": "en-GB"  # Или "cy-GB" для валлийского
}


class FSA_FHRS_API:
    """Класс для работы с FSA FHRS API"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Базовый метод для выполнения запросов"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return {}
    
    # ==================== СПРАВОЧНИКИ ====================
    
    def get_business_types(self, basic: bool = True) -> Dict:
        """
        Получить список типов бизнеса
        
        Args:
            basic: True для краткого списка, False для детального
        
        Returns:
            Dict с типами бизнеса
        """
        endpoint = "BusinessTypes/basic" if basic else "BusinessTypes"
        print(f"\n🔍 Запрос типов бизнеса...")
        return self._make_request(endpoint)
    
    def get_ratings(self) -> Dict:
        """Получить справочник рейтингов (0-5, Pass/Improvement)"""
        print(f"\n🔍 Запрос справочника рейтингов...")
        return self._make_request("Ratings")
    
    def get_authorities(self, basic: bool = True) -> Dict:
        """Получить список местных органов власти"""
        endpoint = "Authorities/basic" if basic else "Authorities"
        print(f"\n🔍 Запрос местных органов власти...")
        return self._make_request(endpoint)
    
    # ==================== ПОИСК ЗАВЕДЕНИЙ ====================
    
    def search_by_name(self, name: str, business_type_id: Optional[int] = None, 
                       page_number: int = 1, page_size: int = 10) -> Dict:
        """
        Поиск заведений по названию
        
        Args:
            name: Название (часть названия)
            business_type_id: ID типа бизнеса (для фильтрации)
            page_number: Номер страницы
            page_size: Размер страницы
        """
        params = {
            "name": name,
            "pageNumber": page_number,
            "pageSize": page_size
        }
        
        if business_type_id:
            params["businessTypeId"] = business_type_id
        
        print(f"\n🔍 Поиск заведений по названию: '{name}'...")
        return self._make_request("Establishments", params)
    
    def search_by_postcode(self, postcode: str, business_type_id: Optional[int] = None,
                          page_number: int = 1, page_size: int = 10) -> Dict:
        """
        Поиск заведений по почтовому индексу
        
        Args:
            postcode: Почтовый индекс (например, "B15 2TT")
            business_type_id: ID типа бизнеса
        """
        params = {
            "address": postcode,
            "pageNumber": page_number,
            "pageSize": page_size
        }
        
        if business_type_id:
            params["businessTypeId"] = business_type_id
        
        print(f"\n🔍 Поиск заведений по почтовому индексу: {postcode}...")
        return self._make_request("Establishments", params)
    
    def search_by_location(self, latitude: float, longitude: float, 
                          max_distance_miles: int = 2, 
                          business_type_id: Optional[int] = None,
                          page_number: int = 1, page_size: int = 10) -> Dict:
        """
        Поиск заведений по географическим координатам
        
        Args:
            latitude: Широта
            longitude: Долгота
            max_distance_miles: Максимальное расстояние в милях
            business_type_id: ID типа бизнеса
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "maxDistanceLimit": max_distance_miles,
            "pageNumber": page_number,
            "pageSize": page_size
        }
        
        if business_type_id:
            params["businessTypeId"] = business_type_id
        
        print(f"\n🔍 Поиск заведений в радиусе {max_distance_miles} миль от ({latitude}, {longitude})...")
        return self._make_request("Establishments", params)
    
    def search_by_local_authority(self, local_authority_id: int, 
                                  business_type_id: Optional[int] = None,
                                  page_number: int = 1, page_size: int = 50) -> Dict:
        """
        Поиск заведений по ID местного органа власти
        
        Args:
            local_authority_id: ID местного органа власти
            business_type_id: ID типа бизнеса
        """
        params = {
            "localAuthorityId": local_authority_id,
            "pageNumber": page_number,
            "pageSize": page_size
        }
        
        if business_type_id:
            params["businessTypeId"] = business_type_id
        
        print(f"\n🔍 Поиск заведений в местном органе власти ID={local_authority_id}...")
        return self._make_request("Establishments", params)
    
    def get_establishment_details(self, establishment_id: int) -> Dict:
        """
        Получить детальную информацию о конкретном заведении
        
        Args:
            establishment_id: FHRSID заведения
        """
        print(f"\n🔍 Запрос деталей заведения ID={establishment_id}...")
        return self._make_request(f"Establishments/{establishment_id}")
    
    # ==================== АНАЛИЗ И ФОРМАТИРОВАНИЕ ====================
    
    def format_establishment_info(self, establishment: Dict) -> str:
        """Форматировать информацию о заведении для вывода"""
        
        name = establishment.get('BusinessName', 'N/A')
        address = establishment.get('AddressLine1', 'N/A')
        postcode = establishment.get('PostCode', 'N/A')
        rating = establishment.get('RatingValue', 'N/A')
        rating_date = establishment.get('RatingDate', 'N/A')
        business_type = establishment.get('BusinessType', 'N/A')
        
        # Scores (если доступны)
        scores = establishment.get('scores', {})
        hygiene = scores.get('Hygiene', 'N/A') if scores else 'N/A'
        structural = scores.get('Structural', 'N/A') if scores else 'N/A'
        management = scores.get('ConfidenceInManagement', 'N/A') if scores else 'N/A'
        
        # Geocode
        geocode = establishment.get('geocode', {})
        lat = geocode.get('latitude', 'N/A') if geocode else 'N/A'
        lon = geocode.get('longitude', 'N/A') if geocode else 'N/A'
        
        # Right to Reply
        right_to_reply = establishment.get('RightToReply', None)
        
        output = f"""
{'='*70}
📍 {name}
{'='*70}
Адрес: {address}, {postcode}
Тип: {business_type}
Координаты: {lat}, {lon}

⭐ ОБЩИЙ РЕЙТИНГ: {rating}/5
📅 Дата инспекции: {rating_date}

🔬 ДЕТАЛЬНЫЕ ОЦЕНКИ:
   • Гигиена (Hygiene): {hygiene}
   • Помещения (Structural): {structural}
   • Менеджмент (Management): {management}
"""
        
        if right_to_reply:
            output += f"\n💬 ОТВЕТ ОПЕРАТОРА:\n   {right_to_reply}\n"
        
        return output


# ==================== ДЕМОНСТРАЦИОННЫЕ ТЕСТЫ ====================

def demo_tests():
    """Основные демонстрационные тесты для RightCareHome"""
    
    api = FSA_FHRS_API()
    
    print("="*70)
    print("🏥 FSA FHRS API - Демонстрация для RightCareHome")
    print("="*70)
    
    # ========== ТЕСТ 1: Получить типы бизнеса ==========
    print("\n" + "="*70)
    print("ТЕСТ 1: Получение типов бизнеса (для поиска care homes)")
    print("="*70)
    
    business_types = api.get_business_types(basic=True)
    
    if business_types:
        print("\n📋 Найденные типы бизнеса, связанные с care:")
        care_types = []
        for bt in business_types.get('businessTypes', []):
            bt_id = bt.get('BusinessTypeId')
            bt_name = bt.get('BusinessTypeName', '')
            if any(keyword in bt_name.lower() for keyword in ['care', 'hospital', 'residential']):
                care_types.append((bt_id, bt_name))
                print(f"   • ID {bt_id}: {bt_name}")
        
        if care_types:
            print(f"\n✅ Найдено {len(care_types)} типов, связанных с care homes")
            print("💡 Используйте BusinessTypeId=7835 для 'Hospitals/Childcare/Caring Premises'")
    
    # ========== ТЕСТ 2: Поиск по названию ==========
    print("\n" + "="*70)
    print("ТЕСТ 2: Поиск домов престарелых по названию 'Manor House'")
    print("="*70)
    
    # Ищем care homes с названием "Manor"
    results = api.search_by_name(
        name="Manor House",
        business_type_id=7835,  # Hospitals/Childcare/Caring Premises
        page_size=5
    )
    
    if results and results.get('establishments'):
        establishments = results['establishments']
        print(f"\n✅ Найдено заведений: {len(establishments)}")
        print(f"📊 Всего в базе: {results.get('meta', {}).get('totalCount', 'N/A')}")
        
        for est in establishments[:3]:  # Показываем первые 3
            print(api.format_establishment_info(est))
    else:
        print("❌ Результаты не найдены")
    
    # ========== ТЕСТ 3: Поиск по почтовому индексу ==========
    print("\n" + "="*70)
    print("ТЕСТ 3: Поиск домов престарелых в Birmingham (B15 2TT)")
    print("="*70)
    
    results = api.search_by_postcode(
        postcode="B15 2TT",
        business_type_id=7835,
        page_size=5
    )
    
    if results and results.get('establishments'):
        establishments = results['establishments']
        print(f"\n✅ Найдено заведений: {len(establishments)}")
        
        for est in establishments[:2]:  # Показываем первые 2
            print(api.format_establishment_info(est))
    else:
        print("ℹ️ Результаты не найдены (возможно, нет care homes с таким postcode)")
    
    # ========== ТЕСТ 4: Поиск по координатам ==========
    print("\n" + "="*70)
    print("ТЕСТ 4: Поиск домов престарелых в радиусе 2 миль от центра Birmingham")
    print("="*70)
    
    # Координаты центра Birmingham
    birmingham_lat = 52.4862
    birmingham_lon = -1.8904
    
    results = api.search_by_location(
        latitude=birmingham_lat,
        longitude=birmingham_lon,
        max_distance_miles=2,
        business_type_id=7835,
        page_size=5
    )
    
    if results and results.get('establishments'):
        establishments = results['establishments']
        print(f"\n✅ Найдено заведений в радиусе 2 миль: {len(establishments)}")
        
        for est in establishments[:2]:  # Показываем первые 2
            print(api.format_establishment_info(est))
    else:
        print("ℹ️ Результаты не найдены")
    
    # ========== ТЕСТ 5: Получение детальной информации ==========
    print("\n" + "="*70)
    print("ТЕСТ 5: Получение детальной информации о конкретном заведении")
    print("="*70)
    
    # Используем ID из предыдущих результатов, если они есть
    if results and results.get('establishments'):
        first_establishment = results['establishments'][0]
        fhrsid = first_establishment.get('FHRSID')
        
        if fhrsid:
            details = api.get_establishment_details(fhrsid)
            
            if details:
                print("\n✅ Детальная информация получена:")
                print(api.format_establishment_info(details))
    
    # ========== ТЕСТ 6: Справочник рейтингов ==========
    print("\n" + "="*70)
    print("ТЕСТ 6: Справочник рейтингов (для интерпретации)")
    print("="*70)
    
    ratings = api.get_ratings()
    
    if ratings:
        print("\n📊 Доступные рейтинги:")
        for rating in ratings.get('ratings', []):
            key = rating.get('ratingKey', 'N/A')
            name = rating.get('ratingName', 'N/A')
            print(f"   • {key}: {name}")
    
    # ========== ИТОГОВАЯ СТАТИСТИКА ==========
    print("\n" + "="*70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА И РЕКОМЕНДАЦИИ")
    print("="*70)
    
    print("""
✅ API работает без ключей и регистрации
✅ Обязательно используйте заголовок 'x-api-version: 2'
✅ BusinessTypeId=7835 для 'Hospitals/Childcare/Caring Premises'

🎯 КЛЮЧЕВЫЕ ПОЛЯ ДЛЯ RightCareHome:
   1. RatingValue (0-5) - общий рейтинг
   2. RatingDate - дата последней инспекции
   3. scores.Hygiene - гигиена (критично для диабета/аллергий)
   4. scores.Structural - состояние помещений
   5. scores.ConfidenceInManagement - менеджмент
   6. geocode - координаты для картографии
   7. RightToReply - официальный ответ оператора

💡 РЕКОМЕНДАЦИИ:
   • Используйте поиск по координатам для нахождения ближайших care homes
   • Комбинируйте с CQC API для полной картины
   • Обновляйте данные еженедельно (FSA обновляет daily)
   • Фильтруйте по RatingValue >= 4 для premium listings
   • Отслеживайте тренд: если rating снизился за год - red flag
    """)


if __name__ == "__main__":
    demo_tests()
