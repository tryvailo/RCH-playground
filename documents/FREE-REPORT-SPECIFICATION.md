# Спецификация Структуры Бесплатного Отчета
## RightCareHome Free Report Blueprint

**Версия:** 2.0  
**Дата:** Январь 2025  
**Аудитория:** Разработчики, Дата-инженеры, Product Team  
**Цель:** Детальное техническое описание структуры бесплатного отчета для миграции в новую систему генерации

---

## 1. ОБЩИЕ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

### 1.1 Формат выдачи
- **Output Format:** Web-based HTML/React components
- **Fallback:** PDF export capability
- **Delivery Method:** Email link + online view
- **Time to Delivery:** Within 10 minutes of assessment completion

### 1.2 Модульность
- Каждая секция должна быть независимым модулем
- Секции можно показывать/скрывать в зависимости от данных
- Возможность изменения порядка секций без breaking changes
- API-first approach: каждая секция получает данные через отдельный endpoint

### 1.3 Персонализация
- Все секции персонализированы на основе входных данных assessment
- Динамическое содержимое на основе: location, care type, budget, funding, duration
- Fallback values для missing data

---

## 2. ВХОДНЫЕ ДАННЫЕ (Assessment Input)

### 2.1 Обязательные поля

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `location_postcode` | String | UK postcode | "B15 2TT" |
| `care_type` | Enum | Тип ухода | "dementia_care", "nursing_care" |
| `budget_range` | String | Недельный бюджет | "1150", "1350", "all" |
| `funding_type` | Enum | Тип финансирования | "privately_funded", "nhs_funded" |
| `duration_type` | Enum | Длительность ухода | "permanent", "respite" |
| `contact_name` | String | Имя контакта | "Sarah Johnson" |
| `contact_email` | Email | Email для отправки | "sarah@example.com" |

### 2.2 Генерируемые поля

| Поле | Описание |
|------|----------|
| `report_id` | Уникальный ID отчета (например, "FREE-2025-01-27-ABC123") |
| `generated_at` | Timestamp генерации отчета |
| `expiry_date` | Дата истечения доступа к отчету (generated_at + 30 дней) |

---

## 3. ДЕТАЛЬНАЯ СТРУКТУРА ОТЧЕТА

### СЕКЦИЯ 1: Expiry Banner

**Название:** Report Expiry Warning Banner  
**Технический ID:** `section_expiry_banner`  
**Позиция:** Fixed top (sticky)  
**Суть и Назначение:**  
Создает sense of urgency и побуждает пользователя сохранить отчет до истечения срока. Снижает bounce rate и увеличивает engagement.

**Составляющие:**

1. **Countdown Timer**
   - Тип: Dynamic numeric display
   - Описание: Показывает оставшееся время до истечения доступа
   - Плейсхолдер для логики: `[Требуется источник данных: expiry_date - current_date, convert to days]`

2. **Save CTA Button**
   - Тип: Interactive button
   - Описание: Кнопка "Save Report" для сохранения в профиль
   - Плейсхолдер для логики: `[Требуется источник данных: user authentication status, if logged_in → direct save, else → show registration modal]`

---

### СЕКЦИЯ 2: Report Header

**Название:** Personalized Report Header  
**Технический ID:** `section_report_header`  
**Позиция:** Top of page (after navigation)  
**Суть и Назначение:**  
Персонализация создает emotional connection ("This is FOR YOU") и подтверждает, что отчет создан специально для получателя на основе его критериев.

**Составляющие:**

1. **Recipient Name Greeting**
   - Тип: Text (H1)
   - Описание: "Report for [Name]"
   - Плейсхолдер для логики: `[Требуется источник данных: contact_name from assessment]`

2. **Location Display**
   - Тип: Text with icon
   - Описание: "Care homes near [Location]"
   - Плейсхолдер для логики: `[Требуется источник данных: location_postcode → resolve to area name via UK postcode API]`

3. **Timeline Display**
   - Тип: Text badge
   - Описание: "Within 3 months" или "ASAP"
   - Плейсхолдер для логики: `[Требуется источник данных: derive from duration_type, if permanent → "Within 3 months", if respite → "Within 1 month"]`

4. **Care Type Tags**
   - Тип: Badge list
   - Описание: Visual tags для типов ухода (например, "Nursing", "Dementia Care")
   - Плейсхолдер для логики: `[Требуется источник данных: care_type from assessment → map to human-readable labels]`

5. **Budget Range Display**
   - Тип: Text
   - Описание: "£5,000-7,000/month"
   - Плейсхолдер для логики: `[Требуется источник данных: budget_range → convert weekly to monthly, format as range]`

6. **Analysis Stats**
   - Тип: Numeric display
   - Описание: "Analysed 156 homes" / "Found 3 matches"
   - Плейсхолдер для логики: `[Требуется источник данных: total_homes_in_area from database, matches_count = 3 (fixed for free report)]`

7. **Report Metadata**
   - Тип: Small text
   - Описание: Report ID and generation timestamp
   - Плейсхолдер для логики: `[Требуется источник данных: report_id, generated_at formatted as "27 January 2025, 14:32"]`

---

### СЕКЦИЯ 3: Value Summary

**Название:** What You're Getting Summary  
**Технический ID:** `section_value_summary`  
**Позиция:** After header  
**Суть и Назначение:**  
Value anchoring: показывает пользователю ЧТО именно он получает в бесплатном отчете до того, как увидит контент. Создает perceived value и снижает bounce rate.

**Составляющие:**

1. **Total Matches Badge**
   - Тип: Numeric badge (large)
   - Описание: "3 Strategic Matches"
   - Плейсхолдер для логики: `[Требуется источник данных: matches_count = 3 (fixed for free tier)]`

2. **Data Points Badge**
   - Тип: Numeric badge
   - Описание: "18 Data Points per Home"
   - Плейсхолдер для логики: `[Требуется источник данных: data_points_count = 18 (fixed for free tier)]`

3. **Features List**
   - Тип: Bullet list with icons
   - Описание: 
     - "3 strategic care home matches (Safe Bet, Best Reputation, Smart Value)"
     - "18 verified data points per home"
     - "Well-being Index score for your area"
     - "Funding eligibility check (NHS CHC, Council, DPA)"
     - "Local area analysis with map"
     - "7-day action plan"
     - "Expert checklists for visits"
   - Плейсхолдер для логики: `[Требуется источник данных: static list, no dynamic data needed]`

---

### СЕКЦИЯ 4: Empathy Section

**Название:** Emotional Validation Section  
**Технический ID:** `section_empathy`  
**Позиция:** Before main content  
**Суть и Назначение:**  
Эмоциональная валидация: "We understand this is hard". Снижает anxiety и создает trust перед показом результатов. Особенно важно для UK audience (empathy before sales).

**Составляющие:**

1. **Empathy Headline**
   - Тип: Text (H2)
   - Описание: "We know how overwhelming this feels"
   - Плейсхолдер для логики: `[Требуется источник данных: static text, no dynamic data]`

2. **Validation Copy**
   - Тип: Paragraph text
   - Описание: Short paragraph validating the difficulty of care home search
   - Плейсхолдер для логики: `[Требуется источник данных: static empathetic copy]`

3. **Reassurance Message**
   - Тип: Text with icon
   - Описание: "You're not alone. We've helped [X] families in [Location] find the right care"
   - Плейсхолдер для логики: `[Требуется источник данных: families_helped_count from database filtered by location_postcode]`

---

### СЕКЦИЯ 5: Priority Score (Interactive)

**Название:** Priority Weighting Tool  
**Технический ID:** `section_priority_score`  
**Позиция:** Before recommendations  
**Суть и Назначение:**  
Engagement mechanism: пользователь активно участвует в формировании результатов (ownership effect). Ранжирует приоритеты (Quality vs Cost vs Proximity), что персонализирует рекомендации.

**Составляющие:**

1. **Interactive Slider/Ranking Interface**
   - Тип: Interactive UI component (drag-and-drop or sliders)
   - Описание: Пользователь ранжирует 3 приоритета:
     - Quality of Care (CQC rating, staff satisfaction)
     - Cost/Value for Money
     - Proximity to Family
   - Плейсхолдер для логики: `[Требуется источник данных: default_weights = [50%, 30%, 20%], user can adjust, store in session/local storage]`

2. **Live Preview**
   - Тип: Dynamic text
   - Описание: "Your matches will prioritize [Quality] over [Cost]"
   - Плейсхолдер для логики: `[Требуется источник данных: real-time calculation based on slider values]`

3. **Confirmation Button**
   - Тип: Button
   - Описание: "See My Matches" CTA
   - Плейсхолдер для логики: `[Требуется источник данных: on click → trigger re-ranking of homes based on priority_weights]`

---

### СЕКЦИЯ 6: Home Recommendations (CORE VALUE)

**Название:** 3 Strategic Care Home Matches  
**Технический ID:** `section_home_recommendations`  
**Позиция:** Center of report (main content)  
**Суть и Назначение:**  
Главная ценность бесплатного отчета: 3 персонализированные рекомендации домов престарелых, подобранные под критерии пользователя. Каждый дом имеет уникальное позиционирование (Safe Bet, Best Reputation, Smart Value).

**Составляющие:**

#### Home Card #1: "Safe Bet"

1. **Home Name**
   - Тип: Text (H3)
   - Описание: Название дома престарелых
   - Плейсхолдер для логики: `[Требуется источник данных: home_name from care_homes table WHERE location NEAR location_postcode AND care_type MATCHES user.care_type, ranked by composite_safety_score]`

2. **Positioning Badge**
   - Тип: Badge
   - Описание: "Safe Bet" label
   - Плейсхолдер для логики: `[Требуется источник данных: static label for position #1]`

3. **Address**
   - Тип: Text with map icon
   - Описание: Full address + distance from user postcode
   - Плейсхолдер для логики: `[Требуется источник данных: address from care_homes table, calculate distance using haversine formula from location_postcode]`

4. **CQC Rating**
   - Тип: Badge (color-coded)
   - Описание: "Outstanding", "Good", "Requires Improvement"
   - Плейсхолдер для логики: `[Требуется источник данных: cqc_overall_rating from care_homes table]`

5. **Weekly Cost**
   - Тип: Numeric display
   - Описание: "From £1,200/week"
   - Плейсхолдер для логики: `[Требуется источник данных: min_weekly_cost from care_homes table filtered by care_type]`

6. **Key Features List**
   - Тип: Bullet list (3-5 items)
   - Описание: Top features that match user priorities
   - Плейсхолдер для логики: `[Требуется источник данных: features from care_homes table, prioritize based on user.priority_weights]`

7. **Priority Match Score**
   - Тип: Percentage bar
   - Описание: "85% match to your priorities"
   - Плейсхолдер для логики: `[Требуется источник данных: calculate weighted score based on priority_weights × home_attributes]`

8. **Contact CTA**
   - Тип: Button
   - Описание: "Request Visit" or "Get Contact Details"
   - Плейсхолдер для логики: `[Требуется источник данных: phone_number, email from care_homes table, track click event]`

#### Home Card #2: "Best Reputation"

*(Same structure as Home #1, but different positioning)*

- Плейсхолдер для логики: `[Требуется источник данных: rank homes by reputation_score (derived from CQC_rating + review_count + review_average)]`

#### Home Card #3: "Smart Value"

*(Same structure as Home #1, but different positioning)*

- Плейсхолдер для логики: `[Требуется источник данных: rank homes by value_score (quality_rating / weekly_cost ratio)]`

---

### СЕКЦИЯ 7: Area Profile

**Название:** Local Area Context  
**Технический ID:** `section_area_profile`  
**Позиция:** After recommendations  
**Суть и Назначение:**  
Дает контекст о локации: демография, средние цены, качество домов в районе. Помогает пользователю понять рынок и подтверждает правильность выбора района.

**Составляющие:**

1. **Area Name**
   - Тип: Text (H2)
   - Описание: "Care Homes in Birmingham"
   - Плейсхолдер для логики: `[Требуется источник данных: location_postcode → resolve to city/town name via UK postcode API]`

2. **Total Homes in Area**
   - Тип: Numeric stat
   - Описание: "147 care homes in Birmingham"
   - Плейсхолдер для логики: `[Требуется источник данных: COUNT care_homes WHERE location = resolved_area]`

3. **Average Weekly Cost**
   - Тип: Numeric stat with comparison
   - Описание: "Average cost: £1,200/week (8% above UK average)"
   - Плейсхолдер для логики: `[Требуется источник данных: AVG(weekly_cost) WHERE location = area, compare to national_average]`

4. **CQC Rating Distribution**
   - Тип: Bar chart or percentage breakdown
   - Описание: "Outstanding: 12% | Good: 68% | Requires Improvement: 20%"
   - Плейсхолдер для логики: `[Требуется источник данных: GROUP BY cqc_rating WHERE location = area, calculate percentages]`

5. **Wellbeing Index Score**
   - Тип: Numeric score (0-100)
   - Описание: "Area Wellbeing Score: 72/100"
   - Плейсхолдер для логики: `[Требуется источник данных: wellbeing_index from area_statistics table WHERE postcode_area = location_postcode]`

6. **Demographics Snapshot**
   - Тип: Icon stats
   - Описание: 
     - "Population 65+: 18%"
     - "Average income: £28,000"
     - "Green spaces: High"
   - Плейсхолдер для логики: `[Требуется источник данных: ONS demographics data WHERE area = resolved_area]`

---

### СЕКЦИЯ 8: Area Map

**Название:** Geographic Visualization  
**Технический ID:** `section_area_map`  
**Позиция:** After area profile  
**Суть и Назначение:**  
Visual confirmation of locations. Показывает где находятся рекомендованные дома относительно user postcode и local amenities (parks, hospitals, transport).

**Составляющие:**

1. **Interactive Map**
   - Тип: Embedded map (Google Maps or Mapbox)
   - Описание: Показывает user location + 3 recommended homes
   - Плейсхолдер для логики: `[Требуется источник данных: user.location_postcode (center), home_1.lat_lng, home_2.lat_lng, home_3.lat_lng as markers]`

2. **Home Markers**
   - Тип: Custom map pins
   - Описание: Pins for each recommended home with labels
   - Плейсхолдер для логики: `[Требуется источник данных: home_name, lat_lng from care_homes table for 3 matched homes]`

3. **Amenities Overlay**
   - Тип: Map layer with icons
   - Описание: Shows nearby parks, hospitals, GP surgeries, transport
   - Плейсхолдер для логики: `[Требуется источник данных: OpenStreetMap or Google Places API → query POIs within 1km radius of user.location_postcode]`

4. **Distance Legend**
   - Тип: Text list
   - Описание: "Home A: 2.3 miles | Home B: 3.1 miles | Home C: 1.8 miles"
   - Плейсхолдер для логики: `[Требуется источник данных: calculate distance from user.location_postcode to each home.lat_lng]`

---

### СЕКЦИЯ 9: Fair Cost Gap

**Название:** Cost Analysis & Potential Overpayment Warning  
**Технический ID:** `section_fair_cost_gap`  
**Позиция:** After area context  
**Суть и Назначение:**  
Problem agitation: показывает пользователю что он может переплачивать, если выберет неправильный дом. Создает FOMO для upgrade к Professional report (где есть детальный Fair Cost Calculator).

**Составляющие:**

1. **Local Authority Name**
   - Тип: Text
   - Описание: "Birmingham City Council"
   - Плейсхолдер для логики: `[Требуется источник данных: location_postcode → resolve to local_authority via UK postcode to council mapping]`

2. **Fair Cost Benchmark**
   - Тип: Numeric stat (highlighted)
   - Описание: "Fair cost for this area: £1,048/week"
   - Плейсхолдер для логики: `[Требуется источник данных: fair_cost_per_week from local_authority_funding table WHERE council = resolved_council AND care_type = user.care_type]`

3. **Market Average**
   - Тип: Numeric stat
   - Описание: "Market average: £1,467/week"
   - Плейсхолдер для логики: `[Требуется источник данных: AVG(weekly_cost) WHERE location = area AND care_type = user.care_type]`

4. **Potential Overpayment**
   - Тип: Numeric stat (alert color)
   - Описание: "Potential overpayment: £419/week (£21,788/year)"
   - Плейсхолдер для логики: `[Требуется источник данных: gap = market_average - fair_cost, multiply by 52 for annual]`

5. **Visual Comparison**
   - Тип: Bar chart or gauge
   - Описание: Visual representation of fair cost vs market average
   - Плейсхолдер для логики: `[Требуется источник данных: fair_cost_per_week, market_average_per_week for visualization]`

6. **Teaser CTA**
   - Тип: Text with link
   - Описание: "Get detailed cost analysis for your 3 homes in Professional Report →"
   - Плейсхолдер для логики: `[Требуется источник данных: link to /professional-assessment with pre-filled data]`

---

### СЕКЦИЯ 10: Funding Eligibility

**Название:** Funding Support Probability Check  
**Технический ID:** `section_funding_eligibility`  
**Позиция:** After cost analysis  
**Суть и Назначение:**  
Создает надежду: "There might be financial help available". Особенно важно для UK audience, где 74% испытывают трудности с funding. Показывает probability scores для NHS CHC, Council Funding, Deferred Payment Agreement.

**Составляющие:**

1. **NHS Continuing Healthcare (CHC) Probability**
   - Тип: Percentage score with gauge
   - Описание: "78% probability you may qualify"
   - Плейсхолдер для логики: `[Требуется источник данных: calculate based on care_type (nursing/dementia higher probability), funding_type from assessment, medical_condition if provided]`

2. **Council Funding Probability**
   - Тип: Percentage score with gauge
   - Описание: "72% probability you may qualify"
   - Плейсхолдер для логики: `[Требуется источник данных: calculate based on budget_range (lower budget → higher probability), local_authority means test thresholds]`

3. **Deferred Payment Agreement (DPA) Probability**
   - Тип: Percentage score with gauge
   - Описание: "85% probability you may qualify"
   - Плейсхолдер для логики: `[Требуется источник данных: calculate based on funding_type (self-funded with property → high probability), UK DPA eligibility rules]`

4. **Potential Weekly Savings**
   - Тип: Numeric stat
   - Описание: "If eligible for Council support: Save up to £419/week"
   - Плейсхолдер для логики: `[Требуется источник данных: gap between market_average and council_funded_rate for local_authority]`

5. **Explainer Copy**
   - Тип: Paragraph text
   - Описание: Short explanation of what each funding type means
   - Плейсхолдер для логики: `[Требуется источник данных: static educational content about NHS CHC, Council Funding, DPA]`

6. **Medical Condition Context**
   - Тип: Text (conditional display)
   - Описание: "Based on [medical_condition], NHS funding is more likely"
   - Плейсхолдер для логики: `[Требуется источник данных: IF user provided medical_condition in assessment → display relevant context]`

7. **Next Steps CTA**
   - Тип: Link
   - Описание: "Get full funding eligibility report with application templates →"
   - Плейсхолдер для логики: `[Требуется источник данных: link to /funding-calculator or Professional Report upgrade]`

---

### СЕКЦИЯ 11: Social Proof

**Название:** Trust & Testimonials  
**Технический ID:** `section_social_proof`  
**Позиция:** Before upsell  
**Суть и Назначение:**  
Build trust перед conversion point. Показывает testimonials от реальных пользователей (особенно из того же региона) + статистику использования сервиса.

**Составляющие:**

1. **Testimonial Cards**
   - Тип: Quote cards (3-4 testimonials)
   - Описание: 
     - Quote text
     - Name (first name + initial)
     - Location
     - Photo (if available)
     - Date
   - Плейсхолдер для логики: `[Требуется источник данных: testimonials table WHERE location NEAR user.location_postcode OR is_featured = true, ORDER BY date DESC LIMIT 3]`

2. **Usage Statistics**
   - Тип: Numeric stats with icons
   - Описание:
     - "Helped [X] families in Birmingham this month"
     - "Average rating: 4.8/5"
     - "Saved families average £3,200/year"
   - Плейсхолдер для логики: `[Требуется источник данных: 
     - COUNT users WHERE location = area AND created_at > current_month
     - AVG(rating) from reviews table
     - AVG(cost_savings) from professional_reports WHERE funding_found = true]`

3. **Trust Badges**
   - Тип: Logo images
   - Описание: "As featured in [The Guardian, BBC, Which?]"
   - Плейсхолдер для логики: `[Требуется источник данных: static press mentions, logo images]`

---

### СЕКЦИЯ 12: Visual Teaser (Upgrade Preview)

**Название:** Professional Report Preview  
**Технический ID:** `section_visual_teaser`  
**Позиция:** Before main CTA  
**Суть и Назначение:**  
Показывает что пользователь УПУСКАЕТ в бесплатном отчете. Blur/pixelate preview секций Professional report (Financial Stability, Staff Satisfaction, Family Visit Patterns). Создает curiosity gap для upsell.

**Составляющие:**

1. **Free vs Professional Comparison Table**
   - Тип: Two-column table
   - Описание: Side-by-side comparison "What's in Free" vs "What's in Professional"
   - Плейсхолдер для логики: `[Требуется источник данных: static feature comparison list, FREE: 18 data points, PRO: 206 data points]`

2. **Blurred Screenshot Previews**
   - Тип: Image gallery with blur effect
   - Описание: Screenshots of exclusive Professional sections:
     - Food Hygiene Rating breakdown
     - Staff satisfaction graphs
     - Family engagement patterns
     - Negotiation scripts
   - Плейсхолдер для логики: `[Требуется источник данных: static screenshot images with CSS blur filter]`

3. **Feature Highlights**
   - Тип: Icon list with badges
   - Описание: List of EXCLUSIVE features with "EXCLUSIVE" or "UK FIRST" badges
   - Плейсхолдер для логики: `[Требуется источник данных: static list of professional features]`

4. **Data Points Counter**
   - Тип: Comparison stat
   - Описание: "Free: 18 data points → Professional: 206 data points (+188)"
   - Плейсхолдер для логики: `[Требуется источник данных: static numbers, FREE = 18, PRO = 206]`

---

### СЕКЦИЯ 13: Upgrade CTA (Conversion Point)

**Название:** Professional Report Upgrade Offer  
**Технический ID:** `section_upgrade_cta`  
**Позиция:** After teaser  
**Суть и Назначение:**  
Main conversion point для upsell в Professional report (£119). Создает urgency + показывает ROI + предлагает payment options.

**Составляющие:**

1. **Headline**
   - Тип: Text (H2)
   - Описание: "Get the full picture before you choose"
   - Плейсхолдер для логики: `[Требуется источник данных: static copy]`

2. **Pricing Display**
   - Тип: Price box
   - Описание: "£119 one-time payment"
   - Плейсхолдер для логики: `[Требуется источник данных: professional_report_price from pricing table]`

3. **Value Proposition List**
   - Тип: Bullet list with checkmarks
   - Описание: What you get in Professional:
     - "206 data points (vs 18 in Free)"
     - "Food Hygiene Data (EXCLUSIVE)"
     - "Staff Satisfaction Insights (EXCLUSIVE)"
     - "Fair Cost Calculator + Negotiation Scripts"
     - "Share with 5 family members (UK FIRST)"
     - etc.
   - Плейсхолдер для логики: `[Требуется источник данных: static professional features list]`

4. **ROI Message**
   - Тип: Text stat
   - Описание: "Average savings: £3,200/year. That's £119 to save £3,200"
   - Плейсхолдер для логики: `[Требуется источник данных: AVG(cost_savings) from professional_reports WHERE funding_found = true]`

5. **Urgency Element**
   - Тип: Timer or limited availability message
   - Описание: "24 reports left today" or "Price increases in 48 hours"
   - Плейсхолдер для логики: `[Требуется источник данных: IF marketing campaign active → display urgency message, ELSE hide]`

6. **Primary CTA Button**
   - Тип: Button (large, prominent)
   - Описание: "Get Professional Report - £119"
   - Плейсхолдер для логики: `[Требуется источник данных: link to /professional-assessment with pre-filled user data]`

7. **Money-Back Guarantee**
   - Тип: Badge + text
   - Описание: "30-day money-back guarantee"
   - Плейсхолдер для логики: `[Требуется источник данных: static guarantee policy]`

8. **Alternative Option**
   - Тип: Text link
   - Описание: "Or continue with your free report • No obligation"
   - Плейсхолдер для логики: `[Требуется источник данных: close modal or scroll down]`

---

### СЕКЦИЯ 14: Action Plan

**Название:** 7-Day Action Roadmap  
**Технический ID:** `section_action_plan`  
**Позиция:** After conversion point  
**Суть и Назначение:**  
Practical value независимо от upsell. Дает пользователю четкий план действий на следующие 7 дней с конкретными задачами и чеклистами. Снижает overwhelm.

**Составляющие:**

1. **Timeline Visual**
   - Тип: Vertical timeline or stepper
   - Описание: 7 days with milestones
   - Плейсхолдер для логики: `[Требуется источник данных: static 7-day plan template]`

2. **Daily Tasks**
   - Тип: Expandable cards (7 cards, one per day)
   - Описание: Each card contains:
     - Day number ("Day 1", "Day 2", etc.)
     - Task headline ("Research your 3 matches")
     - Checklist of sub-tasks (3-5 items)
     - Time estimate ("30 minutes")
   - Плейсхолдер для логики: `[Требуется источник данных: static task templates, personalize with user's home names]`

3. **Day 1 Example**
   - Headline: "Research your 3 matched homes online"
   - Checklist:
     - "Visit [Home A] website"
     - "Read CQC inspection report for [Home B]"
     - "Check Google reviews for [Home C]"
     - "Compare weekly costs"
   - Плейсхолдер для логики: `[Требуется источник данных: home_name, website_url, cqc_report_url from care_homes table for 3 matched homes]`

4. **Downloadable Checklists**
   - Тип: PDF download links
   - Описание: 
     - "Telephone Enquiry Checklist"
     - "In-Person Visit Checklist"
     - "Questions to Ask Staff"
   - Плейсхолдер для логики: `[Требуется источник данных: static PDF files stored in assets folder]`

5. **Progress Tracker**
   - Тип: Interactive checkboxes
   - Описание: User can tick off completed tasks
   - Плейсхолдер для логики: `[Требуется источник данных: store in localStorage or user profile if logged in]`

---

### СЕКЦИЯ 15: Report Footer

**Название:** Legal, Data Sources & Contact  
**Технический ID:** `section_report_footer`  
**Позиция:** Bottom of report  
**Суть и Назначение:**  
Transparency + trust building. Показывает откуда берутся данные (credibility), legal disclaimers, и contact information для support.

**Составляющие:**

1. **Data Sources Disclaimer**
   - Тип: Small text with links
   - Описание: "Data sources: Official regulatory data, financial records, community engagement patterns. Last updated: [date]"
   - Плейсхолдер для логики: `[Требуется источник данных: last_data_sync_date from system metadata]`

2. **Report Metadata**
   - Тип: Small text
   - Описание: "Report ID: [report_id] | Generated: [timestamp] | Expires: [expiry_date]"
   - Плейсхолдер для логики: `[Требуется источник данных: report_id, generated_at, expiry_date]`

3. **Legal Disclaimer**
   - Тип: Small text
   - Описание: Standard disclaimer about data accuracy, not financial advice, etc.
   - Плейсхолдер для логики: `[Требуется источник данных: static legal text]`

4. **Verification Links**
   - Тип: Hyperlinks
   - Описание: "Verify data: CQC website | Check Food Hygiene ratings | View Local Authority funding rules"
   - Плейсхолдер для логики: `[Требуется источник данных: static external links to official sources]`

5. **Contact Support**
   - Тип: Text with email/phone
   - Описание: "Questions about this report? Contact us at support@rightcarehome.co.uk"
   - Плейсхолдер для логики: `[Требуется источник данных: static contact information]`

6. **Privacy & Terms Links**
   - Тип: Hyperlinks
   - Описание: "Privacy Policy | Terms of Service | Refund Policy"
   - Плейсхолдер для логики: `[Требуется источник данных: links to /privacy-policy, /terms-of-service, /refund-policy]`

---

### СЕКЦИЯ 16: Save & Share Bar (Sticky)

**Название:** Report Actions Toolbar  
**Технический ID:** `section_save_share_bar`  
**Позиция:** Fixed bottom (sticky)  
**Суть и Назначение:**  
Persistence mechanism. Позволяет пользователю сохранить отчет в профиль или поделиться с семьей. Снижает churn и увеличивает viral coefficient.

**Составляющие:**

1. **Save Report Button**
   - Тип: Button
   - Описание: "Save to My Account"
   - Плейсхолдер для логики: `[Требуется источник данных: IF user logged_in → save report_id to user.saved_reports, ELSE → show registration modal]`

2. **Share Button**
   - Тип: Button with dropdown
   - Описание: "Share with Family"
   - Options:
     - "Copy shareable link"
     - "Email to family member"
     - "Download as PDF"
   - Плейсхолдер для логики: `[Требуется источник данных: 
     - Generate shareable link: /shared-report/[report_id]
     - Send email with report link
     - Generate PDF export]`

3. **Print Button**
   - Тип: Button
   - Описание: "Print Report"
   - Плейсхолдер для логики: `[Требуется источник данных: trigger browser print dialog with print-friendly CSS]`

4. **Back to Top Button**
   - Тип: Button (icon only)
   - Описание: Arrow up icon
   - Плейсхолдер для логики: `[Требуется источник данных: scroll to top of page]`

---

## 4. ДОПОЛНИТЕЛЬНЫЕ ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

### 4.1 Conditional Logic

**Секции с условным отображением:**

| Секция | Условие показа |
|--------|----------------|
| Fair Cost Gap | Только если `fair_cost_data` доступна для `location_postcode` |
| Funding Eligibility | Только если `funding_type !== 'not_sure'` |
| NHS CHC Probability | Только если `care_type IN ('nursing_care', 'nursing_dementia_care')` |
| Medical Condition Context | Только если user предоставил `medical_condition` в assessment |

### 4.2 Error Handling

**Fallback стратегии для missing data:**

| Отсутствующие данные | Fallback |
|----------------------|----------|
| Home recommendations (нет matches) | Показать "No exact matches found, here are closest alternatives" + расширить радиус поиска |
| Fair Cost benchmark (нет данных для council) | "Fair cost data not available for your council" + показать national average |
| Wellbeing Index | "Data not available" + hide секцию |
| Testimonials (нет для location) | Показать featured testimonials из других регионов |

### 4.3 Performance

- **Page Load Time:** < 3 seconds (critical for engagement)
- **Time to Interactive:** < 5 seconds
- **Mobile Optimization:** Mobile-first responsive design
- **Image Optimization:** Lazy load all images below fold

### 4.4 Analytics & Tracking

**Events для отслеживания:**

| Event | Trigger | Назначение |
|-------|---------|------------|
| `report_viewed` | Report page load | Measure delivery success rate |
| `priority_score_completed` | User submits priorities | Measure engagement |
| `home_card_clicked` | Click on home card | Measure interest in matches |
| `upgrade_cta_clicked` | Click on Professional CTA | Measure conversion intent |
| `report_saved` | User saves report | Measure retention |
| `report_shared` | User shares report | Measure viral coefficient |
| `action_plan_task_checked` | User checks off task | Measure practical usage |

---

## 5. МАТРИЦА ЗАВИСИМОСТЕЙ ДАННЫХ

### 5.1 Основные источники данных

| Источник | Что предоставляет |
|----------|-------------------|
| **Assessment Input** | User-provided: postcode, care_type, budget, funding, duration, contact info |
| **Care Homes Database** | Home details: name, address, CQC rating, weekly cost, features, contact |
| **Local Authority Data** | Fair cost benchmarks, council funding thresholds, DPA rules |
| **UK Postcode API** | Resolve postcode to area name, lat/lng, local authority |
| **Area Statistics** | Demographics, wellbeing index, average costs |
| **Testimonials Database** | User reviews, ratings, social proof |
| **System Metadata** | Report ID generation, timestamps, expiry calculation |

### 5.2 Calculated Fields

| Field | Formula/Logic |
|-------|---------------|
| `composite_safety_score` | CQC rating weight × 0.4 + Financial stability × 0.3 + Staff satisfaction × 0.3 |
| `reputation_score` | CQC rating × 0.5 + Review average × 0.3 + Review count (normalized) × 0.2 |
| `value_score` | (Quality rating / Weekly cost) × 100 |
| `priority_match_percentage` | (Home attributes · User priority weights) / max_possible_score × 100 |
| `nhs_chc_probability` | Based on care_type (nursing → +40%), medical_condition (complex → +30%), assessment criteria |
| `council_funding_probability` | Based on budget_range (lower → higher probability), local authority means test |
| `dpa_probability` | Based on funding_type (self-funded → +50%), property ownership assumed |

---

## 6. БУДУЩИЕ УЛУЧШЕНИЯ (V2.0+)

### 6.1 Персонализация на основе ML

- **Recommendation Engine:** Использовать ML для более точного matching на основе поведения предыдущих пользователей
- **Dynamic Priority Weights:** Автоматически подбирать веса на основе implicit signals (время на странице, клики)

### 6.2 Интеграция с Live Data

- **Real-time Availability:** Показывать актуальную доступность мест в домах
- **Live Pricing:** Динамические цены от провайдеров
- **Recent Inspection Updates:** Автоматическое обновление при новых CQC инспекциях

### 6.3 Интерактивные элементы

- **Virtual Tours:** 360° фото/видео домов
- **Live Chat:** С care advisors для вопросов
- **Booking Integration:** Прямое бронирование визитов через платформу

---

## КОНЕЦ СПЕЦИФИКАЦИИ

**Версия:** 2.0  
**Последнее обновление:** Январь 2025  
**Контакт:** Product Team
