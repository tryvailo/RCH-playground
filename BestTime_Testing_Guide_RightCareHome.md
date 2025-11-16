# 🧪 BestTime.app Testing Guide для RightCareHome

**Цель:** Определить, подходит ли BestTime.app для анализа footfall данных 15,000 UK care homes

**Timeline:** 3-5 дней  
**Budget:** £0-20 (free trial + возможно небольшая оплата)  
**Expected outcome:** Go/No-Go решение по использованию BestTime

---

## 📋 **PHASE 1: PREPARATION (Day 1 - 30 минут)**

### **Step 1.1: Регистрация в BestTime**

1. Перейдите на https://besttime.app
2. Создайте аккаунт (получите 100 free API credits)
3. Получите API ключи:
   - **Private API Key** (для write operations)
   - **Public API Key** (для read operations)

💡 **Tip:** Сохраните ключи в `.env` файл:
```bash
BESTTIME_PRIVATE_KEY=pri_xxxxxxxxxxxxxxxxxx
BESTTIME_PUBLIC_KEY=pub_xxxxxxxxxxxxxxxxxx
```

### **Step 1.2: Выбор тестовых домов**

Выберите **20 care homes** для pilot test с разнообразными характеристиками:

**Критерии выбора:**

| Категория | Количество | Критерии |
|-----------|------------|----------|
| **CQC Outstanding** | 5 домов | Топ-рейтинг, чтобы проверить вашу гипотезу |
| **CQC Good** | 8 домов | Средний рейтинг |
| **CQC Requires Improvement** | 5 домов | Проблемные дома |
| **CQC Inadequate** | 2 дома | Худшие дома |

**География:**
- 10 домов в **London/South East** (urban, high density)
- 5 домов в **Manchester/Birmingham** (medium cities)
- 5 домов в **rural areas** (low density)

**Размер:**
- 5 small (<30 beds)
- 10 medium (30-60 beds)
- 5 large (60+ beds)

### **Step 1.3: Подготовьте тестовый датасет**

Создайте CSV файл `test_homes.csv`:

```csv
home_id,name,address,city,postcode,cqc_rating,beds,location_type,known_issues
1,Brambles Care Home,"123 High Street, London",London,SW1A 1AA,Outstanding,45,urban,none
2,Oaklands Nursing Home,"456 Park Road, Manchester",Manchester,M1 1AD,Good,32,urban,none
3,Riverside Care,"789 River Lane, Devon",Devon,EX1 1AB,Requires Improvement,25,rural,recent_complaints
4,Meadowview Residence,"321 Green Ave, Birmingham",Birmingham,B1 2AB,Good,58,urban,staff_turnover
...
```

---

## 🔬 **PHASE 2: API TESTING (Day 1-2)**

### **Step 2.1: Setup Development Environment**

**Install dependencies:**
```bash
pip install requests pandas python-dotenv
```

**Create test script** `test_besttime.py`:

```python
import requests
import json
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class BestTimeAnalyzer:
    def __init__(self):
        self.private_key = os.getenv('BESTTIME_PRIVATE_KEY')
        self.public_key = os.getenv('BESTTIME_PUBLIC_KEY')
        self.base_url = "https://besttime.app/api/v1"
        
    def create_forecast(self, name, address):
        """
        Create new forecast for a venue
        Cost: 2 credits (if successful)
        """
        url = f"{self.base_url}/forecasts"
        
        params = {
            'api_key_private': self.private_key,
            'venue_name': name,
            'venue_address': address
        }
        
        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}
    
    def get_venue_forecast(self, venue_id):
        """
        Get existing forecast data
        Cost: 1 credit per call
        """
        url = f"{self.base_url}/forecasts/{venue_id}"
        
        params = {
            'api_key_public': self.public_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'status': 'failed'}
    
    def analyze_footfall(self, forecast_data):
        """
        Extract key metrics from BestTime response
        """
        if 'error' in forecast_data or forecast_data.get('status') == 'failed':
            return None
        
        analysis = forecast_data.get('analysis', {})
        
        metrics = {
            'venue_id': forecast_data.get('venue_info', {}).get('venue_id'),
            'venue_name': forecast_data.get('venue_info', {}).get('venue_name'),
            'data_available': True,
            'busy_hours': analysis.get('busy_hours', []),
            'peak_hours': analysis.get('peak_hours', []),
            'quiet_hours': analysis.get('quiet_hours', []),
            'hour_analysis': analysis.get('hour_analysis', []),
            'week_analysis': analysis.get('week_analysis', {}),
            'forecast_updated': forecast_data.get('forecast_updated_on'),
        }
        
        return metrics
    
    def calculate_rightcarehome_score(self, metrics):
        """
        Calculate custom score based on your hypotheses:
        1. Visit patterns (when families visit)
        2. Consistency (regular patterns = good management)
        3. Activity level (too quiet = red flag?)
        """
        if not metrics or not metrics.get('data_available'):
            return None
        
        score = {
            'has_weekend_activity': False,
            'has_evening_visits': False,
            'activity_consistency': 0,
            'overall_score': 0
        }
        
        # Analyze peak hours
        peak_hours = metrics.get('peak_hours', [])
        
        # Check for weekend activity (families typically visit weekends)
        weekend_peaks = [h for h in peak_hours if h.get('day_int', 0) in [5, 6]]  # Sat, Sun
        score['has_weekend_activity'] = len(weekend_peaks) > 0
        
        # Check for evening visits (after work 17:00-20:00)
        evening_peaks = [h for h in peak_hours if 17 <= h.get('hour', 0) <= 20]
        score['has_evening_visits'] = len(evening_peaks) > 0
        
        # Calculate consistency (variance in hourly data)
        hour_analysis = metrics.get('hour_analysis', [])
        if hour_analysis:
            intensities = [h.get('intensity_nr', 0) for h in hour_analysis]
            if intensities:
                avg = sum(intensities) / len(intensities)
                variance = sum((x - avg) ** 2 for x in intensities) / len(intensities)
                score['activity_consistency'] = 100 - min(variance, 100)
        
        # Overall score (0-100)
        score['overall_score'] = (
            (40 if score['has_weekend_activity'] else 0) +
            (30 if score['has_evening_visits'] else 0) +
            (score['activity_consistency'] * 0.3)
        )
        
        return score


# Initialize analyzer
analyzer = BestTimeAnalyzer()

# Load test homes
df = pd.read_csv('test_homes.csv')

results = []

print("🚀 Starting BestTime.app Pilot Test\n")
print(f"Testing {len(df)} care homes...\n")

for idx, row in df.iterrows():
    print(f"[{idx+1}/{len(df)}] Testing: {row['name']}")
    
    # Create forecast
    full_address = f"{row['address']}, {row['city']}, {row['postcode']}, UK"
    forecast = analyzer.create_forecast(row['name'], full_address)
    
    # Wait a moment for processing
    import time
    time.sleep(2)
    
    # Analyze results
    metrics = analyzer.analyze_footfall(forecast)
    
    if metrics:
        score = analyzer.calculate_rightcarehome_score(metrics)
        
        result = {
            'home_id': row['home_id'],
            'name': row['name'],
            'cqc_rating': row['cqc_rating'],
            'beds': row['beds'],
            'location_type': row['location_type'],
            'data_available': True,
            'venue_id': metrics['venue_id'],
            'weekend_activity': score['has_weekend_activity'] if score else None,
            'evening_visits': score['has_evening_visits'] if score else None,
            'activity_score': score['overall_score'] if score else None,
            'forecast_updated': metrics['forecast_updated']
        }
        
        print(f"  ✅ Data available | Score: {result['activity_score']:.1f}")
    else:
        result = {
            'home_id': row['home_id'],
            'name': row['name'],
            'cqc_rating': row['cqc_rating'],
            'beds': row['beds'],
            'location_type': row['location_type'],
            'data_available': False,
            'venue_id': None,
            'weekend_activity': None,
            'evening_visits': None,
            'activity_score': None,
            'forecast_updated': None
        }
        
        print(f"  ❌ No data available")
    
    results.append(result)
    
    # Save intermediate results
    pd.DataFrame(results).to_csv('besttime_results.csv', index=False)
    
    print()

print(f"\n✅ Test Complete! Results saved to besttime_results.csv")
```

### **Step 2.2: Run the test**

```bash
python test_besttime.py
```

**Expected output:**
```
🚀 Starting BestTime.app Pilot Test

Testing 20 care homes...

[1/20] Testing: Brambles Care Home
  ✅ Data available | Score: 78.5

[2/20] Testing: Oaklands Nursing Home
  ❌ No data available

[3/20] Testing: Riverside Care
  ✅ Data available | Score: 45.2

...
```

---

## 📊 **PHASE 3: ANALYSIS (Day 2-3)**

### **Step 3.1: Evaluate Data Coverage**

Create analysis script `analyze_results.py`:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load results
df = pd.read_csv('besttime_results.csv')

print("=" * 60)
print("📊 BESTTIME.APP PILOT TEST RESULTS")
print("=" * 60)
print()

# 1. DATA COVERAGE
coverage_rate = (df['data_available'].sum() / len(df)) * 100
print(f"1️⃣ DATA COVERAGE")
print(f"   Total homes tested: {len(df)}")
print(f"   Homes with data: {df['data_available'].sum()}")
print(f"   Coverage rate: {coverage_rate:.1f}%")
print()

# 2. COVERAGE BY LOCATION TYPE
print(f"2️⃣ COVERAGE BY LOCATION")
location_coverage = df.groupby('location_type').agg({
    'data_available': ['count', 'sum', 'mean']
}).round(2)
print(location_coverage)
print()

# 3. COVERAGE BY CQC RATING
print(f"3️⃣ COVERAGE BY CQC RATING")
cqc_coverage = df.groupby('cqc_rating').agg({
    'data_available': ['count', 'sum', 'mean']
}).round(2)
print(cqc_coverage)
print()

# 4. COVERAGE BY SIZE
print(f"4️⃣ COVERAGE BY HOME SIZE")
df['size_category'] = pd.cut(df['beds'], bins=[0, 30, 60, 100], 
                              labels=['Small (<30)', 'Medium (30-60)', 'Large (60+)'])
size_coverage = df.groupby('size_category').agg({
    'data_available': ['count', 'sum', 'mean']
}).round(2)
print(size_coverage)
print()

# 5. CORRELATION WITH CQC (for homes with data)
df_with_data = df[df['data_available'] == True].copy()

if len(df_with_data) > 0:
    print(f"5️⃣ ACTIVITY SCORE vs CQC RATING")
    print(f"   (для {len(df_with_data)} домов с данными)")
    print()
    
    # Map CQC to numeric
    cqc_map = {
        'Outstanding': 4,
        'Good': 3,
        'Requires Improvement': 2,
        'Inadequate': 1
    }
    df_with_data['cqc_numeric'] = df_with_data['cqc_rating'].map(cqc_map)
    
    # Calculate correlation
    if df_with_data['activity_score'].notna().sum() > 2:
        corr = df_with_data[['cqc_numeric', 'activity_score']].corr().iloc[0, 1]
        print(f"   Correlation: {corr:.3f}")
        
        avg_scores = df_with_data.groupby('cqc_rating')['activity_score'].mean()
        print(f"\n   Average Activity Scores:")
        for rating, score in avg_scores.items():
            print(f"   {rating}: {score:.1f}")
    else:
        print("   ⚠️ Insufficient data for correlation analysis")
    print()

# 6. KEY INSIGHTS
print("=" * 60)
print("🎯 KEY INSIGHTS & RECOMMENDATIONS")
print("=" * 60)
print()

if coverage_rate >= 70:
    print("✅ RECOMMENDATION: PROCEED with BestTime.app")
    print(f"   Coverage rate of {coverage_rate:.1f}% is sufficient for your use case")
elif coverage_rate >= 50:
    print("⚠️ RECOMMENDATION: CONDITIONAL PROCEED")
    print(f"   Coverage rate of {coverage_rate:.1f}% is moderate")
    print("   Consider hybrid approach with other data sources")
elif coverage_rate >= 30:
    print("⚠️ RECOMMENDATION: PROCEED WITH CAUTION")
    print(f"   Coverage rate of {coverage_rate:.1f}% is low")
    print("   BestTime should be supplementary data, not primary")
else:
    print("❌ RECOMMENDATION: DO NOT PROCEED")
    print(f"   Coverage rate of {coverage_rate:.1f}% is too low")
    print("   Consider alternative: Huq or proxy metrics approach")

print()

# Generate visualization
if len(df_with_data) > 0:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Coverage by location
    ax1 = axes[0, 0]
    location_data = df.groupby('location_type')['data_available'].mean() * 100
    location_data.plot(kind='bar', ax=ax1, color=['#2ecc71', '#e74c3c'])
    ax1.set_title('Data Coverage by Location Type')
    ax1.set_ylabel('Coverage %')
    ax1.set_ylim([0, 100])
    
    # Plot 2: Coverage by CQC rating
    ax2 = axes[0, 1]
    cqc_data = df.groupby('cqc_rating')['data_available'].mean() * 100
    cqc_order = ['Outstanding', 'Good', 'Requires Improvement', 'Inadequate']
    cqc_data = cqc_data.reindex([x for x in cqc_order if x in cqc_data.index])
    cqc_data.plot(kind='bar', ax=ax2, color=['#f39c12', '#3498db', '#e67e22', '#e74c3c'])
    ax2.set_title('Data Coverage by CQC Rating')
    ax2.set_ylabel('Coverage %')
    ax2.set_ylim([0, 100])
    
    # Plot 3: Activity score distribution
    ax3 = axes[1, 0]
    if df_with_data['activity_score'].notna().sum() > 0:
        df_with_data['activity_score'].hist(bins=10, ax=ax3, color='#9b59b6', edgecolor='black')
        ax3.set_title('Activity Score Distribution')
        ax3.set_xlabel('Activity Score')
        ax3.set_ylabel('Frequency')
    
    # Plot 4: Activity score vs CQC
    ax4 = axes[1, 1]
    if df_with_data['activity_score'].notna().sum() > 0:
        cqc_scores = df_with_data.groupby('cqc_rating')['activity_score'].mean()
        cqc_scores = cqc_scores.reindex([x for x in cqc_order if x in cqc_scores.index])
        cqc_scores.plot(kind='bar', ax=ax4, color=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'])
        ax4.set_title('Average Activity Score by CQC Rating')
        ax4.set_ylabel('Activity Score')
    
    plt.tight_layout()
    plt.savefig('besttime_analysis.png', dpi=300, bbox_inches='tight')
    print(f"📊 Visualization saved to besttime_analysis.png")
    print()
```

### **Step 3.2: Run analysis**

```bash
python analyze_results.py
```

---

## 🎯 **PHASE 4: DECISION CRITERIA (Day 3)**

### **Decision Matrix**

| Metric | Threshold | Result | Weight | Decision |
|--------|-----------|--------|--------|----------|
| **Overall Coverage** | ≥70% | __%  | 40% | ✅/❌ |
| **Urban Coverage** | ≥75% | __%  | 20% | ✅/❌ |
| **Outstanding Coverage** | ≥60% | __%  | 20% | ✅/❌ |
| **Correlation with CQC** | ≥0.3 | __  | 20% | ✅/❌ |

**Decision Rules:**

1. **GO (Proceed with BestTime)** if:
   - Overall coverage ≥ 70% AND
   - Urban coverage ≥ 75% AND
   - At least 2 other criteria met

2. **CONDITIONAL GO** if:
   - Overall coverage 50-70% OR
   - 2 out of 4 criteria met
   - → Use BestTime as **supplementary data**

3. **NO-GO (Reject BestTime)** if:
   - Overall coverage < 50% OR
   - Urban coverage < 60%
   - → Pivot to **Huq** or **proxy metrics approach**

---

## 📝 **PHASE 5: DEEP DIVE VALIDATION (Day 4)**

### **Manual Validation on 5 Homes**

For the 5 homes with **highest activity scores**, do manual validation:

#### **Validation Checklist:**

1. **Call the care home:**
   ```
   Script: "Hi, I'm researching care homes. 
   What are your typical visiting hours? 
   Are weekends busier than weekdays for family visits?"
   ```

2. **Check Google Reviews patterns:**
   - Do review dates correlate with BestTime peak times?
   - Do reviews mention "busy visiting times"?

3. **Cross-reference with CQC inspection dates:**
   - Did BestTime show spike on CQC inspection date?

4. **Check social media (if available):**
   - Do Facebook posts about "family day" align with peaks?

**Create validation spreadsheet:**

```csv
home_name,besttime_peak_days,actual_visiting_hours,validation_match,notes
Brambles,Weekend evenings,Weekends 14:00-19:00,YES,Perfect match
Oaklands,Weekdays afternoon,Flexible anytime,PARTIAL,Some correlation
...
```

---

## 🚨 **CRITICAL ISSUES TO WATCH**

### **Red Flags:**

1. **False Positives from Adjacent Buildings**
   - ⚠️ If care home is in shopping center/mixed-use building
   - ⚠️ If near busy restaurant/pub
   - **Action:** Note in dataset, potentially exclude from analysis

2. **No Data for Small/Rural Homes**
   - ⚠️ <50 beds in rural areas may have insufficient GPS signals
   - **Action:** Calculate rural coverage separately

3. **Live Data Availability**
   - ⚠️ Check if real-time data is available (pink vs blue)
   - **Action:** Note % of homes with live data

### **Data Quality Checks:**

```python
def validate_data_quality(forecast_data):
    """
    Check for suspicious patterns
    """
    flags = []
    
    analysis = forecast_data.get('analysis', {})
    
    # Check 1: All hours have same intensity = suspicious
    hour_analysis = analysis.get('hour_analysis', [])
    if hour_analysis:
        intensities = [h.get('intensity_nr', 0) for h in hour_analysis]
        if len(set(intensities)) < 3:
            flags.append("SUSPICIOUS: Flat activity pattern")
    
    # Check 2: Peaks at unusual times (3-6 AM) = might be noise
    peak_hours = analysis.get('peak_hours', [])
    night_peaks = [h for h in peak_hours if 3 <= h.get('hour', 0) <= 6]
    if len(night_peaks) > 0:
        flags.append("WARNING: Night-time peaks detected")
    
    # Check 3: No weekend activity = suspicious for care home
    weekend_peaks = [h for h in peak_hours if h.get('day_int', 0) in [5, 6]]
    if len(weekend_peaks) == 0:
        flags.append("WARNING: No weekend activity")
    
    return flags
```

---

## 📊 **DELIVERABLES**

After completing the test, you should have:

1. ✅ **besttime_results.csv** - Raw results
2. ✅ **besttime_analysis.png** - Visualizations
3. ✅ **validation_notes.csv** - Manual validation
4. ✅ **decision_memo.md** - Final recommendation

**Decision Memo Template:**

```markdown
# BestTime.app Pilot Test - Decision Memo

**Date:** [Date]  
**Analyst:** [Your Name]

## Executive Summary
- Tested: 20 care homes across UK
- Coverage rate: ___%
- Recommendation: [GO / CONDITIONAL GO / NO-GO]

## Key Findings
1. Data Coverage: ___
2. Urban vs Rural: ___
3. Correlation with CQC: ___

## Decision
[Detailed reasoning]

## Next Steps
[Action items]

## Budget Impact
- Annual cost: £___
- Cost per home: £___
- ROI estimate: ___
```

---

## 💰 **COST TRACKING**

```python
def calculate_costs(num_homes, num_calls):
    """
    Calculate BestTime costs
    """
    costs = {
        'initial_forecast': num_homes * 2,  # 2 credits per forecast
        'monthly_refresh': num_homes * 2,   # if refreshing monthly
        'annual_refreshes': num_homes * 2 * 12,
    }
    
    # Premium plan pricing (~$0.008/credit)
    price_per_credit = 0.008
    
    costs['initial_cost_usd'] = costs['initial_forecast'] * price_per_credit
    costs['annual_cost_usd'] = costs['annual_refreshes'] * price_per_credit
    costs['annual_cost_gbp'] = costs['annual_cost_usd'] * 0.79  # rough conversion
    
    return costs

# For 2,500 homes
costs_2500 = calculate_costs(2500, 0)
print(f"Initial forecast: ${costs_2500['initial_cost_usd']:.2f}")
print(f"Annual cost: ${costs_2500['annual_cost_usd']:.2f} (£{costs_2500['annual_cost_gbp']:.2f})")
```

---

## 🎓 **LESSONS LEARNED TEMPLATE**

After test, document:

```markdown
## What Worked
- [Item 1]
- [Item 2]

## What Didn't Work
- [Item 1]
- [Item 2]

## Surprises
- [Unexpected finding 1]
- [Unexpected finding 2]

## Alternative Approaches to Consider
- [ ] Huq (UK-specific)
- [ ] Proxy metrics (review velocity, photo uploads)
- [ ] Manual data collection
- [ ] Partnership with care home management software
```

---

## 🚀 **QUICK START CHECKLIST**

- [ ] Day 1: Register BestTime, get API keys
- [ ] Day 1: Create test dataset (20 homes)
- [ ] Day 1: Run test script
- [ ] Day 2: Analyze results
- [ ] Day 3: Manual validation (5 homes)
- [ ] Day 4: Write decision memo
- [ ] Day 5: Present findings to team

---

## 📞 **SUPPORT**

If you encounter issues:
- BestTime Support: Check their website live chat
- API Documentation: https://documentation.besttime.app/
- Community: Their blog has tutorials

---

## ⚡ **FAST TRACK (If Time-Constrained)**

Minimum viable test:
1. Test just **10 homes** (5 Outstanding + 5 others)
2. Focus only on coverage rate
3. Make decision based on: Coverage ≥70% → GO, <70% → NO-GO
4. Total time: **2 hours**

---

**Good luck with your pilot test! 🚀**

*Remember: The goal is not perfection, but a data-driven decision on whether to invest further in BestTime or pivot to alternatives.*
