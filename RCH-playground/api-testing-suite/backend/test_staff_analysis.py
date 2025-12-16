#!/usr/bin/env python3
"""
Test script for Staff Quality Analysis with Indeed Search
Run this after starting the backend server.

Usage:
    python test_staff_analysis.py
    
Or if server is running, use curl:
    curl -X POST http://localhost:8000/api/staff-quality/analyze \
        -H "Content-Type: application/json" \
        -d '{"location_id": "1-10224972832"}'
"""
import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_staff_analysis():
    """Test staff quality analysis for Westgate House Care Home"""
    
    # Initialize credentials
    from config_manager import get_credentials
    from utils.auth import credentials_store
    
    creds = get_credentials()
    credentials_store['default'] = creds
    
    print('=' * 70)
    print('🔍 STAFF QUALITY ANALYSIS TEST')
    print('=' * 70)
    
    # Check credentials
    print('\n📋 Credentials check:')
    if creds.google_places:
        print(f'  ✅ Google API Key: {creds.google_places.api_key[:20]}...')
        search_engine_id = getattr(creds.google_places, 'search_engine_id', None)
        if search_engine_id:
            print(f'  ✅ Search Engine ID: {search_engine_id}')
        else:
            print(f'  ⚠️ Search Engine ID: Not configured (Indeed Search disabled)')
    else:
        print('  ❌ Google Places not configured')
    
    if creds.firecrawl and getattr(creds.firecrawl, 'api_key', None):
        print(f'  ✅ Firecrawl API Key: {creds.firecrawl.api_key[:20]}...')
    else:
        print('  ⚠️ Firecrawl: Not configured')
    
    if creds.openai and getattr(creds.openai, 'api_key', None):
        print(f'  ✅ OpenAI API Key: {creds.openai.api_key[:20]}...')
    else:
        print('  ⚠️ OpenAI: Not configured')
    
    if creds.perplexity and getattr(creds.perplexity, 'api_key', None):
        print(f'  ✅ Perplexity API Key: {creds.perplexity.api_key[:20]}...')
    else:
        print('  ⚠️ Perplexity: Not configured')
    
    # Initialize service
    print('\n🔧 Initializing StaffQualityService...')
    from services.staff_quality_service import StaffQualityService
    service = StaffQualityService()
    
    # Test with first preset home (Westgate House Care Home)
    location_id = '1-10224972832'
    home_name = 'Westgate House Care Home'
    
    print(f'\n🏠 Testing with: {home_name}')
    print(f'   Location ID: {location_id}')
    print('=' * 70)
    
    try:
        print('\n⏳ Running analysis... (this may take 30-60 seconds)')
        result = await service.analyze_by_location_id(location_id)
        
        print('\n✅ ANALYSIS COMPLETE')
        print('=' * 70)
        
        # Care home info
        care_home = result.get('care_home', {})
        print(f'\n📍 Care Home:')
        print(f'   Name: {care_home.get("name")}')
        print(f'   Address: {care_home.get("address")}')
        print(f'   Postcode: {care_home.get("postcode")}')
        print(f'   Local Authority: {care_home.get("local_authority")}')
        
        # CQC data
        cqc_data = result.get('cqc_data', {})
        print(f'\n📊 CQC Data:')
        print(f'   Well-Led Rating: {cqc_data.get("well_led")}')
        print(f'   Effective Rating: {cqc_data.get("effective")}')
        print(f'   Last Inspection: {cqc_data.get("last_inspection_date")}')
        
        staff_sentiment = cqc_data.get('staff_sentiment', {})
        if staff_sentiment:
            print(f'\n   CQC Staff Sentiment Analysis:')
            print(f'   - Score: {staff_sentiment.get("score")}/100')
            print(f'   - Positive mentions: {staff_sentiment.get("positive")}')
            print(f'   - Neutral mentions: {staff_sentiment.get("neutral")}')
            print(f'   - Negative mentions: {staff_sentiment.get("negative")}')
        
        # Reviews
        reviews = result.get('reviews', [])
        print(f'\n📝 Employee Reviews Found: {len(reviews)}')
        
        # Count by source
        sources = {}
        sentiments = {'POSITIVE': 0, 'MIXED': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
        for r in reviews:
            src = r.get('source', 'Unknown')
            sources[src] = sources.get(src, 0) + 1
            sent = r.get('sentiment', 'NEUTRAL')
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        print('\n   By Source:')
        for src, count in sources.items():
            print(f'   - {src}: {count}')
        
        print('\n   By Sentiment:')
        for sent, count in sentiments.items():
            if count > 0:
                print(f'   - {sent}: {count}')
        
        # Show sample reviews
        if reviews:
            print('\n   Sample Reviews:')
            for i, rev in enumerate(reviews[:5]):
                text = rev.get('text', '')[:150]
                print(f'\n   [{i+1}] {rev.get("source")} | {rev.get("sentiment")} | Rating: {rev.get("rating")}')
                if text:
                    print(f'       "{text}..."')
        
        # Staff Quality Score
        score = result.get('staff_quality_score', {})
        print(f'\n{"=" * 70}')
        print(f'⭐ STAFF QUALITY SCORE: {score.get("overall_score")}/100 - {score.get("category")}')
        print(f'   Confidence: {score.get("confidence")}')
        print(f'{"=" * 70}')
        
        # Components breakdown
        components = score.get('components', {})
        print(f'\n📊 Score Components:')
        
        cqc_well_led = components.get('cqc_well_led', {})
        print(f'   1. CQC Well-Led: {cqc_well_led.get("score", "N/A")}/100')
        print(f'      Rating: {cqc_well_led.get("rating")} | Weight: {cqc_well_led.get("weight", 0)*100:.0f}%')
        
        cqc_effective = components.get('cqc_effective', {})
        print(f'   2. CQC Effective: {cqc_effective.get("score", "N/A")}/100')
        print(f'      Rating: {cqc_effective.get("rating")} | Weight: {cqc_effective.get("weight", 0)*100:.0f}%')
        
        cqc_sentiment = components.get('cqc_staff_sentiment', {})
        print(f'   3. CQC Staff Sentiment: {cqc_sentiment.get("score", "N/A")}/100')
        print(f'      Weight: {cqc_sentiment.get("weight", 0)*100:.0f}%')
        
        emp_sentiment = components.get('employee_sentiment', {})
        print(f'   4. Employee Reviews: {emp_sentiment.get("score", "N/A")}/100')
        print(f'      Reviews analyzed: {emp_sentiment.get("review_count", 0)} | Weight: {emp_sentiment.get("weight", 0)*100:.0f}%')
        
        # Flags
        flags = score.get('flags', [])
        if flags:
            print(f'\n⚠️ Flags & Warnings:')
            for flag in flags:
                flag_type = '🔴' if flag.get('type') == 'red' else '🟡'
                print(f'   {flag_type} {flag.get("message")}')
        
        # Themes
        themes = score.get('themes', {})
        positive_themes = themes.get('positive', [])
        negative_themes = themes.get('negative', [])
        
        if positive_themes or negative_themes:
            print(f'\n📋 Key Themes from Reviews:')
            if positive_themes:
                print(f'   ✅ Positive: {", ".join(positive_themes)}')
            if negative_themes:
                print(f'   ❌ Concerns: {", ".join(negative_themes)}')
        
        # Data Quality
        data_quality = score.get('data_quality', {})
        print(f'\n📈 Data Quality:')
        print(f'   CQC Data Age: {data_quality.get("cqc_data_age")}')
        print(f'   Reviews Found: {data_quality.get("review_count")}')
        print(f'   Insufficient Data: {data_quality.get("has_insufficient_data")}')
        
        print('\n' + '=' * 70)
        print('✅ TEST COMPLETED SUCCESSFULLY')
        print('=' * 70)
        
        # Save full result to file
        with open('staff_analysis_result.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print('\n💾 Full result saved to: staff_analysis_result.json')
        
        return result
        
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    result = asyncio.run(test_staff_analysis())
