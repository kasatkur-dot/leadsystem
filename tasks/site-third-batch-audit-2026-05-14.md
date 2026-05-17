# Site third batch audit — 2026-05-14

Scope: финальный SEO/GEO-аудит, mobile QA, ссылки, JSON-LD, sitemap, robots перед возможным будущим preview.

Что не запускалось:

- Vercel/GitHub deploy;
- формы;
- CRM/Bitrix24;
- платные API;
- публикации.

Откатная копия перед аудитом:

```text
backups/site-before-third-tz-audit-20260514-235106
```

## Проверки

- `node --check site/assets/app.bundle.js` — OK.
- CSS-баланс `site/styles.css` — `0`.
- HTML-файлов проверено: `10`.
- JSON-LD блоков найдено: `11`.
- JSON-LD ошибок: `0`.
- Локальных битых ссылок/ассетов: `0`.
- `site/sitemap.xml` парсится как XML.
- URL в sitemap: `10`; локальных отсутствующих файлов: `0`.
- `site/robots.txt` доступен локально.
- Главная, `robots.txt`, `sitemap.xml` доступны локально через HTTP `200 OK`.
- Внешние публичные ссылки отвечают `200`: Яндекс Карты, 2GIS, MAX, Telegram, НОПРИЗ, Т-Банк.
- Запрещённые обещания в публичных файлах сайта не найдены: `100% согласуем`, `гарантированное согласование`, `узаконим всё`, `без отказов`, `быстро без документов`, `согласуем всё`.

## Mobile QA

Проверены viewport:

- `390x844`;
- `768x1024`;
- `1440x900`.

Результат: горизонтального переполнения нет (`scrollWidth == innerWidth`).

Контрольные скриншоты:

```text
output/playwright/site-third-batch-home-mobile.png
output/playwright/site-third-batch-home-desktop.png
output/playwright/site-third-batch-static-pd-mobile.png
```

## Замечания перед production

- `robots.txt`, canonical, OG и JSON-LD сейчас указывают на будущий домен `https://wektorplus-pro.ru/`. Перед production нужно подтвердить, что именно этот домен будет использоваться.
- На сайте есть Google Fonts. Для production можно оставить или позже заменить на локальные шрифты, если понадобится полностью независимая статическая версия.
- Security headers проверяются только на реальном хостинге, поэтому сейчас не проверялись.

## Вывод

Третья партия ТЗ закрыта на локальном уровне. Сайт можно готовить к preview только после отдельного подтверждения Яники.
