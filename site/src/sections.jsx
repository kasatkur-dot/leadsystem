// Section components for Vektor Plus-Pro site — light glass architecture layout

const LINKS = {
  phone: "tel:+79385091377",
  email: "mailto:office@wektorplus-pro.ru",
  max: "https://max.ru/id100005517_biz",
  telegram: "https://t.me/wektorpluspro",
  yandex: "https://yandex.ru/maps/org/vektor_plyus_pro/136957193786/",
  twoGis: "https://2gis.ru/krasnodar/firm/70000001103967582",
  nopriz: "https://reestr.nopriz.ru/",
  contractor: "https://www.tbank.ru/business/contractor/legal/1230100001812/",
};

const externalAttrs = { target: "_blank", rel: "noreferrer" };
const internalWindowAttrs = {};

const Nav = ({ onOpenMenu }) => (
  <nav className="nav" aria-label="Главное меню">
    <div className="nav-inner">
      <a href="#top" className="nav-logo" aria-label="Вектор Плюс-Про — на главную">
        <img className="nav-logo-img" src="assets/brand/vpp-logo-mark.png" width="500" height="500" alt="" aria-hidden="true" decoding="async" fetchPriority="high" />
        <span className="nav-logo-text">
          <span className="sr-only">Вектор Плюс-Про</span>
          Проектная организация
          <small>ООО «Вектор Плюс-Про»</small>
        </span>
      </a>
      <ul className="nav-links">
        <li><a href="#services" {...internalWindowAttrs}>Услуги</a></li>
        <li><a href="#trust" {...internalWindowAttrs}>Доверие</a></li>
        <li><a href="#cases" {...internalWindowAttrs}>Кейсы</a></li>
        <li><a href="#process" {...internalWindowAttrs}>Процесс</a></li>
        <li><a href="#faq" {...internalWindowAttrs}>FAQ</a></li>
        <li><a href="#media" {...internalWindowAttrs}>Медиа</a></li>
        <li><a href="#about" {...internalWindowAttrs}>О компании</a></li>
        <li><a href="#team" {...internalWindowAttrs}>Команда</a></li>
      </ul>
      <div className="nav-cta">
        <a href="#contacts" className="btn btn-primary nav-contact-btn">
          <span className="btn-stack">
            <span>Обсудить объект</span>
            <small>+7 938 509-13-77</small>
          </span>
          <I.Arrow />
        </a>
        <button className="nav-burger" onClick={onOpenMenu} aria-label="Открыть меню"><I.Menu /></button>
      </div>
    </div>
  </nav>
);

const Drawer = ({ open, onClose }) => (
  <div className={`drawer ${open ? "open" : ""}`} onClick={onClose} role="dialog" aria-modal="true" aria-label="Меню">
    <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
      <div className="drawer-head">
        <span className="nav-logo">
          <img className="nav-logo-img" src="assets/brand/vpp-logo-mark.png" width="500" height="500" alt="" aria-hidden="true" decoding="async" />
          <span className="nav-logo-text">Проектная организация<small>ООО «Вектор Плюс-Про»</small></span>
        </span>
        <button className="nav-burger" onClick={onClose} aria-label="Закрыть"><I.Close /></button>
      </div>
      <ul className="drawer-list">
        {[
          ["#services", "Услуги"],
          ["#trust", "Доверие"],
          ["#cases", "Кейсы"],
          ["#process", "Процесс работы"],
          ["#faq", "FAQ"],
          ["#media", "Медиа"],
          ["#about", "О компании"],
          ["#team", "Команда проекта"],
          ["#contacts", "Контакты"],
        ].map(([h, t]) => <li key={h}><a href={h} {...internalWindowAttrs} onClick={onClose}>{t}</a></li>)}
      </ul>
      <a href="#contacts" className="btn btn-primary" onClick={onClose} style={{ alignSelf: "stretch" }}>
        Обсудить объект <I.Arrow />
      </a>
    </div>
  </div>
);

const Hero = () => (
  <section className="section hero" id="top">
    <div className="container">
      <div className="hero-inner">
        <div className="hero-left">
          <h1>
            Проектируем здания, <span className="mark">реконструкции</span> и перепланировки
          </h1>
          <p className="hero-sub">
            <span>
              Проектируем частные дома, коммерческие помещения, склады, ангары, производственные здания,
              котельные, павильоны, пристройки, перепланировки и&nbsp;реконструкции.
            </span>
            <span>
              Помогаем пройти путь от&nbsp;идеи до&nbsp;стройки: разбираем объект, оцениваем риски,
              подбираем нужный состав работ, готовим проект для согласования, разрешения
              на&nbsp;строительство, экспертизы и&nbsp;реализации.
            </span>
            <span className="hero-sub-accent">
              Наш плюс&nbsp;— не&nbsp;просто чертежи, а&nbsp;понятное решение: что можно сделать,
              сколько это стоит, какие этапы нужны и&nbsp;как безопасно довести объект до&nbsp;результата.
            </span>
          </p>
          <div className="hero-actions">
            <a href="#contacts" className="btn btn-primary">Обсудить объект <I.Arrow /></a>
            <a href="#services" className="btn btn-secondary">Посмотреть услуги</a>
          </div>
        </div>

        <div className="hero-visual">
          <div className="hero-photo" style={{ backgroundImage: `url("${IMG.hero}")` }} />
          <div className="hero-overlay">
            <div className="hero-floats">
              <a className="hero-float" href="sections/project-sections/index.html" aria-label="Открыть страницу про разделы проектной документации">
                <span className="hero-float-icon"><I.Layers /></span>
                <span className="hero-float-text">
                  <span className="hero-float-label">Разделы</span>
                  <span className="hero-float-value">ПЗ · ПЗУ · АР · КР · ИОС · ПОС</span>
                </span>
              </a>
              <a className="hero-float" href="sections/engineering-standards/index.html" aria-label="Открыть страницу про инженерные и обязательные разделы">
                <span className="hero-float-icon"><I.Doc /></span>
                <span className="hero-float-text">
                  <span className="hero-float-label">Инженерия и нормы</span>
                  <span className="hero-float-value">ОВ · ВК · ЭОМ · СС · ПБ · ООС · ОДИ · СМ</span>
                </span>
              </a>
              <a className="hero-float" href="sections/working-sets/index.html" aria-label="Открыть страницу про рабочие комплекты">
                <span className="hero-float-icon"><I.Doc /></span>
                <span className="hero-float-text">
                  <span className="hero-float-label">Рабочие комплекты</span>
                  <span className="hero-float-value">АР · КЖ · КМ · КМД · ТХ · спецификации</span>
                </span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="path" role="list" aria-label="Путь работы">
        {[
          ["01", "Запрос"],
          ["02", "Исходные данные"],
          ["03", "Состав работ"],
          ["04", "Документация"],
        ].map(([n, t]) => (
          <div className="path-step" role="listitem" key={n}>
            <span className="path-step-num">{n}</span>
            <h3 className="path-step-title">{t}</h3>
          </div>
        ))}
      </div>

      <div className="hero-stats">
        <div className="hero-stat">
          <div className="hero-stat-num">200+</div>
          <div className="hero-stat-label">выполненных объектов и&nbsp;проектных задач</div>
        </div>
        <div className="hero-stat">
          <div className="hero-stat-num">15+</div>
          <div className="hero-stat-label">регионов работы по&nbsp;России</div>
        </div>
        <div className="hero-stat">
          <div className="hero-stat-num">СРО</div>
          <div className="hero-stat-label">П-166-30062011 — допуск к&nbsp;проектным работам</div>
        </div>
        <div className="hero-stat">
          <div className="hero-stat-num">10+</div>
          <div className="hero-stat-label">направлений: ПД, РД, АР, КР, КЖ, КМ</div>
        </div>
      </div>
    </div>
  </section>
);

const ProofNumbers = () => {
  const metrics = [
    ["100+", "выполненных объектов и проектных задач", "Не один типовой шаблон, а разные задачи: от перепланировки до КР, КЖ, КМ и рабочей документации."],
    ["15+", "регионов работы по России", "Дистанционно собираем исходные данные, выезды и обследования согласуем отдельно под объект."],
    ["СРО", "П-166-30062011", "Проектная компетенция подтверждена документами; реквизиты и карточки доступны для проверки."],
    ["0", "обещаний результата до проверки", "Сначала смотрим объект, документы и ограничения, затем честно называем состав работ и следующий шаг."],
  ];

  return (
    <section className="section proof-numbers" aria-labelledby="proof-title">
      <div className="container">
        <div className="proof-panel">
          <div className="proof-copy">
            <span className="section-eyebrow">Почему выбирают нас</span>
            <h2 className="section-title" id="proof-title">
              Цифры, которые помогают заказчику <span className="mark">быстрее принять решение</span>
            </h2>
            <p className="section-lead">
              Мы&nbsp;не&nbsp;афишируем возраст компании ради красивой строки. Для заказчика важнее другое:
              подтверждаемая компетенция, понятный состав работ, опыт с&nbsp;разными объектами и&nbsp;честная
              позиция до&nbsp;старта.
            </p>
          </div>
          <div className="proof-metrics">
            {metrics.map(([n, t, d]) => (
              <article className="proof-metric" key={t}>
                <strong>{n}</strong>
                <h3>{t}</h3>
                <p>{d}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

const Services = () => {
  const items = [
    {
      n: "01", t: "Проектная документация", img: IMG.svcPD,
      d: "Когда нужно: экспертиза, разрешение на строительство, реконструкция, новое строительство или капремонт. Что входит: разделы ПД под объект, проверка исходных данных и состыковка решений. Клиент получает понятный комплект и список того, что ещё нужно уточнить.",
      tags: ["ПД", "экспертиза", "разрешение"], featured: true,
    },
    {
      n: "02", t: "Рабочая документация", img: IMG.svcRD,
      d: "Когда нужно: строителям нужны чертежи, узлы, спецификации и понятные решения для площадки. Что входит: рабочие комплекты по согласованным разделам. Клиент получает материалы, по которым можно планировать работы, закупки и контроль.",
      tags: ["РД", "узлы", "спецификации"], large: true,
    },
    {
      n: "03", t: "Архитектура и&nbsp;конструктив — АР, КР, КЖ, КМ", img: IMG.svcAR,
      d: "Когда нужно: важно связать архитектуру, нагрузки, железобетон, металл и существующие ограничения. Что входит: АР, КР, КЖ, КМ по задаче. Клиент получает решения, которые можно проверять, строить и согласовывать со смежниками.",
      tags: ["АР", "КР", "КЖ", "КМ"],
    },
    {
      n: "04", t: "Перепланировки", img: IMG.svcPP,
      d: "Когда нужно: квартира, нежилое помещение, ипотечный объект или изменение планировки. Что входит: разбор БТИ, планов, ограничений и технической возможности. Клиент получает безопасный маршрут без обещаний результата до проверки.",
      tags: ["БТИ", "квартиры", "нежилые"],
      href: "#contacts",
    },
    {
      n: "05", t: "Реконструкции и&nbsp;капитальный ремонт", img: IMG.svcRec,
      d: "Когда нужно: существующее здание меняет функцию, нагрузки, планировку или инженерную схему. Что входит: анализ исходных, конструктив, усиления, ограничения и документация. Клиент получает состав работ по реальному состоянию объекта.",
      tags: ["реконструкция", "обследование", "усиления"],
    },
    {
      n: "06", t: "Коммерческие, общественные и&nbsp;производственные объекты", img: IMG.svcCom,
      d: "Когда нужно: офис, магазин, склад, ангар, школа, павильон или производственное здание. Что входит: подбор разделов под назначение, нормы и исходные данные. Клиент получает понятный комплект под свой тип объекта.",
      tags: ["офис", "склад", "школа"],
    },
  ];

  return (
    <section className="section" id="services">
      <div className="container">
        <div className="section-head">
          <span className="section-eyebrow">Услуги · 06 направлений</span>
          <h2 className="section-title">Что мы&nbsp;<em>проектируем</em> и&nbsp;для&nbsp;каких задач</h2>
          <p className="section-lead">
            Состав работ зависит от&nbsp;объекта, исходных данных и&nbsp;требований согласующих органов.
            Мы&nbsp;не&nbsp;продаём шаблон&nbsp;— подбираем разделы документации под конкретную задачу.
          </p>
        </div>
        <div className="svc-grid">
          {items.map((it, i) => (
            <article
              key={i}
              className={`svc-card ${it.featured ? "featured" : ""} ${it.large ? "large" : ""}`}
              style={{ "--bg-img": `url("${it.img}")` }}
            >
              <style>{`.svc-card:nth-child(${i+1})::before { background-image: var(--bg-img); }`}</style>
              <span className="svc-num">{it.n} · направление</span>
              <h3 className="svc-title" dangerouslySetInnerHTML={{ __html: it.t }} />
              <p className="svc-desc">{it.d}</p>
              <div className="svc-meta">
                {it.tags.map((tag) => <span key={tag}>{tag}</span>)}
              </div>
              <a href={it.href || "#contacts"} className="svc-link">{it.href ? "Открыть направление" : "Обсудить направление"} <I.Arrow size={14} /></a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

const IntakeBasics = () => {
  const items = [
    ["Город и объект", "где находится объект, что это: квартира, дом, коммерческое помещение, здание, склад или производство"],
    ["Задача", "что нужно сделать: ПД, РД, АР/КР/КЖ/КМ, перепланировка, реконструкция, капремонт или первичный разбор"],
    ["Документы", "что уже есть: БТИ, ГПЗУ, ТУ, старый проект, обмеры, планы, фото или эскиз"],
    ["Масштаб", "примерная площадь, этажность, назначение помещения и желаемый срок, если он уже понятен"],
  ];

  return (
    <section className="section intake-basics" aria-labelledby="intake-basics-title">
      <div className="container">
        <div className="intake-panel">
          <div className="intake-copy">
            <span className="section-eyebrow">Первый разбор · без сложной формы</span>
            <h2 className="section-title" id="intake-basics-title">
              Что обычно нужно прислать, чтобы мы&nbsp;<span className="mark">поняли задачу</span>
            </h2>
            <p className="section-lead">
              Не&nbsp;нужно сразу собирать полный архив документов. Для первого безопасного шага
              достаточно коротко описать объект и&nbsp;показать, какие исходные данные уже есть.
            </p>
          </div>
          <div className="intake-grid">
            {items.map(([title, text], index) => (
              <article className="intake-card" key={title}>
                <span className="intake-num">{String(index + 1).padStart(2, "0")}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

const ClientSegments = () => {
  const groups = [
    ["Общественные объекты", ["школы", "детские сады", "социальная инфраструктура", "капитальный ремонт"]],
    ["Коммерческие помещения", ["офисы", "магазины", "общепит", "перепланировки нежилых"]],
    ["Производство и склады", ["ангары", "складские комплексы", "металлокаркас", "КМ и КЖ"]],
    ["Реконструкции", ["обследование", "усиление", "существующие здания", "рабочие решения"]],
    ["Жилые объекты", ["квартиры", "ипотечные перепланировки", "БТИ", "пакет для подачи"]],
    ["Частное строительство", ["ИЖС", "коттеджи", "проектные материалы", "разрешительные процедуры"]],
    ["Техзаказчики", ["ПД", "РД", "экспертиза", "состав разделов"]],
    ["Региональные проекты", ["Краснодар", "Адыгея", "Юг России", "дистанционная работа"]],
  ];

  return (
    <section className="section segments" aria-labelledby="segments-title">
      <div className="container">
        <div className="section-head wide">
          <span className="section-eyebrow">Типы задач · по России</span>
          <h2 className="section-title" id="segments-title">
            Работаем не&nbsp;с&nbsp;абстрактной «стройкой», а&nbsp;с&nbsp;<span className="mark">конкретными задачами заказчика</span>
          </h2>
          <p className="section-lead">
            Если клиент ищет проектную организацию, ему важно быстро понять: делаем ли мы&nbsp;его тип объекта,
            какие документы нужны и&nbsp;где может быть риск. Поэтому показываем сегменты открыто, без чужих
            логотипов и&nbsp;без раскрытия заказчиков.
          </p>
        </div>
        <div className="segment-board">
          {groups.map(([title, tags]) => (
            <article className="segment-card" key={title}>
              <h3>{title}</h3>
              <div className="segment-tags">
                {tags.map(tag => <span key={tag}>{tag}</span>)}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

const Standards = () => {
  const items = [
    ["01", "Разбор задачи до сметы", "Сначала смотрим цель, объект и исходные данные. Так заказчик понимает, за что платит, а не получает случайный список разделов."],
    ["02", "Состав работ по объекту", "Отдельно показываем, где нужна ПД, где РД, где АР, КР, КЖ или КМ, а где достаточно проектных материалов под конкретную процедуру."],
    ["03", "Работа с ограничениями", "БТИ, ГПЗУ, ТУ, конструктив, инженерия, региональные требования и требования уполномоченных органов проверяются до обещаний."],
    ["04", "Прозрачные этапы", "Фиксируем вход, этапы, ответственных, перечень исходных данных и формат результата, чтобы проект не превращался в бесконечную переписку."],
    ["05", "Безопасные материалы", "Реальные чертежи, адреса, кадастровые номера, суммы и персональные данные не публикуем без обезличивания и разрешения."],
    ["06", "Следующий шаг после комплекта", "После подготовки материалов объясняем, что делать дальше: экспертиза, подача, уточнение исходных, согласование или рабочая стадия."],
  ];

  return (
    <section className="section standards" aria-labelledby="standards-title">
      <div className="container">
        <div className="standards-head">
          <div>
            <span className="section-eyebrow">Проектная работа · 06 опор</span>
            <h2 className="section-title" id="standards-title">
              Проектная организация для задач, где важны <span className="mark">документы, нормы и ответственность</span>
            </h2>
          </div>
          <p>
            По аналогии с сильным коммерческим предложением: заказчику нужен не красивый лозунг,
            а понятный путь от запроса до комплекта документов, с прозрачными этапами и без рискованных обещаний.
          </p>
        </div>
        <div className="standards-grid">
          {items.map(([n, title, text]) => (
            <article className="standard-card" key={n}>
              <span>{n}</span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

const Trust = () => (
  <section className="section" id="trust">
    <div className="container">
      <div className="section-head">
        <span className="section-eyebrow">Доверие · проверочный центр</span>
        <h2 className="section-title">Реквизиты, СРО, карты и&nbsp;<em>безопасные доказательства</em></h2>
        <p className="section-lead">
          Перед началом проекта заказчик может проверить юридическое лицо, членство в&nbsp;СРО,
          публичные карточки, каналы связи и&nbsp;примеры задач без&nbsp;раскрытия клиентских данных.
        </p>
      </div>

      <div className="trust-grid">
        <div className="trust-main">
          <p className="trust-quote">
            «Прежде чем&nbsp;называть сроки и&nbsp;состав работ, мы&nbsp;всегда смотрим объект, исходные
            документы и&nbsp;ограничения. Это честнее по&nbsp;отношению к&nbsp;заказчику&nbsp;— и&nbsp;к&nbsp;тем,
            кто потом будет строить и&nbsp;согласовывать.»
          </p>
          <dl className="trust-data">
            <div><dt>Юр. лицо</dt><dd>ООО «Вектор Плюс-Про»</dd></div>
            <div><dt>ИНН</dt><dd>0100005517</dd></div>
            <div><dt>ОГРН</dt><dd>1230100001812</dd></div>
            <div><dt>СРО</dt><dd>П-166-30062011</dd></div>
            <div><dt>Город</dt><dd>Краснодар, работа по&nbsp;России</dd></div>
            <div><dt>Адрес</dt><dd>Таманская&nbsp;180, офис&nbsp;410</dd></div>
          </dl>
          <div className="trust-checks" aria-label="Что можно проверить до обращения">
            {["Юридическое лицо", "СРО", "Яндекс Карты", "2GIS", "MAX-канал", "Telegram", "безопасные кейсы"].map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>

        <div className="trust-side">
          {[
            ["Карты", "Яндекс Карты — карточка организации", LINKS.yandex],
            ["Карты", "2GIS — карточка организации", LINKS.twoGis],
            ["MAX", "Канал «СИЛА Проекта»", LINKS.max],
            ["Telegram", "Публичный канал и быстрый контакт", LINKS.telegram],
            ["Реестр", "СРО — НОПРИЗ, реестр членов", LINKS.nopriz],
          ].map(([e, t, h]) => (
            <a className="trust-card" href={h} key={t} {...externalAttrs}>
              <span className="trust-card-l">
                <span className="trust-card-eyebrow">{e}</span>
                <span className="trust-card-title">{t}</span>
              </span>
              <I.ArrowOut />
            </a>
          ))}
        </div>
      </div>
    </div>
  </section>
);

const Cases = ({ onOpen }) => {
  const cases = [
    {
      id: 1, tag: "Образовательный объект", img: IMG.caseSchool,
      title: "Социальная инфраструктура · комплекс на&nbsp;два&nbsp;корпуса",
      region: "Юг России · крупный населённый пункт",
      cls: "lg",
      task: "Подготовить проектную и рабочую документацию по образовательному объекту с двумя корпусами и переходной галереей.",
      inputs: "Исходные данные по участку, назначению объекта, планировочной логике, геологии и требованиям к образовательной функции.",
      did: "Проверили исходные данные и геологию, согласовали архитектурные и конструктивные решения с учётом нормативов для образовательных объектов, выпустили АР, КР, КЖ.",
      result: "Комплект документации, пригодный для последующих стадий и взаимодействия с надзорными органами.",
      hidden: "Не раскрываем точный адрес, заказчика, служебные отметки, договорные суммы и рабочие файлы.",
      check: "Реквизиты ООО, членство в СРО и публичные карточки.",
    },
    {
      id: 2, tag: "Капитальный ремонт", img: IMG.caseSchoolRem,
      title: "Здание школы · усиление и&nbsp;инженерные сети",
      region: "Краснодарский край",
      cls: "md",
      task: "Привести существующее здание школы к актуальным требованиям без полной реконструкции.",
      inputs: "Планы существующего здания, фотофиксация, данные по конструкциям, инженерным сетям и ограничениям эксплуатации.",
      did: "Обследование конструктива, расчёт усилений, узлы по КЖ, рабочая документация по разделам, согласование решений с заказчиком.",
      result: "Решения, на основании которых заказчик планирует производство работ и закупку.",
      hidden: "Не публикуем точный адрес, внутренние обследования, сметы, персональные данные и штампы.",
      check: "Реквизиты, СРО, общедоступные данные о составе документации по капитальному ремонту.",
    },
    {
      id: 3, tag: "Производственный объект", img: IMG.caseWarehouse,
      title: "Складской комплекс · ангарного типа",
      region: "Регион ЦФО",
      cls: "md",
      task: "Запроектировать складской объект с учётом нагрузок от стеллажного хранения и техники.",
      inputs: "Назначение склада, предполагаемые нагрузки, габариты, требования эксплуатации и исходные материалы по участку.",
      did: "Архитектурные и конструктивные разделы, КМ для металлокаркаса, согласование решений с поставщиком металлоконструкций.",
      result: "Документация для производства работ и комплектации.",
      hidden: "Не раскрываем заказчика, точный адрес, коммерческие параметры, спецификации поставщиков и договорные условия.",
      check: "СРО, реквизиты, публичная карточка организации.",
    },
    {
      id: 4, tag: "Перепланировка", img: IMG.caseOffice,
      title: "Нежилое помещение · перевод под офис",
      region: "Краснодар",
      cls: "sm",
      task: "Подготовить материалы по перепланировке под коммерческое использование.",
      inputs: "План БТИ, описание будущей функции, сведения о помещении, фото и ограничения по существующей планировке.",
      did: "Анализ исходных документов, БТИ и технической возможности, проектные материалы под последующее обращение в уполномоченный орган.",
      result: "Решение о согласовании принимает уполномоченный орган. Заказчик получил пакет, пригодный для подачи.",
      hidden: "Не показываем номер помещения, собственника, документы БТИ, суммы и служебные отметки.",
      check: "Реквизиты ООО, СРО, понятная логика работы.",
    },
    {
      id: 5, tag: "КР / КЖ / КМ", img: IMG.caseTower,
      title: "Конструктивные разделы · многоэтажное здание",
      region: "Поволжье",
      cls: "sm",
      task: "Разработать конструктивные разделы для многоэтажного здания смешанного назначения.",
      inputs: "Архитектурные планы, данные по нагрузкам, геометрии здания, смежным разделам и требованиям эксплуатации.",
      did: "Расчёт несущих конструкций, КЖ, КМ, узлы, спецификации, согласование между разделами АР и инженерными системами смежников.",
      result: "Комплект КР, состыкованный с архитектурой и инженерией заказчика.",
      hidden: "Не раскрываем расчётные файлы, точный адрес, заказчика, внутренние замечания и закрытые чертежи.",
      check: "Реквизиты, СРО, состав разделов в открытых нормативах.",
    },
  ];

  return (
    <section className="section" id="cases">
      <div className="container">
        <div className="section-head">
          <span className="section-eyebrow">Кейсы · 05 безопасных примеров</span>
          <h2 className="section-title">Что мы&nbsp;делали&nbsp;— <em>без&nbsp;имён, адресов и&nbsp;штампов</em></h2>
          <p className="section-lead">
            В&nbsp;карточках&nbsp;— тип объекта, регион без&nbsp;точного адреса, задача,
            что сделала компания, результат и&nbsp;что можно проверить. Без&nbsp;кадастровых номеров,
            сумм договоров и&nbsp;внутренних документов.
          </p>
        </div>

        <div className="cases-grid">
          {cases.map(c => (
            <button className={`case-card ${c.cls}`} key={c.id} onClick={() => onOpen(c)}>
              <div className="case-viz" style={{ backgroundImage: `url("${c.img}")` }} />
              <div className="case-body">
                <span className="case-tag">{c.tag}</span>
                <h3 className="case-title" dangerouslySetInnerHTML={{ __html: c.title }} />
                <span className="case-region"><I.Pin size={14} /> {c.region}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};

const CaseModal = ({ data, onClose }) => {
  if (!data) return null;
  return (
    <div className="modal" onClick={onClose} role="dialog" aria-modal="true" aria-label="Описание кейса">
      <div className="modal-panel" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Закрыть">
          <I.Close size={16} />
        </button>
        <div className="modal-viz" style={{ backgroundImage: `url("${data.img}")` }} />
        <div className="modal-body">
          <span className="modal-tag">{data.tag}</span>
          <h3 dangerouslySetInnerHTML={{ __html: data.title }} />
          <span style={{ fontSize: 14, color: "var(--ink-soft)", display: "flex", gap: 8, alignItems: "center" }}>
            <I.Pin size={14}/> {data.region}
          </span>
          <dl style={{ display: "flex", flexDirection: "column", gap: 14, margin: "8px 0 0" }}>
            <div className="modal-block"><dt>Задача клиента</dt><dd>{data.task}</dd></div>
            <div className="modal-block"><dt>Исходные данные</dt><dd>{data.inputs}</dd></div>
            <div className="modal-block"><dt>Что сделала компания</dt><dd>{data.did}</dd></div>
            <div className="modal-block"><dt>Результат</dt><dd>{data.result}</dd></div>
            <div className="modal-block"><dt>Что не раскрываем</dt><dd>{data.hidden}</dd></div>
            <div className="modal-block"><dt>Что можно проверить</dt><dd>{data.check}</dd></div>
          </dl>
        </div>
      </div>
    </div>
  );
};

const ClientVoices = () => {
  const voices = [
    {
      type: "Перепланировка",
      who: "Собственник квартиры или нежилого помещения",
      text: "Важно понять, можно ли делать изменения, какие документы нужны, что зависит от банка, БТИ и уполномоченного органа.",
      result: "Даём безопасный маршрут: проверка исходных, техническая возможность, состав материалов и следующий шаг.",
    },
    {
      type: "Коммерческий объект",
      who: "Предприниматель, арендатор, собственник помещения",
      text: "Нужно открыть объект, сделать ремонт или реконструкцию и не потерять время из-за неправильного состава документации.",
      result: "Разделяем ПД, РД, перепланировку, инженерные и конструктивные задачи, чтобы не смешивать всё в один непонятный проект.",
    },
    {
      type: "Реконструкция и КР",
      who: "Технический заказчик или представитель организации",
      text: "Нужен подрядчик, который говорит языком разделов, конструкций, исходных данных и ответственности, а не только красивых картинок.",
      result: "Показываем состав работ, проверяем ограничения, учитываем смежников и готовим материалы по согласованному объему.",
    },
  ];

  return (
    <section className="section voices" aria-labelledby="voices-title">
      <div className="container">
        <div className="section-head wide">
          <span className="section-eyebrow">Что важно клиентам</span>
          <h2 className="section-title" id="voices-title">
            Люди приходят не&nbsp;за&nbsp;чертежами, а&nbsp;за&nbsp;<span className="mark">понятным решением своей ситуации</span>
          </h2>
          <p className="section-lead">
            Реальные отзывы с&nbsp;именами публикуем только после отдельного разрешения. Пока показываем
            типовые запросы, с&nbsp;которыми к&nbsp;нам приходят заказчики из&nbsp;разных отраслей.
          </p>
        </div>
        <div className="voice-grid">
          {voices.map((item) => (
            <article className="voice-card" key={item.type}>
              <span className="voice-type">{item.type}</span>
              <h3>{item.who}</h3>
              <blockquote>{item.text}</blockquote>
              <p>{item.result}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

const Process = () => {
  const steps = [
    ["01", "Запрос", "Вход: город, тип объекта, задача.", "Действие: первичный разбор ситуации.", "Выход: что нужно прислать дальше."],
    ["02", "Исходные данные", "Вход: БТИ, ГПЗУ, ТУ, обмеры, фото, старый проект.", "Действие: проверка ограничений и расхождений.", "Выход: список рисков и недостающих данных."],
    ["03", "Состав работ", "Вход: задача, документы и ограничения.", "Действие: определяем ПД, РД, АР, КР, КЖ, КМ.", "Выход: понятные границы проекта."],
    ["04", "Документация", "Вход: согласованный состав работ.", "Действие: проектирование и состыковка решений.", "Выход: комплект материалов по задаче."],
    ["05", "Проверка", "Вход: подготовленный комплект.", "Действие: внутренний контроль и ответы на замечания.", "Выход: аккуратные правки по согласованному объему."],
    ["06", "Следующий шаг", "Вход: готовые материалы и задача клиента.", "Действие: объясняем дальнейший маршрут.", "Выход: экспертиза, подача, стройка или уточнение исходных."],
  ];

  return (
    <section className="section" id="process">
      <div className="container">
        <div className="section-head wide">
          <span className="section-eyebrow">Процесс · 06 шагов</span>
          <h2 className="section-title">От&nbsp;брифа до&nbsp;готового комплекта <span className="mark">без хаоса в документах</span></h2>
          <p className="section-lead">
            Полный цикл с&nbsp;учётом специфики проектирования: исходные данные, ограничения,
            состав разделов, проверка, передача комплекта и&nbsp;следующий безопасный шаг.
          </p>
        </div>
        <div className="process-board">
          <div className="process-flow-head">
            <div className="process-input"><small>вход</small><strong>запрос клиента</strong></div>
            <div className="process-output"><small>выход</small><strong>понятный проектный комплект</strong></div>
          </div>
          <div className="process-list">
          {steps.map(([n, t, a, b, c]) => (
            <article className="process-step" key={n}>
              <span className="process-step-num">{n}</span>
              <h3 className="process-step-title">{t}</h3>
              <ul className="process-step-list">
                <li>{a}</li>
                <li>{b}</li>
                <li>{c}</li>
              </ul>
            </article>
          ))}
          </div>
          <div className="process-bottom">
            <div><span>первичный разбор</span><strong>от 1 рабочего дня</strong></div>
            <div><span>срок проекта</span><strong>по ТЗ и исходным данным</strong></div>
            <div><span>важное правило</span><strong>не обещаем согласование до проверки</strong></div>
          </div>
        </div>
      </div>
    </section>
  );
};

const Faq = () => {
  const [open, setOpen] = React.useState(0);
  const items = [
    ["Что делать, если нет всех исходных документов?",
      "Это нормальная стартовая ситуация. Пришлите то, что есть: планы, фото, старый проект, документы на объект или участок. Мы скажем, чего хватает для первого разбора, а что нужно запросить или уточнить."],
    ["Можно ли начать без ГПЗУ или ТУ?",
      "Иногда можно начать с предварительного разбора, но для точного состава работ ГПЗУ, ТУ и другие исходные данные могут быть обязательны. Мы сразу отделяем то, что можно оценить сейчас, от того, что нельзя обещать без документов."],
    ["Чем проект для разрешения на строительство отличается от рабочей документации?",
      "Проектная документация нужна для проверки решений, экспертизы и разрешительных процедур. Рабочая документация — это более детальные чертежи, узлы и спецификации, по которым строители выполняют работы."],
    ["Когда нужна экспертиза?",
      "Это зависит от типа объекта, назначения, параметров, региона и требований законодательства. Мы не назначаем экспертизу вслепую: сначала смотрим задачу, исходные данные и ограничения."],
    ["Что делать, если БТИ не совпадает с фактом?",
      "Нужно отдельно разобраться, где расхождение: в старых документах, фактической планировке или уже выполненных работах. После проверки можно понять, какие материалы нужны и какой путь безопаснее."],
    ["Можно ли согласовать перепланировку в ипотечной квартире?",
      "Иногда можно, иногда нет. Зависит от банка, объекта, характера работ и требований уполномоченного органа. Мы готовим проектные материалы и оцениваем техническую возможность, но не обещаем решение до проверки."],
    ["Почему нельзя назвать точную цену без документов?",
      "Цена зависит от состава разделов, площади, сложности, исходных данных, обследований и требований органов. Без этих вводных точная сумма будет угадыванием, а не профессиональной оценкой."],
    ["Можно ли работать дистанционно?",
      "Да. По многим задачам можно начать удалённо: передать документы, обсудить объект, согласовать состав работ. Если нужен выезд, обмер или обследование, это отдельно согласуется под объект."],
    ["Какие документы обычно нужны для коммерческого помещения?",
      "Обычно нужны правоустанавливающие документы, планы БТИ или обмеры, данные по назначению помещения, фото, сведения о текущем состоянии и описание будущей функции. Точный список зависит от задачи."],
    ["Что получает клиент после первичного разбора?",
      "Понимание следующего шага: какие исходные данные нужны, какие риски видны сейчас, какой состав работ может потребоваться и какой формат документации подходит под задачу."],
  ];
  return (
    <section className="section" id="faq">
      <div className="container">
        <div className="faq-grid">
          <div>
            <span className="section-eyebrow" style={{ marginBottom: 14, display: "inline-flex" }}>FAQ · честные ответы</span>
            <h2 className="section-title" style={{ marginBottom: 18 }}>Частые <em>вопросы</em>&nbsp;— по&nbsp;делу</h2>
            <p className="section-lead">
              Если вашего вопроса нет&nbsp;— напишите в&nbsp;MAX, Telegram или&nbsp;на&nbsp;почту. Ответим
              без&nbsp;обещаний, которых не&nbsp;можем сдержать.
            </p>
          </div>
          <div className="faq-list">
            {items.map(([q, a], i) => (
              <div className={`faq-item ${open === i ? "open" : ""}`} key={i}>
                <button className="faq-q" onClick={() => setOpen(open === i ? -1 : i)} aria-expanded={open === i} aria-controls={`faq-a-${i}`}>
                  <span>{q}</span>
                  <span className="faq-icon" aria-hidden="true" />
                </button>
                <div className="faq-a" id={`faq-a-${i}`} role="region"><div className="faq-a-inner">{a}</div></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

const Media = () => (
  <section className="section" id="media">
    <div className="container">
      <div className="section-head">
        <span className="section-eyebrow">Медиа · центр объяснений</span>
        <h2 className="section-title">Видео, <em>схемы</em>, чек-листы и&nbsp;разборы ошибок</h2>
        <p className="section-lead">
          Это не&nbsp;декоративная витрина, а&nbsp;материалы для первого понимания: какой путь проходит
          объект, какие документы нужны и&nbsp;что чаще всего тормозит проект.
        </p>
      </div>
      <div className="media-grid">
        <article className="media-card video">
          <video className="media-video" controls preload="metadata" poster={IMG.videoCover}>
            <source src="assets/media/project-path-demo.mp4" type="video/mp4" />
            Ваш браузер не поддерживает воспроизведение видео.
          </video>
          <div className="video-content">
            <span className="video-meta">Видео-разбор · без автозвука</span>
            <h3 className="video-title">Как понять, какие документы нужны для&nbsp;вашего объекта</h3>
          </div>
        </article>

        <div className="media-card diagram">
          <span className="media-eyebrow">Схема</span>
          <h3 className="media-title">От&nbsp;запроса до&nbsp;документации</h3>
          <p className="media-desc">Понятная карта работы: четыре опоры, на&nbsp;которых стоит проект — запрос, исходные данные, состав работ, документация.</p>
          <div className="diagram-img" style={{ backgroundImage: `url("${IMG.diagram}")` }} />
        </div>

        <a className="media-card s" href={LINKS.max} {...externalAttrs}>
          <span className="media-eyebrow"><I.Channel size={12}/> &nbsp;MAX-канал</span>
          <h3 className="media-title">«СИЛА Проекта»</h3>
          <p className="media-desc">MAX-канал команды: разборы, новости отрасли и&nbsp;ответы на&nbsp;вопросы клиентов.</p>
          <span className="media-link">Перейти в&nbsp;MAX <I.ArrowOut size={12}/></span>
        </a>

        <a className="media-card s" href={LINKS.telegram} {...externalAttrs}>
          <span className="media-eyebrow"><I.Send size={12}/> &nbsp;Telegram</span>
          <h3 className="media-title">Короткие посты</h3>
          <p className="media-desc">Быстрые материалы по&nbsp;ПД, РД и&nbsp;типовым ошибкам.</p>
          <span className="media-link">Открыть Telegram <I.ArrowOut size={12}/></span>
        </a>

        <div className="media-card checklist">
          <span className="media-eyebrow">Чек-лист</span>
          <h3 className="media-title">Исходные данные для&nbsp;старта проекта</h3>
          <ul className="checklist-list">
            <li>документы на&nbsp;объект и&nbsp;участок</li>
            <li>планы БТИ или&nbsp;обмеры</li>
            <li>исходно-разрешительные документы</li>
            <li>описание цели и&nbsp;горизонт сроков</li>
            <li>фото текущего состояния объекта</li>
          </ul>
        </div>

        <div className="media-card m">
          <span className="media-eyebrow">Разбор</span>
          <h3 className="media-title">Типовые ошибки в&nbsp;документах заказчика</h3>
          <p className="media-desc">Что чаще всего тормозит проект: устаревшие планы, расхождение БТИ и&nbsp;факта, отсутствие исходно-разрешительных, нестыковки между разделами.</p>
          <span className="media-link">Материал готовится <I.Arrow size={12}/></span>
        </div>

        <div className="media-card s">
          <span className="media-eyebrow">Будущие материалы</span>
          <h3 className="media-title">VK / Дзен / кейсы</h3>
          <p className="media-desc">Длинные разборы и&nbsp;обзоры появятся после подготовки безопасных материалов без клиентских данных.</p>
          <span className="media-link">Без автозвука и чужих видео</span>
        </div>
      </div>
    </div>
  </section>
);

const About = () => (
  <section className="section" id="about">
    <div className="container">
      <div className="about-grid">
        <div className="about-text">
          <span className="section-eyebrow" style={{ marginBottom: 14, display: "inline-flex" }}>О&nbsp;компании</span>
          <h2 className="section-title" style={{ marginBottom: 24 }}>Проектная организация, которая <em>разбирается</em> до&nbsp;того, как&nbsp;обещает</h2>
          <p>
            ООО «Вектор Плюс-Про»&nbsp;— проектная организация из&nbsp;Краснодара. Работаем
            с&nbsp;проектной и&nbsp;рабочей документацией, архитектурными и&nbsp;конструктивными разделами,
            реконструкциями, капитальным ремонтом, перепланировками и&nbsp;объектами коммерческого,
            общественного и&nbsp;производственного назначения.
          </p>
          <p>
            Наша задача&nbsp;— не&nbsp;обещать быстрый результат вслепую, а&nbsp;сначала разобраться
            в&nbsp;исходных данных, ограничениях и&nbsp;цели заказчика. После этого мы&nbsp;показываем
            состав работ, обсуждаем риски и&nbsp;следующий шаг.
          </p>
          <div className="about-pillars">
            <div className="about-pillar">
              <div className="about-pillar-num">06</div>
              <div className="about-pillar-text">направлений работы&nbsp;— от&nbsp;квартиры до&nbsp;производственного комплекса</div>
            </div>
            <div className="about-pillar">
              <div className="about-pillar-num">15+</div>
              <div className="about-pillar-text">регионов России — выездная и&nbsp;дистанционная работа</div>
            </div>
            <div className="about-pillar">
              <div className="about-pillar-num">СРО</div>
              <div className="about-pillar-text">П-166-30062011 — допуск к&nbsp;проектной деятельности</div>
            </div>
            <div className="about-pillar">
              <div className="about-pillar-num">ПД·РД</div>
              <div className="about-pillar-text">оба&nbsp;типа документации — от&nbsp;концепции до&nbsp;площадки</div>
            </div>
          </div>
        </div>
        <div className="about-visual" style={{ backgroundImage: `url("${IMG.about}")` }}>
          <div className="about-visual-overlay">
            <span className="about-visual-chip">Краснодар</span>
            <span className="about-visual-chip">Работа по России</span>
          </div>
        </div>
      </div>
    </div>
  </section>
);

const Team = () => {
  const leads = [
    {
      role: "Директор",
      name: "Черная Яна Александровна",
      text: "Организационное управление, коммуникация с заказчиком, договорная логика, контроль процесса и сроков по согласованному составу работ.",
    },
    {
      role: "ГИП",
      name: "Макеев Сергей Владимирович",
      text: "Главный инженер проекта: отвечает за техническую логику, состав разделов, проектные решения и связку ПД/РД со смежными задачами.",
    },
  ];

  const specialists = [
    ["Архитектор", "Архитектурные решения, планировочная логика, АР, привязка проектной идеи к нормативам и исходным данным."],
    ["Конструктор / КР", "Конструктивная схема здания, несущие решения, усиления, проверка технической реализуемости решений."],
    ["Инженер КЖ", "Железобетонные конструкции, узлы, армирование, спецификации и рабочие решения по разделу КЖ."],
    ["Инженер КМ", "Металлические конструкции, каркасы, связи, спецификации и решения по разделу КМ."],
    ["Специалист по исходным данным", "БТИ, обмеры, ГПЗУ, ТУ, старые проекты, фотофиксация и проверка того, чего не хватает для старта."],
    ["Координатор документации", "Комплектность, версии файлов, выдача материалов, коммуникация со смежниками и контроль понятности результата."],
  ];

  return (
    <section className="section team" id="team">
      <div className="container">
        <div className="section-head wide">
          <span className="section-eyebrow">Команда проекта</span>
          <h2 className="section-title">За проектом стоят <span className="mark">люди и роли</span>, а не безличный файл</h2>
          <p className="section-lead">
            Состав команды зависит от задачи: для перепланировки не нужен тот же набор специалистов,
            что для реконструкции школы или складского объекта. Мы подключаем профильные роли только
            там, где они действительно нужны для результата.
          </p>
        </div>

        <div className="team-grid">
          <div className="team-leads">
            {leads.map((person) => (
            <article className="team-lead-card" key={person.role}>
              <span className="team-role">{person.role}</span>
              <h3>{person.name}</h3>
              <p>{person.text}</p>
            </article>
            ))}
          </div>

          <div className="team-specialists" aria-label="Профильные специалисты проекта">
            {specialists.map(([role, text]) => (
              <article className="team-specialist" key={role}>
                <h3>{role}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </div>
        <p className="team-note">
          Публично называем только подтверждённые роли и&nbsp;имена. Состав команды подбирается под задачу:
          перепланировка, ПД, РД, конструктив, реконструкция или коммерческий объект требуют разного набора специалистов.
        </p>
      </div>
    </section>
  );
};

const ConsultationPrep = () => {
  const items = [
    "город и тип объекта",
    "что нужно сделать: перепланировка, проект здания, реконструкция, КР/КЖ/КМ, ПД или РД",
    "план помещения, план БТИ, эскиз или фото планировки, если они есть",
    "короткое описание задачи: что хотите изменить, построить, согласовать или проверить",
    "для коммерческого или нежилого объекта — назначение помещения и примерную площадь",
  ];

  return (
    <div className="consultation-prep" aria-labelledby="consultation-prep-title">
      <div className="consultation-prep-copy">
        <span className="consultation-prep-kicker">Первый разбор без лишней тревоги</span>
        <h3 id="consultation-prep-title">Что подготовить до консультации</h3>
        <p>
          Не нужен полный комплект документов. Для первого разбора достаточно того,
          что уже есть сейчас.
        </p>
      </div>
      <div className="consultation-prep-list">
        <p>Чтобы мы поняли задачу и подсказали следующий шаг, можно прислать:</p>
        <ul>
          {items.map((item) => <li key={item}>{item}</li>)}
        </ul>
        <strong>Если документов пока нет — это нормально. Подскажем, какие исходные данные понадобятся именно для вашей задачи.</strong>
      </div>
    </div>
  );
};

const Contacts = () => (
  <section className="section contacts" id="contacts">
    <div className="contacts-bg" style={{ backgroundImage: `url("${IMG.contacts}")` }} />
    <div className="container">
      <div className="section-head">
        <span className="section-eyebrow">Контакты · 07 каналов связи</span>
        <h2 className="section-title">Напишите по&nbsp;объекту&nbsp;— расскажем <em>по&nbsp;делу</em></h2>
        <p className="section-lead">
          Напишите город, тип объекта, задачу и&nbsp;какие документы уже есть. Мы&nbsp;ответим,
          какие исходные данные нужны для первого безопасного шага, и&nbsp;покажем возможный
          состав работ без&nbsp;обещаний до&nbsp;изучения объекта.
        </p>
      </div>
      <ConsultationPrep />
      <div className="contacts-grid">
        <div className="contact-channels">
          <a className="contact-btn primary" href={LINKS.phone}>
            <span className="contact-btn-eyebrow"><I.Phone size={11}/> Телефон</span>
            <span className="contact-btn-value">+7 938 509-13-77</span>
          </a>
          <a className="contact-btn" href={LINKS.email}>
            <span className="contact-btn-eyebrow"><I.Mail size={11}/> Email</span>
            <span className="contact-btn-value">office@wektorplus-pro.ru</span>
          </a>
          <a className="contact-btn" href={LINKS.max} aria-label="MAX-аккаунт для сообщений" {...externalAttrs}>
            <span className="contact-btn-eyebrow"><I.Account size={11}/> MAX-аккаунт</span>
            <span className="contact-btn-value">Написать в&nbsp;MAX</span>
          </a>
          <a className="contact-btn" href={LINKS.max} aria-label="MAX-канал СИЛА Проекта" {...externalAttrs}>
            <span className="contact-btn-eyebrow"><I.Channel size={11}/> MAX-канал</span>
            <span className="contact-btn-value">«СИЛА Проекта»</span>
          </a>
          <a className="contact-btn" href={LINKS.telegram} aria-label="Telegram" {...externalAttrs}>
            <span className="contact-btn-eyebrow"><I.Send size={11}/> Telegram</span>
            <span className="contact-btn-value">Написать в&nbsp;Telegram</span>
          </a>
          <a className="contact-btn" href={LINKS.yandex} aria-label="Яндекс Карты" {...externalAttrs}>
            <span className="contact-btn-eyebrow"><I.Map size={11}/> Яндекс Карты</span>
            <span className="contact-btn-value">Карточка организации</span>
          </a>
          <a className="contact-btn" href={LINKS.twoGis} aria-label="2GIS" {...externalAttrs}>
            <span className="contact-btn-eyebrow"><I.Map size={11}/> 2GIS</span>
            <span className="contact-btn-value">Карточка организации</span>
          </a>
          <a className="contact-btn" href={LINKS.yandex} aria-label="Адрес" {...externalAttrs}>
            <span className="contact-btn-eyebrow"><I.Pin size={11}/> Адрес</span>
            <span className="contact-btn-value">Краснодар, Таманская&nbsp;180</span>
          </a>
        </div>

        <div className="contact-card">
          <div className="contact-card-row"><span className="contact-card-label">Юр. лицо</span><span className="contact-card-value">ООО «Вектор Плюс-Про»</span></div>
          <div className="contact-card-row"><span className="contact-card-label">ИНН / ОГРН</span><span className="contact-card-value">0100005517 / 1230100001812</span></div>
          <div className="contact-card-row"><span className="contact-card-label">СРО</span><span className="contact-card-value">СРО-П-166-30062011</span></div>
          <div className="contact-card-row"><span className="contact-card-label">Адрес</span><span className="contact-card-value">Краснодар, Таманская&nbsp;180, офис&nbsp;410</span></div>
          <div className="contact-card-row"><span className="contact-card-label">География</span><span className="contact-card-value">Краснодар · работа по&nbsp;России</span></div>
          <div className="contact-card-row"><span className="contact-card-label">Часы работы</span><span className="contact-card-value">Пн–Пт · 09:00–18:00 (МСК+0)</span></div>
        </div>
      </div>
    </div>
  </section>
);

const Footer = () => (
  <footer className="footer">
    <div className="container">
      <div className="footer-grid">
        <div className="footer-col">
          <div className="footer-brand">Вектор Плюс-Про</div>
          <p className="footer-tagline">
            Проектная организация. Проектная и&nbsp;рабочая документация, архитектурные
            и&nbsp;конструктивные разделы, реконструкции, перепланировки.
          </p>
        </div>
        <div className="footer-col">
          <h4>Разделы</h4>
          <ul>
            <li><a href="#services">Услуги</a></li>
            <li><a href="#cases">Кейсы</a></li>
            <li><a href="#process">Процесс</a></li>
            <li><a href="#faq">FAQ</a></li>
            <li><a href="#about">О&nbsp;компании</a></li>
            <li><a href="#team">Команда</a></li>
          </ul>
        </div>
        <div className="footer-col">
          <h4>Связь</h4>
          <ul>
            <li><a href={LINKS.phone}>+7 938 509-13-77</a></li>
            <li><a href={LINKS.email}>office@wektorplus-pro.ru</a></li>
            <li><a href={LINKS.max} {...externalAttrs}>MAX-аккаунт</a></li>
            <li><a href={LINKS.max} {...externalAttrs}>MAX-канал «СИЛА Проекта»</a></li>
            <li><a href={LINKS.telegram} {...externalAttrs}>Telegram</a></li>
          </ul>
        </div>
        <div className="footer-col">
          <h4>Карты и&nbsp;реестры</h4>
          <ul>
            <li><a href={LINKS.yandex} {...externalAttrs}>Яндекс Карты</a></li>
            <li><a href={LINKS.twoGis} {...externalAttrs}>2GIS</a></li>
            <li><a href={LINKS.nopriz} {...externalAttrs}>Реестр СРО</a></li>
            <li><a href={LINKS.contractor} {...externalAttrs}>Реквизиты ООО</a></li>
          </ul>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© 2020–2026 ООО «Вектор Плюс-Про». ИНН 0100005517 · ОГРН 1230100001812 · СРО-П-166-30062011</span>
        <span>Краснодар, Таманская 180, оф. 410 · работа по России</span>
      </div>
    </div>
  </footer>
);

Object.assign(window, {
  Nav, Drawer, Hero, ProofNumbers, Services, IntakeBasics, ClientSegments, Standards, Trust, Cases, CaseModal, ClientVoices, Process, Faq, Media, About, Team, Contacts, Footer,
});
