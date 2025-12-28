#!/usr/bin/env python3
"""
Скрипт для генерации профессионального отчета для первого профайла и детального анализа
"""
import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from routers.report_routes import generate_professional_report

async def analyze_professional_report():
    """Генерация отчета и детальный анализ"""
    
    print("="*80)
    print("ГЕНЕРАЦИЯ И АНАЛИЗ ПРОФЕССИОНАЛЬНОГО ОТЧЕТА")
    print("="*80)
    
    # 1. Load questionnaire
    print("\n1. ЗАГРУЗКА АНКЕТЫ")
    questionnaire_path = Path(__file__).parent.parent / "frontend" / "public" / "sample_questionnaires" / "professional_questionnaire_1_dementia.json"
    
    if not questionnaire_path.exists():
        print(f"   ❌ Анкета не найдена: {questionnaire_path}")
        print(f"   Ищу альтернативные пути...")
        # Try alternative path
        questionnaire_path = Path(__file__).parent.parent.parent / "frontend" / "public" / "sample_questionnaires" / "professional_questionnaire_1_dementia.json"
        if not questionnaire_path.exists():
            print(f"   ❌ Анкета не найдена и по альтернативному пути: {questionnaire_path}")
            return
    
    with open(questionnaire_path, 'r', encoding='utf-8') as f:
        questionnaire = json.load(f)
    
    print(f"   ✅ Анкета загружена: {questionnaire_path}")
    print(f"   Клиент: {questionnaire.get('client_name', questionnaire.get('profile_description', 'Unknown'))}")
    
    # 2. Generate report
    print("\n2. ГЕНЕРАЦИЯ ОТЧЕТА")
    print("   Это может занять несколько минут...")
    
    request_data = {
        "questionnaire": questionnaire
    }
    
    try:
        response = await generate_professional_report(request_data)
        
        if not response:
            print("   ❌ Отчет не сгенерирован (пустой ответ)")
            return
        
        report = response.get('report', response)
        
        print(f"\n   ✅ Отчет сгенерирован успешно")
        print(f"   Количество домов: {len(report.get('careHomes', []))}")
        
        # 3. Детальный анализ
        print("\n" + "="*80)
        print("3. ДЕТАЛЬНЫЙ АНАЛИЗ ОТЧЕТА")
        print("="*80)
        
        care_homes = report.get('careHomes', [])
        if not care_homes:
            print("   ⚠️  Нет домов в отчете")
            return
        
        print(f"\n   📊 Анализ топ-5 домов:")
        
        for idx, home in enumerate(care_homes[:5], 1):
            print(f"\n   {'='*60}")
            print(f"   ДОМ #{idx}: {home.get('name', 'Unknown')}")
            print(f"   {'='*60}")
            
            # Factor Scores
            factor_scores = home.get('factorScores', [])
            print(f"\n   📈 Factor Scores ({len(factor_scores)} категорий):")
            for factor in factor_scores:
                category = factor.get('category', 'Unknown')
                score = factor.get('score', 0)
                max_score = factor.get('maxScore', 100)
                verified = factor.get('verified', False)
                status = "✅" if verified else "⚠️"
                percentage = (score / max_score * 100) if max_score > 0 else 0
                print(f"      {status} {category}: {score:.1f}/{max_score} ({percentage:.1f}%)")
            
            # Additional Services - детальный анализ
            print(f"\n   🔍 Детальный анализ Additional Services:")
            additional_services_factor = next((f for f in factor_scores if f.get('category') == 'Additional Services'), None)
            if additional_services_factor:
                print(f"      ✅ Категория найдена в factorScores")
                print(f"      Score: {additional_services_factor.get('score', 0)}")
                print(f"      MaxScore: {additional_services_factor.get('maxScore', 100)}")
                print(f"      Verified: {additional_services_factor.get('verified', False)}")
            else:
                print(f"      ❌ Категория НЕ найдена в factorScores")
            
            # Проверка данных services в home
            print(f"\n   🔍 Проверка данных services в home:")
            services = home.get('services') or home.get('rawData', {}).get('services')
            amenities = home.get('amenities') or home.get('rawData', {}).get('amenities')
            additional_services = home.get('additional_services') or home.get('rawData', {}).get('additional_services')
            
            print(f"      services: {services if services else 'None'}")
            print(f"      amenities: {amenities if amenities else 'None'}")
            print(f"      additional_services: {additional_services if additional_services else 'None'}")
            
            if services:
                if isinstance(services, list):
                    print(f"      services count: {len(services)}")
                    print(f"      services list: {services[:5]}")
                elif isinstance(services, dict):
                    print(f"      services dict keys: {list(services.keys())[:5]}")
            
            # Financial Stability
            print(f"\n   💰 Financial Stability:")
            financial_stability = home.get('financialStability')
            if financial_stability:
                risk_score = financial_stability.get('risk_score')
                altman_z = financial_stability.get('altman_z_score')
                print(f"      ✅ Данные найдены")
                print(f"      risk_score: {risk_score}")
                print(f"      altman_z_score: {altman_z}")
            else:
                print(f"      ❌ Данные НЕ найдены")
            
            # LLM Insights
            print(f"\n   🤖 LLM Insights:")
            llm_insights = report.get('llmInsights', {})
            if llm_insights:
                insights = llm_insights.get('insights', {})
                top_home_analysis = insights.get('top_home_analysis', [])
                home_insight = next((h for h in top_home_analysis if h.get('home_name') == home.get('name') or h.get('rank') == idx), None)
                if home_insight:
                    print(f"      ✅ LLM Insight найден для этого дома")
                    print(f"      Model: {llm_insights.get('model', 'Unknown')}")
                    print(f"      Why recommended: {home_insight.get('why_recommended', 'N/A')[:100]}...")
                else:
                    print(f"      ⚠️  LLM Insight не найден для этого дома")
                    print(f"      Всего insights: {len(top_home_analysis)}")
            else:
                print(f"      ❌ LLM Insights отсутствуют в отчете")
        
        # 4. Сохранение результатов
        print("\n" + "="*80)
        print("4. СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
        print("="*80)
        
        output_file = Path(__file__).parent / "professional_report_analysis.json"
        analysis_data = {
            "report_summary": {
                "total_homes": len(care_homes),
                "client_name": questionnaire.get('client_name', questionnaire.get('profile_description', 'Unknown'))
            },
            "homes_analysis": []
        }
        
        for idx, home in enumerate(care_homes[:5], 1):
            factor_scores = home.get('factorScores', [])
            additional_services_factor = next((f for f in factor_scores if f.get('category') == 'Additional Services'), None)
            
            home_analysis = {
                "rank": idx,
                "name": home.get('name'),
                "factor_scores_count": len(factor_scores),
                "additional_services": {
                    "in_factor_scores": additional_services_factor is not None,
                    "score": additional_services_factor.get('score') if additional_services_factor else None,
                    "max_score": additional_services_factor.get('maxScore') if additional_services_factor else None,
                    "verified": additional_services_factor.get('verified') if additional_services_factor else None
                },
                "services_data": {
                    "services": home.get('services'),
                    "amenities": home.get('amenities'),
                    "additional_services": home.get('additional_services')
                },
                "financial_stability": {
                    "present": home.get('financialStability') is not None,
                    "risk_score": home.get('financialStability', {}).get('risk_score') if home.get('financialStability') else None
                }
            }
            analysis_data["homes_analysis"].append(home_analysis)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Результаты сохранены в: {output_file}")
        
        # 5. Итоговый отчет
        print("\n" + "="*80)
        print("5. ИТОГОВЫЙ ОТЧЕТ")
        print("="*80)
        
        additional_services_count = sum(1 for h in care_homes[:5] 
                                       if next((f for f in h.get('factorScores', []) 
                                               if f.get('category') == 'Additional Services'), None))
        
        financial_stability_count = sum(1 for h in care_homes[:5] if h.get('financialStability'))
        
        print(f"\n   📊 Статистика:")
        print(f"      Additional Services в factorScores: {additional_services_count}/5")
        print(f"      Financial Stability данные: {financial_stability_count}/5")
        print(f"      LLM Insights: {'✅' if llm_insights else '❌'}")
        
        if additional_services_count < 5:
            print(f"\n   ⚠️  ПРОБЛЕМА: Additional Services отсутствует в factorScores для {5 - additional_services_count} домов")
        
        if financial_stability_count < 5:
            print(f"\n   ⚠️  ПРОБЛЕМА: Financial Stability данные отсутствуют для {5 - financial_stability_count} домов")
        
        print("\n" + "="*80)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("="*80)
        
    except Exception as e:
        print(f"\n   ❌ Ошибка при генерации отчета: {e}")
        import traceback
        print(f"\n   Traceback:")
        print(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(analyze_professional_report())

