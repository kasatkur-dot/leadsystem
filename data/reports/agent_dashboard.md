# Agent Dashboard Snapshot

Дата сборки: `2026-05-16T23:17:05Z`

Статус: read-only Markdown-снимок из `data/reports/agent_dashboard.json`.

Безопасность: этот снимок не запускает Redis, Bitrix24, Telegram, IMAP, LLM, scheduler, publisher и не показывает значения секретов.

## Верхняя панель

| Поле | Значение |
| --- | --- |
| project_name | design-studio-lead-engine |
| overall_status | OK |
| current_stage | 2026-05-17 — Подключён Агент безопасности как контрольный слой системы |
| next_small_step | открыть `data/reports/agent_dashboard.html` и глазами проверить новый блок `Security Agent Control Layer` рядом с управленческими блоками. |
| last_checked_at | 2026-05-16T23:16:40Z |

### Запреты

| Запрет | Статус |
| --- | --- |
| scheduler_locked | true |
| mass_collection_locked | true |
| real_publish_locked | true |
| real_outreach_locked | true |
| secrets_visible | false |

## Карта агентов

| Агент | Департамент | Статус | Файл |
| --- | --- | --- | --- |
| Agent 1 Scout | Разведка источников | planned/manual | agents/agent1_scout/__init__.py |
| Agent 2 Collector | Сбор лидов | partial | agents/agent2_collector/__init__.py |
| Agent 3 Processor | Обработка и скоринг | tested_partial | agents/agent3_processor/__init__.py |
| Agent 4 Publisher | Контент и доверие | dry_run/manual | agents/agent4_publisher/__init__.py |
| Agent 5 CRM | CRM и аналитика | tested | agents/agent5_crm/__init__.py |
| Agent 6 Outreach | Первое касание | planned/locked | agents/agent6_outreach/__init__.py |

## Карта источников

- Статус: `OK`
- Справочник: `content/library/sources/channel-registry-mvp.csv`
- Всего MVP-каналов: 17
- Первая волна: 9
- Planned-каналы: 8
- Watchlist конкурентов: 15
- Источники из лекции 15.05: 12
- Каналы Яники ждут заполнения: 5

### Каналы по владельцам

| Владелец | Каналов |
| --- | --- |
| agent2_collector | 4 |
| agent4_publisher | 9 |
| agent5_crm | 2 |
| agent6_outreach | 2 |

### Все 17 MVP-каналов

| Канал | Волна | Статус | Владелец | Flow | Заметка |
| --- | --- | --- | --- | --- | --- |
| Gmail tenders | wave_1 | active | agent2_collector | B | Current MVP source for engineering tenders |
| Telegram chats | wave_1 | active | agent6_outreach | A_B | Current MVP source for Telegram demand signals |
| Outbound manual | wave_1 | active | agent6_outreach | A_B | Manual and agent-assisted outbound touchpoints |
| Avito | wave_1 | manual | agent2_collector | A_B | Track manually before automation |
| Profi.ru | wave_1 | manual | agent2_collector | A | Track manually before collector |
| Yandex Services | wave_1 | manual | agent2_collector | A_B | Track manually before collector |
| Yandex Maps | wave_1 | manual | agent4_publisher | A_B | Manual calls and messages from map card |
| Referrals | wave_1 | manual | agent5_crm | A_B | Track who referred the client |
| Old inquiries | wave_1 | manual | agent5_crm | A_B | Reactivation of old leads and existing contacts |
| Yandex Direct | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires landing UTM budget and goals |
| Google Ads | wave_3 | planned | agent4_publisher | A_B | From lecturer dashboard. Later after geo and landing decisions |
| VK Ads | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires landing and UTM |
| Meta Ads | wave_3 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires legal and geo check |
| Telegram Ads | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires UTM or bot entry |
| Dzen and RSY | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Separate paid traffic from organic content |
| Influencer TG | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Use unique link or promo per placement |
| SEO organic | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Needs site or landing pages |

### Первая волна

| Канал | Волна | Статус | Владелец | Flow | Заметка |
| --- | --- | --- | --- | --- | --- |
| Gmail tenders | wave_1 | active | agent2_collector | B | Current MVP source for engineering tenders |
| Telegram chats | wave_1 | active | agent6_outreach | A_B | Current MVP source for Telegram demand signals |
| Outbound manual | wave_1 | active | agent6_outreach | A_B | Manual and agent-assisted outbound touchpoints |
| Avito | wave_1 | manual | agent2_collector | A_B | Track manually before automation |
| Profi.ru | wave_1 | manual | agent2_collector | A | Track manually before collector |
| Yandex Services | wave_1 | manual | agent2_collector | A_B | Track manually before collector |
| Yandex Maps | wave_1 | manual | agent4_publisher | A_B | Manual calls and messages from map card |
| Referrals | wave_1 | manual | agent5_crm | A_B | Track who referred the client |
| Old inquiries | wave_1 | manual | agent5_crm | A_B | Reactivation of old leads and existing contacts |

### Planned-каналы

| Канал | Волна | Статус | Владелец | Flow | Заметка |
| --- | --- | --- | --- | --- | --- |
| Yandex Direct | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires landing UTM budget and goals |
| Google Ads | wave_3 | planned | agent4_publisher | A_B | From lecturer dashboard. Later after geo and landing decisions |
| VK Ads | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires landing and UTM |
| Meta Ads | wave_3 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires legal and geo check |
| Telegram Ads | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Requires UTM or bot entry |
| Dzen and RSY | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Separate paid traffic from organic content |
| Influencer TG | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Use unique link or promo per placement |
| SEO organic | wave_2 | planned | agent4_publisher | A_B | From lecturer dashboard. Needs site or landing pages |

### Контентные поверхности Agent 4

- MAX-канал СИЛА Проекта
- Telegram
- VK
- Дзен
- Яндекс Карты
- 2GIS
- новый сайт / блог

### Watchlist конкурентов Agent 1

| Источник | Платформа | Сегмент | Статус | Зачем смотреть |
| --- | --- | --- | --- | --- |
| Проектирование зданий | telegram | B | active_manual | B2B-аудитория проектировщиков ГИПов и руководителей проектных компаний |
| Рупор ГИП | telegram | B | active_manual | Новости нормы и проектная документация для ГИПов |
| ПРОЕКТИРОВАНИЕ ЗДАНИЙ ЧАТ | telegram | B | planned_manual | Чат проектировщиков и вакансий как источник боли и спроса |
| PEREPLAN. Перепланировка и согласование | telegram | A | active_manual | Крупный B2C/B2B канал по перепланировкам Москвы и Петербурга |
| Согласование перепланировки в Москве и МО | telegram | A | active_manual | Узкая аудитория дизайнеров ремонтников риелторов |
| МОСтройпроект | website | A | active_manual | Сильная упаковка с кейсами сроками стоимостью и документами |
| Ресог | website | A | active_manual | Перепланировки с фокусом на требования 2026 и бывших сотрудников Жилинспекции |
| Replan Estate | website | A+B | active_manual | Нежилые помещения проектная документация согласования ремонт под ключ |
| Архитектоника | website | A | active_manual | Перепланировки под ключ Москва |
| Согласуем | website | A | active_manual | Перепланировки под ключ Москва |
| DOCUMENTALL | vk | A+B | planned_manual | СПб и ЛО перепланировка реконструкция полный цикл |
| REPLAN Новосибирск | vk | A | planned_manual | Региональный конкурент по перепланировкам |
| МОСтройпроект VK | vk | A | planned_manual | VK-упаковка крупного конкурента |
| ПКСтрой | vk | A | planned_manual | Перепланировки Москва опыт с 2008 |
| Яндекс Недвижимость: перепланировка | website | A | active_manual | Поисковая статья с понятной структурой для B2C |

### Growth source map из лекции 15.05

Файл: `content/library/sources/lecture-2026-05-15-growth-source-map.csv`
Скоринг: `OK`
Отчёт скоринга: `data/reports/lecture_growth_source_score.json`
Требуют approval или уточнения: 10

| Источник | Платформа | Сегмент | Статус | Зачем смотреть |
| --- | --- | --- | --- | --- |
| MAX-канал СИЛА Проекта | MAX | all_segments | approved | Главная площадка доверия и прогрева после входа из внешних источников |
| Telegram-каналы коммерческой недвижимости | Telegram | commercial_real_estate | candidate | Искать собственников арендаторов УК девелоперов ТЦ БЦ складов |
| VK-сообщества предпринимателей и коммерческой недвижимости | VK | b2b | candidate | Проверять темы аренды ремонта fit-out реконструкции и перепланировок |
| Форумы и обсуждения предпринимателей | Forums | b2b | candidate | Ловить реальные вопросы про открытие магазина офиса склада и согласования |
| 2GIS карточки и категории | 2GIS | local_search | candidate | Понять спрос по городам и привести карточку к единой аналитике |
| Яндекс Карты и Яндекс Бизнес | Yandex | local_search | candidate | Проверить видимость по проектированию и перепланировке |
| Avito Услуги проектирование | Avito | private_and_small_business | candidate | Вторичный поток вопросов по проектированию и перепланировке |
| Коммерческие тендерные площадки | Tender | b2b | candidate | Искать ПД РД реконструкцию перепланировку обследования для юрлиц |
| Сайты девелоперов и УК | Web | b2b | candidate | Собрать список компаний где могут быть объекты и запросы на проектирование |
| Складские операторы и индустриальные парки | Web | warehouses | candidate | Приоритет для складов ангаров реконструкций и ПД РД |
| Ритейл и франчайзи | Web | retail_fitout | candidate | Магазины ТЦ fit-out перепланировки под арендодателя и УК |
| Старые контакты и сделки Bitrix24 | Bitrix24 | crm_base | approved_readonly | Найти дубли старые лиды и сегменты для аккуратной реактивации |

### Каналы Яники: ждут ссылок

| Источник | Платформа | Сегмент | Статус | Зачем смотреть |
| --- | --- | --- | --- | --- |
|  | telegram|vk|max|dzen|website|other | A|B|A+B | pending_yanika_input |  |
|  | telegram|vk|max|dzen|website|other | A|B|A+B | pending_yanika_input |  |
|  | telegram|vk|max|dzen|website|other | A|B|A+B | pending_yanika_input |  |
|  | telegram|vk|max|dzen|website|other | A|B|A+B | pending_yanika_input |  |
|  | telegram|vk|max|dzen|website|other | A|B|A+B | pending_yanika_input |  |

### Backlog-источники

- 2GIS как отдельный lead/referrer source
- VK-группы и обсуждения
- коммерческие тендерные площадки
- HH.ru вакансии как сигнал спроса на проектирование
- партнёры: риелторы, дизайнеры, юристы, кадастровые инженеры
- сайт / лендинги / SEO-страницы услуг
- лид-магнит ПРОВЕРКА перепланировки
- ЕИС и госзакупки
- закупки девелоперов и сетевых компаний
- каталоги франшиз и коммерческой недвижимости
- банки, ипотечные брокеры, оценщики и страховые
- БТИ / кадастровые / юридические партнёры
- поставщики, подрядчики fit-out и вывесок
- форумы, Яндекс Q, TenChat
- GEO/AI visibility: ChatGPT, Perplexity, Яндекс/Алиса и нейропоиск
- Reels/shorts radar и ROMI по контенту позже

## Bitrix CRM Hygiene

- Статус: `LIMITED_AUDIT`
- Отчёт: `data/reports/bitrix_readonly_audit.json`
- Сформирован: `2026-05-14T21:34:41Z`
- Полный отчёт: `False`

### Сводка

| Метрика | Значение |
| --- | --- |
| contacts | 150 |
| leads_total | 150 |
| leads_active | 0 |
| deals_total | 150 |
| statuses | 5 |
| sources | 24 |

### Качество данных

| Проблема | Количество |
| --- | --- |
| leads_without_source | 0 |
| leads_without_phone_or_email | 24 |
| contacts_without_phone_or_email | 37 |

### Дубли

| Тип | Групп |
| --- | --- |
| contacts_by_phone | 2 |
| contacts_by_email | 2 |
| contacts_by_name_hash | 4 |
| leads_by_phone | 3 |
| leads_by_email | 4 |
| strong_groups_to_review_first | 4 |
| total_phone_email_groups | 11 |

### Источники лидов

| ID | Название | Кол-во |
| --- | --- | --- |
| CALL | Звонок | 78 |
| EMAIL | Электронная почта | 46 |
| 12|MAX_NUMBER_REDHAM | Max - Max | 26 |

### Стадии сделок

| ID | Кол-во |
| --- | --- |
| NEW | 55 |
| UC_O7PVUC | 28 |
| LOSE | 12 |
| UC_L031LQ | 8 |
| C4:NEW | 8 |
| C2:EXECUTING | 7 |
| WON | 6 |
| UC_VYUJ7T | 5 |
| UC_8VSK99 | 3 |
| UC_B696WE | 3 |
| C2:PREPAYMENT_INVOICE | 2 |
| C2:NEW | 2 |

### Очередь чистки

- контакты-дубли по телефону
- контакты-дубли по обычному email
- лиды-дубли по телефону
- контакты без телефона/email, у которых нет сделок
- расшифровать стадии сделок UC_*


## VPP AI-manager dry-run

- Статус: `READY`
- Dry-run: `true`
- Сценариев: `3`
- Отчёт: `data/reports/vpp_ai_manager_dry_run.json`
- Markdown: `data/reports/vpp_ai_manager_dry_run.md`

### Сводка

| Метрика | Значение |
| --- | --- |
| scenarios_ready | 3 |
| enough_for_kp | 1 |
| need_missing_data | 2 |
| missing_data_total | 2 |
| bitrix_dry_run_not_sent | 3 |

### Сценарии

| Сценарий | Сегмент | Flow | Score | Данные | Чего не хватает | Следующий шаг | КП 24ч | Bitrix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Склад / ангар | b2b_warehouse_angar | B | hot | enough_for_kp | нет | kp_prepare | true | DRY_RUN_NOT_SENT |
| Коммерческая перепланировка | b2b_commercial_replan | A | hot | enough_for_review | город | ask_missing_data_then_review | false | DRY_RUN_NOT_SENT |
| Перепланировка квартиры | b2c_apartment_replan | A | warm | enough_for_review | город | ask_missing_data_then_review | false | DRY_RUN_NOT_SENT |

### Внешние вызовы

| Сервис | Вызван |
| --- | --- |
| redis | false |
| bitrix24 | false |
| telegram_send | false |
| max_send | false |
| imap | false |
| llm | false |
| scheduler | false |
| publisher | false |
| ads | false |

Safety: Это локальный dry-run: контакты заредактированы, Bitrix24/Redis/MAX/Telegram/LLM/реклама не вызывались.


## First Safe Growth Tests

- Статус: `READY`
- Тестов: `3`
- Отчёт: `data/reports/first_safe_growth_tests.json`

| ID | Источник | Режим | Действие | Approval | Stop rule |
| --- | --- | --- | --- | --- | --- |
| safe_growth_001 | Старые контакты и сделки Bitrix24 | read_only | Сегментировать старые контакты и сделки, найти дубли и кандидатов на ручную реактивацию. | true | Остановиться до любых изменений карточек, объединения дублей или сообщений клиентам. |
| safe_growth_002 | MAX-канал СИЛА Проекта | draft_only | Подготовить 5 B2B-постов первой волны без публикации. | true | Остановиться до публикации, автопостинга или платного продвижения. |
| safe_growth_003 | Коммерческие тендерные площадки | read_only | Подготовить фильтры тендеров и чеклист решения участвовать или нет. | true | Остановиться до регистрации, оплаты агрегатора, подачи заявки или загрузки документов. |

### Отложено

- Реактивация старых контактов Bitrix24 только после отдельного approval.
- Публикация MAX-постов только после approval.
- Регистрация, оплата и подача тендеров только после отдельного решения.
- Telegram/VK/форумы только после списка конкретных площадок и проверки правил.
- Реклама только после бюджета, UTM, стоп-правил и готового лендинга/поста.


## Bitrix Reactivation Readonly Plan

- Статус: `READY`
- Отчёт: `data/reports/bitrix_reactivation_readonly_plan.json`
- Audit limited_by_pages: `true`

### Summary

| Метрика | Значение |
| --- | --- |
| contacts | 150 |
| leads_total | 150 |
| leads_active | 0 |
| deals_total | 150 |
| total_duplicate_groups | 11 |
| contacts_without_phone_or_email | 37 |
| leads_without_phone_or_email | 24 |
| leads_without_source | 0 |

### Cleanup Queue

| ID | Очередь | Count | Priority | Action |
| --- | --- | --- | --- | --- |
| cleanup_001 | Контакты-дубли по телефону | 2 | P1 | Ручная проверка групп дублей. Ничего не объединять автоматически. |
| cleanup_002 | Контакты-дубли по email | 2 | P1 | Проверить, где один клиент создан несколько раз. |
| cleanup_003 | Лиды-дубли по телефону/email | 7 | P2 | Понять, какие лиды можно связать с контактом или сделкой. |
| cleanup_004 | Контакты без телефона/email | 37 | P2 | Отделить полезные карточки от пустых. |
| cleanup_005 | Лиды без телефона/email | 24 | P2 | Понять, есть ли email/телефон в комментариях или связанной сделке. |
| cleanup_006 | Лиды без источника | 0 | P3 | Назначить источник по истории только там, где он очевиден. |

### Reactivation Buckets

| ID | Группа | Priority | Status |
| --- | --- | --- | --- |
| reactivation_001 | Старые заявки с контактом | P1 | NOT_PREPARED_APPROVAL_REQUIRED |
| reactivation_002 | Сделки без понятного следующего шага | P1 | NOT_PREPARED_APPROVAL_REQUIRED |
| reactivation_003 | Лиды без источника, но с контактом | P2 | NOT_PREPARED_APPROVAL_REQUIRED |
| reactivation_004 | Пустые карточки | P4 | DO_NOT_CONTACT |

### Нужен approval перед

- `merge_duplicates`
- `update_contact`
- `update_lead`
- `close_lead`
- `create_task`
- `send_message`
- `reactivation_campaign`


## Tender Filter Pack Dry Run

- Статус: `READY`
- Фильтров: `6`
- Файл: `content/library/sources/tender-filter-pack-vpp.csv`
- Отчёт: `data/reports/tender_filter_pack_dry_run.json`

| Filter | Segment | Priority | Status | Stop rule |
| --- | --- | --- | --- | --- |
| tender_001 | warehouse_design | P1 | OK | Не подавать заявку, не оплачивать площадку и не создавать сделку без approval. |
| tender_002 | commercial_reconstruction | P1 | OK | Не подавать заявку, не оплачивать площадку и не создавать сделку без approval. |
| tender_003 | retail_fitout | P2 | OK | Не подавать заявку, не оплачивать площадку и не создавать сделку без approval. |
| tender_004 | commercial_replan | P1 | OK | Не подавать заявку, не оплачивать площадку и не создавать сделку без approval. |
| tender_005 | project_sections | P2 | OK | Не подавать заявку, не оплачивать площадку и не создавать сделку без approval. |
| tender_006 | private_house_secondary | P3 | OK | Не подавать заявку, не оплачивать площадку и не создавать сделку без approval. |

### Нужен approval перед

- `open_paid_aggregator`
- `register_tender_platform`
- `upload_documents`
- `submit_bid`
- `create_bitrix_deal`
- `create_manager_task`


## Client Acquisition Pack

- Статус: `READY`
- Маршрутов: `6`
- Approval required: `6`
- Отчёт: `data/reports/client_acquisition_pack_dry_run.json`

| Route | Segment | Priority | Source | Offer | Approval |
| --- | --- | --- | --- | --- | --- |
| route_001 | commercial_replan | P1 | MAX | Разбор готовности коммерческой перепланировки к КП | APPROVAL_REQUIRED |
| route_002 | warehouse_design | P1 | Tender | ПД/РД для склада или ангара после проверки исходных данных | APPROVAL_REQUIRED |
| route_003 | commercial_reconstruction | P1 | Tender | Первичная проверка реконструкции: состав работ, обследование, экспертиза | APPROVAL_REQUIRED |
| route_004 | retail_fitout | P2 | MAX | Проект для магазина/ТЦ/fit-out под требования арендодателя | APPROVAL_REQUIRED |
| route_005 | project_sections | P2 | Tender | Отдельные разделы ПД/РД для юрлиц | APPROVAL_REQUIRED |
| route_006 | private_house_secondary | P3 | MAX | Проект дома как вторичный поток после B2B | APPROVAL_REQUIRED |

### Supporting assets

- `docs/client-acquisition-operating-system-from-lecture.md`
- `content/growth/approved-only-outreach-templates-vpp.md`
- `site/landing-drafts/b2b-segment-landing-blueprints.md`
- `content/pipeline/drafts/max-b2b-first-wave-2026-05-16.md`
- `docs/tender-readonly-filter-and-decision-pack.md`


## Three Qualified Leads Sprint

- Статус: `READY`
- Цель: `3 qualified leads`
- Sprint items: `15`
- Target qualified leads: `3`
- Ready/draft items: `7`
- Approval required items: `12`
- Отчёт: `data/reports/three_qualified_leads_sprint.json`

### Перенос астрометодики

- `expert`: ВПП: СРО, 10+ лет, проектирование, перепланировки, реконструкция
- `product`: AI-проверка исходных данных к КП
- `content_factory`: MAX B2B posts + future landing pages + tender filters
- `traffic_sources`: MAX, Tender, Bitrix old base, future Telegram/VK/ABM
- `warmup`: серия экспертных постов и approved-only ответы
- `conversion`: Bitrix24 -> КП -> договор

### Sprint items

| ID | Week | Segment | Agent | Source | Metric | Target | Status | Next |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tql_001 | 1 | commercial_replan | agent4_publisher | MAX | content_ready | 1 | published_manual_unverified | collect_post_url_and_first_reactions |
| tql_002 | 1 | warehouse_design | agent4_publisher | MAX | content_ready | 1 | published_manual_unverified_public | collect_exact_post_url_or_wait_maxstat_index |
| tql_003 | 1 | commercial_reconstruction | agent4_publisher | MAX | content_ready | 1 | approved | prepare_manual_publication |
| tql_004 | 1 | retail_fitout | agent4_publisher | MAX | content_ready | 1 | draft | prepare_final_post |
| tql_005 | 1 | b2b_kp_readiness | agent4_publisher | MAX | content_ready | 1 | draft | prepare_final_post |
| tql_006 | 1 | all_b2b | agent5_crm | Bitrix24 | crm_readiness | 1 | partial_limited_audit | need_full_audit |
| tql_007 | 2 | warehouse_design | agent1_scout | Tender | source_candidates | 3 | ready | find_candidates_when_network_available |
| tql_008 | 2 | commercial_replan | agent1_scout | Tender | source_candidates | 3 | ready | find_candidates_when_network_available |
| tql_009 | 2 | retail_fitout | agent6_outreach | ABM | company_shortlist | 10 | planned | prepare_shortlist |
| tql_010 | 2 | commercial_replan | agent3_processor | AI_manager | qualified_lead_scenario | 1 | ready | use_existing_scenario |
| tql_011 | 2 | warehouse_design | agent3_processor | AI_manager | qualified_lead_scenario | 1 | ready | use_existing_scenario |
| tql_012 | 2 | commercial_reconstruction | agent3_processor | AI_manager | qualified_lead_scenario | 1 | planned | add_reconstruction_scenario |
| tql_013 | 3 | commercial_replan | agent5_crm | MAX_OR_Bitrix | qualified_leads | 1 | planned | manual_test_after_approval |
| tql_014 | 3 | warehouse_design | agent5_crm | Tender | qualified_leads | 1 | planned | manual_test_after_approval |
| tql_015 | 3 | commercial_reconstruction | agent5_crm | MAX_OR_Tender | qualified_leads | 1 | planned | manual_test_after_approval |


## Карта взаимодействий агентов

показать, как агенты взаимодействуют между собой и через какие очереди/файлы передают результат

### Основной поток лида

- Статус: `partly_tested`
- Цепочка: Agent 1 Scout -> Agent 2 Collector -> Redis leads:raw -> Agent 3 Processor -> Redis leads:qualified -> Agent 5 CRM -> Bitrix24 / Telegram / отчёт
- Что проходит: source card -> RawLead -> QualifiedLead -> CRM record
- Safety: Полный runtime с настоящим LLM и Agent 5 пока запускать только отдельным контролируемым тестом.

### Контентный поток

- Статус: `dry_run/manual`
- Цепочка: Agent 1 Scout -> Agent 4 Publisher -> content:published -> Agent 5 CRM -> ROMI / канал-отчёт
- Что проходит: боли рынка -> черновик/публикация -> событие контента -> аналитика канала
- Safety: Реальные публикации заблокированы без отдельного подтверждения.

### Outreach поток

- Статус: `planned/locked`
- Цепочка: Agent 6 Outreach -> approval человека -> leads:outreach -> Agent 5 CRM -> Bitrix24 / следующий шаг
- Что проходит: кандидат -> одобренный ответ -> заинтересованный диалог -> CRM
- Safety: Отправка сообщений и real outreach заблокированы.

### Контрольный поток

- Статус: `active/read_only`
- Цепочка: REPORT.md -> 6 agent files -> scripts/check_agent_okr_contract.py -> agent_dashboard.json -> agent_dashboard.html
- Что проходит: факты из файлов -> checker report -> визуальная панель
- Safety: Checker только читает локальные файлы и пишет локальный JSON-отчёт.


## Chief of Staff / Handoff / Escalation / Weekly digest

- Статус: `read_only/planned_runtime_later`
- Источник: `docs/chief-of-staff-handoff-protocol.md`
- Правило: агент = роль / ответственность; skill = действие внутри роли
- Chief of Staff: CLAUDE.md / AGENTS.md / REPORT.md
- Смысл: режим координации, а не Agent 7
- Ответственность: принять задачу, восстановить контекст, выбрать маршрут, проверить результат и обновить память

### Нервная система

вход задачи -> маршрутизация -> агенты -> QA/checker -> результат -> память

### Шаблоны

| Шаблон | Зачем | Поля |
| --- | --- | --- |
| task-handoff | передать задачу от слоя/агента к следующему владельцу | от кого, кому, цель, контекст, формат результата, риски, нужна ли Яника |
| agent-result | вернуть итог работы агента в едином формате | что сделано, что проверено, статус, отчёты, риски, следующий шаг |
| escalation-to-yana | остановиться и вынести решение человеку | ситуация, вариант 1, плюсы/минусы, вариант 2, рекомендация, что решить Янике |
| weekly digest | будущий недельный итог Agent 5/dashboard | фокус недели, что сделано, лиды и CRM, контент, ROMI, блокеры, план |

### Эскалация Янике

- платный API или рост бюджета
- реальная публикация
- массовый сбор лидов
- реальная outreach-отправка
- изменение CRM-логики
- персональные данные или юридические обещания

Weekly digest: Agent 5 CRM/Analytics + dashboard reports позже


## MAS Reference Layer

- Статус: `read_only/spec_only`
- Источник: `research/external-mas-ip-analysis-2026-05-15.md`
- URL: `http://193.233.131.92/`
- Модель: Внешняя модель описывает операционный центр: входящая задача -> Chief Orchestrator -> департамент -> профильный агент -> сценарий выполнения -> артефакт -> контроль качества -> следующий шаг.
- Правило применения: берём принципы управления, но не расширяем систему: остаются 6 агентов + checker, не Agent 7

### Что берём

| Блок | Зачем | Где | Статус |
| --- | --- | --- | --- |
| Agent Inspector | карточка выбранного агента: роль, входы, выходы, правила, KPI, файлы, блокеры | правая панель dashboard | planned |
| Scenario Timeline | путь задачи по шагам, чтобы видеть где она находится | нижняя timeline-панель | planned |
| Artifact Tracker | каждый этап закрывается только проверяемым артефактом | детали сценария и event stream | planned |
| Status model | единые статусы: locked/manual/ready/queued/running/needs_review/failed/done | карта агентов, event stream, детали агента | planned |
| OSINT protocol | проверка фактов и рисков по открытым источникам | Agent 1 Scout и Agent 5 CRM, без нового агента | future_safe_protocol |
| AI Operator Chat | чат понимает, какой агент выбран оператором | future-layer после read-only dashboard | later_locked |

### Сценарии

| Сценарий | Цепочка | Артефакт |
| --- | --- | --- |
| Первый входящий запрос | сайт/MAX/Telegram/email -> AI-менеджер -> Agent 3 -> Agent 5 -> Bitrix24 сделка -> человек | intake_card + bitrix_deal |
| Тендерный лид | Gmail tender -> Agent 2 -> Agent 3 -> Agent 5 -> Bitrix24 -> analytics | raw_lead + qualified_lead + crm_event |
| Контентный сигнал | Agent 1 Scout -> Agent 4 Publisher -> content event -> Agent 5 -> ROMI later | source_signal_card + content_draft/content_event |
| CRM hygiene | Bitrix24 audit -> Agent 5 -> duplicate queue -> human cleanup | crm_hygiene_report |
| ROMI | source -> lead -> deal -> revenue -> channel -> profit -> ROMI | channel_report / romi_report |

### Артефакты

| Этап | Артефакт |
| --- | --- |
| Agent 1 Scout | source_signal_card |
| Agent 2 Collector | raw_lead |
| Agent 3 Processor | qualified_lead |
| AI-менеджер | intake_card |
| Agent 4 Publisher | content_draft или published_content_event |
| Agent 5 CRM | bitrix_deal или crm_hygiene_report |
| Agent 5 Analytics | channel_report или romi_report |
| Agent 6 Outreach | approved_reply или outreach_lead |
| Checker | agent_okr_contract_check.json |

### Status model

`locked`, `manual`, `ready`, `queued`, `running`, `needs_review`, `failed`, `done`

### OSINT-правила

- важный факт подтверждать 2-3 источниками
- хранить URL, дату проверки и уровень доверия
- не использовать серые методы, взлом, утечки и закрытые персональные данные
- не принимать автоматическое решение по крупной сделке без человека
- для крупной сделки отдавать человеку короткий risk-summary

### Later-locks

- AI Operator Chat не запускать до правил доступа и контроля стоимости LLM
- POST /api/chat и /api/chat/audio внешнего референса не тестировать без отдельного решения
- OSINT/MCP-интеграции не подключать до первого MVP и preflight

## Security Agent Control Layer

- Статус: `ACTIVE`
- Источник: `agents/Агент безопастности/AGENT_SECURITY.md`
- Документ: `docs/security-agent-control-layer.md`
- Не Agent 7: `true`
- Смысл: единый контроль безопасности для всех 6 агентов, checker/dashboard, LLM, MCP/API и будущих интеграций

### Красные линии

- деньги, лимиты, подписки и платные API только после явного подтверждения
- production, deploy, реальные публикации, outreach и массовые действия только после approval
- секреты, токены, cookies, session-файлы, PII и CRM-данные не показывать и не отправлять наружу
- новые MCP/API, внешняя telemetry и скрытые фоновые действия только через preflight

### Зелёный коридор

- локальные dry-run и read-only проверки
- локальные тесты, compileall, checker и dashboard builder
- синтетические или обезличенные данные
- обычные правки файлов без внешних отправок

### AI-риски

- prompt injection
- lethal trifecta
- SSRF
- slopsquatting
- markdown/image exfiltration
- неструктурированный LLM output
- небезопасные MCP-инструменты

### Куда подключён

- `CLAUDE.md`
- `AGENTS.md`
- `.claude/rules/security.md`
- `docs/claude-project-rules.md`
- `docs/security-agent-control-layer.md`
- `scripts/check_agent_okr_contract.py`
- `data/reports/agent_dashboard.json`
- `data/reports/agent_dashboard.md`
- `data/reports/agent_dashboard.html`

### По агентам

| Агент | Контроль |
| --- | --- |
| Agent 1 Scout | только публичные источники, без закрытых персональных данных |
| Agent 2 Collector | один источник сначала, без массового сбора и без серых методов |
| Agent 3 Processor | structured LLM I/O, prompt injection guard, без PII наружу |
| Agent 4 Publisher | нет публикаций без approval, нет неподтверждённых обещаний |
| Agent 5 CRM | CRM/Bitrix24/Telegram только по разрешённому сценарию, секреты не выводить |
| Agent 6 Outreach | нет массовых отправок и первого касания без approval человека |
| Checker/dashboard | read-only, статусы без секретов, без внешних вызовов |

## Scenario Artifact Contract

- Статус: `read_only/local_contract`
- Документ сценариев: `docs/agent-scenario-artifact-contract.md`
- Документ субролей: `docs/agent-subroles-and-kpi-map.md`
- Правило: каждый этап закрыт только если есть вход, выход, статус, next_step и проверяемый артефакт

### Сценарии и артефакты

| Сценарий | Timeline | Артефакты | MVP-статус |
| --- | --- | --- | --- |
| Первый входящий запрос | site/MAX/Telegram/email -> intake_card -> Agent 3 -> Agent 5 -> crm_payload_preview -> human_next_step | intake_card, qualified_lead, crm_payload_preview, human_next_step | OK_LOCAL_DRY_RUN_READY_FOR_MANUAL_REVIEW |
| Контент даёт лид | SignalCard -> content_brief -> content_draft -> approval_card -> content_metric_event -> Agent 5 analytics | SignalCard, content_brief, content_draft, approval_card, content_metric_event | draft/manual |
| Тендерный лид | Gmail/IMAP tender -> Agent 2 -> raw_lead -> Agent 3 -> qualified_lead -> Agent 5 -> Bitrix24/human | raw_lead, normalized_raw_lead, qualified_lead, crm_payload_preview | partial_tested |
| ROMI канала | source -> cost -> lead -> deal -> revenue -> profit -> ROMI -> channel_decision | channel_registry_row, channel_cost_row, channel_fact_row, channel_report, channel_decision | csv_mvp_exists |

### Единый Status model

`locked`, `manual`, `draft`, `approval_ready`, `approved`, `queued`, `running`, `needs_review`, `failed`, `done`, `published_manual_unverified_public`

### Запреты

- не создавать Agent 7
- не запускать scheduler без отдельного подтверждения
- не запускать массовый сбор
- не публиковать и не отправлять outreach без approval
- не показывать секреты

## Детали агентов

### Agent 1 Scout

- Департамент: Разведка источников
- Готовность: 35%
- KR-готовность: 67%
- Описание: Ищет, где могут появляться будущие заказчики и какие темы важны рынку.
- OKR: Дать системе понятный список перспективных источников и первый следующий шаг по каждому источнику.
- Что доделать: Сделать первую source card для одного выбранного источника и передать её Agent 2.

Источники по агенту:

- Смысл: Смотрит весь рынок: 17 системных каналов, конкурентов, каналы Яники и backlog-источники.
- Основных источников: 17
- Watchlist: 15
- Каналы Яники ждут: 5

- Gmail tenders
- Telegram chats
- Outbound manual
- Avito
- Profi.ru
- Yandex Services
- Yandex Maps
- Referrals
- Old inquiries
- Yandex Direct
- Google Ads
- VK Ads
- Meta Ads
- Telegram Ads
- Dzen and RSY
- Influencer TG
- SEO organic

Watchlist:
- Проектирование зданий
- Рупор ГИП
- ПРОЕКТИРОВАНИЕ ЗДАНИЙ ЧАТ
- PEREPLAN. Перепланировка и согласование
- Согласование перепланировки в Москве и МО
- МОСтройпроект
- Ресог
- Replan Estate
- Архитектоника
- Согласуем
- DOCUMENTALL
- REPLAN Новосибирск
- МОСтройпроект VK
- ПКСтрой
- Яндекс Недвижимость: перепланировка

Каналы Яники ждут заполнения:
- yanika_channel_001
- yanika_channel_002
- yanika_channel_003
- yanika_channel_004
- yanika_channel_005

Backlog-источники:
- 2GIS как отдельный lead/referrer source
- VK-группы и обсуждения
- коммерческие тендерные площадки
- HH.ru вакансии как сигнал спроса на проектирование
- партнёры: риелторы, дизайнеры, юристы, кадастровые инженеры
- сайт / лендинги / SEO-страницы услуг
- лид-магнит ПРОВЕРКА перепланировки
- ЕИС и госзакупки
- закупки девелоперов и сетевых компаний
- каталоги франшиз и коммерческой недвижимости
- банки, ипотечные брокеры, оценщики и страховые
- БТИ / кадастровые / юридические партнёры
- поставщики, подрядчики fit-out и вывесок
- форумы, Яндекс Q, TenChat
- GEO/AI visibility: ChatGPT, Perplexity, Яндекс/Алиса и нейропоиск
- Reels/shorts radar и ROMI по контенту позже

Главная метрика:
- Покрытие карты источников: 17 / 17 каналов
- Когда закрыта: все каналы системы есть в справочнике и имеют владельца

OKR/KR метрики:

| Метрика | Число |
| --- | --- |
| Учтены все каналы системы | 17 / 17 каналов |
| Каналы первой волны разложены по агентам | 9 / 9 каналов |
| Planned-каналы из дашборда лектора учтены | 8 / 8 каналов |
| Конкурентные и рыночные источники в watchlist | 15 / 15 строк |
| Source cards первой волны готовы | 0 / 9 карточек |
| Личные каналы Яники заполнены | 0 / 5 ссылок |

Защитные метрики:
- 0 источников переводятся в активный сбор без владельца, next_action и проверки риска
- 0 неподтверждённых утверждений о конкурентах попадает в итоговые рекомендации

Суброли:
| Суброль | Что делает | Артефакт | KPI |
| --- | --- | --- | --- |
| Market Research Agent | рыночный спрос, сегменты, темы | SignalCard | 5+ полезных сигналов перед запуском нового источника |
| Competitor Analyst | конкуренты, упаковка, доказательства | competitor_note | у каждого конкурента есть ссылка, сегмент, сильная сторона и risk_notes |
| Source Radar | новые каналы лидов и контента | source_signal_card | 100% новых источников имеют owner_agent и next_action |
| Reviews/Maps Monitor | карты, отзывы, вопросы клиентов | review_signal | отзывы превращаются в боли, FAQ и темы, без копирования |
| Demand Signal Curator | отбор сигналов и handoff | handoff_recommendation | 100% SignalCard имеют recommended_action, handoff_to, risk_notes |

Скиллы:
- поиск источников
- анализ конкурентов
- анализ отзывов
- поиск тендерного спроса

### Agent 2 Collector

- Департамент: Сбор лидов
- Готовность: 45%
- KR-готовность: 50%
- Описание: Забирает лиды из разрешённого источника и превращает их в сырые карточки.
- OKR: Безопасно получить первый тестовый лид из одного источника и передать его на квалификацию.
- Что доделать: Провести один безопасный тест сбора из одного источника без массового парсинга.

Источники по агенту:

- Смысл: Собирает входящие лиды из разрешённых площадок первой волны.
- Основных источников: 4
- Watchlist: 0
- Каналы Яники ждут: 0

- Gmail tenders
- Avito
- Profi.ru
- Yandex Services

Главная метрика:
- Покрытие источников сбора Agent 2: 1 / 4 источников
- Когда закрыта: по каждому источнику Agent 2 есть хотя бы один тестовый RawLead или ручной сигнал

OKR/KR метрики:

| Метрика | Число |
| --- | --- |
| Источники сбора Agent 2 учтены | 4 / 4 каналов |
| Автоматизированный или проверенный сбор | 1 / 4 источников |
| Тестовые RawLead для покрытия Agent 2 | 1 / 4 лидов |
| Месячный пилот сбора | 0 / 20 RawLead |
| Redis-передача RawLead доказана | 1 / 1 тест |

Защитные метрики:
- 0 массовых сборов, парсингов и реальных площадок без отдельного подтверждения
- дубли должны отсекаться до передачи дальше; целевой порог дублей после фильтра — 0

Суброли:
| Суброль | Что делает | Артефакт | KPI |
| --- | --- | --- | --- |
| Tender/Email Collector | почта и тендерные письма | raw_lead | RawLead создаётся без потери source и raw_text |
| Marketplace Collector | Avito, Profi, Яндекс Услуги позже | marketplace_raw_lead | один источник за раз, не все платформы сразу |
| Directory Collector | карты и каталоги позже | directory_signal | только разрешённые публичные сигналы |
| Lead Normalizer | единый формат RawLead | normalized_raw_lead | 100% RawLead имеют source, flow, raw_text, created_at |
| Duplicate Guard | дубли до передачи дальше | duplicate_decision | явные дубли не уходят в Agent 3 |

Скиллы:
- разбор писем
- разметка источника
- нормализация данных

### Agent 3 Processor

- Департамент: Обработка и скоринг
- Готовность: 70%
- KR-готовность: 67%
- Описание: Очищает лид, понимает его смысл, ставит приоритет и предлагает следующий шаг.
- OKR: Отделить сильные заявки от слабых и дать менеджеру понятное действие по каждому лиду.
- Что доделать: Закрыть полный handoff: Agent 3 -> Agent 5 на одном тестовом лиде.

Источники по агенту:

- Смысл: Не ходит наружу: принимает RawLead от Agent 2/6 и должен уметь обработать лиды из всех каналов первой волны.
- Основных источников: 9
- Watchlist: 0
- Каналы Яники ждут: 0

- Gmail tenders
- Telegram chats
- Outbound manual
- Avito
- Profi.ru
- Yandex Services
- Yandex Maps
- Referrals
- Old inquiries

Backlog-источники:
- после MVP обработка всех 17 каналов, а не только wave_1

Главная метрика:
- Обработанные тестовые лиды по первой волне: 1 / 9 лидов
- Когда закрыта: по одному тестовому лиду из каждого wave_1 канала проходит score и next_action

OKR/KR метрики:

| Метрика | Число |
| --- | --- |
| Сквозной тест лида обработан | 1 / 1 тест |
| Покрытие первой волны источников | 1 / 9 лидов |
| Режимы скоринга проверены | 2 / 2 режима |
| CRM-handoff проверен | 1 / 1 тест |
| Категории score проверены | 1 / 4 категорий |

Защитные метрики:
- ошибочные hot-лиды после появления реальной выборки — не выше 10%
- 0 QualifiedLead без source, score_reason и recommended_action

Суброли:
| Суброль | Что делает | Артефакт | KPI |
| --- | --- | --- | --- |
| Cleaner | шум, мусор, оффтопик | clean_lead | оффтопик не попадает в CRM |
| Enricher | город, объект, площадь, контакт | lead_enrichment | доступные поля извлекаются из текста |
| Scorer | hot/warm/cold/off | score_result | каждый score имеет score_reason |
| Offer/Next-Step Architect | оффер и следующий шаг | qualified_lead | каждый QualifiedLead имеет recommended_action |
| QA Classifier | проверка завышенного score | processor_quality_note | после выборки ошибочные hot-лиды не выше 10% |

Скиллы:
- очистка данных
- выделение сути
- скоринг лида
- подготовка оффера

### Agent 4 Publisher

- Департамент: Контент и доверие
- Готовность: 40%
- KR-готовность: 34%
- Описание: Готовит контент, который объясняет экспертизу студии и усиливает доверие.
- OKR: Стабильно готовить черновики контента и материалы доверия без автопубликации.
- Что доделать: Держать публикации в dry-run и позже связать контент-события с аналитикой Agent 5.

Источники по агенту:

- Смысл: Отвечает за каналы доверия, контентные поверхности, сайт, карты и будущие платные/органические источники.
- Основных источников: 9
- Watchlist: 0
- Каналы Яники ждут: 0

- Yandex Maps
- Yandex Direct
- Google Ads
- VK Ads
- Meta Ads
- Telegram Ads
- Dzen and RSY
- Influencer TG
- SEO organic

Контентные поверхности:
- MAX-канал СИЛА Проекта
- Telegram
- VK
- Дзен
- Яндекс Карты
- 2GIS
- новый сайт / блог

Backlog-источники:
- новый сайт / SEO-страницы
- лид-магнит ПРОВЕРКА
- GEO/AI visibility
- Reels/shorts radar
- ROMI по контенту

Главная метрика:
- Контентные поверхности учтены: 5 / 7 поверхностей
- Когда закрыта: MAX, Telegram, VK, Дзен, Яндекс Карты, 2GIS и сайт/блог учитываются отдельно

OKR/KR метрики:

| Метрика | Число |
| --- | --- |
| Контентные поверхности учтены | 5 / 7 поверхностей |
| Черновики первой недели | 0 / 5 материалов |
| Ядро месячного плана | 0 / 20 тем |
| Полный адаптированный план после MVP | 0 / 52 материала |
| Поля согласования в шаблоне | 3 / 3 поля |

Защитные метрики:
- 0 реальных публикаций без отдельного подтверждения Яники
- 0 материалов с персональными данными или обещаниями без доказательств
- стоимость генерации должна быть заполнена у 100% материалов перед публикацией

Суброли:
| Суброль | Что делает | Артефакт | KPI |
| --- | --- | --- | --- |
| Content Strategist | рубрика, формат, этап воронки | content_brief | у каждого материала есть формат, воронка и канал |
| Copywriter | черновик в стиле СИЛА Проекта | content_draft | посты не повторяют одну структуру подряд |
| Editor | стиль, доказательства, запреты | editor_check | 0 неподтверждённых обещаний и общих рекламных фраз |
| Visual/Media Brief Creator | ТЗ на визуал, анимацию, видео позже | media_brief | медиа только как ТЗ или dry-run до approval |
| Approval Coordinator | согласование и правки | approval_card | 100% материалов имеют статус, стоимость, причину перегенерации при правках |
| Content Metrics Analyst | связь постов с метриками и лидами позже | content_metric_event | каждый опубликованный материал позже получает content_metric_event |

Скиллы:
- копирайтинг
- SEO-темы
- визуальные промпты
- UTM-логика

### Agent 5 CRM

- Департамент: CRM и аналитика
- Готовность: 80%
- KR-готовность: 81%
- Описание: Создаёт лид в CRM, отправляет уведомление и считает результативность каналов.
- OKR: Довести квалифицированный лид до CRM, уведомления и отчёта по результативности.
- Что доделать: Закрыть один сквозной тест: квалифицированный лид -> Bitrix24 -> Telegram -> отчёт.

Источники по агенту:

- Смысл: Считает всю сквозную аналитику по 17 каналам и принимает CRM-события.
- Основных источников: 17
- Watchlist: 0
- Каналы Яники ждут: 0

- Gmail tenders
- Telegram chats
- Outbound manual
- Avito
- Profi.ru
- Yandex Services
- Yandex Maps
- Referrals
- Old inquiries
- Yandex Direct
- Google Ads
- VK Ads
- Meta Ads
- Telegram Ads
- Dzen and RSY
- Influencer TG
- SEO organic

Backlog-источники:
- visit_count
- visitor_id
- CR visit->deal
- ROMI по контенту

Главная метрика:
- Каналы в сквозной аналитике: 17 / 17 каналов
- Когда закрыта: каждый канал есть в registry, costs, facts и итоговом channel_report

OKR/KR метрики:

| Метрика | Число |
| --- | --- |
| Каналы в сквозной аналитике | 17 / 17 каналов |
| Каналы первой волны отслеживаются | 9 / 9 каналов |
| Сквозной CRM-тест закрыт | 1 / 1 тест |
| CRM-цепочка урока 5 покрыта | 5 / 6 шагов |
| Тестовые Bitrix24-создания | 4 / 3 теста |
| Метрика лектора CR visit->deal | 0 / 1 метрика |

Защитные метрики:
- 0 секретов, webhook и token-значений в отчётах
- 0 реальных клиентских данных в тестовых лидах
- доля лидов без source в реальной работе должна быть не выше 10%

Суброли:
| Суброль | Что делает | Артефакт | KPI |
| --- | --- | --- | --- |
| CRM Router | Bitrix24 payload для лида/сделки | crm_payload_preview | payload создаётся локально до реальной отправки |
| Notifier | уведомление человека | notification_event | уведомления без секретов и лишних персональных данных |
| Attribution Agent | first_touch, last_touch, канал, UTM | attribution_record | 100% тестовых лидов имеют first_touch_channel и last_touch_channel |
| ROMI Reporter | CPL, CAC, profit, ROMI | channel_report | spend -> leads -> deals -> revenue -> profit -> ROMI |
| CRM Hygiene Analyst | дубли, пустые поля, слабые карточки | crm_hygiene_report | дубли и пустые поля попадают в очередь ручной чистки |
| Weekly Digest Owner | недельный итог системы позже | weekly_digest | лиды, CRM, контент, ROMI и блокеры раз в неделю |

Скиллы:
- Bitrix24
- воронка CRM
- сквозная аналитика
- отчёты

### Agent 6 Outreach

- Департамент: Первое касание
- Готовность: 25%
- KR-готовность: 40%
- Описание: Готовит аккуратное первое касание, но не отправляет его без согласования человека.
- OKR: Подготовить безопасный первый контакт по найденному диалогу, но отправлять только после одобрения.
- Что доделать: Сначала сделать approval-flow на черновике без реальной отправки сообщений.

Источники по агенту:

- Смысл: Готовит первое касание по диалогам и ручному outbound, но ничего не отправляет без approval.
- Основных источников: 2
- Watchlist: 0
- Каналы Яники ждут: 0

- Telegram chats
- Outbound manual

Главная метрика:
- Outreach-источники первой волны проверены: 0 / 2 источников
- Когда закрыта: Telegram-чаты и outbound manual прошли ручной кандидат-тест без отправки спама

OKR/KR метрики:

| Метрика | Число |
| --- | --- |
| Outreach-источники первой волны учтены | 2 / 2 источника |
| Кандидаты для ручной проверки | 0 / 10 кандидатов |
| Черновики первых ответов | 0 / 5 ответов |
| Outreach -> CRM тест | 0 / 1 тест |
| Реальные отправки до approval | 0 <= 0 сообщений |

Защитные метрики:
- 0 сообщений без approval
- после разрешения пилотный лимит — не больше 5 отправок в день
- 0 жалоб/спам-сигналов

Суброли:
| Суброль | Что делает | Артефакт | KPI |
| --- | --- | --- | --- |
| Social Listening Monitor | релевантные обсуждения | outreach_candidate | кандидат не создаётся без URL/контекста и причины релевантности |
| Candidate Qualifier | риск спама и релевантность | outreach_decision | спорные кандидаты идут в escalation-to-yana |
| Reply Draft Writer | человеческий ответ | reply_draft | ответ полезный, не спамный, без давления |
| Approval Gatekeeper | запрет отправки без человека | approval_required | 0 реальных отправок без approval |
| Outreach Sender | отправка после approval | sent_outreach_event | после разрешения не больше 5 отправок в день на пилоте |
| Dialog Converter | интерес -> OutreachLead | outreach_lead | заинтересованный ответ уходит в Agent 5 |

Скиллы:
- поиск диалогов
- текст первого касания
- согласование
- продажный диалог


## Event stream

| Время | Событие | Статус | Файл |
| --- | --- | --- | --- |
| 2026-05-16T23:16:40Z | agent_okr_contract_check | OK | data/reports/agent_okr_contract_check.json |
| 2026-05-16T23:16:40Z | agent_dashboard | OK | data/reports/agent_dashboard.json |
| 2026-05-16T22:48:40Z | task-handoff | task-handoff | data/reports/first_inbound_scenario_handoff_to_human.json |
| 2026-05-16T22:43:44Z | first_inbound_scenario_artifact_check | first_inbound_scenario_artifact_check | data/reports/first_inbound_scenario_artifact_check.json |
| 2026-05-16T22:10:22Z | content_funnel_contract_check | нет данных | data/reports/content_funnel_contract_check.json |
| 2026-05-16T22:10:22Z | three_qualified_leads_sprint | нет данных | data/reports/three_qualified_leads_sprint.json |
| 2026-05-16T22:10:04Z | max_b2b_002_public_metrics_attempt | нет данных | data/reports/max_b2b_002_public_metrics_attempt.json |
| 2026-05-16T20:44:49Z | agent4_unified_llm_router_test | agent4_unified_llm_router_test | data/reports/agent4_unified_llm_router_test.json |
| 2026-05-16T14:07:17Z | client_acquisition_pack_dry_run | нет данных | data/reports/client_acquisition_pack_dry_run.json |
| 2026-05-16T13:57:37Z | tender_filter_pack_dry_run | нет данных | data/reports/tender_filter_pack_dry_run.json |

## Dashboard метрик

### agent_health

| Метрика | Значение |
| --- | --- |
| agent_contract_status | OK |
| visual_map_status | OK |
| admin_dashboard_spec_status | OK |
| dashboard_viewer_status | OK |
| agents_count | 6 |

### system_scope

| Метрика | Значение |
| --- | --- |
| total_channels | 17 |
| wave_1_channels | 9 |
| wave_2_channels | 6 |
| wave_3_channels | 2 |
| active_channels | 3 |
| manual_channels | 6 |
| planned_channels | 8 |
| competitor_watchlist_sources | 15 |
| yanika_pending_sources | 5 |
| agent2_collection_channels | 4 |
| agent6_outreach_channels | 2 |
| content_surfaces_target | 7 |
| crm_lesson_5_chain_steps | 6 |

### lead_funnel

| Метрика | Значение |
| --- | --- |
| pipeline_health_test_leads | 1/1 |
| wave_1_source_coverage_target | 1/9 |
| agent2_source_coverage_target | 1/4 |
| monthly_pilot_raw_leads_target | 0/20 |
| bitrix_test_creations | 4 |

### quality

| Метрика | Значение |
| --- | --- |
| score_categories_checked | 1/4 |
| llm_modes_checked | 2/2 |
| max_false_hot_rate_after_real_sample | <=10% |
| qualified_without_source_target | 0 |

### crm_sla

| Метрика | Значение |
| --- | --- |
| lesson_5_crm_chain_covered | 5/6 |
| bitrix24_send_status | OK |
| telegram_send_status | OK |
| missing_crm_layer | personal КП/landing status + visit_count/visitor_id |

### crm_hygiene

| Метрика | Значение |
| --- | --- |
| status | LIMITED_AUDIT |
| contacts | 150 |
| leads_total | 150 |
| leads_active | 0 |
| deals_total | 150 |
| contacts_without_phone_or_email | 37 |
| leads_without_phone_or_email | 24 |
| contact_phone_duplicate_groups | 2 |
| contact_email_duplicate_groups | 2 |
| lead_phone_duplicate_groups | 3 |
| lead_email_duplicate_groups | 4 |
| report_file | data/reports/bitrix_readonly_audit.json |

### vpp_ai_manager

| Метрика | Значение |
| --- | --- |
| status | READY |
| scenario_count | 3 |
| enough_for_kp | 1 |
| need_missing_data | 2 |
| bitrix_dry_run_not_sent | 3 |
| report_file | data/reports/vpp_ai_manager_dry_run.json |

### content

| Метрика | Значение |
| --- | --- |
| content_surfaces_tracked_now | 5/7 |
| first_week_drafts_target | 0/5 |
| monthly_core_topics_target | 0/20 |
| monthly_adapted_items_later | 0/52 |
| approval_fields_in_template | 3/3 |

### outreach

| Метрика | Значение |
| --- | --- |
| wave_1_outreach_sources | 2/2 |
| candidate_review_target | 0/10 |
| reply_drafts_target | 0/5 |
| outreach_to_crm_test | 0/1 |
| real_sends_without_approval | 0 |

### romi

| Метрика | Значение |
| --- | --- |
| status | CSV MVP есть; visit->deal из дашборда лектора ещё не закрыт |
| report_file | data/reports/channel_report_mvp.csv |
| registry_channels | 17/17 |
| cost_rows | 17/17 |
| fact_rows | 17/17 |
| report_rows | 17/17 |
| missing_visit_to_deal | visit_count + visitor_id + CR_visit_to_deal |

### safety

| Метрика | Значение |
| --- | --- |
| security_agent_status | ACTIVE |
| security_agent_file | agents/Агент безопастности/AGENT_SECURITY.md |
| locked_actions | ['scheduler', 'mass_collection', 'real_publish', 'real_outreach'] |
| secrets_visible | false |


## Checker

| Поле | Значение |
| --- | --- |
| script | scripts/check_agent_okr_contract.py |
| report_file | data/reports/agent_okr_contract_check.json |
| agent_contract_status | OK |
| visual_map_status | OK |
| admin_dashboard_spec_status | OK |
| security_agent_status | OK |
| dashboard_viewer_builder_status | FOUND |
| dashboard_viewer_status | OK |
| dashboard_viewer_file | data/reports/agent_dashboard.html |

## Следующий маленький шаг

открыть `data/reports/agent_dashboard.html` и глазами проверить новый блок `Security Agent Control Layer` рядом с управленческими блоками.
