#!/usr/bin/env python3
"""
RightCareHome - FSA FHRS Integration Module
Практические примеры интеграции для разных тарифов
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Уровни риска для пищевой безопасности"""
    CRITICAL = "🚨 CRITICAL"
    WARNING = "⚠️ WARNING"
    SAFE = "✅ SAFE"
    EXCELLENT = "⭐ EXCELLENT"
    UNKNOWN = "ℹ️ UNKNOWN"


class TierLevel(Enum):
    """Тарифные планы RightCareHome"""
    FREE = "free"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"


@dataclass
class CareHomeRating:
    """Структура данных о рейтинге дома престарелых"""
    fhrsid: int
    name: str
    address: str
    postcode: str
    rating_value: str
    rating_date: datetime
    hygiene_score: Optional[int]
    structural_score: Optional[int]
    management_score: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    distance: Optional[float]
    right_to_reply: Optional[str]
    scheme_type: str  # FHRS или FHIS
    
    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            'fhrsid': self.fhrsid,
            'name': self.name,
            'address': self.address,
            'postcode': self.postcode,
            'rating_value': self.rating_value,
            'rating_date': self.rating_date.isoformat(),
            'hygiene_score': self.hygiene_score,
            'structural_score': self.structural_score,
            'management_score': self.management_score,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'distance': self.distance,
            'right_to_reply': self.right_to_reply,
            'scheme_type': self.scheme_type
        }


class FSARightCareHomeIntegration:
    """Класс интеграции FSA API для RightCareHome"""
    
    BASE_URL = "https://api.ratings.food.gov.uk"
    CARE_HOME_BUSINESS_TYPE_ID = 7835  # Hospitals/Childcare/Caring Premises
    
    def __init__(self):
        self.headers = {
            "x-api-version": "2",
            "Accept": "application/json",
            "Accept-Language": "en-GB"
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Базовый метод для запросов к API"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {}
    
    def _parse_establishment(self, data: Dict) -> CareHomeRating:
        """Парсинг данных о заведении в структурированный объект"""
        
        # Парсинг даты
        rating_date_str = data.get('RatingDate', '')
        try:
            rating_date = datetime.fromisoformat(rating_date_str.replace('Z', '+00:00'))
        except:
            rating_date = datetime.now()
        
        # Парсинг scores
        scores = data.get('scores', {})
        hygiene = scores.get('Hygiene') if scores else None
        structural = scores.get('Structural') if scores else None
        management = scores.get('ConfidenceInManagement') if scores else None
        
        # Парсинг geocode
        geocode = data.get('geocode', {})
        lat = float(geocode.get('latitude')) if geocode and geocode.get('latitude') else None
        lon = float(geocode.get('longitude')) if geocode and geocode.get('longitude') else None
        
        return CareHomeRating(
            fhrsid=data.get('FHRSID'),
            name=data.get('BusinessName', 'Unknown'),
            address=f"{data.get('AddressLine1', '')}, {data.get('AddressLine3', '')}",
            postcode=data.get('PostCode', ''),
            rating_value=data.get('RatingValue', 'Unknown'),
            rating_date=rating_date,
            hygiene_score=hygiene,
            structural_score=structural,
            management_score=management,
            latitude=lat,
            longitude=lon,
            distance=data.get('Distance'),
            right_to_reply=data.get('RightToReply', ''),
            scheme_type=data.get('SchemeType', 'FHRS')
        )
    
    # ==================== ПОИСК ====================
    
    def find_care_homes_near_location(
        self, 
        latitude: float, 
        longitude: float, 
        radius_miles: int = 5,
        min_rating: Optional[int] = None
    ) -> List[CareHomeRating]:
        """
        Найти дома престарелых рядом с координатами
        
        Args:
            latitude: Широта
            longitude: Долгота
            radius_miles: Радиус поиска в милях
            min_rating: Минимальный рейтинг (опционально)
        
        Returns:
            Список объектов CareHomeRating
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'maxDistanceLimit': radius_miles,
            'businessTypeId': self.CARE_HOME_BUSINESS_TYPE_ID,
            'pageSize': 50
        }
        
        response = self._make_request('Establishments', params)
        
        if not response or 'establishments' not in response:
            return []
        
        results = []
        for est in response['establishments']:
            care_home = self._parse_establishment(est)
            
            # Фильтр по минимальному рейтингу (если указан)
            if min_rating and care_home.rating_value.isdigit():
                if int(care_home.rating_value) < min_rating:
                    continue
            
            results.append(care_home)
        
        # Сортировка по расстоянию
        results.sort(key=lambda x: x.distance if x.distance else float('inf'))
        
        return results
    
    def find_care_home_by_postcode(self, postcode: str) -> List[CareHomeRating]:
        """Найти дома престарелых по почтовому индексу"""
        params = {
            'address': postcode,
            'businessTypeId': self.CARE_HOME_BUSINESS_TYPE_ID,
            'pageSize': 20
        }
        
        response = self._make_request('Establishments', params)
        
        if not response or 'establishments' not in response:
            return []
        
        return [self._parse_establishment(est) for est in response['establishments']]
    
    def get_care_home_details(self, fhrsid: int) -> Optional[CareHomeRating]:
        """Получить детальную информацию о конкретном доме престарелых"""
        response = self._make_request(f'Establishments/{fhrsid}')
        
        if not response:
            return None
        
        return self._parse_establishment(response)
    
    # ==================== АНАЛИЗ И ОЦЕНКА ====================
    
    def assess_food_safety_risk(self, care_home: CareHomeRating) -> Tuple[RiskLevel, str]:
        """
        Оценить риск пищевой безопасности
        
        Returns:
            Tuple[RiskLevel, explanation]
        """
        rating = care_home.rating_value
        days_since_inspection = (datetime.now() - care_home.rating_date).days
        
        # FHIS (Шотландия)
        if care_home.scheme_type == 'FHIS':
            if rating.lower() == 'improvement required':
                return (RiskLevel.CRITICAL, "Требуется улучшение гигиенических стандартов (Шотландия)")
            elif rating.lower() == 'pass':
                return (RiskLevel.SAFE, "Удовлетворяет стандартам пищевой гигиены (Шотландия)")
        
        # FHRS (Англия, Уэльс, Сев. Ирландия)
        if rating.isdigit():
            rating_int = int(rating)
            
            # Критические проблемы
            if rating_int <= 2:
                return (RiskLevel.CRITICAL, 
                       f"Критически низкий рейтинг ({rating}/5). "
                       "НЕ рекомендуется для жильцов с диабетом или аллергиями.")
            
            # Требуется улучшение
            if rating_int == 3:
                hygiene_warning = ""
                if care_home.hygiene_score and care_home.hygiene_score > 10:
                    hygiene_warning = " Особенно проблемы с гигиеной."
                
                return (RiskLevel.WARNING, 
                       f"Удовлетворительный рейтинг ({rating}/5), но есть области для улучшения.{hygiene_warning}")
            
            # Хороший или отличный
            if rating_int >= 4:
                # Проверка давности инспекции
                if days_since_inspection > 730:  # 2 года
                    return (RiskLevel.WARNING,
                           f"Хороший рейтинг ({rating}/5), но инспекция была {days_since_inspection} дней назад. "
                           "Рекомендуется уточнить дату следующей проверки.")
                
                # Детальная проверка scores
                if care_home.hygiene_score is not None:
                    if care_home.hygiene_score <= 5:
                        return (RiskLevel.EXCELLENT,
                               f"Отличный рейтинг ({rating}/5) с превосходной гигиеной. "
                               "Идеально подходит для жильцов с особыми диетическими требованиями.")
                
                return (RiskLevel.SAFE,
                       f"Хороший рейтинг ({rating}/5). Стандарты пищевой безопасности соблюдаются.")
        
        return (RiskLevel.UNKNOWN, "Рейтинг недоступен или ожидается инспекция.")
    
    def generate_diabetes_suitability_score(self, care_home: CareHomeRating) -> Tuple[int, str]:
        """
        Оценить пригодность для жильцов с диабетом (0-100)
        
        Returns:
            Tuple[score (0-100), explanation]
        """
        score = 0
        explanation_parts = []
        
        # 1. Общий рейтинг (40 баллов)
        if care_home.rating_value.isdigit():
            rating = int(care_home.rating_value)
            score += rating * 8  # 5*8 = 40
            
            if rating >= 5:
                explanation_parts.append("✓ Отличный общий рейтинг")
            elif rating >= 4:
                explanation_parts.append("✓ Хороший общий рейтинг")
            else:
                explanation_parts.append("✗ Низкий рейтинг - риск для диабетической диеты")
        
        # 2. Гигиена (30 баллов) - чем ниже score, тем лучше
        if care_home.hygiene_score is not None:
            hygiene = care_home.hygiene_score
            if hygiene <= 5:
                score += 30
                explanation_parts.append("✓ Превосходная гигиена приготовления")
            elif hygiene <= 10:
                score += 20
                explanation_parts.append("✓ Хорошая гигиена приготовления")
            elif hygiene <= 15:
                score += 10
                explanation_parts.append("⚠ Удовлетворительная гигиена")
            else:
                explanation_parts.append("✗ Проблемы с гигиеной - риск контаминации")
        
        # 3. Менеджмент (20 баллов) - важно для контроля диет
        if care_home.management_score is not None:
            mgmt = care_home.management_score
            if mgmt <= 5:
                score += 20
                explanation_parts.append("✓ Отличный контроль качества питания")
            elif mgmt <= 10:
                score += 15
                explanation_parts.append("✓ Хороший контроль питания")
            elif mgmt <= 20:
                score += 10
                explanation_parts.append("⚠ Базовый контроль питания")
            else:
                explanation_parts.append("✗ Слабый контроль питания - риск ошибок в диете")
        
        # 4. Свежесть инспекции (10 баллов)
        days_since = (datetime.now() - care_home.rating_date).days
        if days_since <= 365:
            score += 10
            explanation_parts.append("✓ Недавняя инспекция")
        elif days_since <= 730:
            score += 5
            explanation_parts.append("⚠ Инспекция более года назад")
        else:
            explanation_parts.append("✗ Инспекция очень давно")
        
        return (score, " | ".join(explanation_parts))
    
    # ==================== ФОРМАТИРОВАНИЕ ПО ТАРИФАМ ====================
    
    def format_for_free_tier(self, care_home: CareHomeRating) -> str:
        """Форматирование для FREE тарифа"""
        risk_level, _ = self.assess_food_safety_risk(care_home)
        
        return f"""
🏥 {care_home.name}
📍 {care_home.postcode}
⭐ FSA Rating: {care_home.rating_value}/5 {risk_level.value}
📅 Inspected: {care_home.rating_date.strftime('%B %Y')}
"""
    
    def format_for_professional_tier(self, care_home: CareHomeRating, 
                                     user_condition: str = "diabetes") -> str:
        """Форматирование для Professional тарифа (£119)"""
        risk_level, risk_explanation = self.assess_food_safety_risk(care_home)
        
        # Специфичный анализ для диабета
        if user_condition.lower() == "diabetes":
            diabetes_score, diabetes_exp = self.generate_diabetes_suitability_score(care_home)
            diabetes_rating = "EXCELLENT" if diabetes_score >= 80 else \
                            "GOOD" if diabetes_score >= 60 else \
                            "FAIR" if diabetes_score >= 40 else "POOR"
        else:
            diabetes_score = 0
            diabetes_exp = ""
            diabetes_rating = ""
        
        output = f"""
{'='*70}
🏥 {care_home.name}
{'='*70}
📍 Location: {care_home.address}, {care_home.postcode}
{"📏 Distance: " + str(care_home.distance) + " miles" if care_home.distance else ""}

🛡️ FOOD QUALITY & SAFETY ANALYSIS
═════════════════════════════════════════════

⭐ Overall FSA Rating: {care_home.rating_value}/5 ({care_home.scheme_type})
📅 Last Inspection: {care_home.rating_date.strftime('%d %B %Y')}

🔬 DETAILED SCORES (lower is better):
"""
        
        if care_home.hygiene_score is not None:
            output += f"   • Hygiene: {care_home.hygiene_score}/20 "
            output += "✓ Excellent\n" if care_home.hygiene_score <= 5 else \
                     "✓ Good\n" if care_home.hygiene_score <= 10 else \
                     "⚠ Fair\n" if care_home.hygiene_score <= 15 else \
                     "✗ Poor\n"
        
        if care_home.structural_score is not None:
            output += f"   • Structural: {care_home.structural_score}/20 "
            output += "✓ Excellent\n" if care_home.structural_score <= 5 else \
                     "✓ Good\n" if care_home.structural_score <= 10 else \
                     "⚠ Fair\n" if care_home.structural_score <= 15 else \
                     "✗ Poor\n"
        
        if care_home.management_score is not None:
            output += f"   • Management: {care_home.management_score}/30 "
            output += "✓ Excellent\n" if care_home.management_score <= 5 else \
                     "✓ Good\n" if care_home.management_score <= 10 else \
                     "⚠ Fair\n" if care_home.management_score <= 20 else \
                     "✗ Poor\n"
        
        output += f"""
🎯 RISK ASSESSMENT:
{risk_level.value}: {risk_explanation}
"""
        
        if user_condition.lower() == "diabetes":
            output += f"""
💉 DIABETES SUITABILITY: {diabetes_rating} ({diabetes_score}/100)
{diabetes_exp}
"""
        
        if care_home.right_to_reply:
            output += f"""
💬 OPERATOR'S RESPONSE:
"{care_home.right_to_reply}"
"""
        
        return output
    
    def format_for_premium_tier(self, care_home: CareHomeRating, 
                               historical_ratings: List[Dict]) -> str:
        """Форматирование для Premium тарифа (£299) с трендами"""
        
        # Базовая информация из Professional
        output = self.format_for_professional_tier(care_home)
        
        # Добавляем анализ трендов
        output += f"""
{'='*70}
📊 FOOD SAFETY TRENDS & PREDICTIONS
{'='*70}
"""
        
        if historical_ratings:
            output += "\n📈 HISTORICAL RATINGS:\n"
            for hist in historical_ratings[-5:]:  # Последние 5 инспекций
                date = hist.get('date', 'Unknown')
                rating = hist.get('rating', 'N/A')
                output += f"   • {date}: {rating}/5\n"
            
            # Анализ тренда
            if len(historical_ratings) >= 2:
                latest = int(historical_ratings[-1].get('rating', 0))
                previous = int(historical_ratings[-2].get('rating', 0))
                
                if latest > previous:
                    output += "\n✅ Trend: IMPROVING (rating increased)\n"
                elif latest < previous:
                    output += "\n⚠️ Trend: DECLINING (rating decreased) - MONITOR CAREFULLY\n"
                else:
                    output += "\n✓ Trend: STABLE (consistent quality)\n"
        
        # Прогноз следующей инспекции
        days_since = (datetime.now() - care_home.rating_date).days
        next_inspection_estimate = care_home.rating_date + timedelta(days=365)
        
        output += f"""
🔮 NEXT INSPECTION:
   Estimated: {next_inspection_estimate.strftime('%B %Y')}
   (Based on annual inspection cycle)
   
⚡ PREMIUM MONITORING:
   ✓ You will receive instant WhatsApp alert if FSA rating changes
   ✓ We monitor this home weekly for rating updates
   ✓ Early warning system active
"""
        
        return output


# ==================== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ====================

def demo_rightcarehome_integration():
    """Демонстрация интеграции для RightCareHome"""
    
    print("="*70)
    print("🏥 RightCareHome x FSA FHRS Integration Demo")
    print("="*70)
    
    fsa = FSARightCareHomeIntegration()
    
    # ========== Сценарий 1: FREE пользователь ищет дома в Birmingham ==========
    print("\n📱 СЦЕНАРИЙ 1: FREE TIER - Быстрый поиск в Birmingham")
    print("="*70)
    
    # Координаты центра Birmingham
    birmingham_lat = 52.4862
    birmingham_lon = -1.8904
    
    care_homes = fsa.find_care_homes_near_location(
        latitude=birmingham_lat,
        longitude=birmingham_lon,
        radius_miles=3,
        min_rating=4  # FREE tier: показываем только 4-5 рейтинг
    )
    
    print(f"\n✅ Найдено {len(care_homes)} домов престарелых с рейтингом 4-5")
    print("\nTOP 3 CARE HOMES (FREE PREVIEW):\n")
    
    for home in care_homes[:3]:
        print(fsa.format_for_free_tier(home))
    
    # ========== Сценарий 2: PROFESSIONAL пользователь с диабетом ==========
    print("\n" + "="*70)
    print("💼 СЦЕНАРИЙ 2: PROFESSIONAL TIER - Детальный анализ для диабета")
    print("="*70)
    
    if care_homes:
        # Берём первый дом для детального анализа
        selected_home = care_homes[0]
        
        # Получаем детальную информацию
        detailed_home = fsa.get_care_home_details(selected_home.fhrsid)
        
        if detailed_home:
            print(fsa.format_for_professional_tier(detailed_home, user_condition="diabetes"))
    
    # ========== Сценарий 3: PREMIUM мониторинг ==========
    print("\n" + "="*70)
    print("⭐ СЦЕНАРИЙ 3: PREMIUM TIER - Мониторинг с трендами")
    print("="*70)
    
    # Mock historical data (в реальности - из вашей БД)
    mock_history = [
        {'date': '2021-10-15', 'rating': '5'},
        {'date': '2022-10-20', 'rating': '5'},
        {'date': '2023-10-18', 'rating': '5'},
        {'date': '2024-10-23', 'rating': '5'}
    ]
    
    if care_homes and care_homes[0]:
        print(fsa.format_for_premium_tier(care_homes[0], mock_history))
    
    # ========== Сценарий 4: Поиск по почтовому индексу ==========
    print("\n" + "="*70)
    print("📮 СЦЕНАРИЙ 4: Поиск по почтовому индексу")
    print("="*70)
    
    homes_by_postcode = fsa.find_care_home_by_postcode("B15 2TT")
    
    print(f"\nНайдено {len(homes_by_postcode)} домов с postcode B15 2TT")
    
    for home in homes_by_postcode[:2]:
        print(fsa.format_for_free_tier(home))


if __name__ == "__main__":
    print("""
⚠️ ПРИМЕЧАНИЕ:
Этот скрипт демонстрирует полную интеграцию FSA FHRS API в RightCareHome.

Для запуска в продакшне:
1. Убедитесь, что домен api.ratings.food.gov.uk доступен
2. Настройте кэширование результатов (Redis/Memcached)
3. Добавьте rate limiting (рекомендуется ≤200 requests/hour)
4. Настройте систему мониторинга изменений рейтингов
5. Интегрируйте с вашей БД для хранения исторических данных

Запуск демо:
$ python3 rightcarehome_fsa_integration.py
""")
    
    # Раскомментируйте для запуска демо
    # demo_rightcarehome_integration()
