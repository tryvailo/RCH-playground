<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# для расчета staff quality берем информацию из

-CQC API - Care Quality Commission (ПРИОРИТЕТ)

- Indeed UK
-Google Reviews (+ LLM обработчик)

напиши алгоритм расчета (без кода) общего итогового рейтинга

Отлично. Теперь у меня есть реальные данные по текучке, CQC методологии и sentiment analysis. Напишу подробный алгоритм расчета Staff Quality Score.

***

# Алгоритм расчета Staff Quality Score (итоговый рейтинг)

## Принцип: взвешенная комбинация трех независимых источников

Staff Quality Score = **0-100** (где 0 = низшее качество, 100 = лучшее качество)

Это **не попытка угадать реальную текучку**, а **честная метрика**, которая объединяет:

1. **Официальную оценку** (CQC)
2. **Голос сотрудников** (Indeed + Google отзывы)
3. **Контекстуальную калибровку** (региональные бенчмарки)

***

## Этап 1: Сбор базовых данных (RAW DATA)

### 1.1 CQC API данные

**Источник:** CQC Inspection Reports + API
**Собираем для каждого дома:**


| Параметр | Как найти | Формат |
| :-- | :-- | :-- |
| **CQC "Well-Led" рейтинг** | Inspection report → "Well-Led" domain | Outstanding / Good / Requires Improvement / Inadequate |
| **CQC "Effective" рейтинг** | Inspection report → "Effective" domain | Outstanding / Good / Requires Improvement / Inadequate |
| **Staff quality mentions** | Текстовый поиск в отчёте по ключевым словам | Positive / Neutral / Negative |
| **Дата последней инспекции** | Inspection date field | YYYY-MM-DD |

**Ключевые слова для поиска в CQC отчётах** (контрольные проверки):

- Положительно: "staff trained", "low turnover", "good morale", "supportive management", "staff development"
- Отрицательно: "staff shortage", "high turnover", "staff morale concern", "insufficient training", "staff vacancy"
- Нейтрально: "staff", "staffing levels"

**Пример парсинга CQC отчёта:**

```
Inspection report text:
"The home maintains good staffing levels with a nurse-to-resident ratio of 1:7. 
Staff are well-trained and morale is high. However, there is some concern about 
recent turnover among care assistants..."

→ Extract:
  - Well-Led rating: Good
  - Effective rating: Good
  - Positive mentions: 2 ("good staffing", "well-trained", "morale is high")
  - Negative mentions: 1 ("concern about recent turnover")
  - Net sentiment: Slightly positive
```


### 1.2 Indeed UK данные

**Источник:** Indeed.co.uk reviews (через scraping или API)
**Собираем для каждого дома:**


| Параметр | Как найти | Формат |
| :-- | :-- | :-- |
| **Количество найденных отзывов** | Search care home name on Indeed | Integer (0-50+) |
| **Рейтинг из Indeed** | Home profile rating | Float (1.0 - 5.0) |
| **Возраст отзывов** | Review date | Months ago |

**Данные по каждому отзыву:**

```
Review 1: "Great management, flexible shifts, but understaffed during peak hours"
Review 2: "Pay is too low for the work. High turnover of staff."
Review 3: "Supportive team, good training provided."
...
```


### 1.3 Google Reviews данные

**Источник:** Google Business Profile (Google Maps)
**Собираем для каждого дома:**


| Параметр | Как найти | Формат |
| :-- | :-- | :-- |
| **Количество найденных отзывов** | Google Maps search | Integer (0-100+) |
| **Средний рейтинг** | Home profile rating | Float (1.0 - 5.0) |
| **Отзывы (полный текст)** | Individual reviews | Text |

**Фильтрация:** Берём ТОЛЬКО отзывы, где:

- Явно упоминается **персонал** ("staff", "carer", "nurse", "worker", "management")
- ИЛИ явно обсуждаются **условия работы** ("work", "job", "shift", "training", "pay")

Это избегает шума от отзывов чистых семей, которые пишут только о себе.

***

## Этап 2: Нормализация CQC рейтингов в шкалу 0-100

### 2.1 Конвертация "Well-Led" рейтинга

"Well-Led" = лидерство, управление персоналом, их стабильность и развитие


| CQC Rating | Points | Обоснование |
| :-- | :-- | :-- |
| **Outstanding** | 95 | Лучший возможный уровень управления |
| **Good** | 75 | Хорошее управление, но нет совершенства |
| **Requires Improvement** | 40 | Серьёзные проблемы с управлением |
| **Inadequate** | 10 | Критические проблемы |

**Логика:** "Well-Led" напрямую связан с quality of staff management, their morale, training investment.

### 2.2 Конвертация "Effective" рейтинга

"Effective" = качество ухода, его результаты (косвенный индикатор staff competence и morale)


| CQC Rating | Points | Обоснование |
| :-- | :-- | :-- |
| **Outstanding** | 90 | Высочайшее качество care = хорошо обученный персонал с высоким моралом |
| **Good** | 70 | Хорошее качество, но не идеально |
| **Requires Improvement** | 35 | Проблемы с качеством указывают на проблемы с персоналом |
| **Inadequate** | 5 | Критические проблемы с delivery of care |

**Логика:** Если персонал плохой, Effective рейтинг будет низким.

### 2.3 Извлечение "Staff Sentiment" из текста CQC отчёта

**Алгоритм:**

```
Шаг 1: Найти все упоминания слов о персонале в отчёте
Шаг 2: Для каждого предложения с упоминанием персонала → применить LLM/VADER sentiment
Шаг 3: Подсчитать долю positive/neutral/negative предложений

Пример:
- Positive mentions: 6 (60%)
- Neutral mentions: 2 (20%)
- Negative mentions: 2 (20%)

→ CQC Staff Sentiment Score = (60% × 1) + (20% × 0) + (20% × -1) = 0.4

→ Конвертировать в 0-100 шкалу:
   Score = 50 + (0.4 × 50) = 70 points
```

**Результат:** CQC_Staff_Sentiment = 0-100 points

***

## Этап 3: Sentiment анализ Indeed + Google Reviews (LLM обработка)

### 3.1 Собрать все найденные отзывы в один корзину

```
Все отзывы (Indeed + Google) по дому:
[
  "Great management, flexible shifts, but understaffed during peak hours",
  "Pay is too low for the work. High turnover of staff.",
  "Supportive team, good training provided.",
  "Management doesn't care about staff wellbeing",
  "Been here 5 years, love my job",
  ...
]

Count_total = количество найденных отзывов
```


### 3.2 Применить sentiment анализ к каждому отзыву

**Инструмент:** OpenAI API (ChatGPT) или VADER + TextBlob для быстрого прототипа

**Запрос для каждого отзыва:**

```
"Analyze sentiment of this care worker review. 
Rate as POSITIVE (about working conditions, management, pay, culture) / 
MIXED (both positive and negative) / 
NEGATIVE (complaints about work) / 
NEUTRAL (general description without opinion):

Review: [review text]

Output: [POSITIVE|MIXED|NEGATIVE|NEUTRAL], confidence 0-100%"
```

**Результат для каждого отзыва:**

```
Sentiment: POSITIVE / MIXED / NEGATIVE / NEUTRAL
Confidence: 0-100%
Topics mentioned: [staffing, pay, management, training, culture, hours, ...list]
```


### 3.3 Агрегировать результаты в один Employee Sentiment Score

**Формула:**

```
Positive_count = количество POSITIVE отзывов
Mixed_count = количество MIXED отзывов  
Negative_count = количество NEGATIVE отзывов
Neutral_count = количество NEUTRAL отзывов
Total = Positive + Mixed + Negative + Neutral

IF Total < 3:
    # Недостаточно данных
    Employee_Sentiment_Score = NULL (не используем в расчёт)
    Data_Quality_Flag = "INSUFFICIENT_DATA"
ELSE:
    # Взвешиваем мнения
    Employee_Sentiment_Score = 
        (Positive_count × 100 + Mixed_count × 50 + Negative_count × 0) / Total
    
    Data_Quality_Flag = "OK" if Total >= 5, "LIMITED" if Total < 5
```

**Пример:**

```
Found reviews: 7
- Positive: 4 (57%)
- Mixed: 2 (29%)
- Negative: 1 (14%)

Employee_Sentiment_Score = (4×100 + 2×50 + 1×0) / 7 = 500 / 7 = 71.4 points
```


### 3.4 Регионализация (калибровка относительно норм)

**Проверка:** Есть ли смещение в отзывах?

```
Из Indeed/Google data извлекаем упоминания:
- Pay: 3 отзыва
- Management: 4 отзыва
- Work-life balance: 2 отзыва  
- Understaffing: 3 отзыва
- Training: 1 отзыв

Compare с региональными нормами (Skills for Care):
Если отзывы часто жалуются на "pay" → проверить местные зарплаты (может быть norm для региона)
Если отзывы часто жалуются на "understaffing" → это красный флаг, не норма
```

**Метод корректировки:**

Если Employee_Sentiment_Score значительно ниже среднего по UK, но соответствует локальным условиям → это нормально (не штраф).

Если Employee_Sentiment_Score значительно ниже и локальных норм → это проблема (штраф).

***

## Этап 4: Расчет итогового Staff Quality Score (финальная формула)

### 4.1 Определить вес каждого компонента

```
Component 1: CQC Well-Led Rating → Weight 40%
Component 2: CQC Effective Rating → Weight 20%
Component 3: CQC Staff Sentiment (из текста отчёта) → Weight 10%
Component 4: Employee Reviews Sentiment (Indeed + Google) → Weight 30%

Rationale:
- CQC Well-Led имеет наибольший вес (40%), потому что это официальная оценка 
  управления и организационной культуры
- CQC Effective имеет 20%, потому что это косвенный индикатор качества персонала
- CQC Staff Sentiment имеет 10%, потому что это вторичная информация из отчёта
- Employee Reviews имеет 30%, потому что это голос сотрудников, но данные ограничены 
  (может быть bias и малый sample size)
```


### 4.2 Применить логику обработки отсутствующих данных

```
IF Employee_Sentiment_Score == NULL (недостаточно отзывов):
    # Перераспределить вес
    Components:
    - CQC Well-Led: 45% (было 40%)
    - CQC Effective: 25% (было 20%)
    - CQC Staff Sentiment: 30% (было 10%)
    - Employee Reviews: 0%
    
    Note in report: "This score based on CQC data only. 
    Only [N] employee reviews found on Indeed/Google. 
    For complete assessment, ask staff directly during visit."
ELSE:
    # Используем полный набор весов
    Staff_Quality_Score = 
        (CQC_WellLed × 0.40) + 
        (CQC_Effective × 0.20) + 
        (CQC_Staff_Sentiment × 0.10) + 
        (Employee_Sentiment_Score × 0.30)
```


### 4.3 Финальная формула

```
Staff_Quality_Score = WEIGHTED_AVERAGE (0-100)

WHERE:

Component 1: CQC_WellLed_Score (0-100)
  Source: CQC inspection report "Well-Led" rating
  Conversion:
    Outstanding = 95
    Good = 75
    Requires Improvement = 40
    Inadequate = 10
  Weight: 40%

Component 2: CQC_Effective_Score (0-100)
  Source: CQC inspection report "Effective" rating
  Conversion:
    Outstanding = 90
    Good = 70
    Requires Improvement = 35
    Inadequate = 5
  Weight: 20%

Component 3: CQC_Staff_Sentiment_Score (0-100)
  Source: LLM sentiment analysis of staff mentions in CQC report
  Calculation:
    Positive_sentences = count of sentences with positive staff sentiment
    Negative_sentences = count of sentences with negative staff sentiment
    Score = (Positive - Negative) / Total_staff_sentences × 50 + 50
  Weight: 10% (or 30% if no employee reviews)

Component 4: Employee_Reviews_Sentiment_Score (0-100)
  Source: Indeed UK + Google Reviews
  Requires: Minimum 3 reviews mentioning work/staff experience
  Calculation:
    Positive_reviews = count of POSITIVE sentiment reviews
    Mixed_reviews = count of MIXED sentiment reviews
    Score = (Positive × 100 + Mixed × 50) / Total_reviews
  Weight: 30% (or 0% if insufficient data)

FINAL FORMULA:
  IF Employee_Reviews_Sentiment_Score exists:
    Staff_Quality_Score = 
      (CQC_WellLed × 0.40) + 
      (CQC_Effective × 0.20) + 
      (CQC_Staff_Sentiment × 0.10) + 
      (Employee_Sentiment × 0.30)
  ELSE:
    Staff_Quality_Score = 
      (CQC_WellLed × 0.45) + 
      (CQC_Effective × 0.25) + 
      (CQC_Staff_Sentiment × 0.30)

Result: Score 0-100
```


***

## Этап 5: Мягкая коррекция (Calibration adjustments)

### 5.1 Проверка временных anomalies

```
IF CQC inspection > 18 months ago:
    # Данные устаревают, apply slight discount
    Staff_Quality_Score = Staff_Quality_Score × 0.95
    Add note: "CQC data from [months] ago. May have changed."

IF CQC inspection < 3 months ago:
    # Недавняя инспекция = более надежные данные, небольшой бонус
    Staff_Quality_Score = Staff_Quality_Score × 1.02
```


### 5.2 Проверка на противоречия (contradiction detection)

```
IF CQC_WellLed = Outstanding BUT Employee_Sentiment_Score < 40:
    # Возможный data quality issue
    Flag: "CONTRADICTION - CQC rates management highly but employee reviews negative. 
    Verify source of reviews and recency."
    
    Action: Review employee comments more carefully. Check if negative reviews are old/outdated.
    If recent and credible → slightly reduce score.

IF CQC_WellLed = Requires Improvement BUT Employee_Sentiment_Score > 70:
    # Также possible contradiction
    Flag: "INCONSISTENCY - CQC identifies management issues but employees satisfied."
    
    Action: May indicate recent improvements. Consider slightly upward adjustment.
```


### 5.3 Confidence level

```
Confidence_Level = function(data_freshness, review_count, CQC_rating_agreement)

High Confidence (80-100%):
  - CQC inspection < 6 months ago
  - AND >= 5 relevant employee reviews found
  - AND no significant contradictions

Medium Confidence (60-80%):
  - CQC inspection < 12 months ago
  - AND 3-4 employee reviews found
  - OR contradictions explained

Low Confidence (<60%):
  - CQC inspection > 18 months ago
  - OR < 3 employee reviews
  - AND significant unexplained contradictions
```


***

## Этап 6: Конвертация Score в читаемую форму

### 6.1 Бинновать в категории

```
Staff Quality Score → Category

90-100: EXCELLENT
  Label: "🟢 EXCELLENT"
  Text: "This home has outstanding staff management and high employee satisfaction."

75-89: GOOD
  Label: "🟢 GOOD"
  Text: "This home has good staff quality with positive employee reviews."

60-74: ADEQUATE
  Label: "🟡 ADEQUATE"
  Text: "This home meets baseline staffing standards, with some areas for improvement."

40-59: CONCERNING
  Label: "🟡 CONCERNING"
  Text: "This home has staffing concerns. Clarify during your visit."

0-39: POOR
  Label: "🔴 POOR"
  Text: "This home has significant staffing issues. Consider carefully before admission."
```


### 6.2 Краткое объяснение

```
Staff Quality Summary (for report):

Score: 73/100 - GOOD

Based on:
✓ CQC "Well-Led" rating: Good (75 points)
✓ CQC "Effective" rating: Good (70 points)
✓ Staff sentiment from CQC report: Positive (72 points)
✓ Employee reviews (5 found on Indeed): Mixed-positive (68 points)

Data Quality: MEDIUM CONFIDENCE
  - CQC data from 4 months ago ✓
  - Limited employee reviews (5 total) - ask staff during visit
  
Key Themes from Reviews:
  Positively mentioned: Management supportive, good training
  Concerns raised: "Understaffed during shifts", "Low pay"
  
Note: This score reflects available public data. 
During your visit, ask about staff retention rate and recent turnover.
```


***

## Этап 7: Red flags (автоматические предупреждения)

Система автоматически генерирует флаги:

```
🚩 RED FLAG: CQC rated "Requires Improvement" for Well-Led
   → Significant management/leadership concerns identified in inspection

🚩 RED FLAG: All employee reviews mention "understaffing" or "high workload"  
   → Clear pattern of staffing problems

⚠️ YELLOW FLAG: CQC inspection > 18 months ago
   → Data may be outdated. Verify current situation.

⚠️ YELLOW FLAG: High staff sentiment in CQC (positive) but negative employee reviews (recent)
   → Possible recent deterioration. Ask directly about what changed.
```


***

## Финальная структура в отчете (Staff Quality Score секция)

```
┌─────────────────────────────────────────────────────────┐
│ SECTION 3: STAFF QUALITY & RATIOS                       │
│                                                           │
│ Overall Staff Quality Score: 73/100  [GOOD]  🟢         │
│ Data confidence: MEDIUM                                   │
│                                                           │
│ COMPONENT BREAKDOWN:                                      │
│ ├─ CQC Well-Led rating:            Good (75)  ✓         │
│ ├─ CQC Effective rating:           Good (70)  ✓         │
│ ├─ Staff sentiment (CQC report):   Mixed+ (72) ~        │
│ └─ Employee reviews sentiment:     Mixed (68) ~ [5 reviews] │
│                                                           │
│ REVIEW ANALYSIS:                                          │
│ Found: 5 reviews on Indeed UK                            │
│ ├─ Positive tone: 2 (40%)  ✓                             │
│ ├─ Mixed tone:    2 (40%)  ~                             │
│ └─ Negative tone: 1 (20%)  ✗                             │
│                                                           │
│ KEY THEMES:                                               │
│ ✓ Management supportive & approachable (3 mentions)      │
│ ✓ Good training program (2 mentions)                     │
│ ✗ "Understaffed during peak shifts" (3 mentions)        │
│ ✗ "Pay is below local average" (2 mentions)             │
│                                                           │
│ 📌 IMPORTANT:                                             │
│ This score based on limited public data (5 reviews).     │
│ During visit, ask about:                                 │
│ - What's your staff turnover rate?                       │
│ - How many shifts lack full coverage?                    │
│ - What's the average tenure of your care staff?          │
└─────────────────────────────────────────────────────────┘
```


***

## Преимущества этого алгоритма

✅ **Прозрачность:** Клиент видит, откуда пришла каждая цифра
✅ **Честность:** Явно показываем ограничения данных
✅ **Надёжность:** Используем официальные + реальные источники
✅ **Масштабируемость:** Может работать автоматически для 1000+ домов
✅ **Аудиты:** Легко проверить, как был рассчитан скор
✅ **Регулярное обновление:** CQC + Indeed данные обновляются → Score обновляется автоматически
<span style="display:none">[^1][^10][^2][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://www.gov.uk/government/publications/review-into-the-operational-effectiveness-of-the-care-quality-commission-full-report/analysis-of-care-quality-commission-data-on-inspections-assessments-and-ratings-2014-to-2024

[^2]: https://www.skillsforcare.org.uk/Adult-Social-Care-Workforce-Data/workforceintelligence/resources/Reports/Regional/Regional-summaries-2024-London.pdf

[^3]: https://www.datacamp.com/tutorial/text-analytics-beginners-nltk

[^4]: https://www.gov.uk/government/publications/review-into-the-operational-effectiveness-of-the-care-quality-commission-full-report/review-into-the-operational-effectiveness-of-the-care-quality-commission-full-report

[^5]: https://www.kingsfund.org.uk/insight-and-analysis/data-and-charts/social-care-workforce-nutshell

[^6]: https://realpython.com/python-nltk-sentiment-analysis/

[^7]: https://www.kingsfund.org.uk/insight-and-analysis/reports/impact-cqc-provider-performance

[^8]: https://www.gov.uk/government/statistics/adult-social-care-workforce-survey-april-2025/adult-social-care-workforce-survey-april-2025-report

[^9]: https://www.youtube.com/watch?v=s33KHjHIxWk

[^10]: https://www.cqc.org.uk/guidance-regulation/providers/assessment/assessing-quality-and-performance/reach-rating

