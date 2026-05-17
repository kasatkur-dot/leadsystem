#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://wektorplus-pro.ru"
COMPANY = "ООО «Вектор Плюс-Про»"


SERVICES = [
    {
        "slug": "pd",
        "title": "Проектная документация",
        "short": "ПД для экспертизы, разрешения на строительство, реконструкции и капитального ремонта.",
        "description": "Проектная документация для коммерческих, общественных, производственных и частных объектов. Подбираем состав разделов под задачу, исходные данные и требования процедуры.",
        "image": "assets/images/service-project-docs.webp",
        "eyebrow": "ПД · экспертиза · разрешение",
        "lead": "Проектная документация нужна, когда заказчику важно не просто получить чертежи, а пройти понятный путь: исходные данные, состав разделов, проектные решения, проверка и следующий юридически безопасный шаг.",
        "when": [
            "планируется строительство, реконструкция или капитальный ремонт объекта",
            "нужен комплект для экспертизы или разрешительной процедуры",
            "требуется связать архитектуру, конструктив и инженерные ограничения",
            "заказчику нужно понять состав разделов до старта бюджета и сроков",
        ],
        "included": [
            "анализ исходных данных и ограничений объекта",
            "подбор состава проектной документации под задачу",
            "архитектурные и конструктивные решения в согласованном объеме",
            "увязка разделов и подготовка материалов для следующей стадии",
        ],
        "inputs": [
            "правоустанавливающие или исходные документы по объекту",
            "ГПЗУ, ТУ, обмеры, обследования или архивные материалы, если они есть",
            "описание цели: строительство, реконструкция, капремонт, изменение назначения",
            "требования заказчика, смежников и согласующих процедур",
        ],
        "result": [
            "понятный состав проектных материалов",
            "комплект ПД по согласованным разделам",
            "перечень недостающих исходных данных, если без них нельзя двигаться дальше",
            "рекомендации по следующему шагу: экспертиза, РД, уточнение исходных или подача",
        ],
        "limits": "Мы не обещаем прохождение экспертизы или согласование до проверки объекта, исходных данных и требований процедуры. Итог зависит от состава документов, состояния объекта и решений уполномоченных органов.",
        "related": ["rd", "kr-kzh-km", "rekonstruktsiya"],
    },
    {
        "slug": "rd",
        "title": "Рабочая документация",
        "short": "РД: рабочие чертежи, узлы и спецификации для производства работ.",
        "description": "Рабочая документация для строительства, реконструкции, капитального ремонта и коммерческих помещений. Делаем чертежи, которые можно использовать на площадке.",
        "image": "assets/images/service-working-docs.webp",
        "eyebrow": "РД · чертежи · спецификации",
        "lead": "Рабочая документация переводит проектные решения в понятный комплект для строителей: размеры, узлы, спецификации, конструктивные решения и привязки. Это снижает риск спорных трактовок на площадке.",
        "when": [
            "есть ПД или концепция, но нужны рабочие чертежи для строительства",
            "строителям нужны узлы, спецификации и точные решения",
            "надо доработать чужую документацию по согласованному объему",
            "важно заранее увидеть противоречия между архитектурой, конструктивом и инженерией",
        ],
        "included": [
            "рабочие чертежи по согласованным разделам",
            "узлы, схемы, спецификации и ведомости",
            "проверка стыков между архитектурой, конструктивом и смежными решениями",
            "ответы на замечания в рамках согласованного состава работ",
        ],
        "inputs": [
            "утвержденные проектные решения или техническое задание",
            "обмеры, исходные планы, данные обследований",
            "требования подрядчика, техзаказчика или эксплуатации",
            "ограничения по материалам, срокам, поставщикам и технологии работ",
        ],
        "result": [
            "рабочий комплект чертежей",
            "узлы и спецификации для закупки и производства работ",
            "понятные границы ответственности по разделам",
            "перечень вопросов, которые нужно решить до выхода на площадку",
        ],
        "limits": "РД не заменяет экспертизу, обследование или согласование, если они нужны по объекту. Сначала проверяем исходные данные и состав работ, затем называем корректный объем.",
        "related": ["pd", "kr-kzh-km", "objects"],
    },
    {
        "slug": "kr-kzh-km",
        "title": "КР, КЖ, КМ — конструктивные разделы",
        "short": "Конструктивные решения, железобетонные и металлические конструкции.",
        "description": "Разделы КР, КЖ и КМ для зданий, реконструкций, усилений, металлокаркасов, фундаментов и рабочих решений.",
        "image": "assets/images/service-architecture-structure.webp",
        "eyebrow": "КР · КЖ · КМ",
        "lead": "Конструктив — это основа безопасности и реализуемости объекта. Важно не просто нарисовать схему, а проверить нагрузки, геометрию, существующие конструкции и связь с архитектурой.",
        "when": [
            "нужен раздел КР для проектной или рабочей документации",
            "проектируются железобетонные конструкции: фундаменты, плиты, колонны, балки",
            "нужны металлические конструкции: каркас, фермы, балки, колонны, узлы",
            "существующее здание требует проверки, усиления или реконструкции",
        ],
        "included": [
            "анализ исходных данных по конструкциям и нагрузкам",
            "конструктивные решения по согласованному составу",
            "узлы, схемы, спецификации и привязки к архитектуре",
            "увязка КР, КЖ, КМ со смежными разделами",
        ],
        "inputs": [
            "архитектурные планы, разрезы, фасады или концепция",
            "данные обследования, геология, нагрузки и требования эксплуатации",
            "информация о существующих конструкциях, если объект реконструируется",
            "требования к материалам, технологии и производству работ",
        ],
        "result": [
            "комплект конструктивных решений",
            "разделы КР, КЖ или КМ в согласованном объеме",
            "узлы и спецификации для следующей стадии",
            "список рисков и вопросов, которые нельзя закрыть без дополнительных данных",
        ],
        "limits": "Мы не выделяем КЖ и КМ в громкие обещания без проверки задачи. Состав разделов зависит от объекта, нагрузок, исходных данных и стадии проектирования.",
        "related": ["pd", "rd", "rekonstruktsiya"],
    },
    {
        "slug": "pereplanirovki",
        "title": "Проектирование перепланировок",
        "short": "Проектные материалы для квартир и нежилых помещений: БТИ, банк, ипотека, подача.",
        "description": "Проектирование перепланировок квартир и нежилых помещений. Проверяем исходные документы, техническую возможность и ограничения до обещаний по результату.",
        "image": "assets/images/service-replanning.webp",
        "eyebrow": "перепланировка · БТИ · банк",
        "lead": "Перепланировка кажется бытовой задачей, но ошибка в документах может остановить ремонт, сделку, ипотеку или подачу. Поэтому сначала проверяем исходные данные и ограничения, а потом называем безопасный маршрут.",
        "when": [
            "планируется изменение планировки квартиры или нежилого помещения",
            "банк, покупатель или продавец просит документы по перепланировке",
            "нужно понять, можно ли переносить зоны, проемы или инженерные элементы",
            "требуется пакет материалов для подачи в уполномоченный орган",
        ],
        "included": [
            "проверка БТИ, исходных планов и цели перепланировки",
            "анализ технической возможности в рамках предоставленных данных",
            "проектные материалы по согласованному составу",
            "объяснение следующего шага: что можно подавать, что нужно уточнить",
        ],
        "inputs": [
            "план БТИ или технический паспорт",
            "правоустанавливающие документы или данные по объекту",
            "эскиз желаемой перепланировки или описание изменений",
            "условия банка, сделки, аренды или будущего использования помещения",
        ],
        "result": [
            "понятная оценка рисков до начала ремонта или сделки",
            "проектные материалы по перепланировке",
            "перечень документов, которых не хватает для безопасной подачи",
            "маршрут дальнейших действий без обещания результата заранее",
        ],
        "limits": "Итоговое решение по согласованию принимает уполномоченный орган. Мы не обещаем результат до проверки объекта, документов и требований конкретной процедуры.",
        "related": ["pd", "rd", "objects"],
    },
    {
        "slug": "rekonstruktsiya",
        "title": "Проектирование реконструкций",
        "short": "Реконструкция, капитальный ремонт, усиления и работа с существующими зданиями.",
        "description": "Проектные решения для реконструкции и капитального ремонта зданий: исходные данные, конструктив, усиления, рабочая документация и сопровождение следующего шага.",
        "image": "assets/images/service-reconstruction.webp",
        "eyebrow": "реконструкция · капремонт · усиление",
        "lead": "Реконструкция сложнее нового строительства: объект уже существует, у него есть история, ограничения, конструкции и инженерные связи. Поэтому работа начинается с проверки фактического состояния и исходных документов.",
        "when": [
            "здание меняет функцию, нагрузку, планировку или конструктивную схему",
            "нужен капитальный ремонт с проектными решениями",
            "требуются усиления, обследование исходных данных или рабочие узлы",
            "заказчику нужно пройти следующий этап без хаоса в документации",
        ],
        "included": [
            "анализ исходных данных и существующего состояния",
            "проектные решения по реконструкции или капитальному ремонту",
            "конструктивные решения, усиления и узлы в согласованном объеме",
            "увязка с архитектурой, эксплуатацией и ограничениями объекта",
        ],
        "inputs": [
            "архивные планы, обмеры, обследования и фотофиксация",
            "описание текущего состояния и цели реконструкции",
            "данные по нагрузкам, инженерии, эксплуатации и ограничениям",
            "требования заказчика, техзаказчика или бюджетной процедуры",
        ],
        "result": [
            "состав работ по реконструкции",
            "проектная или рабочая документация по согласованным разделам",
            "решения по усилениям и конструктиву, если они входят в задачу",
            "перечень рисков, которые нужно закрыть до следующей стадии",
        ],
        "limits": "Без исходных данных и обследования нельзя честно обещать сроки, стоимость и состав решений. Сначала отделяем подтвержденные факты от предположений.",
        "related": ["pd", "rd", "kr-kzh-km"],
    },
    {
        "slug": "objects",
        "title": "Коммерческие, общественные и производственные объекты",
        "short": "Офисы, склады, ангары, школы, общественные здания и коммерческие помещения.",
        "description": "Проектирование коммерческих, общественных и производственных объектов: состав документации, конструктив, перепланировки, реконструкции и рабочие решения.",
        "image": "assets/images/service-commercial.webp",
        "eyebrow": "бизнес · склады · общественные объекты",
        "lead": "У коммерческого или общественного объекта есть не только планировка, но и назначение, поток людей, эксплуатация, требования к безопасности, конструктиву и будущей подаче документов.",
        "when": [
            "нужно открыть, изменить или реконструировать коммерческое помещение",
            "проектируется склад, ангар, производственное или общественное здание",
            "требуются ПД, РД, КР, КЖ, КМ или перепланировка нежилого помещения",
            "заказчику нужно понять состав работ до договора со строителями",
        ],
        "included": [
            "разбор назначения объекта и требований к документации",
            "подбор состава разделов под задачу и стадию",
            "архитектурные и конструктивные решения в согласованном объеме",
            "пояснение следующего шага: РД, экспертиза, подача, уточнение исходных",
        ],
        "inputs": [
            "документы на помещение, здание или участок",
            "планы, обмеры, техническое задание и описание будущей функции",
            "требования арендатора, собственника, эксплуатации или подрядчика",
            "данные по нагрузкам, оборудованию, людям, инженерии и ограничениям",
        ],
        "result": [
            "понятный состав проектной задачи",
            "проектные или рабочие материалы по согласованным разделам",
            "решения, которые можно обсуждать со строителями и смежниками",
            "перечень ограничений, которые влияют на сроки, стоимость и процедуру",
        ],
        "limits": "Для общественных, производственных и коммерческих объектов состав документации зависит от назначения, площади, стадии, региона, исходных данных и требований процедуры.",
        "related": ["pd", "rd", "pereplanirovki"],
    },
]


SERVICE_BY_SLUG = {service["slug"]: service for service in SERVICES}

SECTION_GUIDE_URLS = [
    ("https://wektorplus-pro.ru/sections/project-sections/", "monthly", "0.7"),
    ("https://wektorplus-pro.ru/sections/engineering-standards/", "monthly", "0.7"),
    ("https://wektorplus-pro.ru/sections/working-sets/", "monthly", "0.7"),
]


def e(value: str) -> str:
    return html.escape(value, quote=True)


def rel(path: str, depth: int) -> str:
    return "../" * depth + path


def render_list(items: list[str]) -> str:
    return "\n".join(f"<li>{e(item)}</li>" for item in items)


def service_json_ld(service: dict[str, object]) -> str:
    url = f"{BASE_URL}/services/{service['slug']}/"
    data = [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "@id": f"{url}#service",
            "name": service["title"],
            "description": service["description"],
            "areaServed": "RU",
            "provider": {"@id": f"{BASE_URL}/#org"},
            "serviceType": service["title"],
            "url": url,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{BASE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Услуги", "item": f"{BASE_URL}/#services"},
                {"@type": "ListItem", "position": 3, "name": service["title"], "item": url},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "@id": f"{BASE_URL}/#org",
            "name": COMPANY,
            "url": BASE_URL,
            "image": f"{BASE_URL}/{service['image']}",
            "logo": f"{BASE_URL}/assets/brand/vpp-logo-full.png",
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
            "sameAs": [
                "https://yandex.ru/maps/org/vektor_plyus_pro/136957193786/",
                "https://2gis.ru/krasnodar/firm/70000001103967582",
                "https://max.ru/id100005517_biz",
                "https://t.me/wektorpluspro",
            ],
        },
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def render_related(service: dict[str, object], depth: int) -> str:
    links = []
    for slug in service["related"]:
        item = SERVICE_BY_SLUG[slug]
        href = rel(f"services/{item['slug']}/index.html", depth)
        links.append(
            f'<a class="static-related-card" href="{href}">'
            f"<span>{e(item['eyebrow'])}</span><strong>{e(item['title'])}</strong>"
            f"<small>{e(item['short'])}</small></a>"
        )
    return "\n".join(links)


def render_service_page(service: dict[str, object]) -> str:
    depth = 2
    canonical = f"{BASE_URL}/services/{service['slug']}/"
    title = f"{service['title']} · Вектор Плюс-Про"
    description = service["description"]
    image = rel(service["image"], depth)
    logo = rel("assets/brand/vpp-logo-mark.png", depth)
    styles = rel("styles.css", depth)
    home = rel("index.html", depth)
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{e(title)}</title>
<meta name="description" content="{e(description)}" />
<meta name="robots" content="index, follow" />
<meta name="theme-color" content="#f5efde" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(description)}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{BASE_URL}/{service['image']}" />
<meta property="og:locale" content="ru_RU" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Onest:wght@400;500;600&family=Unbounded:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap&subset=cyrillic,cyrillic-ext,latin" rel="stylesheet" />
<link rel="icon" type="image/png" href="{rel("assets/brand/vpp-logo-mark.png", depth)}" />
<link rel="apple-touch-icon" href="{rel("assets/brand/vpp-logo-mark.png", depth)}" />
<link rel="preload" as="image" href="{image}" type="image/webp" />
<link rel="stylesheet" href="{styles}" />
<script type="application/ld+json">
{service_json_ld(service)}
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
  <section class="section static-service-hero">
    <div class="container static-service-hero-grid">
      <div>
        <a class="static-back" href="{home}#services">← Все услуги</a>
        <span class="section-eyebrow">{e(service['eyebrow'])}</span>
        <h1>{e(service['title'])}</h1>
        <p class="hero-sub">{e(service['lead'])}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{home}#contacts">Обсудить задачу</a>
          <a class="btn btn-secondary" href="tel:+79385091377">Позвонить</a>
        </div>
      </div>
      <div class="static-service-visual" style="background-image:url('{image}')">
        <span>{e(service['short'])}</span>
      </div>
    </div>
  </section>
  <section class="section static-service-content">
    <div class="container static-service-layout">
      <article class="static-service-main">
        <section>
          <span class="section-eyebrow">Когда нужна услуга</span>
          <h2>В каких ситуациях это помогает</h2>
          <ul>{render_list(service['when'])}</ul>
        </section>
        <section>
          <span class="section-eyebrow">Состав работ</span>
          <h2>Что может входить в работу</h2>
          <ul>{render_list(service['included'])}</ul>
        </section>
        <section>
          <span class="section-eyebrow">Исходные данные</span>
          <h2>Что желательно подготовить</h2>
          <ul>{render_list(service['inputs'])}</ul>
        </section>
        <section>
          <span class="section-eyebrow">Результат</span>
          <h2>Что получает заказчик</h2>
          <ul>{render_list(service['result'])}</ul>
        </section>
        <section class="static-warning">
          <span class="section-eyebrow">Ограничения</span>
          <h2>Что важно знать заранее</h2>
          <p>{e(service['limits'])}</p>
        </section>
        <section>
          <span class="section-eyebrow">Первый разбор</span>
          <h2>Что написать в обращении</h2>
          <ul>
            <li>город и тип объекта;</li>
            <li>что нужно сделать по этому направлению;</li>
            <li>какие документы, планы, фото или исходные данные уже есть;</li>
            <li>примерную площадь, назначение и желаемый срок, если они понятны.</li>
          </ul>
        </section>
      </article>
      <aside class="static-service-aside" aria-label="Контакты и реквизиты">
        <div class="static-aside-card">
          <h2>Проверяемые данные</h2>
          <dl>
            <div><dt>Компания</dt><dd>{COMPANY}</dd></div>
            <div><dt>ИНН</dt><dd>0100005517</dd></div>
            <div><dt>ОГРН</dt><dd>1230100001812</dd></div>
            <div><dt>СРО</dt><dd>СРО-П-166-30062011</dd></div>
            <div><dt>Адрес</dt><dd>Краснодар, Таманская улица, 180, офис 410</dd></div>
          </dl>
        </div>
        <div class="static-aside-card">
          <h2>Связаться</h2>
          <a href="tel:+79385091377">+7 938 509-13-77</a>
          <a href="mailto:office@wektorplus-pro.ru">office@wektorplus-pro.ru</a>
          <a href="https://max.ru/id100005517_biz" target="_blank" rel="noreferrer">MAX-канал «СИЛА Проекта»</a>
          <a href="https://t.me/wektorpluspro" target="_blank" rel="noreferrer">Telegram</a>
        </div>
      </aside>
    </div>
  </section>
  <section class="section static-related">
    <div class="container">
      <div class="section-head">
        <span class="section-eyebrow">Связанные услуги</span>
        <h2 class="section-title">Что часто смотрят вместе с этим направлением</h2>
      </div>
      <div class="static-related-grid">
        {render_related(service, depth)}
      </div>
    </div>
  </section>
</main>
<footer class="static-footer">
  <div class="container">
    <a href="{home}">Вектор Плюс-Про</a>
    <span>Проектная организация · Краснодар · работа по России</span>
  </div>
</footer>
</body>
</html>
"""


def render_sitemap() -> str:
    urls = [
        ("https://wektorplus-pro.ru/", "weekly", "1.0"),
        *[
            (f"https://wektorplus-pro.ru/services/{service['slug']}/", "monthly", "0.8")
            for service in SERVICES
        ],
        *SECTION_GUIDE_URLS,
    ]
    body = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>"
        for loc, freq, priority in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def main() -> None:
    services_dir = ROOT / "services"
    for service in SERVICES:
        target_dir = services_dir / service["slug"]
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "index.html").write_text(render_service_page(service), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(), encoding="utf-8")
    print(f"generated {len(SERVICES)} service pages")


if __name__ == "__main__":
    main()
