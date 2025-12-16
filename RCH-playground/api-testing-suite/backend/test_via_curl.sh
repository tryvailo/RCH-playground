#!/bin/bash
# Test Staff Quality Analysis via API
# Make sure backend is running: uvicorn main:app --reload

echo "========================================"
echo "🔍 STAFF QUALITY ANALYSIS TEST"
echo "========================================"

echo ""
echo "📍 Testing: Westgate House Care Home"
echo "   Location ID: 1-10224972832"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Server not running! Start it with:"
    echo "   cd backend && uvicorn main:app --reload"
    exit 1
fi

echo "✅ Server is running"
echo ""
echo "⏳ Running analysis... (this may take 30-60 seconds)"
echo ""

# Run analysis
result=$(curl -s -X POST http://localhost:8000/api/staff-quality/analyze \
    -H "Content-Type: application/json" \
    -d '{"location_id": "1-10224972832"}')

# Check if result is valid JSON
if echo "$result" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo "✅ Analysis completed!"
    echo ""
    echo "$result" | python3 -c "
import sys, json
data = json.load(sys.stdin)

# Care Home
care_home = data.get('care_home', {})
print('📍 Care Home:')
print(f'   Name: {care_home.get(\"name\")}')
print(f'   Address: {care_home.get(\"address\")}')
print(f'   Postcode: {care_home.get(\"postcode\")}')

# CQC Data
cqc = data.get('cqc_data', {})
print(f'\n📊 CQC Data:')
print(f'   Well-Led: {cqc.get(\"well_led\")}')
print(f'   Effective: {cqc.get(\"effective\")}')

sentiment = cqc.get('staff_sentiment', {})
if sentiment:
    print(f'   Staff Sentiment Score: {sentiment.get(\"score\")}/100')

# Reviews
reviews = data.get('reviews', [])
print(f'\n📝 Reviews Found: {len(reviews)}')

sources = {}
for r in reviews:
    src = r.get('source', 'Unknown')
    sources[src] = sources.get(src, 0) + 1

for src, count in sources.items():
    print(f'   - {src}: {count}')

# Score
score = data.get('staff_quality_score', {})
print(f'\n⭐ STAFF QUALITY SCORE: {score.get(\"overall_score\")}/100')
print(f'   Category: {score.get(\"category\")}')
print(f'   Confidence: {score.get(\"confidence\")}')

# Components
components = score.get('components', {})
print(f'\n📊 Components:')
for name, comp in components.items():
    if isinstance(comp, dict):
        print(f'   - {name}: {comp.get(\"score\", \"N/A\")} (weight: {comp.get(\"weight\", 0)*100:.0f}%)')

# Flags
flags = score.get('flags', [])
if flags:
    print(f'\n⚠️ Flags:')
    for f in flags[:3]:
        print(f'   - {f.get(\"message\", \"\")[:80]}...')
"
    
    # Save to file
    echo "$result" > staff_analysis_result.json
    echo ""
    echo "💾 Full result saved to: staff_analysis_result.json"
else
    echo "❌ Error:"
    echo "$result"
fi
