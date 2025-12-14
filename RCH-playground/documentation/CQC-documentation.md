# Полное руководство по CQC API для работы с базой домов престарелых Великобритании

CQC API мигрировал на новую платформу Azure API Management в 2023-2024 году, требуя теперь обязательной аутентификации через subscription key вместо опционального partnerCode. **Базовый URL изменился на `https://api.service.cqc.org.uk`**, а доступ предоставляется через developer portal с лимитом 2000 запросов в минуту. API обновляется ежедневно и предоставляет полный доступ к данным о всех зарегистрированных провайдерах медицинских и социальных услуг в Англии, включая около 192 домов престарелых в Бирмингеме.

Эта миграция представляет критическое изменение для всех интеграций: старый URL `api.cqc.org.uk` постепенно выводится из эксплуатации, и все приложения должны быть обновлены для работы с новой системой аутентификации. API сохраняет RESTful архитектуру и структуру endpoint'ов, возвращая JSON-документы с богатой информацией о рейтингах, инспекциях, regulated activities и детальных характеристиках каждого учреждения. Для Birmingham доступны специфические параметры поиска через local authority code "Birmingham" или GSS code "E08000025" в регионе West Midlands.

## Миграция на новую платформу и система аутентификации

CQC завершила миграцию API на платформу Azure API Management между 2023-2024 годами, существенно изменив модель доступа к данным. Старая система с опциональным `partnerCode` параметром заменена обязательной subscription-based аутентификацией, что требует предварительной регистрации в developer portal. Новый базовый URL **`https://api.service.cqc.org.uk`** заменяет устаревший `https://api.cqc.org.uk/public/v1`, хотя структура endpoint'ов остается неизменной для обеспечения обратной совместимости.

Для получения доступа к API необходимо зарегистрироваться на **https://api-portal.service.cqc.org.uk/signup**, создать учетную запись, и получить subscription key из профиля пользователя. Система предоставляет два ключа - Primary и Secondary - для обеспечения rotation без простоя сервиса. Аутентификация осуществляется через HTTP header **`Ocp-Apim-Subscription-Key`**, который должен включаться во все запросы. Альтернативный метод через query parameter `subscription-key` технически возможен, но header-метод является стандартным и рекомендуемым.

Технические требования ужесточились: теперь поддерживается только TLS 1.2 и выше, версии TLS 1.0 и 1.1 больше не работают. Rate limit остается на уровне 2000 запросов в минуту для authenticated клиентов, хотя точные лимиты для новой платформы могут варьироваться в зависимости от subscription tier. API продолжает обновлять данные ежедневно, синхронизируясь с информацией на официальном сайте CQC, и все данные доступны под Open Government Licence 3.0.

Критические breaking changes включают обязательность аутентификации (ранее опциональную), смену base URL, и необходимость получения subscription key через portal. При этом сохраняются все endpoint paths (`/public/v1/providers`, `/public/v1/locations`), структура ответов, query параметры и опции фильтрации. Для миграции существующих интеграций необходимо обновить base URL, добавить Ocp-Apim-Subscription-Key header, удалить partnerCode (если использовался), и протестировать соединение с TLS 1.2+.

## Структура данных и доступные поля в CQC API

API предоставляет комплексную информацию о каждой локации через REST endpoint `/public/v1/locations/{locationId}`, возвращая JSON-документы с более чем 50 полями различных типов. Основная идентификационная информация включает **locationId** (уникальный идентификатор типа "1-545611283"), **providerId** (ID провайдера), **name** (название учреждения), **organisationType** ("Location"), и **type** (тип сервиса, например "Social Care" или "Primary Medical Services").

Регистрационные данные охватывают **registrationStatus** (обычно "Registered"), **registrationDate** (формат YYYY-MM-DD), **odsCode** (Organisation Data Service код), и **uprn** (Unique Property Reference Number). Географическая информация представлена детальным адресом (postalAddressLine1/2, postalAddressTownCity, postalAddressCounty, postalCode), регионом (например "West Midlands"), координатами (onspdLatitude, onspdLongitude), parliamentary constituency, и local authority name. CCG (Clinical Commissioning Group) данные включают четыре поля: onspdCcgCode/Name и odsCcgCode/Name для привязки к системе здравоохранения.

Для care homes критически важны специфические поля: **careHome** (флаг "Y" или "N"), **numberOfBeds** (целое число, указывающее вместимость), **inspectionDirectorate** (например "Adult social care"), lastInspection date, и lastReport publicationDate. Контактная информация включает mainPhoneNumber на уровне локации и website на уровне провайдера.

Система рейтингов CQC структурирована через объект **currentRatings** с тремя ключевыми компонентами. Первый - **overall** rating, содержащий общую оценку (возможные значения: "Outstanding", "Good", "Requires improvement", "Inadequate", "No published rating", "Not Rated"), дату отчета (reportDate), идентификатор отчета (reportLinkId как UUID), и опциональный organisationId, указывающий на унаследованный рейтинг от предшественника при смене владельца.

Второй компонент - **keyQuestionRatings** array, содержащий оценки по пяти ключевым вопросам инспекции. Каждый вопрос (Safe, Effective, Caring, Responsive, Well-led) имеет собственный рейтинг по той же шкале, дату отчета и reportLinkId. Эти пять вопросов оцениваются равновесно: Safe проверяет защиту от злоупотреблений и предотвратимого вреда, Effective оценивает достижение хороших результатов на основе доказательной медицины, Caring измеряет отношение персонала (compassion, kindness, dignity, respect), Responsive проверяет соответствие услуг потребностям людей, и Well-led оценивает качество руководства и governance.

Правила агрегации рейтингов строгие: для получения "Outstanding" overall требуется минимум 2 outstanding + 3 good по ключевым вопросам. Если 2+ вопроса оценены как "Requires improvement", общий рейтинг не может быть выше "Requires improvement". Если 2+ вопроса получили "Inadequate", общий рейтинг автоматически становится "Inadequate". Третий компонент - **serviceRatings** array, предоставляющий рейтинги по inspection areas (conditions, mothers, old, population, problems, vulnerable), каждый со своим rating, reportDate и reportLinkId.

Regulated activities представлены массивом объектов с **name** (например "Treatment of disease, disorder or injury", "Accommodation for persons who require nursing or personal care"), **code** (RA5, RA1, RA15 и др.), и **contacts** array, содержащий информацию о Registered Managers и Nominated Individuals с их титулами, именами и ролями. GacServiceTypes классифицируют услуги правительственным стандартам ("Doctors/Gps", "Care home service with nursing"), inspectionCategories определяют коды и primary флаги (P2, C1), locationTypes указывают тип учреждения (GP Practice, Care Home), и specialisms описывают специализации ("Dementia", "Learning disabilities", "Services for everyone").

Inspection history доступна через массив **reports**, где каждый объект содержит linkId (UUID), reportDate (дата публикации), reportUri (путь к отчету), опциональный firstVisitDate (дата визита инспекции), и reportType (Location или Provider). Отчеты можно получить как PDF (по умолчанию) или plain text, установив HTTP header `Accept: text/plain`. **historicRatings** array хранит предыдущие рейтинги с той же структурой, что и currentRatings, позволяя отслеживать изменения качества во времени. **inspectionAreas** определяет области оценки с inspectionAreaId, полным описанием inspectionAreaName, и status (Active, Superseded, Retired).

Relationships между локациями отслеживаются через массив, содержащий relatedLocationId, relatedLocationName, type (HSCA Predecessor/Successor), и reason (NHS Transfer, Change of ownership). С 1 апреля 2019 года новые локации наследуют рейтинги от предшественников при смене владельца, адреса или бизнес-структуры - это индицируется присутствием organisationId в объекте рейтинга. Provider-level поля включают brandId/brandName для NHS организаций, ownershipType (NHS Body, Private, Voluntary/Charity), и locationIds array со всеми локациями под управлением провайдера.

## Географический поиск и практические примеры для Birmingham

Поиск care homes по географическому признаку осуществляется через endpoint **`GET /public/v1/locations`** с множественными параметрами фильтрации. Ключевые geographic параметры включают **localAuthority** (название local authority, case-sensitive), **region** (регион типа "West Midlands"), **postcode** (почтовый индекс), и **constituency** (parliamentary constituency). Специфический для care homes параметр **careHome** принимает значения "Y" или "TRUE" для возврата только домов престарелых, "N" или "FALSE" для исключения их, или NULL для всех типов локаций.

Для Birmingham используется несколько идентификаторов: **Local Authority name "Birmingham"** (регистрозависимый), **GSS Code "E08000025"** (официальный ONS код), Reference Code "BIR", и Billing Authority Code "E4601". Birmingham расположен в регионе **West Midlands** (код E12000005) и классифицируется как Metropolitan District (MD). При формировании запросов необходимо использовать точное написание "Birmingham" с заглавной буквы, либо GSS код для гарантированной точности.

Дополнительные фильтры значительно расширяют возможности поиска: **inspection_directorate** может быть "Adult social care", "Hospitals", "Primary medical services" или "Unspecified"; **overall_rating** фильтрует по CQC рейтингу (Outstanding, Good, Requires improvement, Inadequate); **gac_service_type_description** уточняет тип сервиса; **regulated_activity** фильтрует по конкретным regulated activities; **primary_inspection_category_code/name** позволяет искать, например, "H1" или "Care homes with nursing". CCG параметры (onspd_ccg_code/name, ods_ccg_code/name) обеспечивают поиск по Clinical Commissioning Group.

Pagination реализуется через параметры **page** (номер страницы, начиная с 1) и **perPage** (результатов на страницу, рекомендуется 500, максимум 1000). Response возвращает метаданные: total (общее количество), totalPages, firstPageUri, lastPageUri, nextPageUri, previousPageUri для навигации, и массив locations с location_id, name, postcode, полным адресом, координатами, ratings, number_of_beds и service types. Sorting параметры не документированы явно - результаты возвращаются в порядке по умолчанию (по location ID), и для кастомной сортировки требуется client-side обработка.

Конкретные API запросы для Birmingham care homes строятся следующим образом. **Базовый поиск всех care homes в Birmingham:**

```
GET https://api.service.cqc.org.uk/public/v1/locations?careHome=Y&localAuthority=Birmingham
Headers: Ocp-Apim-Subscription-Key: {your-subscription-key}
```

**Поиск с pagination и региональным фильтром:**

```
GET https://api.service.cqc.org.uk/public/v1/locations?page=1&perPage=500&careHome=Y&region=West%20Midlands
Headers: Ocp-Apim-Subscription-Key: {your-subscription-key}
```

**Только care homes с рейтингом Good или Outstanding:**

```
GET https://api.service.cqc.org.uk/public/v1/locations?careHome=Y&localAuthority=Birmingham&overall_rating=Good
Headers: Ocp-Apim-Subscription-Key: {your-subscription-key}
```

**Фильтрация по Adult social care directorate:**

```
GET https://api.service.cqc.org.uk/public/v1/locations?careHome=Y&localAuthority=Birmingham&inspection_directorate=Adult%20social%20care
Headers: Ocp-Apim-Subscription-Key: {your-subscription-key}
```

**Получение детальной информации о конкретной локации:**

```
GET https://api.service.cqc.org.uk/public/v1/locations/1-545611283
Headers: Ocp-Apim-Subscription-Key: {your-subscription-key}
```

Birmingham насчитывает приблизительно **192 care homes** согласно Care Sourcer (другие источники указывают до 250), с более чем **352 учреждениями**, имеющими рейтинг Good или выше по данным Birmingham City Council. Рынок характеризуется **14% переизбытком мест** в residential care для людей 65+ лет и более низким уровнем поступлений в residential care по сравнению с региональным средним. Пропорционально Birmingham имеет меньше care home beds на 100,000 взрослых, чем в среднем по West Midlands.

Типичные типы care homes в Birmingham включают **Residential Care** (24-часовая поддержка с повседневными активностями - купание, одевание, медикаменты), **Nursing Homes** (24-часовой nursing care от Registered Nurses для сложных медицинских нужд), **Dementia Care** (специализированная помощь для Alzheimer's и деменции - 117 учреждений), и **Respite Care** (краткосрочные размещения для временного облегчения). Распространенные специализации: Specialist Dementia Care (117 facilities), Physical Disability Support (90), Palliative/End of Life Care (76), Younger Adults (75), Sensory Impairment (66), Learning Disabilities, Mental Health Conditions, и Complex Care Needs включая dual diagnosis.

Качественное распределение рейтингов в Birmingham показывает интересные тенденции: более **75% людей** с council-funded support поддерживаются провайдерами с рейтингом Good или Outstanding. Care homes в Birmingham имеют **более высокие CQC рейтинги**, чем comparators в West Midlands local authorities, хотя общий показатель зарегистрированных провайдеров ниже из-за более низких результатов homecare providers. Выдающиеся примеры включают **Victoria Lodge Care Home** (Acocks Green) с overall Outstanding рейтингом, и **Manor House** (Kingstanding) с Overall Outstanding, rated Outstanding для caring, responsive, well-led и Good для safe и effective.

Средняя стоимость в Birmingham составляет £1,137-£1,203 в неделю, в то время как West Midlands средние показатели - £597/неделю для residential care и £920/неделю для nursing homes. Birmingham-специфические challenges включают недостаток provision для complex care needs, ограниченные culturally appropriate care опции, недостаточные bed-based emergency/respite care для working-age adults, и пробелы в услугах для людей с learning disabilities/autism.

## Оптимальные практики и стратегии имплементации

Обработка ошибок требует понимания HTTP status codes и соответствующих стратегий реагирования. **401 Unauthorized** указывает на отсутствие или невалидные credentials - необходимо проверить subscription key и authentication headers. **403 Forbidden** означает, что сервер понимает запрос, но отказывает в авторизации из-за недостаточных permissions - следует проверить access permissions и API subscription level. **404 Not Found** сигнализирует, что провайдер/локация не существует по указанному ID - возможно, учреждение было дерегистрировано или архивировано, требуется верификация идентификатора.

**429 Too Many Requests** - критически важная ошибка rate limiting, требующая немедленной имплементации exponential backoff. CQC API лимитирует 2000 запросов в минуту для authenticated клиентов, и превышение этого лимита вызывает 429 response. Правильная стратегия включает проверку **Retry-After header** в response (если присутствует, ждать указанное количество секунд), и если header отсутствует - применять exponential backoff с jitter. **500 Internal Server Error** указывает на временные server-side проблемы, требующие retry logic с exponential backoff и контакта syndicationapi@cqc.org.uk при персистентных проблемах.

Rate limit management требует многоуровневого подхода. Во-первых, всегда включать subscription key во все запросы для получения полного лимита 2000 req/min. Во-вторых, имплементировать request throttling на application level, целясь в 1900 запросов/минуту для создания буфера. В-третьих, использовать sliding window rate limiting для сглаживания request patterns. В-четвертых, отслеживать request counts per minute внутри приложения. Exponential backoff алгоритм должен следовать формуле: `wait_time = (base_delay * 2^retry_count) + random_jitter` с начальной задержкой 1 секунда, максимум 3-5 attempts, backoff multiplier 2, максимальным backoff 32-64 секунды, и jitter ±500ms для предотвращения thundering herd эффекта.

Практическая имплементация retry logic в JavaScript:

```javascript
async function fetchWithRetry(url, maxRetries = 3) {
  let retries = 0;
  
  while (retries <= maxRetries) {
    try {
      const response = await fetch(url, {
        headers: {'Ocp-Apim-Subscription-Key': process.env.CQC_API_KEY}
      });
      
      if (response.ok) return await response.json();
      
      if (response.status === 429 || response.status >= 500) {
        const retryAfter = response.headers.get('Retry-After');
        const backoffTime = retryAfter 
          ? parseInt(retryAfter) * 1000
          : Math.min((Math.pow(2, retries) * 1000), 32000) + Math.random() * 1000;
        
        await new Promise(resolve => setTimeout(resolve, backoffTime));
        retries++;
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      if (retries === maxRetries) throw error;
      retries++;
    }
  }
}
```

Caching стратегии критичны для эффективной работы с CQC API. Данные обновляются **ежедневно** в синхронизации с CQC website, что делает 24-часовой TTL оптимальным для большинства use cases. Рекомендуемая архитектура - **Cache-Aside (Lazy Loading) pattern**: проверять cache первым, при cache miss запрашивать API, и сохранять результат в cache для последующих запросов. Provider/Location master data следует кэшировать на 24 часа, ratings data на 12-24 часа (так как inspections меняются нечасто), reports на 24-48 часов (статичны после публикации), и Changes endpoint polling каждые 1-6 часов для near real-time обновлений.

Многоуровневое кэширование обеспечивает оптимальную производительность: client-side browser cache для статических ассетов, CDN/Edge cache для географического распределения, application-level cache (Redis/Memcached) для API responses, и database query result caching. Cache eviction policies должны использовать LRU (Least Recently Used) для varied access patterns, TTL-based expiry по типу данных, и manual invalidation через Changes API для идентификации stale data. Мониторинг cache hit rates критически важен для adjustment стратегии - целевой показатель выше 80%.

Changes API использование для cache invalidation - ключевая оптимизация. CQC предоставляет dedicated `/changes` endpoints для provider и location изменений, принимающие startTimestamp и endTimestamp параметры в ISO8601 формате. Оптимальная стратегия: при каждом последующем вызове устанавливать startTime равным endTime предыдущего вызова для continuous tracking. Polling frequency зависит от требований: real-time applications - каждые 1-6 часов, near real-time - каждые 12 часов, batch updates - ежедневно.

Практический пример incremental cache refresh:

```javascript
let lastSyncTime = '2024-01-01T00:00:00Z';

async function syncChanges() {
  const now = new Date().toISOString();
  
  const providerChanges = await fetch(
    `https://api.service.cqc.org.uk/public/v1/changes/provider?` +
    `startTimestamp=${lastSyncTime}&endTimestamp=${now}`,
    {headers: {'Ocp-Apim-Subscription-Key': process.env.CQC_API_KEY}}
  ).then(r => r.json());
  
  for (const change of providerChanges) {
    cache.delete(`provider_${change.providerId}`);
  }
  
  lastSyncTime = now;
}

setInterval(syncChanges, 3600000); // Poll every hour
```

Batch request capabilities ограничены отсутствием native batch endpoint в CQC API, но эффективная bulk обработка возможна через pagination с perPage=1000 и параллельные запросы с rate limiting. Для fetching multiple providers рекомендуется batch processing с размером batch 30 запросов в секунду (2000/60 = ~33, используем 30 для safety margin) и 1-секундной паузой между batches. Connection pooling и HTTP keep-alive должны использоваться для persistent connections и reuse HTTP clients across requests.

Мониторинг и observability требуют tracking ключевых метрик: request rate (requests/minute), error rate по status codes, cache hit ratio (цель >80%), average response time (цель <2s), и retry frequency. Алерты должны срабатывать при 429 error rate >5%, 5xx error rate >1%, response time >2s, или cache hit rate <80%. Structured logging с correlation IDs обеспечивает traceability, а APM tools (Datadog, New Relic) предоставляют comprehensive visibility.

Community libraries предоставляют готовые решения: **tap-cqc-org-uk** (Python Singer tap для ETL pipelines с Meltano framework, поддерживает incremental sync через Changes API), **cqcr** (R package на CRAN с built-in pagination handling и filtering), и **Microsoft Power Platform Connector** (pre-built connector для Power Automate и Power Apps). Эти инструменты имплементируют best practices из коробки и могут служить reference implementations.

## Выводы и стратегические рекомендации

Успешная интеграция с CQC API в 2024-2025 требует фундаментального понимания миграции на Azure API Management platform и соответствующей адаптации всех существующих интеграций. Обязательная аутентификация через Ocp-Apim-Subscription-Key представляет breaking change, но обеспечивает более надежную и масштабируемую инфраструктуру с четкими rate limits и subscription management. Ключевое стратегическое решение - имплементировать robust caching layer с 24-часовым TTL и hourly polling Changes API для incremental updates, что минимизирует API calls и обеспечивает data freshness.

Для Birmingham-специфических приложений критически важно использовать точные параметры фильтрации: localAuthority="Birmingham" (case-sensitive), careHome="Y", и region="West Midlands" для comprehensive coverage примерно 192 care homes в регионе. Pagination с perPage=500 обеспечивает optimal balance между response size и number of requests, а combination фильтров (inspection_directorate="Adult social care", overall_rating="Good") позволяет создавать highly targeted queries для specific use cases.

Architectural pattern для production systems должен включать multi-layer caching (CDN/edge, application Redis, database), circuit breaker implementation для resilience против API failures, exponential backoff с jitter для retries, и comprehensive monitoring с alerting на critical metrics. Data consistency handling требует понимания 24-hour update cycle и eventual consistency model, с versioning tracking для cached data и clear communication к end users о data freshness expectations.

Технический долг migration с legacy api.cqc.org.uk URL должен быть приоритезирован, так как старая платформа постепенно выводится из эксплуатации. TLS 1.2+ requirement означает необходимость audit существующих HTTP clients и infrastructure для compatibility. Community resources (tap-cqc-org-uk, cqcr) предоставляют proven patterns и могут accelerate development, особенно для ETL pipelines и analytics applications.

Финальная рекомендация: начинать с базовой имплементации через developer portal registration, тестировать на небольшом subset Birmingham care homes для validation endpoint behavior и response structures, затем постепенно scale до full production load с comprehensive error handling, caching, и monitoring. Поддержка CQC через syndicationapi@cqc.org.uk responsive и helpful для technical questions и edge cases, делая integration процесс manageable даже для complex requirements.