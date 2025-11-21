# Professional Report Viewer Feature

Генератор профессиональных отчетов для RightCareHome на основе детального questionnaire (17 вопросов, 5 секций).

## Структура

```
src/features/professional-report/
├── ProfessionalReportViewer.tsx    # Главный компонент
├── types.ts                         # TypeScript типы
├── hooks/
│   └── useProfessionalReport.ts    # TanStack Query хук для API
├── components/
│   └── QuestionLoader.tsx          # Компонент загрузки questionnaire
└── README.md
```

## Основные компоненты

### ProfessionalReportViewer
Главный компонент с хедером и сайдбаром:
- Загрузка professional questionnaire (6 sample файлов или drag & drop)
- Генерация отчета через API
- Отображение результатов
- Анимация загрузки (симуляция 24-48h обработки)

### QuestionLoader
Компонент для загрузки professional questionnaire:
- Выбор из 6 sample файлов (`public/sample_questionnaires/professional_questionnaire_*.json`)
- Drag & drop для загрузки своего JSON
- Валидация всех 5 секций
- Отображение описания профиля

### useProfessionalReport
TanStack Query хук для:
- Генерации отчета (`useGenerateProfessionalReport`)
- Проверки статуса генерации (`useCheckProfessionalReportStatus`)

## Структура Professional Questionnaire

### Section 1: Contact & Emergency Information
- Q1: Names of contact person and patient
- Q2: Email address
- Q3: Contact phone number
- Q4: Emergency contact (HIGH PRIORITY)

### Section 2: Location & Budget
- Q5: Preferred city or region
- Q6: Maximum distance (5km/15km/30km/distance_not_important)
- Q7: Planned monthly budget and funding source

### Section 3: Medical Needs
- Q8: What types of care are needed? (checkbox)
- Q9: Main medical conditions (checkbox, exclusive option)
- Q10: Level of mobility
- Q11: Medication management needs (HIGH PRIORITY)
- Q12: Patient age range

### Section 4: Safety & Special Needs
- Q13: Fall history in past year (CRITICAL)
- Q14: Major allergies (HIGH PRIORITY, exclusive option)
- Q15: Special dietary requirements (exclusive option)
- Q16: Social personality type

### Section 5: Timeline
- Q17: When is placement needed?

## Sample Questionnaires

6 тестовых профилей доступны в `public/sample_questionnaires/`:

1. **professional_questionnaire_1_dementia.json**
   - Пожилой человек с деменцией
   - Специализированный dementia care
   - Бюджет: £5-7K (LA funding)

2. **professional_questionnaire_2_diabetes_mobility.json**
   - Диабет + проблемы мобильности
   - Медицинский уход (nursing)
   - Высокий риск падений

3. **professional_questionnaire_3_cardiac_nursing.json**
   - Сердечные заболевания
   - Премиум бюджет (£7K+)
   - Планирование на 2-3 месяца

4. **professional_questionnaire_4_healthy_residential.json**
   - Относительно здоровый человек
   - Минимальные потребности
   - Низкий бюджет (<£3K)

5. **professional_questionnaire_5_high_fall_risk.json**
   - Высокий риск падений (CRITICAL)
   - Специальная диета
   - Срочно

6. **professional_questionnaire_6_complex_multiple.json**
   - Множественные медицинские условия
   - Самый сложный профиль
   - 95+ лет

## API

### POST /api/professional-report

**Request:**
```json
{
  "section_1_contact_emergency": {
    "q1_names": "Contact: John Doe; Patient: Jane Smith",
    "q2_email": "example@email.com",
    "q3_phone": "+44 7123 456789",
    "q4_emergency_contact": "Emergency Contact +44 7987 654321"
  },
  "section_2_location_budget": {
    "q5_preferred_city": "Birmingham",
    "q6_max_distance": "15km",
    "q7_budget": "5000_7000_local"
  },
  "section_3_medical_needs": {
    "q8_care_types": ["specialised_dementia"],
    "q9_medical_conditions": ["dementia_alzheimers"],
    "q10_mobility_level": "walking_aids",
    "q11_medication_management": "several_simple_routine",
    "q12_age_range": "85_94"
  },
  "section_4_safety_special_needs": {
    "q13_fall_history": "1_2_no_serious_injuries",
    "q14_allergies": ["no_allergies"],
    "q15_dietary_requirements": ["no_special_requirements"],
    "q16_social_personality": "moderately_sociable"
  },
  "section_5_timeline": {
    "q17_placement_timeline": "next_month"
  }
}
```

**Response:**
```json
{
  "questionnaire": { ... },
  "report": {
    "reportId": "uuid",
    "clientName": "Jane Smith",
    "careHomes": [ ... ],
    "analysisSummary": {
      "totalHomesAnalyzed": 50,
      "factorsAnalyzed": 156,
      "analysisTime": "24-48 hours"
    }
  },
  "generated_at": "2025-01-XX",
  "report_id": "uuid",
  "job_id": "uuid",
  "status": "completed"
}
```

## Особенности

### Отличия от Free Report

| Аспект | Free Report | Professional Report |
|--------|-------------|---------------------|
| Вопросов | 4-6 | 17 |
| Секций | 1 | 5 |
| Домов анализируется | 3 | 5 |
| Источников данных | 4 | 15+ |
| Matching points | 50 | 156 |
| Confidence level | 70% | 93-95% |
| Время генерации | Instant | 24-48h |
| Страниц PDF | 6-8 | 30-35 |
| Цена | Free | £119 |

### Валидация

Все 5 секций обязательны:
- Section 1: Contact & Emergency (Q1-Q4)
- Section 2: Location & Budget (Q5-Q7)
- Section 3: Medical Needs (Q8-Q12)
- Section 4: Safety & Special Needs (Q13-Q16)
- Section 5: Timeline (Q17)

### Исключающие опции

- Q9: Если выбрано `no_serious_medical`, другие условия не должны быть выбраны
- Q14: Если выбрано `no_allergies`, другие аллергии не должны быть выбраны
- Q15: Если выбрано `no_special_requirements`, другие требования не должны быть выбраны

## Использование

### В приложении

Перейдите на `/professional-report` для доступа к интерфейсу.

### Программно

```typescript
import ProfessionalReportViewer from './features/professional-report/ProfessionalReportViewer';

// В роутере
<Route path="/professional-report" element={<ProfessionalReportViewer />} />
```

## TODO

- [ ] Реализовать полный ReportRenderer для Professional Report
- [ ] Добавить компоненты для всех 20 секций отчета
- [ ] Интегрировать PDF генерацию
- [ ] Добавить статус трекинг для async jobs
- [ ] Реализовать email delivery

---

**Конец документа**

