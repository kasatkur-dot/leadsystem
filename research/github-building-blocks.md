# GitHub — строительные блоки системы

Версия: 1.0
Дата: 2026-04-26
Статус: исследование завершено

---

## Главный вывод

**Готового комплексного решения под нашу задачу нет.**
Причины: русскоязычные платформы (Avito, VK, Profi.ru, ЯУ), Bitrix24, двухпоточная архитектура,
система одобрения ответов, поведение под человека — в комбинации не встречается нигде.

Но под каждый агент есть хорошие строительные блоки.

---

## Карта: репозиторий → наш агент

### Агент 2: Коллектор лидов

| Репозиторий | Что берём | Ссылка |
|---|---|---|
| **Duff89/parser_avito** | Парсер Avito: мониторинг новых объявлений, уведомления в TG, фильтрация по ключам, прокси-поддержка | https://github.com/Duff89/parser_avito |
| **blohinn/telegram-avito-bot** | Avito → Telegram бот, лёгкий, рабочий | https://github.com/blohinn/telegram-avito-bot |
| **unnohwn/telegram-scraper** | Telethon-скрапер Telegram: real-time, медиа, экспорт | https://github.com/unnohwn/telegram-scraper |
| **ergoncugler/web-scraping-telegram** | Скрапинг TG: текст, реакции, ответы, комментарии, группы | https://github.com/ergoncugler/web-scraping-telegram |
| **bellingcat/vk-url-scraper** | VK URL scraper — Python API + CLI | https://github.com/bellingcat/vk-url-scraper |
| **DaliaO15/VK-post-scraper** | Полный пайплайн скрапинга VK постов | https://github.com/DaliaO15/VK-post-scraper |

### Агент 3: Процессор (скоринг и квалификация)

| Репозиторий | Что берём | Ссылка |
|---|---|---|
| **brightdata/ai-lead-generator** | AI-скоринг лидов через OpenAI → заменяем на Claude API, архитектура квалификации | https://github.com/brightdata/ai-lead-generator |
| **kaymen99/sales-outreach-automation-langgraph** | Пайплайн: исследование лида → квалификация → персонализированный оффер → CRM | https://github.com/kaymen99/sales-outreach-automation-langgraph |
| **IsaacBell/leads-db** | B2B система лидогенерации с БД и скорингом | https://github.com/IsaacBell/leads-db |

### Агент 6: Социальный аутрич (мониторинг + ответы)

| Репозиторий | Что берём | Ссылка |
|---|---|---|
| **SoCloseSociety/MiloAgent** | ⭐ Ближайший аналог всей системы аутрича. Берём: архитектуру самообучения, A/B тест текстов, стратегический скоринг, multi-account management | https://github.com/SoCloseSociety/MiloAgent |
| **security-hab/telegram-keyword-monitor** | Telethon: мониторинг ключевых слов в TG-каналах, пересылка релевантных сообщений | https://github.com/security-hab/telegram-keyword-monitor |
| **afolivieri/streaming_overseer** | Мониторинг TG-каналов по ключам в реалтайм | https://github.com/afolivieri/streaming_overseer |
| **paulpierre/informer** | ⭐ Инфраструктура: user accounts (не bot), 500+ каналов, обработка rate limiting / FloodWait | https://github.com/paulpierre/informer |
| **SokinjoNS/tg-message-listener-main** | Telethon message listener + routing по handlers | https://github.com/SokinjoNS/tg-message-listener-main |
| **filip-michalsky/SalesGPT** | ⭐ Движок продающего диалога: стадии разговора, база знаний, работа с возражениями → используем когда человек ответил | https://github.com/filip-michalsky/SalesGPT |

### Агент 6: Hunter (проактивный поиск)

| Репозиторий | Что берём | Ссылка |
|---|---|---|
| **Madi-S/Lead-Generation** | Python lead generation техники для поиска по множеству источников | https://github.com/Madi-S/Lead-Generation |
| **toofast1/awesome-ai-lead-generation** | Кюрированный список AI-инструментов для social listening и аутрича | https://github.com/toofast1/awesome-ai-lead-generation |

### Оркестратор

| Репозиторий | Что берём | Ссылка |
|---|---|---|
| **beredfb/multi-agent-orchestrator-v2** | Паттерн оркестрации, фоллбэк при сбое агентов, multi-agent chains | https://github.com/beredfb/multi-agent-orchestrator-v2 |
| **hoangsonww/AI-Agents-Orchestrator** | Координация нескольких AI-агентов, REPL + UI дашборд | https://github.com/hoangsonww/AI-Agents-Orchestrator |

---

## Ключевая статья

**"Autonomous Lead Generation & Outreach — Top 30 Open-Source Projects"**
https://huggingface.co/blog/samihalawa/automating-lead-generation-with-ai

Обзор 30 лучших open-source проектов по автоматической лидогенерации и аутричу.
Разобраны: скрапинг, квалификация, персонализированный аутрич, CRM-интеграции.
Обязательно прочитать перед началом разработки Агента 6.

---

## Что НЕ найдено на GitHub (придётся писать своё)

| Компонент | Статус |
|---|---|
| Profi.ru парсер | Не найдено — пишем своё |
| Яндекс Услуги парсер | Не найдено — пишем своё |
| Bitrix24 + lead pipeline | Bitrix24 API есть официально, интеграции — пишем своё |
| Система одобрения ответов (✅/✏️/❌) | Не найдено — пишем своё |
| Двухпоточная архитектура (перепланировки + проектирование) | Не найдено — уникально |
| Поведение под человека (тайминги, прогрев, рандомизация) | Частично в MiloAgent |
| Тендерный email-парсинг на русском | Не найдено — используем свой tender_scraper.py |

---

## Дополнение 2026-04-28 — HH_searcher

**Проект:** HH_searcher (локальный, не публичный на GitHub — скриншот от другого разработчика)

**Что делает:** Playwright + авторизованная сессия HH.ru → LLM скоринг вакансий → генерация сопроводительных писем → автоотклик

**Стек:** Python 3.11 + Playwright + OpenAI API + FastAPI + SQLite + JSONL логи

**Что берём в нашу систему:**

| Что берём | Куда применяем |
|---|---|
| Авторизация HH через Playwright + сохранённая сессия | `agent2_collector/hh_collector/` — читаем вакансии как сигнал |
| LLM скоринг вакансий по релевантности | `agent3_processor/scorer/` — усиливаем промпты скоринга |
| Генерация персонализированных писем через LLM | `agent6_outreach/cold_email/` — письма застройщикам |
| JSONL формат логов прогонов | Все агенты — структура лог-файлов |

**Что НЕ берём:** Web-admin (у нас TG), SQLite (у нас PostgreSQL), логика откликов на вакансии (нам не нужно).

---

## Приоритет изучения (в каком порядке читать код)

1. **MiloAgent** — понять общую архитектуру AI growth agent
2. **paulpierre/informer** — понять как правильно работать с Telethon без банов
3. **SalesGPT** — понять как строить диалог со стадиями продажи
4. **Duff89/parser_avito** — взять как основу парсера Avito
5. **kaymen99/sales-outreach-automation-langgraph** — понять пайплайн квалификации
6. Статья HuggingFace Top-30 — обзор экосистемы
