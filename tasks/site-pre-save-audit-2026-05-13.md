# Site Pre-Save Audit - 2026-05-13

Цель: проверить блок `site` перед будущим сохранением отдельной партией.

Это не commit, не `git add`, не push, не deploy и не публикация.

## Проверенный scope

- `site/`
- `content/site/`
- `content/studio_brand/`
- `docs/site-*`
- `docs/new-site-*`

## Результат

Вердикт: блок `site` можно готовить как отдельную партию для будущего сохранения после подтверждения пользователя.

Staged-файлов не было и `git add` не выполнялся.

## Что готово к сохранению

- статическая версия сайта `site/`;
- локальные React runtime-файлы и собранный `site/assets/app.bundle.js`;
- статические SEO/GEO страницы услуг и справочных разделов;
- локальные изображения и медиа;
- site-документация;
- подготовительные материалы `content/site/` и `content/studio_brand/`.

## Проверки

- `node --check site/assets/app.bundle.js` - OK.
- `node --check site/tools/build-bundle.mjs` - OK.
- `.venv/bin/python -m py_compile site/tools/generate-local-visuals.py site/tools/generate-section-guide-pages.py site/tools/generate-service-pages.py` - OK.
- CSS brace balance: `0`.
- HTML files: `10`.
- JSON-LD blocks: `11`.
- JSON-LD errors: `0`.
- Missing local refs: `0`.
- `sitemap.xml` parses: OK.
- `sitemap_urls`: `10`.
- Local HTTP preview:
  - `/` -> `200 OK`;
  - `/services/pereplanirovki/index.html` -> `200 OK`;
  - `/sections/project-sections/index.html` -> `200 OK`.

## Секреты и чувствительные данные

Реальных токенов/API-ключей/credentials в проверенном scope не найдено.

Найденные совпадения по словам `SECRET/TOKEN/API_KEY` не являются пользовательскими секретами:

- CSS `mask-image`;
- React production internals `__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED`.

Публичные реквизиты компании, телефон, email, ИНН, ОГРН, СРО и адрес офиса присутствуют как часть сайта и проектного ТЗ. Это не секреты, но перед реальной публикацией пользователь должен подтвердить их актуальность.

В site-документах есть предупреждения про реальные документы, договоры, адреса и клиентские данные. Это правила безопасности, а не публикация клиентских данных.

## Мусор и временные файлы

В проверенном scope не найдено:

- `.DS_Store`;
- `.log`;
- `.tmp`;
- `.bak`;
- `.orig`;
- `*~`.

## Не блокирует, но помнить перед production

- В HTML есть внешние ссылки на Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`). Для локального сохранения это не блокер, но перед production можно решить: оставить или локализовать шрифты.
- `site/assets/images/hero-building.png` весит около `2.4M`. Для локального сохранения допустимо, но перед production желательно оптимизировать или заменить на WebP/AVIF.
- Внешние ссылки на `max.ru`, `t.me` и канонические URL `wektorplus-pro.ru` ожидаемы, но перед публикацией стоит финально проверить.

## Точный список файлов для будущего `git add`

Не запускать без подтверждения пользователя.

```bash
git add -- \
  content/site/cases-safe-mvp.md \
  content/site/consultation-prep-block.md \
  content/studio_brand/audience_fears.md \
  content/studio_brand/customer_profiles.md \
  content/studio_brand/system_prompt.md \
  docs/new-site-design-brief.md \
  docs/new-site-structure.md \
  docs/site-claude-design-code-review.md \
  docs/site-design-audit-2026-05-07.md \
  docs/site-design-skills-map.md \
  docs/site-design-upgrade-plan.md \
  docs/site-selling-geo-audit-2026-05-07.md \
  docs/site-visual-assets-safe-review.md \
  docs/site-visual-assets-wide-audit.md \
  site/DESIGN.md \
  site/README.md \
  site/assets/app.bundle.js \
  site/assets/brand/vpp-logo-full.png \
  site/assets/brand/vpp-logo-mark.png \
  site/assets/images/about-engineering-office.webp \
  site/assets/images/case-education-campus.webp \
  site/assets/images/case-office-replanning.webp \
  site/assets/images/case-school-renovation.webp \
  site/assets/images/case-structural-tower.webp \
  site/assets/images/case-warehouse.webp \
  site/assets/images/contacts-building-bg.webp \
  site/assets/images/hero-building.png \
  site/assets/images/hero-building.webp \
  site/assets/images/media-diagram.webp \
  site/assets/images/media-video-cover.webp \
  site/assets/images/service-architecture-structure.webp \
  site/assets/images/service-commercial.webp \
  site/assets/images/service-project-docs.webp \
  site/assets/images/service-reconstruction.webp \
  site/assets/images/service-replanning.webp \
  site/assets/images/service-working-docs.webp \
  site/assets/media/project-path-demo.mp4 \
  site/assets/vendor/react-dom.production.min.js \
  site/assets/vendor/react.production.min.js \
  site/index.html \
  site/open-site.command \
  site/robots.txt \
  site/sections/engineering-standards/index.html \
  site/sections/project-sections/index.html \
  site/sections/working-sets/index.html \
  site/services/kr-kzh-km/index.html \
  site/services/objects/index.html \
  site/services/pd/index.html \
  site/services/pereplanirovki/index.html \
  site/services/rd/index.html \
  site/services/rekonstruktsiya/index.html \
  site/sitemap.xml \
  site/src/app.jsx \
  site/src/icons.jsx \
  site/src/images.js \
  site/src/sections.jsx \
  site/styles.css \
  site/tools/build-bundle.mjs \
  site/tools/generate-local-visuals.py \
  site/tools/generate-section-guide-pages.py \
  site/tools/generate-service-pages.py
```

## Следующий маленький шаг

Если пользователь подтверждает, можно выполнить именно этот `git add` как site Batch. Commit, push и deploy делать только отдельным подтверждением.
