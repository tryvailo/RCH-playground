#!/usr/bin/env python3
"""
Скрипт для создания mock данных из care_homes_db.csv
Заполняет недостающие поля тестовыми данными для FREE Report
"""
import csv
import random
from datetime import datetime, timedelta

# Тестовые данные для заполнения
def generate_mock_data(row, index):
    """Генерирует mock данные для строки"""
    
    beds_total = int(row.get('beds_total', 0) or 0)
    
    # beds_available: случайное число от 0 до beds_total
    beds_available = random.randint(0, max(1, beds_total // 2)) if beds_total > 0 else 0
    
    # has_availability: true если есть доступные места
    has_availability = beds_available > 0
    
    # availability_status
    if beds_available > 0:
        availability_status = random.choice(['Available', 'Limited availability', 'Waiting list'])
    else:
        availability_status = random.choice(['Full', 'Waiting list only'])
    
    # availability_last_checked: случайная дата в последние 30 дней
    days_ago = random.randint(0, 30)
    availability_last_checked = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    
    # Google rating: случайное значение от 3.5 до 5.0
    google_rating = round(random.uniform(3.5, 5.0), 1)
    
    # review_count: случайное число от 5 до 150
    review_count = random.randint(5, 150)
    
    # review_average_score: то же что google_rating
    review_average_score = google_rating
    
    # Pricing: генерируем реалистичные цены на основе типа ухода
    care_residential = row.get('care_residential', 'false').lower() == 'true'
    care_nursing = row.get('care_nursing', 'false').lower() == 'true'
    care_dementia = row.get('care_dementia', 'false').lower() == 'true'
    care_respite = row.get('care_respite', 'false').lower() == 'true'
    
    # Базовые цены (weekly GBP)
    if care_residential:
        fee_residential_from = random.randint(600, 1200)
    else:
        fee_residential_from = None
    
    if care_nursing:
        fee_nursing_from = random.randint(800, 1500)
    else:
        fee_nursing_from = None
    
    if care_dementia:
        fee_dementia_from = random.randint(900, 1400)
    else:
        fee_dementia_from = None
    
    if care_respite:
        fee_respite_from = random.randint(700, 1300)
    else:
        fee_respite_from = None
    
    # Facilities: случайные значения
    wheelchair_access = random.choice([True, False])
    ensuite_rooms = random.choice([True, False])
    secure_garden = random.choice([True, False])
    wifi_available = random.choice([True, False])
    parking_onsite = random.choice([True, False])
    
    # Обновляем строку
    row['beds_available'] = str(beds_available)
    row['has_availability'] = str(has_availability).lower()
    row['availability_status'] = availability_status
    row['availability_last_checked'] = availability_last_checked
    row['google_rating'] = str(google_rating)
    row['review_count'] = str(review_count)
    row['review_average_score'] = str(review_average_score)
    
    if fee_residential_from:
        row['fee_residential_from'] = str(fee_residential_from)
    if fee_nursing_from:
        row['fee_nursing_from'] = str(fee_nursing_from)
    if fee_dementia_from:
        row['fee_dementia_from'] = str(fee_dementia_from)
    if fee_respite_from:
        row['fee_respite_from'] = str(fee_respite_from)
    
    row['wheelchair_access'] = str(wheelchair_access).lower()
    row['ensuite_rooms'] = str(ensuite_rooms).lower()
    row['secure_garden'] = str(secure_garden).lower()
    row['wifi_available'] = str(wifi_available).lower()
    row['parking_onsite'] = str(parking_onsite).lower()
    
    return row


def process_csv(input_file, output_file, max_rows=30):
    """Обрабатывает CSV файл и создаёт mock версию"""
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        rows = []
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            # Заполняем mock данными
            row = generate_mock_data(row, i)
            rows.append(row)
    
    # Записываем результат
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Создан файл {output_file} с {len(rows)} строками mock данных")


if __name__ == '__main__':
    input_file = 'care_homes_db.csv'
    output_file = 'care_homes_mock_30.csv'
    
    process_csv(input_file, output_file, max_rows=30)

