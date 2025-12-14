# RightCareHome Professional Report - Техническая Спецификация Структуры

**Версия:** 2.0  
**Дата:** 12 декабря 2025  
**Аудитория:** Разработчики, Data Engineers, Product Team  
**Цель:** Blueprint для миграции в новую систему генерации отчетов

---

## 1. ОБЩИЕ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

### 1.1 Формат выдачи
- **Формат:** Web-based PDF (HTML → PDF рендеринг)
- **Страниц:** 23 (фиксированная структура)
- **Breakpoints:** Desktop-first, адаптация для mobile/tablet view
- **Print-friendly:** Каждая страница имеет `break-after-page` для печати

### 1.2 Требования к модульности
- Каждая секция = независимый React компонент
- Все компоненты принимают `props` из единого data provider
- Секции не должны иметь hard-coded данных
- Каждый компонент имеет fallback UI для отсутствующих данных

### 1.3 Входные данные (Assessment Input)

**Технический ID источника:** `professional_assessment_data`

| Поле | Тип | Обязательное | Источник |
|------|-----|--------------|----------|
| `full_name` | string | Yes | User input |
| `email` | string | Yes | User input |
| `phone` | string | Yes | User input |
| `emergency_contact` | string | Yes | User input |
| `preferred_location` | string | Yes | User input (town/postcode) |
| `max_distance` | enum | Yes | ["5 miles", "10 miles", "20 miles", "50 miles"] |
| `placement_timeline` | enum | Yes | ["Urgent (1-2 weeks)", "Soon (1-2 months)", "Planning ahead (3-6 months)"] |
| `care_types[]` | array | Yes | ["Residential", "Nursing", "Dementia", "Palliative", "Respite"] |
| `medical_conditions[]` | array | No | ["Dementia/Alzheimer's", "Diabetes", "Heart conditions", ...] |
| `mobility_level` | enum | Yes | ["Fully mobile", "Walks with aid", "Wheelchair user", "Bed-bound"] |
| `medication_management` | enum | Yes | ["Independent", "Reminders needed", "Full administration required"] |
| `special_equipment[]` | array | No | ["Hospital bed", "Hoist", "Oxygen", "Catheter care", ...] |
| `fall_history` | enum | Yes | ["No falls", "Occasional falls", "Frequent falls", "Recent serious fall"] |
| `major_allergies[]` | array | No | ["Penicillin", "Latex", "Eggs", "Nuts", ...] |
| `dietary_requirements[]` | array | No | ["Diabetic diet", "Vegetarian", "Halal", "Soft food", ...] |
| `behavioral_concerns[]` | array | No | ["Wandering", "Aggression", "Sundowning", ...] |
| `monthly_budget` | enum | Yes | ["<£3,000", "£3,000-£4,000", "£4,000-£5,000", "£5,000+"] |

---

## 2. ДЕТАЛЬНАЯ СТРУКТУРА ОТЧЕТА

---

### СЕКЦИЯ 1: EXECUTIVE SUMMARY (Страница 1)

**Технический ID:** `section_executive_summary`

**Суть и Назначение:**  
Первая страница отчета. Дает немедленный ответ на вопрос "Какой дом престарелых лучше для моего близкого?". Клиент видит топ-3 рекомендации с телефонами и может действовать сразу, не читая весь отчет. Снижает decision paralysis.

**Компоненты UI:**

1. **Заголовок секции**
   - Тип: Heading (h1)
   - Описание: "Your Professional Care Home Analysis for [full_name]"
   - Плейсхолдер: `[DATA_SLOT] full_name из assessment`

2. **Дата генерации**
   - Тип: Text
   - Описание: "Report generated on [date]"
   - Плейсхолдер: `[DATA_SLOT] report_generation_timestamp`

3. **Топ-3 рекомендации (карточки)**
   - Тип: Ranked list с карточками
   - Описание: 3 care home с ranking badges (#1, #2, #3)
   - Для каждого дома:
     - Название дома: `[DATA_SLOT] care_home.name`
     - Overall Score (0-100): `[DATA_SLOT] care_home.overall_score`
     - Адрес: `[DATA_SLOT] care_home.address`
     - Телефон: `[DATA_SLOT] care_home.phone`
     - Waiting list status: `[DATA_SLOT] care_home.waiting_list_status` (enum: "Available now", "2-4 weeks", "3+ months")
     - Why recommended: `[DATA_SLOT] care_home.match_reason` (краткий текст 1-2 предложения)

4. **Срочность действия**
   - Тип: Alert box
   - Описание: Conditional на основе `placement_timeline`
   - Плейсхолдер: 
     - `[LOGIC] IF placement_timeline === "Urgent (1-2 weeks)" THEN "⚠️ Given your urgent timeline, we recommend calling #1 choice today"`
     - `[DATA_SLOT] top_choice.phone`

5. **Next Step CTA**
   - Тип: Button/Link
   - Описание: "Jump to 14-Day Action Plan (Page 15)"
   - Плейсхолдер: `[DATA_SLOT] internal_link to page 15`

---

### СЕКЦИЯ 2: TABLE OF CONTENTS (Страница 2)

**Технический ID:** `section_table_of_contents`

**Суть и Назначение:**  
Навигация по 23 страницам отчета. Клиент не теряется в документе, может перейти к интересующей секции. Показывает структуру отчета и создает ощущение контроля.

**Компоненты UI:**

1. **Заголовок**
   - Тип: Heading (h2)
   - Описание: "Table of Contents"

2. **7 групп секций**
   - Тип: Grouped list с иконками
   - Описание: Навигация сгруппирована по темам:
     1. Overview (Pages 1-5)
     2. Quality Analysis (Pages 6-11)
     3. Financial & Funding (Pages 12-14)
     4. Action Plan (Page 15)
     5. Lifestyle & Location (Pages 16-19)
     6. Trust & Support (Pages 20-22)
     7. Appendix (Page 23)
   - Для каждой секции:
     - Название: `[DATA_SLOT] section_name`
     - Страницы: `[DATA_SLOT] page_range`
     - Иконка: `[DATA_SLOT] section_icon`
     - Клик: `[LOGIC] Navigate to page_number`

3. **Progress indicator**
   - Тип: Circular progress
   - Описание: "You've viewed X of 23 pages"
   - Плейсхолдер: `[DATA_SLOT] user_reading_progress` (if tracked)

---

### СЕКЦИЯ 3: DASHBOARD (Страница 3)

**Технический ID:** `section_dashboard`

**Суть и Назначение:**  
At-a-glance overview топ-выбора. Клиент за 10 секунд понимает общую картину: насколько хорошо совпадает дом с его требованиями, без деталей.

**Компоненты UI:**

1. **Overall Match Score**
   - Тип: Большое числовое значение (0-100) + gauge chart
   - Описание: Weighted score на основе priorities
   - Плейсхолдер: 
     - `[DATA_SLOT] top_choice.overall_score`
     - `[FORMULA] Weighted average of category_scores based on user_priorities`

2. **Verdict Badge**
   - Тип: Badge (цветокодированный)
   - Описание: Качественная оценка
   - Плейсхолдер:
     - `[LOGIC] IF overall_score >= 85 THEN "Excellent Match"`
     - `[LOGIC] IF overall_score 70-84 THEN "Good Match"`
     - `[LOGIC] IF overall_score < 70 THEN "Fair Match"`

3. **Category Scores (6 категорий)**
   - Тип: Bar chart horizontal
   - Описание: Breakdown по категориям
   - Для каждой категории:
     - Название: ["Safety", "Medical Care", "Staff Quality", "Financial Stability", "Comfort", "Location"]
     - Score (0-100): `[DATA_SLOT] top_choice.category_scores.{category_name}`
     - Visual indicator: progress bar + numerical value

4. **Social Proof Testimonial**
   - Тип: Quote card
   - Описание: Одна цитата семьи
   - Плейсхолдер: `[DATA_SLOT] testimonial.text` + `testimonial.author`

---

### СЕКЦИЯ 4: YOUR PRIORITIES MATCH (Страница 4)

**Технический ID:** `section_user_need_match`

**Суть и Назначение:**  
Показывает, что рекомендации персонализированы под ИХ конкретные нужды, а не generic rankings. Клиент видит, что система поняла их приоритеты.

**Компоненты UI:**

1. **Заголовок**
   - Тип: Heading (h2)
   - Описание: "How Our Top 3 Match Your Specific Needs"

2. **User Priorities визуализация**
   - Тип: Tag cloud или weighted list
   - Описание: Топ-5 приоритетов клиента (извлеченные из assessment)
   - Плейсхолдер:
     - `[LOGIC] Extract top priorities from: care_types, medical_conditions, mobility_level, dietary_requirements`
     - Пример: ["Dementia care", "Wheelchair accessible", "Diabetic diet", "Close to family (Manchester)"]
     - `[DATA_SLOT] user_priorities[]`

3. **Comparison table (3 homes × priorities)**
   - Тип: Matrix table
   - Описание: Насколько каждый дом соответствует каждому приоритету
   - Структура:
     - Rows: Top 3 homes
     - Columns: User priorities
     - Cell values: `[DATA_SLOT] home.priority_match_scores.{priority}` (Score 0-10 или ✓/✗)

4. **Explanation text**
   - Тип: Paragraph
   - Описание: "We weighted our analysis based on what matters most to you"
   - Плейсхолдер: Static text

---

### СЕКЦИЯ 5: AT-A-GLANCE COMPARISON (Страница 5)

**Технический ID:** `section_dot_matrix_comparison`

**Суть и Назначение:**  
Быстрое side-by-side сравнение всех 5 homes по ключевым метрикам. Print-friendly формат для family meetings.

**Компоненты UI:**

1. **Comparison Table**
   - Тип: Data table (5 rows × 8 columns)
   - Описание: Все 5 homes в одной таблице
   - Columns:
     1. Home Name: `[DATA_SLOT] home.name`
     2. Overall Score: `[DATA_SLOT] home.overall_score`
     3. Safety: `[DATA_SLOT] home.category_scores.safety`
     4. Medical Care: `[DATA_SLOT] home.category_scores.medical_care`
     5. Staff Quality: `[DATA_SLOT] home.category_scores.staff_quality`
     6. Financial: `[DATA_SLOT] home.category_scores.financial_stability`
     7. Comfort: `[DATA_SLOT] home.category_scores.comfort`
     8. Location: `[DATA_SLOT] home.category_scores.location`

2. **Visual Indicators**
   - Тип: Icons или colored dots
   - Описание: Для каждой ячейки: зеленый (high score), желтый (medium), красный (low)
   - Плейсхолдер:
     - `[LOGIC] IF score >= 80 THEN green`
     - `[LOGIC] IF score 60-79 THEN yellow`
     - `[LOGIC] IF score < 60 THEN red`

---

### СЕКЦИЯ 6: SAFETY ANALYSIS (Страница 6)

**Технический ID:** `section_category_safety`

**Суть и Назначение:**  
Отвечает на эмоциональный вопрос "Will Mum be safe here?". Разбирает CQC safety ratings, incident history, staffing ratios, emergency protocols.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Will Mum be safe here?"
   - Плейсхолдер: `[DATA_SLOT] Use 'Mum' if relationship === 'mother' else use generic 'your loved one'`

2. **Top Home Safety Score**
   - Тип: Large number + progress circle
   - Описание: Safety score топ-дома (0-100)
   - Плейсхолдер: `[DATA_SLOT] top_choice.category_scores.safety`

3. **Key Metrics Breakdown**
   - Тип: Grid of stat cards (3-4 карточки)
   - Для каждой метрики:
     - Название: ["CQC Safety Rating", "Incident Rate", "Night Staffing Ratio", "Emergency Response Time"]
     - Значение: `[DATA_SLOT] top_choice.safety_metrics.{metric_name}`
     - Benchmark: `[DATA_SLOT] industry_average.{metric_name}`
     - Сравнение: `[FORMULA] (home_value - industry_avg) / industry_avg * 100` (% better/worse)

4. **Strengths (топ-3)**
   - Тип: List с иконками
   - Описание: Топ-3 сильные стороны по безопасности
   - Плейсхолдер: `[DATA_SLOT] top_choice.safety_strengths[]` (array of strings)

5. **Concerns (если есть)**
   - Тип: Warning list
   - Описание: Любые concerns или areas for improvement
   - Плейсхолдер: `[DATA_SLOT] top_choice.safety_concerns[]` (array of strings)

6. **What to Do Next Box**
   - Тип: Call-out box
   - Описание: Actionable next step
   - Плейсхолдер: Static text: "Book a safety walkthrough - ask to see night-time staffing rota and emergency procedures"

7. **Verification Items**
   - Тип: Checklist
   - Описание: Что проверить во время визита
   - Плейсхолдер: `[DATA_SLOT] safety_verification_checklist[]` (static или dynamic)

---

### СЕКЦИЯ 7: FOOD SAFETY & HYGIENE (FSA) (Страница 7)

**Технический ID:** `section_fsa_food_hygiene`

**Суть и Назначение:**  
EXCLUSIVE DATA. Official Food Standards Agency ratings. Критично для 45% residents с dietary needs. Ни один конкурент не показывает эти данные.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Will the food be safe and nutritious?"

2. **FSA Rating (0-5 stars)**
   - Тип: Large visual rating (звезды)
   - Описание: Official FSA rating
   - Плейсхолдер: `[DATA_SLOT] top_choice.fsa_rating` (0-5)

3. **Breakdown по категориям FSA**
   - Тип: 3 score cards
   - Описание: FSA scores by sub-categories:
     1. Hygienic Food Handling: `[DATA_SLOT] top_choice.fsa_hygiene_score`
     2. Cleanliness & Condition: `[DATA_SLOT] top_choice.fsa_cleanliness_score`
     3. Management of Food Safety: `[DATA_SLOT] top_choice.fsa_management_score`

4. **Inspection Date & Trend**
   - Тип: Text + trend arrow
   - Описание: Дата последней инспекции
   - Плейсхолдер:
     - `[DATA_SLOT] top_choice.fsa_inspection_date`
     - `[LOGIC] Show trend: IF previous_rating < current_rating THEN "Improving ↑" ELSE "Stable →"`

5. **Conditional: Dietary Needs Match**
   - Тип: Conditional block
   - Описание: If user has dietary_requirements, show специализацию дома
   - Плейсхолдер:
     - `[LOGIC] IF user.dietary_requirements.length > 0 THEN show this block`
     - `[DATA_SLOT] user.dietary_requirements[]`
     - `[DATA_SLOT] top_choice.dietary_specialties[]` (что дом умеет готовить)

6. **What to Do Next**
   - Тип: Call-out box
   - Описание: "Ask to see sample menus and speak with the head chef about [user's dietary needs]"
   - Плейсхолдер: `[DATA_SLOT] user.dietary_requirements[]`

---

### СЕКЦИЯ 8: MEDICAL CARE ANALYSIS (Страница 8)

**Технический ID:** `section_category_medical_care`

**Суть и Назначение:**  
"Will they manage Mum's health conditions properly?" Показывает clinical quality, nursing coverage, specialist access.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Will they manage Mum's health needs properly?"

2. **Medical Care Score**
   - Тип: Large number + visual
   - Описание: Score 0-100
   - Плейсхолдер: `[DATA_SLOT] top_choice.category_scores.medical_care`

3. **Key Metrics**
   - Тип: Grid of cards
   - Метрики:
     - CQC Clinical Rating: `[DATA_SLOT] top_choice.cqc_clinical_rating`
     - Nursing Coverage (hours/day): `[DATA_SLOT] top_choice.nursing_hours_per_day`
     - GP Visit Frequency: `[DATA_SLOT] top_choice.gp_visit_frequency`
     - Hospital Readmission Rate: `[DATA_SLOT] top_choice.hospital_readmission_rate`

4. **Conditional: Medical Conditions Match**
   - Тип: Conditional block
   - Описание: Если user указал medical_conditions, показать соответствие
   - Плейсхолдер:
     - `[LOGIC] IF user.medical_conditions.length > 0 THEN show`
     - `[DATA_SLOT] user.medical_conditions[]`
     - `[DATA_SLOT] top_choice.specialties[]` (matching specialties)
     - `[LOGIC] Flag if any condition NOT covered: "⚠️ Note: This home does not specialize in [condition]. We recommend asking about their experience."`

5. **Strengths & Concerns**
   - Тип: Two columns
   - Плейсхолдер:
     - `[DATA_SLOT] top_choice.medical_strengths[]`
     - `[DATA_SLOT] top_choice.medical_concerns[]`

6. **What to Do Next**
   - Тип: Call-out
   - Описание: "Request meeting with clinical lead to discuss [user's specific conditions]"
   - Плейсхолдер: `[DATA_SLOT] user.medical_conditions[]`

---

### СЕКЦИЯ 9: STAFF QUALITY ANALYSIS (Страница 9)

**Технический ID:** `section_category_staff_quality`

**Суть и Назначение:**  
"Who will be caring for your loved one every day?" Staff quality = #1 concern для 64% families. High turnover = poor continuity.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Who will be caring for Mum every day?"

2. **Staff Quality Score**
   - Тип: Large number + visual
   - Плейсхолдер: `[DATA_SLOT] top_choice.category_scores.staff_quality`

3. **Key Metrics**
   - Тип: Stat cards
   - Метрики:
     - Staff Retention Rate: `[DATA_SLOT] top_choice.staff_retention_rate` (%, benchmark: 65%)
     - Agency Staff Usage: `[DATA_SLOT] top_choice.agency_staff_percentage` (%, lower = better)
     - Staff-to-Resident Ratio: `[DATA_SLOT] top_choice.staff_to_resident_ratio`
     - Training Level (NVQ): `[DATA_SLOT] top_choice.staff_training_level`

4. **Why This Matters**
   - Тип: Info box
   - Описание: "High staff turnover means unfamiliar faces caring for your loved one. Agency staff lack continuity and relationships."
   - Плейсхолдер: Static text

5. **Strengths**
   - Тип: List
   - Плейсхолдер: `[DATA_SLOT] top_choice.staff_strengths[]`

6. **What to Do Next**
   - Тип: Call-out
   - Описание: "Ask about staff retention and whether same carers will look after [name] regularly"
   - Плейсхолдер: `[DATA_SLOT] user.full_name`

---

### СЕКЦИЯ 10: COMMUNITY REPUTATION (Страница 10)

**Технический ID:** `section_community_reputation`

**Суть и Назначение:**  
"What do other families really think?" Aggregated reviews, sentiment analysis, management responsiveness.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "What do other families really think?"

2. **Trust Score**
   - Тип: Large number (0-100)
   - Описание: Composite trust score
   - Плейсхолдер: `[DATA_SLOT] top_choice.trust_score`

3. **Review Summary**
   - Тип: Stats grid
   - Метрики:
     - Google Rating: `[DATA_SLOT] top_choice.google_rating` (1-5 stars)
     - Number of Reviews: `[DATA_SLOT] top_choice.review_count`
     - CareHome.co.uk Rating: `[DATA_SLOT] top_choice.carehome_rating`

4. **Sentiment Analysis**
   - Тип: Bar chart
   - Описание: Breakdown of positive/neutral/negative sentiment
   - Плейсхолдер:
     - `[DATA_SLOT] top_choice.sentiment_breakdown.positive_percent`
     - `[DATA_SLOT] top_choice.sentiment_breakdown.neutral_percent`
     - `[DATA_SLOT] top_choice.sentiment_breakdown.negative_percent`

5. **Management Responsiveness**
   - Тип: Badge + description
   - Описание: Как management отвечает на reviews
   - Плейсхолдер:
     - `[DATA_SLOT] top_choice.management_response_rate` (%)
     - `[LOGIC] IF response_rate > 80% THEN "Highly responsive to feedback"`

6. **Sample Reviews**
   - Тип: Quote cards (2-3 quotes)
   - Описание: Representative positive and critical reviews
   - Плейсхолдер: `[DATA_SLOT] top_choice.sample_reviews[]` (array of review objects)

---

### СЕКЦИЯ 11: FAMILY ENGAGEMENT INSIGHTS (Страница 11)

**Технический ID:** `section_google_places_insights`

**Суть и Назначение:**  
EXCLUSIVE DATA from Google Places BigQuery. Real behavioural data: family visit patterns, dwell time, repeat rates. High repeat rate = happy families.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Do families keep coming back?"

2. **Key Metrics**
   - Тип: Stat cards (4 cards)
   - Метрики:
     - Average Visit Duration: `[DATA_SLOT] top_choice.avg_visit_duration_minutes` (minutes)
     - Repeat Visitor Rate: `[DATA_SLOT] top_choice.repeat_visitor_rate` (%, higher = better)
     - Monthly Footfall Trend: `[DATA_SLOT] top_choice.footfall_trend` (Growing/Stable/Declining)
     - Peak Visiting Times: `[DATA_SLOT] top_choice.peak_visiting_hours[]` (array of time ranges)

3. **12-Month Footfall Trend Chart**
   - Тип: Line chart
   - Описание: Visitor count по месяцам (последние 12 месяцев)
   - Плейсхолдер: `[DATA_SLOT] top_choice.footfall_12_month[]` (array of monthly counts)

4. **What This Means**
   - Тип: Interpretation box
   - Описание: Conditional interpretation
   - Плейсхолдер:
     - `[LOGIC] IF footfall_trend === "Growing" THEN "✅ Increasing family visits suggest improving care quality and satisfaction"`
     - `[LOGIC] IF footfall_trend === "Declining" THEN "⚠️ Declining visits may be an early warning sign. Ask management about recent changes"`

5. **EXCLUSIVE Badge**
   - Тип: Badge
   - Описание: "EXCLUSIVE DATA — Only available in RightCareHome reports"
   - Плейсхолдер: Static

6. **What to Do Next**
   - Тип: Call-out
   - Описание: "Visit during peak family hours ([times]) to observe atmosphere and speak with other visitors"
   - Плейсхолдер: `[DATA_SLOT] top_choice.peak_visiting_hours[]`

---

### СЕКЦИЯ 12: FINANCIAL STABILITY (Страница 12)

**Технический ID:** `section_category_financial_stability`

**Суть и Назначение:**  
"Is this home financially stable?" Protects against closures (700+ UK care homes closed since 2015) and unexpected fee hikes.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Is this home financially stable?"

2. **Financial Stability Score**
   - Тип: Large number (0-100)
   - Плейсхолдер: `[DATA_SLOT] top_choice.category_scores.financial_stability`

3. **Key Indicators**
   - Тип: Stat cards
   - Метрики:
     - Altman Z-Score: `[DATA_SLOT] top_choice.altman_z_score` (>2.6 = safe, 1.1-2.6 = grey zone, <1.1 = distress)
     - Years in Operation: `[DATA_SLOT] top_choice.years_in_operation`
     - Ownership Type: `[DATA_SLOT] top_choice.ownership_type` (enum: "Independent", "Small chain", "Large chain", "Private equity")
     - Recent Fee Increases: `[DATA_SLOT] top_choice.fee_increase_history[]` (last 3 years)

4. **Bankruptcy Risk Assessment**
   - Тип: Visual gauge + text
   - Описание: Risk level
   - Плейсхолдер:
     - `[LOGIC] Based on altman_z_score: Low Risk / Medium Risk / High Risk`
     - `[DATA_SLOT] top_choice.bankruptcy_risk_level`

5. **Ownership Structure Flag**
   - Тип: Conditional warning
   - Описание: Flag private equity ownership
   - Плейсхолдер:
     - `[LOGIC] IF ownership_type === "Private equity" THEN show warning: "⚠️ Private equity ownership can mean cost-cutting pressures. Ask about stability guarantees."`

6. **Fee Transparency**
   - Тип: Rating (1-5 stars)
   - Описание: How transparent are fees?
   - Плейсхолдер: `[DATA_SLOT] top_choice.fee_transparency_rating`

7. **What to Do Next**
   - Тип: Call-out
   - Описание: "Ask for written confirmation of fee increase policy and notice periods"

---

### СЕКЦИЯ 13: FAIR COST GAP CALCULATOR (Страница 13)

**Технический ID:** `section_fair_cost_calculator`

**Суть и Назначение:**  
EXCLUSIVE FEATURE. "Are you being overcharged?" Compares quoted fees vs fair market value. Provides negotiation scripts. Average savings: £3,000-8,000/year.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Are you paying a fair price?"

2. **Cost Comparison Table (5 homes)**
   - Тип: Data table
   - Для каждого дома:
     - Home Name: `[DATA_SLOT] home.name`
     - Quoted Weekly Fee: `[DATA_SLOT] home.quoted_weekly_fee`
     - Fair Market Price: `[DATA_SLOT] home.fair_market_price` (from algorithm)
     - Overcharge Amount: `[FORMULA] quoted_fee - fair_market_price`
     - Overcharge Percent: `[FORMULA] (overcharge_amount / fair_market_price) * 100`
     - Negotiation Potential: `[DATA_SLOT] home.negotiation_potential` (estimated savings)

3. **Top Choice Deep Dive**
   - Тип: Detailed card для топ-выбора
   - Метрики:
     - Current Annual Cost: `[FORMULA] quoted_weekly_fee * 52`
     - Fair Annual Cost: `[FORMULA] fair_market_price * 52`
     - Potential Annual Savings: `[FORMULA] (overcharge * 52)`
     - 5-Year Impact: `[FORMULA] annual_savings * 5`

4. **Benchmark Data**
   - Тип: Info box
   - Описание: "Our algorithm compares against 15,000+ UK care homes with similar ratings and location"
   - Плейсхолдер: Static text

5. **Negotiation Scripts**
   - Тип: Expandable sections (3 scripts)
   - Описание: Word-for-word scripts
   - Scripts:
     1. "How to ask for a discount"
     2. "Negotiating based on market data"
     3. "Requesting fee freeze guarantee"
   - Плейсхолдер: `[DATA_SLOT] negotiation_scripts[]` (static templates with personalized data)

6. **ROI Calculation**
   - Тип: Highlight box
   - Описание: "This £119 report identified £[X] in potential savings = [Y]x return on investment"
   - Плейсхолдер:
     - `[FORMULA] ROI = potential_annual_savings / 119`

7. **What to Do Next**
   - Тип: Call-out
   - Описание: "Use our negotiation script when discussing fees (see templates above)"

---

### СЕКЦИЯ 14: FUNDING OPTIONS (Страница 14)

**Технический ID:** `section_funding_integration`

**Суть и Назначение:**  
UK FIRST feature. "What help is available to pay for care?" 152 local authority specific rules. NHS CHC worth £500-1,500/week if eligible.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "What help is available to pay for care?"

2. **4 Funding Routes**
   - Тип: 4 expandable cards
   - Routes:
     1. NHS Continuing Healthcare (CHC)
     2. Council Funding
     3. Deferred Payment Agreement (DPA)
     4. Attendance Allowance

3. **NHS CHC Eligibility Check**
   - Тип: Checklist + probability score
   - Описание: Based on user's medical_conditions and care_types
   - Плейсхолдер:
     - `[LOGIC] Calculate CHC eligibility probability based on: medical_conditions, care_types, mobility_level, medication_management`
     - `[DATA_SLOT] chc_eligibility_probability` (Low/Medium/High)
     - Показать criteria checklist
     - Value if eligible: `[DATA_SLOT] chc_weekly_value` (static: "£500-1,500/week")

4. **Local Authority Specific Rules**
   - Тип: Conditional block
   - Описание: YOUR council's exact rules
   - Плейсхолдер:
     - `[LOGIC] Extract local authority from preferred_location postcode`
     - `[DATA_SLOT] local_authority_name` (1 of 152 councils)
     - `[DATA_SLOT] local_authority_rules.{council_name}` (means test threshold, contact phone, website)

5. **Council Funding Calculator**
   - Тип: Form calculator
   - Описание: Basic means test estimate
   - Inputs:
     - Savings: `[USER_INPUT]`
     - Property value: `[USER_INPUT]`
   - Output: `[FORMULA] IF savings < £23,250 THEN "Likely eligible" ELSE "Unlikely eligible"`

6. **Contact Information**
   - Тип: Contact cards
   - Для каждого funding route:
     - Organization name
     - Phone number: `[DATA_SLOT] contact_phone`
     - Website: `[DATA_SLOT] contact_website`
     - Application process: Brief steps

7. **152 COUNCILS Badge**
   - Тип: Badge
   - Описание: "Your local council rules included — 152 councils mapped"
   - Плейсхолдер: Static

8. **What to Do Next**
   - Тип: Call-out
   - Описание: "Ring [your council name] adult social care team on [phone number] to request needs assessment"
   - Плейсхолдер:
     - `[DATA_SLOT] local_authority_name`
     - `[DATA_SLOT] local_authority_phone`

---

### СЕКЦИЯ 15: 14-DAY ACTION PLAN (Страница 15)

**Технический ID:** `section_action_plan`

**Суть и Назначение:**  
"What should I do next?" Day-by-day checklist. Transforms overwhelming decision into manageable steps.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "Your 14-Day Action Plan"

2. **Timeline Structure: Week 1 + Week 2**
   - Тип: Two column layout (Week 1 | Week 2)

**Week 1: Research & Shortlist**

3. **Day 1-2: Initial Contact**
   - Тип: Checklist tasks
   - Tasks:
     - "☐ Call [Top Choice Name] on [phone number]"
       - Плейсхолдер: `[DATA_SLOT] top_choice.name`, `[DATA_SLOT] top_choice.phone`
     - "☐ Ask about availability and waiting list"
     - "☐ Request brochure and fee breakdown"

4. **Day 3-4: Funding Check**
   - Тип: Checklist tasks
   - Tasks:
     - "☐ Call [Local Authority] on [phone] to request needs assessment"
       - Плейсхолдер: `[DATA_SLOT] local_authority_name`, `[DATA_SLOT] local_authority_phone`
     - "☐ Check NHS CHC eligibility (see Page 14)"
     - "☐ Apply for Attendance Allowance"

5. **Day 5-7: Schedule Visits**
   - Тип: Checklist tasks
   - Tasks:
     - "☐ Book visit to [Top Choice] — aim for peak visiting hours ([times])"
       - Плейсхолдер: `[DATA_SLOT] top_choice.name`, `[DATA_SLOT] top_choice.peak_visiting_hours[]`
     - "☐ Book visit to [#2 Choice]"
       - Плейсхолдер: `[DATA_SLOT] second_choice.name`
     - "☐ Print verification checklists (see Pages 6-12)"

**Week 2: Visits & Decision**

6. **Day 8-10: Conduct Visits**
   - Тип: Checklist tasks
   - Tasks:
     - "☐ Visit [Top Choice] — use verification checklist"
     - "☐ Ask to see available rooms (not just show rooms)"
     - "☐ Request to speak with current residents' families"
     - "☐ Observe staff interactions and atmosphere"

7. **Day 11-12: Compare & Decide**
   - Тип: Checklist tasks
   - Tasks:
     - "☐ Complete comparison table (Page 5) based on visits"
     - "☐ Discuss with family members — share this report"
     - "☐ Check gut feeling: Would [name] be happy here?"
       - Плейсхолдер: `[DATA_SLOT] user.full_name`

8. **Day 13-14: Secure Place**
   - Тип: Checklist tasks
   - Tasks:
     - "☐ Negotiate fee using scripts (Page 13)"
     - "☐ Request written confirmation of fees and terms"
     - "☐ Pay deposit to secure room"
     - "☐ Coordinate move-in date"

9. **Progress Tracker**
   - Тип: Visual progress bar
   - Описание: "X of 15 tasks completed"
   - Плейсхолдер: `[LOGIC] Track completion if interactive`

---

### СЕКЦИЯ 16: COMFORT & LIFESTYLE (Страница 16)

**Технический ID:** `section_category_comfort`

**Суть и Назначение:**  
"Will Mum be comfortable and happy here?" Room types, activities, dining, gardens. Quality of daily life often matters more than clinical ratings.

**Компоненты UI:**

1. **Emotional Headline**
   - Тип: Heading (h2)
   - Описание: "Will Mum be comfortable and happy here?"

2. **Comfort Score**
   - Тип: Large number (0-100)
   - Плейсхолдер: `[DATA_SLOT] top_choice.category_scores.comfort`

3. **Room & Facilities**
   - Тип: Grid of cards
   - Метрики:
     - Private Rooms: `[DATA_SLOT] top_choice.private_room_percentage` (%)
     - En-suite Availability: `[DATA_SLOT] top_choice.ensuite_availability` (Yes/No/Some)
     - Average Room Size: `[DATA_SLOT] top_choice.avg_room_size_sqm` (square meters)
     - Wheelchair Accessible: `[DATA_SLOT] top_choice.wheelchair_accessible` (Yes/No)

4. **Activities & Social**
   - Тип: Stat cards
   - Метрики:
     - Weekly Activities: `[DATA_SLOT] top_choice.weekly_activities_count`
     - Outdoor Space: `[DATA_SLOT] top_choice.outdoor_space_description`
     - Day Trips/Outings: `[DATA_SLOT] top_choice.outings_per_month`

5. **Dining**
   - Тип: Description cards
   - Метрики:
     - Meal Choice: `[DATA_SLOT] top_choice.meal_choice_availability`
     - Dining Ambience: `[DATA_SLOT] top_choice.dining_ambience_rating`

6. **Strengths**
   - Тип: List
   - Плейсхолдер: `[DATA_SLOT] top_choice.comfort_strengths[]`

7. **Photos (if available)**
   - Тип: Image gallery
   - Плейсхолдер: `[DATA_SLOT] top_choice.room_photos[]` (array of image URLs)

8. **What to Do Next**
   - Тип: Call-out
   - Описание: "Ask to see actual available rooms, not just show rooms"

---

### СЕКЦИЯ 17: LIFESTYLE DEEP DIVE (Страница 17)

**Технический ID:** `section_comfort_lifestyle_deep_dive`

**Суть и Назначение:**  
"What will daily life actually look like?" Activity calendar, personalization, visiting policies, pet policies.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "A Day in the Life at [Top Choice Name]"
   - Плейсхолдер: `[DATA_SLOT] top_choice.name`

2. **Sample Daily Schedule**
   - Тип: Timeline visualization
   - Описание: Typical day
   - Плейсхолдер: `[DATA_SLOT] top_choice.sample_daily_schedule[]` (array of time slots)

3. **Activity Calendar Analysis**
   - Тип: Tag cloud или frequency chart
   - Описание: Types of activities offered
   - Плейсхолдер: `[DATA_SLOT] top_choice.activity_categories[]` (e.g., "Arts & Crafts", "Music", "Exercise", "Outings")

4. **Personalization**
   - Тип: Description block
   - Описание: How does home personalize care?
   - Плейсхолдер: `[DATA_SLOT] top_choice.personalization_description`

5. **Visiting Policies**
   - Тип: Info cards
   - Метрики:
     - Visiting Hours: `[DATA_SLOT] top_choice.visiting_hours`
     - Overnight Guests: `[DATA_SLOT] top_choice.overnight_guests_allowed` (Yes/No)
     - Family Involvement: `[DATA_SLOT] top_choice.family_involvement_policy`

6. **Pet Policy**
   - Тип: Badge + description
   - Плейсхолдер: `[DATA_SLOT] top_choice.pet_policy` (enum: "Pets welcome", "Visiting pets only", "No pets")

7. **What to Do Next**
   - Тип: Call-out
   - Описание: "Request copy of weekly activity schedule and ask about personalised care plans"

---

### СЕКЦИЯ 18: LOCATION WELLBEING (Страница 18)

**Технический ID:** `section_wellbeing_comparison`

**Суть и Назначение:**  
"Is the surrounding area pleasant?" Neighbourhood comparison: green space, noise, air quality, walkability.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "How does the neighbourhood compare?"

2. **Wellbeing Scores (5 homes)**
   - Тип: Comparison table
   - Для каждого дома:
     - Home Name: `[DATA_SLOT] home.name`
     - Green Space Access: `[DATA_SLOT] home.green_space_score` (0-10)
     - Noise Level: `[DATA_SLOT] home.noise_level` (Quiet/Moderate/Busy)
     - Air Quality Index: `[DATA_SLOT] home.air_quality_index`
     - Walkability Score: `[DATA_SLOT] home.walkability_score` (0-100)

3. **Top Choice Deep Dive**
   - Тип: Detailed cards для топ-выбора
   - Metrics:
     - Nearest Park: `[DATA_SLOT] top_choice.nearest_park_distance` (meters)
     - Local Amenities: `[DATA_SLOT] top_choice.local_amenities[]` (array: shops, cafes, library)
     - Crime Rate: `[DATA_SLOT] top_choice.neighbourhood_crime_rate` (vs UK average)

4. **What This Means**
   - Тип: Interpretation box
   - Описание: "Location affects family visiting frequency and resident wellbeing"
   - Плейсхолдер: Static text

---

### СЕКЦИЯ 19: AREA MAP (Страница 19)

**Технический ID:** `section_area_map`

**Суть и Назначение:**  
"What's nearby?" Interactive map showing hospitals, GPs, pharmacies, parks, shops, transport with walking distances.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "What's nearby [Top Choice Name]?"
   - Плейсхолдер: `[DATA_SLOT] top_choice.name`

2. **Interactive Map**
   - Тип: Map embed (Google Maps или similar)
   - Центр карты: `[DATA_SLOT] top_choice.coordinates` (lat, lng)
   - Markers:
     - Care Home: Pin на `[DATA_SLOT] top_choice.coordinates`
     - Nearest Hospital: `[DATA_SLOT] top_choice.nearest_hospital` (coordinates + name)
     - GP Surgeries: `[DATA_SLOT] top_choice.nearby_gps[]` (array of coordinates)
     - Pharmacies: `[DATA_SLOT] top_choice.nearby_pharmacies[]`
     - Parks: `[DATA_SLOT] top_choice.nearby_parks[]`
     - Shops: `[DATA_SLOT] top_choice.nearby_shops[]`

3. **Distance Table**
   - Тип: Data table
   - Для каждого POI:
     - Type: ["Hospital", "GP", "Pharmacy", "Park", "Supermarket"]
     - Name: `[DATA_SLOT] poi.name`
     - Walking Distance: `[DATA_SLOT] poi.walking_distance_meters`
     - Walking Time: `[FORMULA] distance / 80 meters per minute`
     - Driving Time: `[DATA_SLOT] poi.driving_time_minutes`

4. **Public Transport**
   - Тип: Info cards
   - Описание: Nearest bus stops, train stations
   - Плейсхолдер:
     - `[DATA_SLOT] top_choice.nearest_bus_stop` (name + distance)
     - `[DATA_SLOT] top_choice.nearest_train_station` (name + distance)

5. **User's Home Distance**
   - Тип: Highlight box
   - Описание: Distance from user's location
   - Плейсхолдер:
     - `[LOGIC] Calculate distance from user.preferred_location to top_choice.coordinates`
     - `[DATA_SLOT] user_to_home_distance` (miles)
     - `[DATA_SLOT] user_to_home_drive_time` (minutes)

6. **What to Do Next**
   - Тип: Call-out
   - Описание: "Test the journey from your home at peak visiting time"

---

### СЕКЦИЯ 20: WHAT FAMILIES SAY (Страница 20)

**Технический ID:** `section_social_proof`

**Суть и Назначение:**  
"You're not alone in this journey." Curated testimonials, success stories. Social proof reduces anxiety.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "What families say about RightCareHome"

2. **3 Testimonial Cards**
   - Тип: Quote cards с фото (если есть consent)
   - Для каждого testimonial:
     - Quote text: `[DATA_SLOT] testimonial.quote`
     - Author name: `[DATA_SLOT] testimonial.author_name`
     - Author location: `[DATA_SLOT] testimonial.author_location` (e.g., "Birmingham")
     - Context: `[DATA_SLOT] testimonial.context` (e.g., "Found care home for mother with dementia")
     - Time saved: `[DATA_SLOT] testimonial.time_saved` (e.g., "Saved 6 weeks of research")
     - Photo: `[DATA_SLOT] testimonial.author_photo_url` (optional)

3. **Success Metrics**
   - Тип: Stat cards
   - Metrics:
     - Families helped: `[DATA_SLOT] platform_total_families_helped`
     - Average time saved: `[DATA_SLOT] platform_avg_time_saved`
     - Average satisfaction: `[DATA_SLOT] platform_avg_satisfaction_rating` (1-5 stars)

4. **Empathy Message**
   - Тип: Highlight box
   - Описание: "You're not alone. Thousands of families have used our reports to make confident decisions."
   - Плейсхолдер: Static text

---

### СЕКЦИЯ 21: YOUR JOURNEY MATTERS (Страница 21)

**Технический ID:** `section_empathy`

**Суть и Назначение:**  
Emotional support. "Peace of Mind for the Journey Ahead." Acknowledges guilt, anxiety. Humanizes the process.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "Peace of Mind for [Recipient Name]'s Journey Ahead"
   - Плейсхолдер: `[DATA_SLOT] user.full_name`

2. **Empathy Paragraphs (3-4 paragraphs)**
   - Тип: Text blocks
   - Темы:
     1. Acknowledging difficulty: "We know this isn't an easy decision"
     2. Permission to feel: "It's normal to feel conflicted, guilty, or overwhelmed"
     3. Quality of decision: "You've done the hard work of researching thoroughly"
     4. Moving forward: "Trust that you're making the best decision with the information available"
   - Плейсхолдер: Static text (well-crafted emotional copy)

3. **Reassurance Box**
   - Тип: Callout box
   - Описание: "This report gives you peace of mind that you've made an informed, thoughtful choice"
   - Плейсхолдер: Static text

4. **What to Remember**
   - Тип: List
   - Points:
     - "No decision is perfect — there's no 'right' answer"
     - "You can visit and adjust if needed"
     - "Other families have navigated this successfully"
   - Плейсхолдер: Static text

---

### СЕКЦИЯ 22: SHARE WITH FAMILY (Страница 22)

**Технический ID:** `section_share_with_family`

**Суть и Назначение:**  
UK FIRST feature. "Decisions are easier together." One-click sharing to 5 family members, 30-day read-only access.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "Share this report with your family"

2. **Share Form**
   - Тип: Interactive form (5 email fields)
   - Описание: Enter up to 5 email addresses
   - Fields:
     - Family Member 1-5 Email: `[USER_INPUT]`
     - Optional: Relationship (Daughter, Son, Sibling, etc.): `[USER_INPUT]`
   - Button: "Send Report Access"

3. **What They Get**
   - Тип: Info box
   - Описание:
     - "✓ Read-only access to this full report for 30 days"
     - "✓ Personalized email with link"
     - "✓ Downloadable PDF summary"
   - Плейсхолдер: Static text

4. **Why This Matters**
   - Тип: Stat box
   - Описание: "78% of care decisions involve 2+ family members. Sharing ensures everyone is informed."
   - Плейсхолдер: Static text

5. **UK FIRST Badge**
   - Тип: Badge
   - Описание: "Only care home service with built-in family collaboration"
   - Плейсхолдер: Static

6. **Preview of Shared Report**
   - Тип: Screenshot или mockup
   - Описание: Visual of what family members will see
   - Плейсхолдер: Static image or dynamic preview

7. **Already Shared?**
   - Тип: Status section
   - Описание: If already shared, show list of recipients and expiry date
   - Плейсхолдер:
     - `[DATA_SLOT] shared_with_emails[]`
     - `[DATA_SLOT] share_expiry_date`

---

### СЕКЦИЯ 23: APPENDIX - DATA & METHODOLOGY (Страница 23)

**Технический ID:** `section_appendix_data_accuracy`

**Суть и Назначение:**  
Full transparency. "How are scores calculated?" Shows data sources, methodology, verification guide. Trust builder.

**Компоненты UI:**

1. **Headline**
   - Тип: Heading (h2)
   - Описание: "Data Sources & Methodology"

2. **Data Sources Table**
   - Тип: Data table
   - Для каждого источника:
     - Source Name: ["CQC", "FSA FHRS", "Companies House", "Google Places", "ONS", etc.]
     - What We Extract: Description
     - Update Frequency: `[DATA_SLOT] source.update_frequency` (e.g., "Monthly", "Quarterly")
     - Last Updated: `[DATA_SLOT] source.last_update_date`

3. **Scoring Methodology**
   - Тип: Expandable sections
   - Для каждой категории (Safety, Medical, Staff, etc.):
     - Formula explanation (high-level, not technical)
     - Weighting factors
     - Benchmarks used
   - Плейсхолдер: Static text (educational, not revealing proprietary algorithms)

4. **Verification Guide**
   - Тип: Checklist
   - Описание: How users can verify data themselves
   - Items:
     - "✓ Check CQC ratings at [URL]"
     - "✓ Verify FSA hygiene ratings at [URL]"
     - "✓ View Companies House financials at [URL]"
   - Плейсхолдер: Static links

5. **Contact Information**
   - Тип: Contact card
   - Информация:
     - Support email: `[DATA_SLOT] support_email`
     - Phone: `[DATA_SLOT] support_phone`
     - Hours: `[DATA_SLOT] support_hours`

6. **Disclaimer**
   - Тип: Legal text (small font)
   - Описание: Standard disclaimer about data accuracy, recommendations, etc.
   - Плейсхолдер: Static legal text

7. **Report ID**
   - Тип: Text
   - Описание: Unique report ID for reference
   - Плейсхолдер: `[DATA_SLOT] report_id`

---

## 3. УСЛОВНАЯ ЛОГИКА (Conditional Rendering)

### 3.1 User Timeline Urgency

**Условие:** `IF user.placement_timeline === "Urgent (1-2 weeks)"`

**Действие:**
- Показать alert на странице 1 (Executive Summary): "⚠️ Given your urgent timeline, we recommend calling [top choice] today"
- Приоритизировать homes с "Available now" waiting list status

---

### 3.2 Dietary Requirements Match

**Условие:** `IF user.dietary_requirements.length > 0`

**Действие:**
- Страница 7 (FSA Food Safety): Показать блок "Your Dietary Needs Match"
- Cross-reference `user.dietary_requirements[]` с `home.dietary_specialties[]`
- Flag если дом НЕ специализируется: "⚠️ Note: [Home] does not list [dietary need] as a specialty. Ask about their experience during visit."

---

### 3.3 Medical Conditions Специализация

**Условие:** `IF user.medical_conditions.length > 0`

**Действие:**
- Страница 8 (Medical Care): Показать "Your Conditions Match"
- Cross-reference `user.medical_conditions[]` с `home.specialties[]`
- Highlight matches зеленым, missing specialties желтым warning

---

### 3.4 Mobility Requirements

**Условие:** `IF user.mobility_level === "Wheelchair user" OR "Bed-bound"`

**Действие:**
- Страница 16 (Comfort): Приоритизировать wheelchair accessibility
- Flag homes БЕЗ wheelchair access: "⚠️ Limited wheelchair accessibility — verify during visit"

---

### 3.5 Local Authority Detection

**Условие:** Extract council from `user.preferred_location` (postcode lookup)

**Действие:**
- Страница 14 (Funding): Показать SPECIFIC council rules для этого council
- Populate council contact phone: `[DATA_SLOT] local_authority_contacts[council_name].phone`

---

### 3.6 Private Equity Ownership Warning

**Условие:** `IF home.ownership_type === "Private equity"`

**Действие:**
- Страница 12 (Financial Stability): Показать warning: "⚠️ Private equity ownership can mean cost-cutting pressures"

---

### 3.7 CHC Eligibility Probability

**Условие:** Calculate based on `user.medical_conditions[]`, `user.care_types[]`, `user.mobility_level`

**Логика:**
\`\`\`
IF (
  "Dementia/Alzheimer's" IN medical_conditions OR
  "Palliative" IN care_types OR
  mobility_level === "Bed-bound" OR
  medication_management === "Full administration required"
) THEN chc_eligibility = "High"
ELSE IF (
  medical_conditions.length >= 2 OR
  "Nursing" IN care_types
) THEN chc_eligibility = "Medium"
ELSE chc_eligibility = "Low"
\`\`\`

**Действие:**
- Страница 14 (Funding): Показать CHC probability badge

---

## 4. ERROR HANDLING & FALLBACKS

### 4.1 Missing Data Points

**Сценарий:** Данные из API недоступны (например, FSA rating отсутствует)

**Стратегия:**
- Показать placeholder: "Data not available — verify directly with care home"
- НЕ показывать пустые секции
- Логировать missing data для review

### 4.2 Failed External API Calls

**Сценарий:** Google Places API timeout или Companies House API down

**Стратегия:**
- Fallback на cached data (если есть)
- Показать "Data temporarily unavailable — last updated [date]"
- Retry после таймаута

### 4.3 Zero Homes Match Criteria

**Сценарий:** Нет homes в preferred_location в рамках max_distance

**Стратегия:**
- Показать "No homes found within [distance]. Showing closest alternatives within [expanded distance]"
- Expand search radius автоматически
- Предложить alternative locations

### 4.4 Incomplete User Assessment

**Сценарий:** User пропустил optional поля (allergies, behavioral concerns)

**Стратегия:**
- Отчет генерируется с доступными данными
- Conditional sections не показываются если данные отсутствуют
- Не блокировать генерацию отчета

---

## 5. ТЕХНИЧЕСКИЕ ЗАВИСИМОСТИ ДАННЫХ

### 5.1 Матрица зависимостей

| Секция/Страница | Требуемые Data Slots | Критичность | Fallback |
|-----------------|----------------------|-------------|----------|
| Executive Summary (P1) | `homes[]`, `overall_scores[]`, `phone[]` | Critical | Cannot render без homes |
| Dashboard (P3) | `top_choice.overall_score`, `category_scores[]` | Critical | Показать "Calculating..." |
| Safety (P6) | `category_scores.safety`, `safety_metrics{}` | High | Показать CQC rating only |
| FSA Food Safety (P7) | `fsa_rating`, `fsa_breakdown{}` | Medium | "Data unavailable" message |
| Medical Care (P8) | `category_scores.medical_care`, `medical_conditions[]` | High | Generic analysis без matching |
| Staff Quality (P9) | `staff_retention_rate`, `agency_usage` | High | CQC staffing rating only |
| Community Reputation (P10) | `trust_score`, `google_rating`, `reviews[]` | Medium | Показать Google rating only |
| Google Places Insights (P11) | `footfall_data[]`, `repeat_rate`, `dwell_time` | Low | Skip page если нет данных |
| Financial Stability (P12) | `altman_z_score`, `ownership_type` | High | CQC rating + generic warning |
| Fair Cost Calculator (P13) | `quoted_fee`, `fair_market_price` | Critical | Cannot skip, use benchmark |
| Funding (P14) | `local_authority_rules{}`, `chc_criteria` | High | Generic UK funding info |
| Action Plan (P15) | `top_choice.phone`, `local_authority_phone` | Critical | Placeholder phone numbers |
| Area Map (P19) | `top_choice.coordinates`, `nearby_pois[]` | Medium | Text address only |
| Share with Family (P22) | `report_id`, `share_functionality` | Critical | Cannot skip feature |

---

## 6. ANALYTICS & TRACKING

### 6.1 Events to Track

| Event Name | Trigger | Data Captured |
|------------|---------|---------------|
| `report_generated` | Отчет успешно создан | `user_id`, `report_id`, `homes_count`, `generation_time_seconds` |
| `page_viewed` | User открывает страницу отчета | `report_id`, `page_number`, `time_spent_seconds` |
| `section_expanded` | User раскрывает expandable section | `report_id`, `section_id` |
| `share_initiated` | User нажимает "Share with Family" | `report_id`, `num_recipients` |
| `share_completed` | Emails отправлены | `report_id`, `recipients_count` |
| `phone_clicked` | User кликает на телефон care home | `report_id`, `home_name`, `page_number` |
| `negotiation_script_viewed` | User читает negotiation script | `report_id` |
| `action_plan_task_checked` | User отмечает задачу в Action Plan | `report_id`, `task_id` |
| `report_downloaded` | User скачивает PDF | `report_id` |
| `funding_calculator_used` | User использует council funding calculator | `report_id`, `savings_input`, `property_input` |

---

## 7. FUTURE ENHANCEMENTS (Roadmap)

### 7.1 Phase 2 Features (Q1 2026)

1. **Interactive Action Plan**
   - User может tick off tasks в отчете
   - Progress tracked в real-time
   - Email reminders для pending tasks

2. **Family Discussion Mode**
   - Collaborative comments на страницах отчета
   - Voting system для family members ("Which home do you prefer?")
   - Discussion thread по каждой секции

3. **Live Data Updates**
   - Отчет автоматически обновляется если CQC rating меняется
   - Notification если waiting list status изменился

4. **Personalized Video Summary**
   - 2-minute AI-generated video summary отчета
   - Narrator читает ключевые insights

### 7.2 Phase 3 Features (Q2 2026)

1. **Virtual Tour Integration**
   - Embedded 360° tours для homes (если доступно)
   - Street View integration на Area Map

2. **Resident Matching Algorithm**
   - AI predicts personality fit между resident и care home culture
   - Based on lifestyle preferences, hobbies, social needs

3. **Post-Move Follow-Up**
   - Automated check-ins после move-in
   - Feedback loop для improving algorithm

---

## 8. ИТОГОВАЯ CHECKLIST для Разработчиков

### 8.1 Перед миграцией убедитесь:

- [ ] Все 23 секции имеют уникальные технические IDs
- [ ] Для каждого `[DATA_SLOT]` определен fallback
- [ ] Conditional logic протестирована для всех edge cases
- [ ] Error handling реализован для failed API calls
- [ ] Analytics events интегрированы
- [ ] Report generation time < 10 seconds (performance benchmark)
- [ ] PDF export работает корректно (page breaks, styling)
- [ ] Mobile responsive для всех секций
- [ ] Accessibility: screen readers, keyboard navigation
- [ ] GDPR compliance: user data handling, sharing permissions

---

**Конец спецификации.**
