#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://wektorplus-pro.ru"
COMPANY = "ООО «Вектор Плюс-Про»"


GUIDES = [
    {
        "slug": "project-sections",
        "title": "Разделы проектной документации",
        "eyebrow": "ПЗ · ПЗУ · АР · КР · ИОС · ПОС",
        "description": "Что означают основные разделы проектной документации: ПЗ, ПЗУ, АР, КР, ИОС и ПОС. Когда они нужны, что входит в работу и какие исходные данные подготовить.",
        "lead": "Проектная документация нужна не для “красивой папки”, а для понятного и проверяемого маршрута: что проектируем, на каком участке, какими решениями, с какими конструкциями, инженерией и организацией работ.",
        "image": "assets/images/service-project-docs.webp",
        "cards": [
            {
                "code": "ПЗ",
                "name": "Пояснительная записка",
                "when": "Нужна почти в каждом комплекте ПД: фиксирует исходные данные, назначение объекта, технико-экономические показатели и общую логику проектных решений.",
                "inputs": "ТЗ, документы на объект или участок, исходные планы, ГПЗУ/ТУ при наличии, описание цели проекта.",
            },
            {
                "code": "ПЗУ",
                "name": "Схема планировочной организации земельного участка",
                "when": "Используется, когда проект связан с земельным участком: новое строительство, реконструкция, размещение здания, подъезды, благоустройство и инженерные связи.",
                "inputs": "ГПЗУ, топосъёмка, границы участка, сведения о существующих зданиях, подъездах и сетях.",
            },
            {
                "code": "АР",
                "name": "Архитектурные решения",
                "when": "Показывает планировки, фасады, разрезы, внешний облик, функциональные зоны и решения, которые заказчик и смежники должны одинаково понимать.",
                "inputs": "Обмеры, планы, задача заказчика, требования к функции, визуалу, доступности и эксплуатации.",
            },
            {
                "code": "КР",
                "name": "Конструктивные и объёмно-планировочные решения",
                "when": "Нужен, когда важно подтвердить конструктивную схему: фундаменты, несущие элементы, перекрытия, нагрузки, усиления или реконструкцию.",
                "inputs": "АР, данные обследования, геология при наличии, нагрузки, сведения о существующих конструкциях.",
            },
            {
                "code": "ИОС",
                "name": "Инженерное оборудование и сети",
                "when": "Объединяет инженерные решения: отопление, вентиляцию, водоснабжение, электроснабжение, связь и другие системы по задаче объекта.",
                "inputs": "Технические условия, требования эксплуатации, планировки, нагрузки, данные о подключениях и существующих сетях.",
            },
            {
                "code": "ПОС",
                "name": "Проект организации строительства",
                "when": "Нужен для понимания, как организовать работы: этапность, стройплощадка, временные решения, безопасность и логистика строительства.",
                "inputs": "Площадка, ограничения объекта, сроки, доступы, данные по существующей застройке, инженерии и технологии работ.",
            },
        ],
    },
    {
        "slug": "engineering-standards",
        "title": "Инженерные и обязательные разделы",
        "eyebrow": "ОВ · ВК · ЭОМ · СС · ПБ · ООС · ОДИ · СМ",
        "description": "Что означают инженерные и специальные разделы проектной документации: отопление и вентиляция, водоснабжение, электрика, связь, пожарная безопасность, экология, доступность и сметы.",
        "lead": "Инженерные и специальные разделы отвечают за то, чтобы объект был не только нарисован, но и работал: тепло, воздух, вода, электричество, связь, безопасность, доступность и понятная стоимость.",
        "image": "assets/images/service-commercial.webp",
        "cards": [
            {
                "code": "ОВ",
                "name": "Отопление, вентиляция и кондиционирование",
                "when": "Нужно для помещений, где важны температура, воздухообмен, комфорт, технологические требования или санитарные нормы.",
                "inputs": "Планы помещений, назначение зон, теплопотери/теплопритоки, оборудование, требования эксплуатации.",
            },
            {
                "code": "ВК",
                "name": "Водоснабжение и канализация",
                "when": "Применяется для объектов с мокрыми зонами, санузлами, технологической водой, подключениями к сетям или локальными системами.",
                "inputs": "Планы, точки водоразбора, ТУ, требования к оборудованию, существующие выпуски и стояки.",
            },
            {
                "code": "ЭОМ",
                "name": "Электрооборудование и освещение",
                "when": "Нужно для распределения электрических нагрузок, освещения, щитов, кабельных трасс и питания оборудования.",
                "inputs": "Мощности оборудования, планировки, требования к освещению, ТУ, категории надёжности.",
            },
            {
                "code": "СС",
                "name": "Сети связи и слаботочные системы",
                "when": "Нужны для связи, интернета, видеонаблюдения, диспетчеризации и систем, которые работают на слаботочных линиях.",
                "inputs": "Планы, требования заказчика, точки подключения, сценарии эксплуатации и безопасности.",
            },
            {
                "code": "ПБ",
                "name": "Пожарная безопасность",
                "when": "Применяется, когда нужно показать меры безопасности: эвакуация, противопожарные решения, ограничения материалов и инженерии.",
                "inputs": "Планы, назначение помещений, количество людей, конструктив, инженерные решения и требования процедуры.",
            },
            {
                "code": "ООС",
                "name": "Охрана окружающей среды",
                "when": "Нужна для оценки влияния объекта и работ на окружающую среду, особенно при строительстве, реконструкции и производственных задачах.",
                "inputs": "Данные об участке, технологии, отходах, источниках воздействия, инженерных решениях.",
            },
            {
                "code": "ОДИ",
                "name": "Доступность для маломобильных групп",
                "when": "Используется для общественных, коммерческих и других объектов, где нужно обеспечить доступность входов, путей движения и санитарных зон.",
                "inputs": "Планировки, входные группы, перепады высот, сценарии движения посетителей и персонала.",
            },
            {
                "code": "СМ",
                "name": "Сметная документация",
                "when": "Помогает понять расчётную стоимость работ и материалов по проектным решениям, если смета входит в задачу.",
                "inputs": "Состав работ, спецификации, ведомости объёмов, требования заказчика или бюджетной процедуры.",
            },
        ],
    },
    {
        "slug": "working-sets",
        "title": "Рабочие комплекты для строительства",
        "eyebrow": "АР · КЖ · КМ · КМД · ТХ · спецификации",
        "description": "Что входит в рабочие комплекты: рабочая архитектура, железобетонные и металлические конструкции, деталировка, технология, спецификации и ведомости.",
        "lead": "Рабочая документация нужна строителям и подрядчикам: она переводит проектные решения в чертежи, узлы, спецификации и понятную последовательность производства работ.",
        "image": "assets/images/service-working-docs.webp",
        "cards": [
            {
                "code": "АР",
                "name": "Рабочие архитектурные решения",
                "when": "Нужны для уточнения планировок, проёмов, разрезов, фасадов, ведомостей отделки и архитектурных узлов.",
                "inputs": "Утверждённые планировки, обмеры, требования к материалам, отделке и эксплуатации.",
            },
            {
                "code": "КЖ",
                "name": "Железобетонные конструкции",
                "when": "Применяются для фундаментов, плит, колонн, балок, стен, лестниц, монолитных и сборных железобетонных элементов.",
                "inputs": "Конструктивная схема, нагрузки, геология, архитектура, данные обследования для существующего здания.",
            },
            {
                "code": "КМ",
                "name": "Металлические конструкции",
                "when": "Нужны для каркасов, ферм, балок, колонн, лестниц, площадок, усилений и других металлических элементов.",
                "inputs": "Нагрузки, пролёты, геометрия, узлы примыкания, требования к производству и монтажу.",
            },
            {
                "code": "КМД",
                "name": "Деталировочные чертежи металлоконструкций",
                "when": "Используются на производстве металлоконструкций: показывают детали, марки, отверстия, сварку, болты и сборочные элементы.",
                "inputs": "Раздел КМ, требования завода, материалы, соединения, технология изготовления и монтажа.",
            },
            {
                "code": "ТХ",
                "name": "Технологические решения",
                "when": "Нужны для объектов, где важен процесс: производство, кухня, склад, оборудование, потоки людей или материалов.",
                "inputs": "Описание технологии, оборудование, потоки, требования санитарии, безопасности и эксплуатации.",
            },
            {
                "code": "СП",
                "name": "Спецификации и ведомости",
                "when": "Помогают закупать материалы и контролировать объёмы: что, сколько, где применяется и к какому комплекту относится.",
                "inputs": "Рабочие чертежи, выбранные материалы, узлы, оборудование и требования подрядчика.",
            },
        ],
    },
]


def e(value: str) -> str:
    return html.escape(value, quote=True)


def rel(path: str, depth: int) -> str:
    return "../" * depth + path


def guide_json_ld(guide: dict[str, object]) -> str:
    url = f"{BASE_URL}/sections/{guide['slug']}/"
    data = [
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "name": guide["title"],
            "description": guide["description"],
            "url": url,
            "about": guide["cards"][0]["name"],
            "publisher": {"@id": f"{BASE_URL}/#org"},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": guide["title"], "item": url},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "@id": f"{BASE_URL}/#org",
            "name": COMPANY,
            "url": BASE_URL,
            "telephone": "+7 938 509-13-77",
            "email": "office@wektorplus-pro.ru",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Таманская улица, 180, офис 410",
                "addressLocality": "Краснодар",
                "addressRegion": "Краснодарский край",
                "addressCountry": "RU",
            },
            "identifier": [
                {"@type": "PropertyValue", "propertyID": "ИНН", "value": "0100005517"},
                {"@type": "PropertyValue", "propertyID": "ОГРН", "value": "1230100001812"},
                {"@type": "PropertyValue", "propertyID": "СРО", "value": "СРО-П-166-30062011"},
            ],
        },
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_cards(cards: list[dict[str, str]]) -> str:
    chunks = []
    for card in cards:
        chunks.append(
            f"""
        <article class="section-guide-card">
          <div class="section-guide-code">{e(card['code'])}</div>
          <div>
            <h2>{e(card['name'])}</h2>
            <dl>
              <div><dt>Когда нужно</dt><dd>{e(card['when'])}</dd></div>
              <div><dt>Что подготовить</dt><dd>{e(card['inputs'])}</dd></div>
            </dl>
          </div>
        </article>"""
        )
    return "\n".join(chunks)


def render_guide_page(guide: dict[str, object]) -> str:
    depth = 2
    canonical = f"{BASE_URL}/sections/{guide['slug']}/"
    title = f"{guide['title']} · Вектор Плюс-Про"
    logo = rel("assets/brand/vpp-logo-mark.png", depth)
    styles = rel("styles.css", depth)
    home = rel("index.html", depth)
    image = rel(str(guide["image"]), depth)
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{e(title)}</title>
<meta name="description" content="{e(str(guide['description']))}" />
<meta name="robots" content="index, follow" />
<meta name="theme-color" content="#f5efde" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(str(guide['description']))}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{BASE_URL}/{guide['image']}" />
<meta property="og:locale" content="ru_RU" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Onest:wght@400;500;600&family=Unbounded:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap&subset=cyrillic,cyrillic-ext,latin" rel="stylesheet" />
<link rel="icon" type="image/png" href="{logo}" />
<link rel="apple-touch-icon" href="{logo}" />
<link rel="preload" as="image" href="{image}" type="image/webp" />
<link rel="stylesheet" href="{styles}" />
<script type="application/ld+json">
{guide_json_ld(guide)}
</script>
</head>
<body class="static-page">
<a class="skip-link" href="#main-content">Перейти к содержанию</a>
<div class="body-fx" aria-hidden="true"><div class="grid"></div><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>
<header class="static-nav">
  <div class="container static-nav-inner">
    <a class="nav-logo" href="{home}" aria-label="Вектор Плюс-Про — на главную">
      <img class="nav-logo-img" src="{logo}" width="500" height="500" alt="" aria-hidden="true" decoding="async" />
      <span class="nav-logo-text"><span class="sr-only">Вектор Плюс-Про</span>Проектная организация<small>ООО «Вектор Плюс-Про»</small></span>
    </a>
    <nav class="static-nav-links" aria-label="Разделы сайта">
      <a href="{home}#services">Услуги</a>
      <a href="{home}#trust">Доверие</a>
      <a href="{home}#cases">Кейсы</a>
      <a href="{home}#contacts">Контакты</a>
    </nav>
    <a class="btn btn-primary nav-contact-btn" href="{home}#contacts"><span class="btn-stack"><span>Обсудить объект</span><small>+7 938 509-13-77</small></span></a>
  </div>
</header>
<main id="main-content">
  <section class="section section-guide-hero">
    <div class="container section-guide-hero-grid">
      <div>
        <a class="static-back" href="{home}#top">← На главную</a>
        <span class="section-eyebrow">{e(str(guide['eyebrow']))}</span>
        <h1>{e(str(guide['title']))}</h1>
        <p class="section-lead">{e(str(guide['lead']))}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{home}#contacts">Обсудить объект</a>
          <a class="btn btn-secondary" href="tel:+79385091377">Позвонить</a>
        </div>
      </div>
      <div class="section-guide-visual" style="background-image:url('{image}')">
        <span>Состав конкретного комплекта зависит от объекта, стадии, исходных данных и требований процедуры.</span>
      </div>
    </div>
  </section>
  <section class="section section-guide-content">
    <div class="container">
      <div class="section-head wide">
        <span class="section-eyebrow">Простым языком</span>
        <h2 class="section-title">Что означает каждый раздел и зачем он заказчику</h2>
        <p class="section-lead">Ниже — не юридическая энциклопедия, а рабочая подсказка: когда раздел появляется в проекте и какие данные лучше подготовить заранее.</p>
      </div>
      <div class="section-guide-grid">
        {render_cards(guide['cards'])}
      </div>
      <div class="section-guide-note">
        <h2>Важное правило</h2>
        <p>Мы не обещаем состав документации “на глаз”. Сначала смотрим объект, цель, исходные документы и ограничения, затем называем нужные разделы и безопасный следующий шаг.</p>
      </div>
    </div>
  </section>
</main>
<footer class="static-footer">
  <div class="container">
    <a href="{home}">Вектор Плюс-Про</a>
    <span>Телефон: +7 938 509-13-77 · Email: office@wektorplus-pro.ru</span>
  </div>
</footer>
</body>
</html>
"""


def main() -> None:
    sections_dir = ROOT / "sections"
    for guide in GUIDES:
        target_dir = sections_dir / guide["slug"]
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "index.html").write_text(render_guide_page(guide), encoding="utf-8")
    print(f"generated {len(GUIDES)} section guide pages")


if __name__ == "__main__":
    main()
