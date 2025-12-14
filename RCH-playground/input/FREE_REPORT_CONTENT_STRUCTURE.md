# БЕСПЛАТНЫЙ ОТЧЕТ - ТЕКУЩИЙ КОНТЕНТ И СТРУКТУРА

**Файл:** `components/report/FreeReportContent.tsx`  
**URL:** `/report/free/[id]`  
**Дата:** 2025-01-27

---

## ОБЩАЯ СТРУКТУРА

Отчет состоит из следующих секций (в порядке отображения):

1. Header (ReportHeader)
2. Navigation (ReportNavigation)
3. Overview Section (ValueProposition + Stats)
4. Your Strategic Options (3 CareHomeCard)
5. Action Plan (NextSteps)
6. Compare & Calculate (ComparisonTable + CostCalculator)
7. Important Warnings (MistakesToAvoid)
8. Trust & Social Proof (Testimonials)
9. Learn More (AboutShortlist)
10. Upgrade Options (ValueBridge + CTA)
11. StickyCTA (фиксированная кнопка)
12. Footer

---

## 1. REPORT HEADER

**Компонент:** `components/report/ReportHeader.tsx`

**Контент:**
- **Заголовок:** "Your Free {city} Shortlist"
- **Подзаголовок:** "{careHomesCount} Care Homes Near {postcode}"
- **Элементы:**
  - Postcode badge с значением postcode
  - Кнопка печати отчета (PrintReportButton)

**Стили:** `report-header-free text-inverse py-lg`

---

## 2. REPORT NAVIGATION

**Компонент:** `components/report/ReportNavigation.tsx`

**Секции навигации:**
- Overview
- Your Homes
- Next Steps
- Compare
- Warnings
- Trust
- Learn More
- Upgrade

**Поведение:** Sticky navigation при скролле

---

## 3. OVERVIEW SECTION

### 3.1 Value Proposition

**Компонент:** `components/report/ValueProposition.tsx`

**Заголовок:**
"Not Just 3 Homes — 3 Strategic Choices"

**Текст:**
"We've analyzed care homes near **{postcode}** using 3 different strategies, so you can choose based on what matters most to YOUR family."

**Информационный блок:**
"💡 **How We Selected These 3 Homes**

Most services just show the *3 closest* homes. We've gone further — applying **3 professional strategies** to give you meaningful choices based on safety, reputation, or value.

**This is what professional care advisors do** — and now it's available to you for free."

**Примечание:**
"**Note:** Availability changes weekly. These homes had spaces as of today."

---

### 3.2 Stats

**Компонент:** `components/report/Stats.tsx`

**Заголовок:**
"Why Families Trust Our Analysis"

**Статистика (3 карточки):**
- **277** Birmingham homes analysed
- **48h** Report delivery time
- **100%** Independent & unbiased

---

## 4. YOUR STRATEGIC OPTIONS

**Разделитель:** "Your Strategic Options"

**Компонент:** `components/report/CareHomeCard.tsx` (отображается 3 раза)

**Заголовок секции:**
"Your 3 Strategic Care Home Options"

**Подзаголовок:**
"We've selected these homes using **different strategies** — not just proximity. Choose the approach that matches your family's priorities."

### Структура карточки Care Home:

**Заголовок карточки:**
- Название care home (с классом `decision-highlight`)
- Локация и postcode
- Бейдж стратегии (Safe Bet / Best Reputation / Smart Value) с иконкой

**Бейджи:**
- CQC: {cqcRating}
- {distance} away

**Цена:**
- £{weeklyPrice} per week

**Блок "Why we chose this home":**
- Заголовок: "Why we chose this home:"
- Текст: {whyChosen}

**Две колонки:**

**Левая колонка - Key Strengths:**
- Список {keyStrengths}

**Правая колонка - Contact:**
- Phone: {contact.phone}
- Email: {contact.email}

**Кнопка (если есть detailedProfile):**
"Show Detailed Profile" / "Hide Detailed Profile"

### Detailed Profile (раскрывающийся блок):

**Заголовок:**
"🏥 {careHome.name} - Detailed Profile"

**Две колонки:**

**Левая колонка:**
- **Specializations:**
  - {title}: {description} (для каждой специализации)
- **Key Features:**
  - Список {keyFeatures}

**Правая колонка:**
- **Recent Performance:**
  - Staff retention: {performance.staffRetention}
  - Family satisfaction: {performance.familySatisfaction}
  - Incident rate: {performance.incidentRate}
- **Things to Consider:**
  - Список {considerations}

---

## 5. ACTION PLAN

**Разделитель:** "Action Plan"

**Компонент:** `components/report/NextSteps.tsx`

**Разделитель внутри:**
"How to Use Your Free Shortlist"

**Заголовок:**
"📋 Your Action Plan"

**Подзаголовок:**
"Follow this structured plan to make the most of your free shortlist"

**Две карточки:**

### Карточка 1: This Week: Phone Calls

**Заголовок:** "📞 This Week: Phone Calls"

**Список действий:**
1. Call each home to check availability
2. Ask about waiting lists (typically 2-4 weeks)
3. Request viewing appointments
4. Clarify additional costs (nursing, activities)

**Примечание:**
"**Best time:** Tuesday-Thursday, 10am-2pm"

### Карточка 2: Next Week: Visits

**Заголовок:** "👀 Next Week: Visits"

**Top 3 questions to ask:**
1. How do you manage [specific condition]?
2. What's your staff-to-resident ratio?
3. Can family members visit anytime?

**What to observe:**
- Are residents engaged and happy?
- Do staff interact kindly?
- Is the environment clean?

### Red Flags Card

**Заголовок:** "🚨 Red Flags"

**Две колонки с предупреждениями:**
- ❌ Staff seem rushed or stressed
- ❌ Residents appear unkempt
- ❌ Strong chemical smells
- ❌ Limited visiting hours
- ❌ No family involvement
- ❌ High staff turnover

### Telephone Enquiry Checklist

**Заголовок:**
"Telephone Enquiry Checklist"

**Подзаголовок:**
"Use this checklist when calling care homes to gather essential information"

**Кнопка:**
"Show Full Checklist (10 questions)" / "Hide Checklist"

**Чеклист (раскрывающийся):**

**4 карточки:**

1. **Availability & Care Services:**
   - 1. Do you currently have beds available?
   - 2. What level of nursing care is available on-site?
   - 3. Do you have experience managing [specific condition]?

2. **Costs & Financial Details:**
   - 4. What exactly is included in the weekly fee?
   - 5. Are there additional charges for activities, laundry, or hairdressing?
   - 6. What are your annual fee increase policies?

3. **Daily Life & Family Involvement:**
   - 7. What are your visiting hours and policies?
   - 8. How do you communicate with families about care?
   - 9. Can you accommodate special dietary requirements?

4. **Next Steps:**
   - 10. When can we arrange a viewing?

**Alert блок:**
"**Printable Checklist**

This telephone enquiry checklist has been included in your email, along with the free shortlist and space to record answers from each care home

[Print This Page]"

**Примечание:**
"**Note:** Our comprehensive assessment includes a detailed 37-point professional checklist for in-person visits, covering medical protocols and safety observations"

---

## 6. COMPARE & CALCULATE

**Разделитель:** "Compare & Calculate"

### 6.1 Comparison Table

**Компонент:** `components/report/ComparisonTable.tsx`

**Заголовок:**
"Quick Comparison: Which Strategy Suits You?"

**Подзаголовок:**
"Compare the three strategic approaches to find the best fit for your family's priorities."

**Таблица сравнения:**

**Заголовки колонок:**
- Priority
- Safe Bet (с иконкой)
- Best Reputation (с иконкой)
- Smart Value (с иконкой)

**Строки:**
- **Main Focus:**
  - Safe Bet: "Peace of mind about safety"
  - Best Reputation: "Proven excellent care"
  - Smart Value: "Budget management"

- **Distance Priority:**
  - Safe Bet: "High (wants close)"
  - Best Reputation: "Medium (willing to travel)"
  - Smart Value: "Flexible"

- **Best For:**
  - Safe Bet: "Families prioritizing safety & convenience"
  - Best Reputation: "Families seeking outstanding care quality"
  - Smart Value: "Budget-conscious families"

- **Weekly Cost:** (выделенная строка)
  - £{weeklyPrice} для каждого дома

- **Recommended Home:**
  - Название каждого care home

**Мобильная версия:** Индикатор "← Swipe to see all columns →"

---

### 6.2 Cost Calculator

**Компонент:** `components/report/CostCalculator.tsx`

**Функционал:**
- Выбор care home из dropdown
- Расчет месячных затрат (базовые + дополнительные)
- График годовых затрат на 3 года (Bar Chart с Chart.js)
- Отображение базовых затрат и дополнительных услуг
- Итоговая проектируемая стоимость за 3 года

**Расчеты:**
- Weekly fee × 4.33 = Monthly base
- Monthly extras: £320 (estimated)
- Yearly costs с учетом инфляции 5% в год
- Total projected cost за 3 года

**График:**
- Bar chart с двумя датасетами:
  - Base Care Costs
  - Additional Services
- Цвета: Primary и Success из brand book

**Отображение:**
- Monthly breakdown
- Yearly breakdown (Year 1, Year 2, Year 3)
- Total projected cost

---

## 7. IMPORTANT WARNINGS

**Разделитель:** "Important Warnings"

**Компонент:** `components/report/MistakesToAvoid.tsx`

**Заголовок:**
"3 Expensive Mistakes to Avoid"

**Подзаголовок:**
"These mistakes cost Birmingham families £3,000-£10,000 per year. Here's how to avoid them with your free shortlist:"

**3 карточки ошибок:**

### Mistake #1: Missing Hidden Fees
- **Real cost:** £180/week in "extras" not mentioned in advertised price = £9,360/year
- **How to avoid:** Use our telephone checklist (below) to ask the right questions, or upgrade to Professional Assessment for expert verification.

### Mistake #2: Choosing Based Only on CQC Rating
- **Real impact:** "Good" rating doesn't mean good fit for YOUR needs
- **How to avoid:** Use our telephone checklist (below) to ask the right questions, or upgrade to Professional Assessment for expert verification.

### Mistake #3: Not Checking Specialist Care Capability
- **Real cost:** Moving homes after 3 months = £500 admin fees + emotional trauma
- **How to avoid:** Use our telephone checklist (below) to ask the right questions, or upgrade to Professional Assessment for expert verification.

**Footer:**
"**Want us to check all of this FOR you?**

Our £119 Professional Assessment includes safety checks + hidden cost analysis + medical capability verification

[Upgrade to Professional Assessment — £119]"

---

## 8. TRUST & SOCIAL PROOF

**Разделитель:** "Trust & Social Proof"

**Компонент:** `components/report/Testimonials.tsx`

**Заголовок:**
"What Birmingham Families Say About Professional Assessment"

**3 отзыва:**

1. **Margaret Thompson, Solihull (14th September 2025)**
   "The Professional assessment revealed hidden fees of £200 per week that we hadn't noticed. Annual savings: £10,400. Worth every penny of the £119 fee."

2. **James Patterson, Edgbaston (8th September 2025)**
   "Started with the free list, but the Professional assessment found us a home that perfectly matched Dad's dementia needs. The free list missed this crucial factor entirely."

3. **Sarah Mitchell, Harborne (22nd August 2025)**
   "The free shortlist showed us 3 nearby homes, but the Professional assessment identified safety concerns at 2 of them that weren't obvious from CQC ratings alone."

---

## 9. LEARN MORE

**Разделитель:** "Learn More"

**Компонент:** `components/report/AboutShortlist.tsx`

**Заголовок:**
"About Your Strategic Shortlist"

**Текст:**
"This free shortlist uses **3 professional selection strategies** — Safe Bet, Best Reputation, and Smart Value — to give you meaningful choices based on different priorities, not just proximity to your postcode.

For assessment based on your loved one's specific medical conditions, detailed safety verification, financial stability checks, and long-term planning, our **Professional Assessment (£119)** provides comprehensive analysis with 5 carefully matched homes and 40+ evaluation criteria.

**Note:** Always verify current information directly with care homes, including bed availability, specialist care capabilities, and detailed fee structures."

---

## 10. UPGRADE OPTIONS

**Разделитель:** "Upgrade Options"

### 10.1 Value Bridge

**Компонент:** `components/report/ValueBridge.tsx`

**Статистика:**
"**73%** of families upgrade"

**Заголовок:**
"Why Families Choose Professional Assessment"

**Подзаголовок:**
"Your free shortlist helps you **start exploring**. Professional Assessment helps you **make the decision** with confidence."

**Сравнение Free vs Professional:**

**FREE Shortlist карточка:**
- Заголовок: "Your FREE Shortlist"
- Подзаголовок: "Great starting point"
- Список:
  - • **3 strategic options** based on Safety, Reputation, Value
  - • **Basic CQC ratings** ("Good", "Outstanding")
  - • **Weekly pricing** and distance information
  - • **Educational content** (3 mistakes, enquiry checklist)
- Футер: "Helps you start exploring"

**Professional Assessment карточка:**
- Бейдж: "RECOMMENDED"
- Заголовок: "Professional Assessment"
- Подзаголовок: "Make the decision with confidence"
- Цена: "£119"
- Список:
  - ✓ **Concrete safety scores:** 91/100 vs 78/100 (not just "Good")
  - ✓ **Medical capability verified:** Can they handle YOUR conditions?
  - ✓ **Financial stability checked:** Will they be here in 5 years?
  - ✓ **Success prediction:** 84% placement success for your profile
  - ✓ **5-year cost calculator:** Hidden fees revealed (save £39,000+)
  - ✓ **5 homes analyzed:** More choice, better decision
- Футер: "Helps you decide in 2 days, not 3 weeks"
- CTA: "Upgrade to Professional Assessment — £119"

**История Thompson Family:**

**Заголовок:**
"Why the Thompson Family Upgraded"

**Статистика:**
"**73%** upgrade within 7 days"

**Challenge:**
"We had 3 good options from the free report. But all showed 'Good' CQC ratings. **We spent 3 weeks trying to figure out if Manor House (£1,200/week) was worth £200 more than Oaklands (£1,000/week).**"

**Solution:**
"Professional Assessment showed Manor House had **91/100 safety score** vs Oaklands' 78/100, plus verified diabetes care staff. **Decision made in 2 days** instead of 3 weeks."

**ROI метрики:**
- Investment: £119
- Time Saved: 3 weeks
- Value: 42x ROI

---

### 10.2 CTA

**Компонент:** `components/report/CTA.tsx`

**Заголовок:**
"Ready for Expert Analysis?"

**Текст:**
"Your free shortlist helped you understand the options.
Professional Assessment gives you the confidence to actually decide."

**CTA кнопка:**
"Upgrade to Professional Assessment — £119"

**Примечание:**
"Delivered in 48 hours • 5 homes analyzed • 40+ factors checked"

---

## 11. STICKY CTA

**Компонент:** `components/report/StickyCTA.tsx`

**Поведение:** Фиксированная кнопка внизу экрана при скролле

**Контент:** CTA для апгрейда на Professional Assessment

---

## 12. FOOTER

**Компонент:** `components/Footer.tsx`

Стандартный footer сайта

---

## ДОПОЛНИТЕЛЬНЫЕ ЭЛЕМЕНТЫ

### Section Dividers

Разделители между секциями с текстом:
- "Your Strategic Options"
- "Action Plan"
- "Compare & Calculate"
- "Important Warnings"
- "Trust & Social Proof"
- "Learn More"
- "Upgrade Options"

### Navigation Sections

ID секций для навигации:
- `section-overview`
- `section-homes`
- `section-next-steps`
- `section-compare`
- `section-warnings`
- `section-trust`
- `section-learn-more`
- `section-upgrade`

---

## ТИПЫ ДАННЫХ

**FreeReportData:**
```typescript
{
  reportId: string;
  postcode: string;
  city: string;
  careHomes: CareHome[];
  generatedAt: string;
}
```

**CareHome:**
```typescript
{
  id: string;
  name: string;
  location: string;
  postcode: string;
  strategy: 'safe_bet' | 'best_reputation' | 'smart_value';
  strategyLabel: string;
  cqcRating: string;
  distance: string;
  weeklyPrice: number;
  whyChosen: string;
  keyStrengths: string[];
  contact: {
    phone: string;
    email: string;
  };
  detailedProfile?: {
    specializations: Array<{title: string, description: string}>;
    keyFeatures: string[];
    performance: {
      staffRetention: string;
      familySatisfaction: string;
      incidentRate: string;
    };
    considerations: string[];
  };
}
```

---

## СТИЛИ И CSS

**Основные CSS файлы:**
- `basic-report.css`
- `free-report.css`

**Ключевые классы:**
- `report-header-free`
- `ranking-card`
- `top-recommendation`
- `care-home-strategy`
- `comparison-table`
- `cost-calculator`
- `value-bridge-section`
- `section-divider`

---

## ПРИМЕЧАНИЯ

1. Отчет использует mock данные, если API не доступен
2. Навигация становится sticky при скролле
3. Cost Calculator использует Chart.js для визуализации
4. Telephone Checklist раскрывается по клику
5. Detailed Profile раскрывается по клику для каждого care home
6. Все ссылки ведут на `/professional-assessment/` для апгрейда

