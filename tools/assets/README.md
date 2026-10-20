# tools/assets — генератор картинок для blog.startupbase.uno

Из этих исходников в CI рендерятся все бинарные ассеты сайта: иллюстрации статьи,
OG-карточки, логотип/марка и фавиконы. Пайплайн воспроизводит то, что раньше
собиралось локально вручную (headless Chromium + Pillow).

## Как это работает

```
tools/assets/src/*.html                       →  render.js (playwright, viewport ×2)  →  out/*.png
tools/assets/src/articles/<slug>/*.html       →  render.js                          →  out/<slug>--*.png
out/*.png                                     →  postprocess.py (Pillow)            →  файлы в репозитории
```

Workflow `.github/workflows/render-assets.yml` запускается:

* автоматически на push в `tools/assets/**` или в сам файл workflow — **все** статьи;
* вручную через **Actions → render-assets → Run workflow** (необязательный фильтр `slug`:
  пусто = все статьи, иначе только одна папка `src/articles/<slug>`, остальные файлы не трогаются).

Он ставит Geist (npm-пакет `geist`, семейства Geist / Geist Mono), Playwright Chromium
и Pillow, рендерит PNG, раскладывает их по путям сайта и коммитит результат в `main`
(сообщение коммита: `assets: render generated images` или
`assets: render generated images (<slug>)` при ручном запуске с фильтром). Если ничего
не изменилось — шаг коммита просто пишет `no asset changes`.

## Структура

| Путь | Что это |
|---|---|
| `src/ds.css` | подмножество токенов LeadUp AI Design System v3, нужное картинкам (тёмная тема, Geist, teal `#00E5C7`) |
| `src/mark-m4.svg` | марка M4 в 32×32 grid (panel + chevron + caret), она же уезжает в `assets/logo/startupbase-mark.svg` |
| `src/mark-512.html` | обёртка: разворачивает M4 на весь холст 512×512, чтобы PNG вышел 1024×1024 из настоящего вектора (не апскейл) |
| `src/og-blog.html` | общая OG-карточка блога 1200×630 (@2 → 2400×1260, потом даунскейл до 1200×630) |
| `src/logo-dark.html`, `src/logo-light.html` | лок-апы словаря 900×160, прозрачный фон, обрезка по ink |
| `src/appicon.html` | app icon 512×512 на `--bg-1` |
| `src/articles/<slug>/article.json` | метаданные статьи: `slug`, `figures[]` (имена webp-файлов по порядку fig1/fig2/fig3), `og_default: true` — если карточка этой статьи идёт в `assets/og/article-default*` |
| `src/articles/<slug>/{fig1,fig2,fig3,cover}.html` | иллюстрации статьи 1440×810 (@2 → 2880×1620) |
| `src/articles/<slug>/og.html` | OG-карточка статьи 1200×630 (@2 → 2400×1260, потом даунскейл) |
| `render.js` | таблицы `SHARED_JOBS` (общие шаблоны) и `ARTICLE_JOBS` (шаблоны статьи); перебирает `src/articles/*/` |
| `postprocess.py` | webp q90/88, PNG-даунскейл OG, contain-fit лок-апов 312×48, фавиконы/ico, apple-touch-icon |

Правила именования вывода рендера: общие шаблоны → `out/<имя>.png`, шаблоны статьи →
`out/<slug>--fig1.png`, `out/<slug>--fig2.png`, `out/<slug>--fig3.png`,
`out/<slug>--cover.png`, `out/<slug>--og.png`.

## Что попадает в репозиторий

На каждую статью в `src/articles/<slug>/`:

```
images/blog/<slug>/<figures[0]>.webp   2880×1620
images/blog/<slug>/<figures[1]>.webp   2880×1620
images/blog/<slug>/<figures[2]>.webp   2880×1620
images/blog/<slug>/cover.webp          2880×1620
images/blog/<slug>/og.png              1200×630
```

Плюс общие файлы (пересобираются всегда, независимо от статей):

```
assets/og/default.png                        1200×630
assets/og/default@2x.png                     2400×1260
assets/og/article-default.png                1200×630        ← из <slug> с "og_default": true
assets/og/article-default@2x.png             2400×1260       ← из <slug> с "og_default": true
assets/logo/startupbase-mark.svg             M4, вектор
assets/logo/startupbase-mark-512.png         512×512
assets/logo/startupbase-mark-128.png         128×128
assets/logo/startupbase-logo-dark@1x.png     312×48 (contain-fit)
assets/logo/startupbase-logo-dark@2x.png     621×84 (обрезка по ink)
assets/logo/startupbase-logo-light@1x.png    312×48
assets/logo/startupbase-logo-light@2x.png    621×84
assets/logo/startupbase-app-icon-512.png     512×512
apple-touch-icon.png                         180×180 (непрозрачный, фон `--bg-0`)
favicon.ico                                  16/32/48/64
favicon-32.png                               32×32
favicon-64.png                               64×64
```

## Как добавить иллюстрации для новой статьи

1. Создать `src/articles/<slug>/` и скопировать туда шаблоны из соседней статьи
   (`fig1.html`, `fig2.html`, `fig3.html`, `cover.html`, `og.html`) — пути к общим
   ассетам внутри них идут на два уровня вверх (`../../ds.css`).
2. Поправить разметку/текст, при необходимости уменьшить/увеличить число `figN.html`.
3. Завести `src/articles/<slug>/article.json`:
   `{"slug": "<slug>", "figures": ["fig-1-...", "fig-2-...", "fig-3-..."]}`;
   `"og_default": true` — только у одной статьи (её OG-карточка обновляет
   `assets/og/article-default*`).
4. Запушить — workflow отрендерит и закоммитит **все** статьи из `src/articles/*/`;
   для одной статьи можно запустить вручную с параметром `slug`.
5. Файлы `images/blog/<slug>/*` больше нигде не перечисляются: пока статьи нет в
   `src/articles/`, её ассеты не перегенерируются и не удаляются.

`render.js` и `postprocess.py` под новую статью править не нужно — они читают
`src/articles/*/article.json`. Править их нужно только если меняется набор
шаблонов статьи (`ARTICLE_JOBS`) или появляется новая общая картинка (`SHARED_JOBS`).

## Правила дизайн-системы, которые соблюдают шаблоны

* teal `#00E5C7` — только текст, 1px-обводка, glow; не как залитая поверхность
  (исключение — марка и CTA-пилюля OG);
* фон `--bg-0..--bg-3`, шрифт Geist / Geist Mono, трекинг `-0.035em` у заголовков;
* не больше одного gradient-text, одного teal-glow и одного grid-паттерна на картинку;
* текст на картинках — без запрещённых слов, числа конкретные, тире длинное (—),
  кавычки «ёлочки»;
* подписи к рисункам (`Fig N.`) и alt-текст живут в самой статье, не в картинке.

## Зависимости (ставятся автоматически)

`playwright` (Chromium), `geist` (шрифты), `Pillow`. Локально нужен Chromium и
системные Geist / Geist Mono — иначе текст отрендерится подменённым шрифтом.
