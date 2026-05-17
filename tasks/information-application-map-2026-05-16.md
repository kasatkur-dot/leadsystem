# Карта применения накопленной информации

Дата: 2026-05-16

Статус: рабочая карта. Код, Bitrix24, MAX, Telegram, Redis, scheduler, LLM, deploy, публикации и платные сервисы не запускались.

## Главный вывод

В проекте уже есть не просто разрозненные документы, а почти полный контур:

```text
сайт
-> контентная воронка
-> входящее обращение
-> AI-менеджер первого касания
-> Agent 3 квалификация
-> Agent 5 сделка Bitrix24
-> dashboard / CRM hygiene / ROMI
```

Сейчас важнее не добавлять новые идеи, а собрать имеющиеся материалы в одну рабочую цепочку MVP.

## Что уже есть и как применить

| Блок информации | Где лежит | Как применить сейчас |
|---|---|---|
| Сайт и публичная упаковка | `site/`, `docs/current-site-improvement-tz.md`, `tasks/site-finalization-checklist-2026-05-15.md` | Довести до preview после подтверждения домена. Сайт остается без формы, ведет в телефон, email, MAX, Telegram, карты. |
| Маршрутизация сайта в Bitrix24 | `docs/site-bitrix24-channel-routing-table.md`, `docs/site-bitrix24-no-form-handoff.md` | Использовать сделки, а не лиды. Хранить сайтовый источник в `UF_CRM_VPP_SITE_SRC` и комментарии. |
| AI-менеджер | `docs/ai-deal-manager-responsibility.md`, `docs/intake-assistant-scenario.md` | Сделать dry-run сценарий первого ответа и карточки входа. Первые 10-20 диалогов только с ручным подтверждением. |
| Bitrix24 структура | `docs/site-bitrix24-channel-routing-table.md`, `data/reports/agent5_bitrix_deal_test.json`, `data/reports/bitrix_deal_custom_fields_sync.json` | Уже доказано создание тестовой сделки. Следующий шаг — использовать тот же payload для dry-run входящего обращения, не на реальном клиенте. |
| CRM hygiene | `data/reports/bitrix_readonly_audit.json`, `data/reports/agent_dashboard.*` | Dashboard показывает качество базы. Нужно обновить полный аудит без `--limit-pages`, затем чистить дубли по очереди. |
| Контентная воронка | `content/pipeline/post-funnel-operating-system.md`, `publication-tracker-mvp.csv`, `topic-response-tracker-mvp.csv` | Публиковать не хаотично, а по цепочке. `lead-post-001` уже approved и готов к MAX dry-run / ручной публикации после заполнения MAX `.env`. |
| Автопубликация | `docs/content-autopublishing-automation-plan.md`, `scripts/dry_run_agent4_max_approved_publication.py` | Пока только approved-only dry-run. Реальная публикация заблокирована, пока `MAX_BOT_TOKEN` и `MAX_CHAT_ID` пустые. |
| MAS-референс | `research/external-mas-ip-analysis-2026-05-15.md`, `docs/admin-dashboard-spec.md`, `data/reports/agent_dashboard.*` | Использовать принципы: Agent Inspector, Scenario Timeline, Artifact Tracker, Status/Queue/Last error. Не создавать новых агентов. |
| Источники и ROMI | `research/traffic-and-first-touch-map.md`, `research/cross-channel-analytics-romi.md`, `content/library/sources/channel-registry-mvp.csv` | Все обращения помечать источником. Для первых каналов считать вручную: источник -> сделка -> выручка. |
| B2B growth-план | `docs/b2b-commercial-growth-sprint-plan.md` | Использовать как адаптацию Operating Center под коммерцию, юрлиц, отдельные лендинги, КП за 24 часа при полных данных и Bitrix-сделки. |
| Будущие инструменты | `content/pipeline/future-opportunities-backlog.md`, `research/github-building-blocks.md` | Держать как backlog. Postiz/TryPost/Dittofeed/OpenPanel не внедрять до ручного MVP и первых данных. |

## Что важно прямо сейчас

### 1. Закрыть один рабочий путь от контента к сделке

Самая полезная цепочка:

```text
lead-post-001
-> MAX
-> человек пишет вопрос / присылает план
-> AI-менеджер собирает факты
-> Agent 5 создает сделку Bitrix24
-> dashboard фиксирует источник и результат
```

Почему это важно: это доказывает не отдельный сайт, не отдельный пост и не отдельную CRM, а всю систему как механизм получения заявок.

### 2. Не запускать полную автоматизацию до ручной проверки

Сейчас нельзя включать:

- автопубликацию по расписанию;
- самостоятельные ответы AI клиентам;
- массовый сбор лидов;
- автоматическое объединение дублей CRM;
- paid traffic;
- новую внешнюю платформу публикаций.

### 3. Dashboard использовать как пульт, а не просто отчет

В `data/reports/agent_dashboard.html` уже должны сходиться:

- агентная карта;
- источники;
- Bitrix CRM hygiene;
- MAS reference layer;
- content funnel status;
- locks.

Если следующий шаг не виден в dashboard, значит процесс еще не управляем.

## Что не хватает

| Чего не хватает | Почему важно | Что сделать |
|---|---|---|
| Полный актуальный Bitrix audit | Текущий JSON может быть ограниченным срезом | Запустить `scripts/audit_bitrix_readonly.py` без `--limit-pages` и пересобрать dashboard. |
| Детальная очередь дублей | Нужна ручная чистка по ID с доказательствами | Запустить `scripts/bitrix_duplicate_review_readonly.py`. |
| MAX реальные переменные | Без них нельзя тестировать реальную публикацию | Заполнить `MAX_BOT_TOKEN` и `MAX_CHAT_ID` локально в `.env`, затем проверить только `SET/EMPTY`. |
| Тестовые диалоги AI-менеджера | Без них нельзя давать AI отвечать клиентам | Создать 10-15 синтетических диалогов: перепланировка, ПД/РД, реконструкция, цена, срочно, документы. |
| Первый inbound dry-run | Нужен мост между сообщением клиента и сделкой | Сделать локальный сценарий: текст обращения -> intake card -> deal payload dry-run. |
| Фактические метрики публикаций | Без них нет ROMI | После ручной публикации заполнить views/reactions/questions/lead_count/deal_count. |
| B2B offer and landing matrix | Нужна связка сегмент -> оффер -> лендинг -> Bitrix -> AI-ответ | Подготовить матрицу по складам/ангарам, ритейлу/fit-out, реконструкции и коммерческим перепланировкам. |

## Очередь действий

1. Обновить полный Bitrix audit и duplicate review.
2. Пересобрать dashboard, чтобы статус CRM был не `LIMITED_AUDIT`.
3. Заполнить MAX `.env` и повторить безопасную проверку `SET/EMPTY`.
4. Опубликовать `lead-post-001` вручную или через отдельный approved-only real test после подтверждения.
5. Подготовить `first_inbound_ai_manager_dry_run`: входящее сообщение -> карточка -> payload сделки.
6. Составить 10 тестовых диалогов AI-менеджера.
7. После первых реальных обращений заполнить `publication-tracker-mvp.csv` и `topic-response-tracker-mvp.csv`.
8. Подготовить B2B offer and landing matrix по `docs/b2b-commercial-growth-sprint-plan.md`.

## Что применять позже

| Идея | Когда вернуться |
|---|---|
| Postiz / TryPost | После 10-20 ручных публикаций и стабильного tracker. |
| Dittofeed | Когда появятся повторные касания, сегменты и база контактов для journeys. |
| OpenPanel | Когда сайт будет опубликован и нужен privacy-friendly web analytics. |
| Keeper.sh / deep research | Для крупных B2B-сделок и проверки контрагентов. |
| Полный AI operator chat в dashboard | После dry-run AI-менеджера и первых проверенных диалогов. |
| Agent 6 social outreach | Только после approval-flow и лимитов, без массовых отправок. |

## Рекомендованный следующий маленький шаг

Сделать `first_inbound_ai_manager_dry_run`:

```text
входящий текст от клиента
-> AI/intake правила без внешнего LLM
-> карточка входа
-> Agent 5 deal payload dry-run
-> локальный отчет
```

Это даст мост между сайтом, контентом, AI-менеджером и Bitrix24 без риска для реальных клиентов.
