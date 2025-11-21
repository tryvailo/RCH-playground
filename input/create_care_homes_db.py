#!/usr/bin/env python3
"""
Скрипт для создания тестовой базы данных PostgreSQL
Конвертирует JSON mock данные в SQL INSERT statements
"""
import json
import sys
from pathlib import Path

def generate_sql_from_json(json_file: str, output_file: str):
    """Генерирует SQL скрипт из JSON файла"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        homes = json.load(f)
    
    sql_statements = []
    
    # SQL для создания таблицы (упрощённая версия)
    sql_statements.append("""
-- Создание таблицы care_homes
CREATE TABLE IF NOT EXISTS care_homes (
    id SERIAL PRIMARY KEY,
    cqc_location_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    city VARCHAR(200),
    postcode VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    region VARCHAR(100),
    local_authority VARCHAR(200),
    telephone VARCHAR(50),
    website VARCHAR(500),
    beds_total INTEGER,
    beds_available INTEGER,
    has_availability BOOLEAN DEFAULT FALSE,
    availability_status VARCHAR(50),
    care_residential BOOLEAN DEFAULT FALSE,
    care_nursing BOOLEAN DEFAULT FALSE,
    care_dementia BOOLEAN DEFAULT FALSE,
    care_respite BOOLEAN DEFAULT FALSE,
    fee_residential_from DECIMAL(10, 2),
    fee_nursing_from DECIMAL(10, 2),
    fee_dementia_from DECIMAL(10, 2),
    fee_respite_from DECIMAL(10, 2),
    cqc_rating_overall VARCHAR(50),
    cqc_rating_safe VARCHAR(50),
    cqc_rating_effective VARCHAR(50),
    cqc_rating_caring VARCHAR(50),
    cqc_rating_responsive VARCHAR(50),
    cqc_rating_well_led VARCHAR(50),
    cqc_last_inspection_date DATE,
    google_rating DECIMAL(2, 1),
    review_count INTEGER,
    wheelchair_access BOOLEAN DEFAULT FALSE,
    ensuite_rooms BOOLEAN DEFAULT FALSE,
    secure_garden BOOLEAN DEFAULT FALSE,
    wifi_available BOOLEAN DEFAULT FALSE,
    parking_onsite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_care_homes_postcode ON care_homes(postcode);
CREATE INDEX IF NOT EXISTS idx_care_homes_local_authority ON care_homes(local_authority);
CREATE INDEX IF NOT EXISTS idx_care_homes_cqc_rating ON care_homes(cqc_rating_overall);
CREATE INDEX IF NOT EXISTS idx_care_homes_beds_available ON care_homes(beds_available) WHERE beds_available > 0;
""")
    
    # Генерация INSERT statements
    sql_statements.append("\n-- Вставка тестовых данных\n")
    sql_statements.append("INSERT INTO care_homes (\n")
    sql_statements.append("    cqc_location_id, name, city, postcode, latitude, longitude,\n")
    sql_statements.append("    region, local_authority, telephone, website,\n")
    sql_statements.append("    beds_total, beds_available, has_availability, availability_status,\n")
    sql_statements.append("    care_residential, care_nursing, care_dementia, care_respite,\n")
    sql_statements.append("    fee_residential_from, fee_nursing_from, fee_dementia_from, fee_respite_from,\n")
    sql_statements.append("    cqc_rating_overall, cqc_rating_safe, cqc_rating_effective, cqc_rating_caring,\n")
    sql_statements.append("    cqc_rating_responsive, cqc_rating_well_led, cqc_last_inspection_date,\n")
    sql_statements.append("    google_rating, review_count,\n")
    sql_statements.append("    wheelchair_access, ensuite_rooms, secure_garden, wifi_available, parking_onsite\n")
    sql_statements.append(") VALUES\n")
    
    values = []
    for home in homes:
        care_types = home.get('care_types', [])
        weekly_costs = home.get('weekly_costs', {})
        cqc_ratings = home.get('cqc_ratings', {})
        facilities = home.get('facilities', {})
        contact = home.get('contact', {})
        
        value_parts = [
            f"'{home['location_id']}'",  # cqc_location_id
            f"'{home['name'].replace(chr(39), chr(39)*2)}'",  # name (escape quotes)
            f"'{home.get('city', '')}'" if home.get('city') else 'NULL',  # city
            f"'{home['postcode']}'",  # postcode
            str(home['latitude']) if home.get('latitude') else 'NULL',  # latitude
            str(home['longitude']) if home.get('longitude') else 'NULL',  # longitude
            f"'{home.get('region', '')}'" if home.get('region') else 'NULL',  # region
            f"'{home.get('local_authority', '')}'" if home.get('local_authority') else 'NULL',  # local_authority
            f"'{contact.get('telephone', '')}'" if contact.get('telephone') else 'NULL',  # telephone
            f"'{contact.get('website', '')}'" if contact.get('website') else 'NULL',  # website
            str(home.get('beds_total', 0)),  # beds_total
            str(home.get('beds_available', 0)),  # beds_available
            'TRUE' if home.get('has_availability') else 'FALSE',  # has_availability
            f"'{home.get('availability_status', '')}'" if home.get('availability_status') else 'NULL',  # availability_status
            'TRUE' if 'residential' in care_types else 'FALSE',  # care_residential
            'TRUE' if 'nursing' in care_types else 'FALSE',  # care_nursing
            'TRUE' if 'dementia' in care_types else 'FALSE',  # care_dementia
            'TRUE' if 'respite' in care_types else 'FALSE',  # care_respite
            str(weekly_costs.get('residential')) if weekly_costs.get('residential') else 'NULL',  # fee_residential_from
            str(weekly_costs.get('nursing')) if weekly_costs.get('nursing') else 'NULL',  # fee_nursing_from
            str(weekly_costs.get('dementia')) if weekly_costs.get('dementia') else 'NULL',  # fee_dementia_from
            str(weekly_costs.get('respite')) if weekly_costs.get('respite') else 'NULL',  # fee_respite_from
            f"'{cqc_ratings.get('overall', '')}'" if cqc_ratings.get('overall') else 'NULL',  # cqc_rating_overall
            f"'{cqc_ratings.get('safe', '')}'" if cqc_ratings.get('safe') else 'NULL',  # cqc_rating_safe
            f"'{cqc_ratings.get('effective', '')}'" if cqc_ratings.get('effective') else 'NULL',  # cqc_rating_effective
            f"'{cqc_ratings.get('caring', '')}'" if cqc_ratings.get('caring') else 'NULL',  # cqc_rating_caring
            f"'{cqc_ratings.get('responsive', '')}'" if cqc_ratings.get('responsive') else 'NULL',  # cqc_rating_responsive
            f"'{cqc_ratings.get('well_led', '')}'" if cqc_ratings.get('well_led') else 'NULL',  # cqc_rating_well_led
            f"'{home.get('cqc_last_inspection_date', '')}'" if home.get('cqc_last_inspection_date') else 'NULL',  # cqc_last_inspection_date
            str(home.get('google_rating')) if home.get('google_rating') else 'NULL',  # google_rating
            str(home.get('review_count', 0)),  # review_count
            'TRUE' if facilities.get('wheelchair_access') else 'FALSE',  # wheelchair_access
            'TRUE' if facilities.get('ensuite_rooms') else 'FALSE',  # ensuite_rooms
            'TRUE' if facilities.get('secure_garden') else 'FALSE',  # secure_garden
            'TRUE' if facilities.get('wifi_available') else 'FALSE',  # wifi_available
            'TRUE' if facilities.get('parking_onsite') else 'FALSE',  # parking_onsite
        ]
        
        values.append(f"({', '.join(value_parts)})")
    
    sql_statements.append(',\n'.join(values))
    sql_statements.append(';')
    
    # Статистика
    sql_statements.append("""

-- Статистика
SELECT 
    COUNT(*) as total_homes,
    COUNT(*) FILTER (WHERE has_availability = TRUE) as homes_with_availability,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Outstanding') as outstanding_homes,
    COUNT(*) FILTER (WHERE cqc_rating_overall = 'Good') as good_homes,
    AVG(google_rating) as avg_google_rating
FROM care_homes;
""")
    
    # Запись в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✅ SQL скрипт создан: {output_file}")
    print(f"📊 Обработано {len(homes)} домов")


if __name__ == '__main__':
    json_file = 'care_homes_mock_simplified.json'
    output_file = 'care_homes_db_from_json.sql'
    
    if not Path(json_file).exists():
        print(f"❌ Файл {json_file} не найден")
        sys.exit(1)
    
    generate_sql_from_json(json_file, output_file)

