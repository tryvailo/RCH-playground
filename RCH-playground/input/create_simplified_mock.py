#!/usr/bin/env python3
"""
Создаёт упрощённую версию mock данных с только нужными полями для FREE Report
"""
import csv
import json

# Поля, которые нужны для FREE Report
ESSENTIAL_FIELDS = [
    'id',
    'cqc_location_id',
    'name',
    'city',
    'postcode',
    'latitude',
    'longitude',
    'region',
    'local_authority',
    'beds_total',
    'beds_available',
    'has_availability',
    'availability_status',
    'care_residential',
    'care_nursing',
    'care_dementia',
    'care_respite',
    'fee_residential_from',
    'fee_nursing_from',
    'fee_dementia_from',
    'fee_respite_from',
    'cqc_rating_overall',
    'cqc_rating_safe',
    'cqc_rating_effective',
    'cqc_rating_caring',
    'cqc_rating_responsive',
    'cqc_rating_well_led',
    'cqc_last_inspection_date',
    'google_rating',
    'review_count',
    'wheelchair_access',
    'ensuite_rooms',
    'secure_garden',
    'wifi_available',
    'parking_onsite',
    'telephone',
    'website'
]


def create_simplified_csv(input_file, output_file):
    """Создаёт упрощённый CSV с только нужными полями"""
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        rows = []
        for row in reader:
            simplified_row = {field: row.get(field, '') for field in ESSENTIAL_FIELDS}
            rows.append(simplified_row)
    
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=ESSENTIAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Создан упрощённый CSV: {output_file} ({len(rows)} строк)")
    return rows


def create_json_version(rows, output_file):
    """Создаёт JSON версию для использования в коде"""
    
    # Преобразуем в удобный формат
    care_homes = []
    for row in rows:
        home = {
            'id': row.get('id'),
            'location_id': row.get('cqc_location_id'),
            'name': row.get('name'),
            'city': row.get('city'),
            'postcode': row.get('postcode'),
            'latitude': float(row.get('latitude', 0)) if row.get('latitude') else None,
            'longitude': float(row.get('longitude', 0)) if row.get('longitude') else None,
            'region': row.get('region'),
            'local_authority': row.get('local_authority'),
            'beds_total': int(row.get('beds_total', 0)) if row.get('beds_total') else 0,
            'beds_available': int(row.get('beds_available', 0)) if row.get('beds_available') else 0,
            'has_availability': row.get('has_availability', 'false').lower() == 'true',
            'availability_status': row.get('availability_status'),
            'care_types': [],
            'weekly_costs': {},
            'cqc_ratings': {
                'overall': row.get('cqc_rating_overall'),
                'safe': row.get('cqc_rating_safe'),
                'effective': row.get('cqc_rating_effective'),
                'caring': row.get('cqc_rating_caring'),
                'responsive': row.get('cqc_rating_responsive'),
                'well_led': row.get('cqc_rating_well_led'),
            },
            'cqc_last_inspection_date': row.get('cqc_last_inspection_date'),
            'google_rating': float(row.get('google_rating', 0)) if row.get('google_rating') else None,
            'review_count': int(row.get('review_count', 0)) if row.get('review_count') else 0,
            'facilities': {
                'wheelchair_access': row.get('wheelchair_access', 'false').lower() == 'true',
                'ensuite_rooms': row.get('ensuite_rooms', 'false').lower() == 'true',
                'secure_garden': row.get('secure_garden', 'false').lower() == 'true',
                'wifi_available': row.get('wifi_available', 'false').lower() == 'true',
                'parking_onsite': row.get('parking_onsite', 'false').lower() == 'true',
            },
            'contact': {
                'telephone': row.get('telephone'),
                'website': row.get('website'),
            }
        }
        
        # Добавляем типы ухода
        if row.get('care_residential', 'false').lower() == 'true':
            home['care_types'].append('residential')
        if row.get('care_nursing', 'false').lower() == 'true':
            home['care_types'].append('nursing')
        if row.get('care_dementia', 'false').lower() == 'true':
            home['care_types'].append('dementia')
        if row.get('care_respite', 'false').lower() == 'true':
            home['care_types'].append('respite')
        
        # Добавляем цены
        if row.get('fee_residential_from'):
            home['weekly_costs']['residential'] = int(row.get('fee_residential_from'))
        if row.get('fee_nursing_from'):
            home['weekly_costs']['nursing'] = int(row.get('fee_nursing_from'))
        if row.get('fee_dementia_from'):
            home['weekly_costs']['dementia'] = int(row.get('fee_dementia_from'))
        if row.get('fee_respite_from'):
            home['weekly_costs']['respite'] = int(row.get('fee_respite_from'))
        
        care_homes.append(home)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(care_homes, outfile, indent=2, ensure_ascii=False)
    
    print(f"✅ Создан JSON файл: {output_file} ({len(care_homes)} домов)")


if __name__ == '__main__':
    input_file = 'care_homes_mock_30.csv'
    csv_output = 'care_homes_mock_simplified.csv'
    json_output = 'care_homes_mock_simplified.json'
    
    rows = create_simplified_csv(input_file, csv_output)
    create_json_version(rows, json_output)
    
    print("\n📊 Статистика:")
    print(f"  - Всего домов: {len(rows)}")
    print(f"  - С доступными местами: {sum(1 for r in rows if r.get('beds_available', '0') != '0' and r.get('beds_available'))}")
    print(f"  - С Google рейтингом: {sum(1 for r in rows if r.get('google_rating'))}")
    print(f"  - С ценами: {sum(1 for r in rows if r.get('fee_residential_from') or r.get('fee_nursing_from'))}")

