# Technical Specification: PROFESSIONAL Report with Dynamic Scoring Weights

Date: 19 November 2025  
Version: 2.0 — WITH DYNAMIC WEIGHTS (CORRECTED)  
Status: ✅ PRODUCTION-READY

---

## 1. Purpose

Complete technical specification for PROFESSIONAL Assessment Report's 156-point matching logic with **adaptive/dynamic weights** based on client profile conditions. This corrected version addresses the critical flaw of static weights and implements context-aware scoring that prioritizes different factors based on individual client needs.

---

## 2. Key Insight: Why Static Weights Fail

**Problem:** Fixed 19% weight for Medical Capabilities is incorrect for:
- Dementia patient → Medical should be 26%+
- High fall risk → Safety should be 25%+
- Complex medications → Medical should be 28%+

**Solution:** Use **dynamic weights** that adapt based on questionnaire answers (Q6-Q18).

---

## 3. Base Weights (Default Profile)

Used when no critical conditions are identified:

| Category | Points | Base Weight | Details |
|----------|--------|-------------|---------|
| Medical Capabilities | 30 | 19% | Condition-specific care match |
| Safety & Quality | 25 | 16% | CQC + FSA + incident history |
| Location & Access | 15 | 10% | Distance + transport access |
| Cultural & Social | 15 | 10% | Visitor analytics + community |
| Financial Stability | 20 | 13% | Companies House analysis |
| Staff Quality | 20 | 13% | Glassdoor + LinkedIn data |
| CQC Compliance | 20 | 13% | Historical + trends |
| Additional Services | 11 | 7% | Specialized programs |
| **TOTAL** | **156** | **100%** | |

---

## 4. Dynamic Weight Adjustment Rules

### 4.1 High Fall Risk (Q13: `high_risk_of_falling`)

**Condition:** Q13 selected "High risk of falling" or "3+ falls with serious injuries"

**Adjustment:** Safety becomes PRIMARY factor

| Category | Base | Adjusted | Change |
|----------|------|----------|--------|
| Safety & Quality | 16% | 25% | **+9%** |
| Medical Capabilities | 19% | 18% | -1% |
| Location & Access | 10% | 8% | -2% |
| Cultural & Social | 10% | 8% | -2% |
| Financial Stability | 13% | 12% | -1% |
| Staff Quality | 13% | 12% | -1% |
| CQC Compliance | 13% | 12% | -1% |
| Additional Services | 7% | 5% | -2% |

**Rationale:**
- Fall prevention programs become CRITICAL
- CQC Safe rating is most important factor
- Homes without excellent fall prevention score 0 on Safety
- Location/Social become less important than safety infrastructure

**Code:**

```python
if user_profile.fall_history in ["3plus_serious", "high_risk_of_falling"]:
    weights['safety'] += 9
    # Proportionally reduce other categories
```

---

### 4.2 Dementia/Alzheimer's (Q9: `dementia_alzheimers`)

**Condition:** Q9 includes "Dementia/Alzheimer's"

**Adjustment:** Medical Capabilities become PRIMARY factor

| Category | Base | Adjusted | Change |
|----------|------|----------|--------|
| Medical Capabilities | 19% | 26% | **+7%** |
| Safety & Quality | 16% | 18% | +2% |
| Location & Access | 10% | 8% | -2% |
| Cultural & Social | 10% | 10% | 0% |
| Financial Stability | 13% | 12% | -1% |
| Staff Quality | 13% | 14% | +1% |
| CQC Compliance | 13% | 10% | -3% |
| Additional Services | 7% | 2% | -5% |

**Rationale:**
- Dementia-trained staff is CRITICAL
- Medical protocols for dementia care are primary differentiator
- Staff quality (trained caregivers) becomes more important
- Activities/social programs less critical (patient cannot participate meaningfully)
- Location/CQC become less important than dementia expertise

**Code:**

```python
if 'dementia_alzheimers' in user_profile.medical_conditions:
    weights['medical'] += 7
    weights['safety'] += 2  # Dementia safety protocols
    weights['staff'] += 1   # Dementia-trained staff
    weights['services'] -= 5  # Activities not relevant for dementia patients
```

---

### 4.3 Multiple Complex Medical Conditions (Q9: 3+ conditions)

**Condition:** Q9 shows 3 or more medical conditions selected

**Adjustment:** Medical Capabilities DOMINATE all factors

| Category | Base | Adjusted | Change |
|----------|------|----------|--------|
| Medical Capabilities | 19% | 29% | **+10%** |
| Safety & Quality | 16% | 15% | -1% |
| Location & Access | 10% | 7% | -3% |
| Cultural & Social | 10% | 7% | -3% |
| Financial Stability | 13% | 13% | 0% |
| Staff Quality | 13% | 14% | +1% |
| CQC Compliance | 13% | 12% | -1% |
| Additional Services | 7% | 3% | -4% |

**Rationale:**
- Multiple conditions require expert nursing care
- Staff qualifications become critical (need diverse expertise)
- Location/social become less important than medical competence
- Simple activities irrelevant for medically complex patients

**Code:**

```python
if len(user_profile.medical_conditions) >= 3:
    weights['medical'] += 10
    weights['location'] -= 3
    weights['social'] -= 3
    weights['staff'] += 1
    weights['services'] -= 4
```

---

### 4.4 Nursing Level Required (Q8: `medical_care_nursing`)

**Condition:** Q8 selected "Medical care (nursing)" (implies complex medical needs)

**Adjustment:** Medical Capabilities & Staff Quality prioritized

| Category | Base | Adjusted | Change |
|----------|------|----------|--------|
| Medical Capabilities | 19% | 22% | **+3%** |
| Safety & Quality | 16% | 16% | 0% |
| Location & Access | 10% | 9% | -1% |
| Cultural & Social | 10% | 8% | -2% |
| Financial Stability | 13% | 13% | 0% |
| Staff Quality | 13% | 16% | **+3%** |
| CQC Compliance | 13% | 11% | -2% |
| Additional Services | 7% | 5% | -2% |

**Rationale:**
- Nursing-level care requires qualified RNs
- Staff quality directly impacts care delivery
- Medical protocols more important than generic CQC compliance

**Code:**

```python
if 'medical_care_nursing' in user_profile.care_types_needed:
    weights['medical'] += 3
    weights['staff'] += 3
    weights['social'] -= 2
```

---

### 4.5 Low Budget Constraint (Q7: `under_3000_*`)

**Condition:** Q7 shows budget under £3,000/month

**Adjustment:** Financial Stability becomes critical (avoid closure risk)

| Category | Base | Adjusted | Change |
|----------|------|----------|--------|
| Medical Capabilities | 19% | 18% | -1% |
| Safety & Quality | 16% | 16% | 0% |
| Location & Access | 10% | 9% | -1% |
| Cultural & Social | 10% | 9% | -1% |
| Financial Stability | 13% | 19% | **+6%** |
| Staff Quality | 13% | 13% | 0% |
| CQC Compliance | 13% | 13% | 0% |
| Additional Services | 7% | 3% | **-4%** |

**Rationale:**
- Homes with low profit margins (Altman Z-score <2.5) are bankruptcy risks
- Must guarantee 5+ year stability (no mid-contract closure)
- Extras/activities less important than financial security
- Budget = long-term placement guarantee

**Code:**

```python
budget_max = extract_budget(user_profile.budget)  # Q7
if budget_max < 3000:
    weights['financial'] += 6
    weights['services'] -= 4
```

---

### 4.6 Urgent Placement (Q17: `urgent_2_weeks`)

**Condition:** Q17 selected "Urgent (within 2 weeks)"

**Adjustment:** Location & Access become critical

| Category | Base | Adjusted | Change |
|----------|------|----------|--------|
| Medical Capabilities | 19% | 18% | -1% |
| Safety & Quality | 16% | 16% | 0% |
| Location & Access | 10% | 17% | **+7%** |
| Cultural & Social | 10% | 9% | -1% |
| Financial Stability | 13% | 12% | -1% |
| Staff Quality | 13% | 13% | 0% |
| CQC Compliance | 13% | 13% | 0% |
| Additional Services | 7% | 2% | **-5%** |

**Rationale:**
- Proximity to family CRITICAL for crisis placements
- Fewer homes available → must prioritize accessible ones
- Transport access essential (frequent family visits)
- Activities irrelevant in crisis situation

**Code:**

```python
if user_profile.placement_timeline == "urgent_2_weeks":
    weights['location'] += 7
    weights['social'] -= 1
    weights['financial'] -= 1
    weights['services'] -= 5
```

---

### 4.7 Combination Conditions (Multiple adjustments)

**When multiple conditions exist, apply adjustments in priority order:**

1. **Fall Risk** (highest priority) → +9%
2. **Dementia** (if not fall risk) → +7%
3. **Multiple conditions** (if not dementia) → +10%
4. **Nursing required** → +3%
5. **Low budget** → +6%
6. **Urgent placement** → +7%

**Important:** Normalize weights to sum to 100%

```python
def calculate_dynamic_weights(user_profile):
    """
    Calculate adaptive weights based on client conditions.
    Priority order: Fall Risk > Dementia > Complex Medical > Nursing > Budget > Urgent
    """
    
    weights = {
        'medical': 19,
        'safety': 16,
        'location': 10,
        'social': 10,
        'financial': 13,
        'staff': 13,
        'cqc': 13,
        'services': 7
    }
    
    # Priority 1: Fall Risk (HIGHEST - overrides other medical adjustments)
    if user_profile.fall_history in ["3plus_serious", "high_risk_of_falling"]:
        weights['safety'] += 9
        weights['medical'] -= 1
        weights['location'] -= 2
        weights['social'] -= 2
        weights['financial'] -= 1
        weights['staff'] -= 1
        weights['cqc'] -= 1
        weights['services'] -= 2
        return normalize_weights(weights)  # STOP here (don't apply other medical adjustments)
    
    # Priority 2: Dementia (if no fall risk)
    if 'dementia_alzheimers' in user_profile.medical_conditions:
        weights['medical'] += 7
        weights['safety'] += 2
        weights['location'] -= 2
        weights['staff'] += 1
        weights['cqc'] -= 3
        weights['services'] -= 5
        return normalize_weights(weights)  # STOP here
    
    # Priority 3: Multiple complex conditions (if not dementia)
    if len(user_profile.medical_conditions) >= 3:
        weights['medical'] += 10
        weights['location'] -= 3
        weights['social'] -= 3
        weights['staff'] += 1
        weights['services'] -= 4
        return normalize_weights(weights)  # STOP here
    
    # Priority 4: Nursing required
    if 'medical_care_nursing' in user_profile.care_types_needed:
        weights['medical'] += 3
        weights['staff'] += 3
        weights['location'] -= 1
        weights['social'] -= 2
        weights['services'] -= 2
    
    # Priority 5: Low budget
    if user_profile.budget < 3000:
        weights['financial'] += 6
        weights['medical'] -= 1
        weights['location'] -= 1
        weights['social'] -= 1
        weights['services'] -= 4
    
    # Priority 6: Urgent placement
    if user_profile.placement_timeline == "urgent_2_weeks":
        weights['location'] += 7
        weights['medical'] -= 1
        weights['social'] -= 1
        weights['financial'] -= 1
        weights['services'] -= 5
    
    # Normalize to ensure sum = 100%
    return normalize_weights(weights)


def normalize_weights(weights):
    """Ensure weights sum to 100%"""
    total = sum(weights.values())
    return {k: round((v / total) * 100, 1) for k, v in weights.items()}
```

---

## 5. Updated Master Scoring Function

```python
def calculate_156_point_match(home, user_profile, enriched_data):
    """
    Calculate comprehensive match score with DYNAMIC WEIGHTS.
    
    1. Determine dynamic weights based on user profile
    2. Calculate individual category scores (0-1.0)
    3. Apply weights to get final score (0-156)
    """
    
    # Step 1: Calculate dynamic weights
    weights = calculate_dynamic_weights(user_profile)
    
    # Step 2: Calculate category scores (0-1.0 scale)
    category_scores = {
        'medical': calculate_medical_capabilities(home, user_profile, enriched_data),
        'safety': calculate_safety_quality(home, user_profile, enriched_data),
        'location': calculate_location_access(home, user_profile),
        'social': calculate_cultural_social(home, user_profile, enriched_data),
        'financial': calculate_financial_stability(home, enriched_data),
        'staff': calculate_staff_quality(home, enriched_data),
        'cqc': calculate_cqc_compliance(home, enriched_data),
        'services': calculate_additional_services(home, user_profile)
    }
    
    # Step 3: Calculate point allocations with adjusted weights
    point_allocations = {
        'medical': category_scores['medical'] * (weights['medical'] / 100) * 156,
        'safety': category_scores['safety'] * (weights['safety'] / 100) * 156,
        'location': category_scores['location'] * (weights['location'] / 100) * 156,
        'social': category_scores['social'] * (weights['social'] / 100) * 156,
        'financial': category_scores['financial'] * (weights['financial'] / 100) * 156,
        'staff': category_scores['staff'] * (weights['staff'] / 100) * 156,
        'cqc': category_scores['cqc'] * (weights['cqc'] / 100) * 156,
        'services': category_scores['services'] * (weights['services'] / 100) * 156
    }
    
    # Step 4: Calculate total match score
    total_score = sum(point_allocations.values())
    
    return {
        'total': int(total_score),
        'normalized': int((total_score / 156) * 100),
        'weights': weights,
        'category_scores': category_scores,
        'point_allocations': point_allocations
    }
```

---

## 6. Example Calculations

### Example 1: High Fall Risk Patient

**Profile:**
- Q9: No specific medical conditions
- Q13: "High risk of falling"
- Q17: Flexible timeline

**Dynamic Weights Applied:**
- Safety & Quality: 25% (↑ from 16%)
- Medical Capabilities: 18% (↓ from 19%)
- Location: 8% (↓ from 10%)
- Other categories reduced proportionally

**Scoring Impact:**
- Home A: Excellent fall prevention (CQC Safe 9.5/10) → Safety Score: 0.95
  - Old: 0.95 × 16% × 156 = 23.76 points
  - **New: 0.95 × 25% × 156 = 36.99 points** (+56% boost)

- Home B: No documented fall prevention (CQC Safe 6.5/10) → Safety Score: 0.65
  - Old: 0.65 × 16% × 156 = 16.25 points
  - **New: 0.65 × 25% × 156 = 25.35 points** (still penalized but less)

**Result:** Homes with excellent fall prevention systems now rank MUCH higher.

---

### Example 2: Dementia Patient

**Profile:**
- Q9: Dementia/Alzheimer's
- Q8: Residential care needed
- Q16: Prefers quiet

**Dynamic Weights Applied:**
- Medical Capabilities: 26% (↑ from 19%)
- Safety & Quality: 18% (↑ from 16%)
- Staff Quality: 14% (↑ from 13%)
- Additional Services: 2% (↓ from 7%)
- CQC Compliance: 10% (↓ from 13%)

**Scoring Impact:**
- Home A: Dementia specialists on staff, 5+ years experience → Medical Score: 0.92
  - Old: 0.92 × 19% × 156 = 27.42 points
  - **New: 0.92 × 26% × 156 = 37.48 points** (+37% boost)

- Home B: General care, no dementia training → Medical Score: 0.55
  - Old: 0.55 × 19% × 156 = 16.39 points
  - **New: 0.55 × 26% × 156 = 22.39 points** (still penalized)

**Result:** Homes with specialized dementia care now rank much higher. Activity programs (usually Home B's strength) become less relevant.

---

### Example 3: Low Budget Constraint

**Profile:**
- Q7: Budget £2,500/month
- Q9: General conditions
- Q13: No fall risk

**Dynamic Weights Applied:**
- Financial Stability: 19% (↑ from 13%)
- Services: 3% (↓ from 7%)
- Location: 9% (↓ from 10%)

**Scoring Impact:**
- Home A: Altman Z-score 3.2 (very safe), profitable → Financial Score: 0.95
  - Old: 0.95 × 13% × 156 = 19.27 points
  - **New: 0.95 × 19% × 156 = 28.16 points** (+46% boost)

- Home B: Altman Z-score 1.5 (bankruptcy risk) → Financial Score: 0.35
  - Old: 0.35 × 13% × 156 = 7.15 points
  - **New: 0.35 × 19% × 156 = 10.41 points** (heavily penalized)

**Result:** Financially stable homes now much more likely to be recommended (avoiding mid-contract closure disaster).

---

## 7. Report Generation with Dynamic Weights

When generating the Professional Report, include:

```markdown
## Match Score Explanation

Your match scores are calculated using adaptive weights based on your specific needs:

**Applied Weights (for your profile):**
- Safety & Quality: 25% ← HIGH PRIORITY (due to fall risk)
- Medical Capabilities: 18%
- Financial Stability: 13%
- Staff Quality: 13%
- CQC Compliance: 12%
- Location & Access: 8%
- Cultural & Social: 8%
- Additional Services: 5%

**Why these weights?**
You indicated high fall risk (Q13), so safety and fall prevention 
programs become our primary matching factor. We prioritize homes 
with excellent CQC Safe ratings and documented fall prevention 
protocols.

**Home Scores (out of 156 points):**
- Manor House: 142 pts (91%) ← HIGHEST MATCH
- Greenfield: 118 pts (76%)
- etc.
```

---

## 8. Database Storage

```sql
-- Store applied weights with report
CREATE TABLE professional_reports (
    id UUID PRIMARY KEY,
    questionnaire_id UUID REFERENCES questionnaires(id),
    applied_weights JSONB,  -- Store weights used for this report
    home_ids UUID[],
    match_scores INTEGER[],
    pdf_s3_url TEXT,
    generated_at TIMESTAMP
);

-- Example JSONB:
{
  "medical": 26,
  "safety": 18,
  "location": 8,
  "social": 10,
  "financial": 12,
  "staff": 14,
  "cqc": 10,
  "services": 2,
  "applied_conditions": ["dementia_alzheimers", "multiple_conditions"]
}
```

---

## 9. Edge Cases

### 9.1 Conflicting Conditions

If user has both **high fall risk** AND **dementia**, apply **Fall Risk** (higher priority):

```python
# Fall Risk overrides Dementia
if "high_risk_of_falling" in conditions:
    # Apply fall risk weights (do NOT also apply dementia weights)
    pass
elif "dementia" in conditions:
    # Apply dementia weights
    pass
```

### 9.2 No Conditions Identified

If questionnaire shows no critical conditions, use **base weights** (19%, 16%, 10%, etc.).

### 9.3 Borderline Cases

If Q13 = "1-2 falls, no serious injuries" (not high risk), use base weights + small adjustments:

```python
if user_profile.fall_history == "12_no_serious":
    weights['safety'] += 2  # Minor boost, not full +9%
```

---

## 10. Performance Impact

- **Weight calculation**: <5ms (simple arithmetic)
- **Scoring with weights**: Same as without (no extra DB queries)
- **Total latency**: No additional overhead
- **Memory**: +1KB per report (weights stored as JSONB)

---

## 11. Testing Checklist

- [ ] Fall risk patient gets high safety scores
- [ ] Dementia patient gets high medical scores
- [ ] Low budget prioritizes financial stability
- [ ] Urgent placement prioritizes location
- [ ] Multiple conditions override individual conditions
- [ ] Weights normalize to 100%
- [ ] Edge cases handled (conflicting conditions)
- [ ] A/B test: Dynamic vs static weights

---

## 12. Documentation

When delivering to engineering team:

1. **Show examples** of weight adjustments (5-6 profiles)
2. **Explain priority order** (Fall Risk > Dementia > etc.)
3. **Provide test cases** with expected outputs
4. **Include database schema** changes
5. **Add error handling** for edge cases

---

**CRITICAL CHANGE:** This v2.0 completely overhauls the matching logic to use context-aware, adaptive weights. This is NOT backward compatible with v1.0 static weights.

**DEPLOYMENT:** Replace entire matching algorithm (Sections 5-8 of previous v1.0 document).

**TESTING DURATION:** 1-2 weeks (A/B test vs v1.0)

---

**End of document.**
