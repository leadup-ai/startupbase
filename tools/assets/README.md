# tools/assets — генератор картинок для blog.startupbase.uno

Из этих исходников в CI рендерятся все бинарные ассеты сайта: иллюстрации статьи,
OG-карточки, логотип/марка и фавиконы. Пайплайн воспроизводит то, что раньше
собиралось локально вручную (headless Chromium + Pillow).

## Как это работает

```
tools/assets/src/*.html   →   render.js (playwright, viewport ×2)   →   out/*.png
out/*.png                 →   postprocess.py (Pillow)               →   файлы в репозитории
```

Workflow `.github/workflows/render-assets.yml` запускается:

* автоматически на push в `tools/assets/**` или в сам файл workflow;
* вручную через **Actions → render-assets → Run workflow** (можно задать `slug`).

Он ставит Geist (npm-пакет `geist`, семейства Geist / Geist Mono), Playwright Chromium
и Pillow, рендерит PNG, раскладывает их по путям сайта и коммитит результат в `main`
(сообщение коммита: `assets: render generated images (<slug>)`). Если ничего не
изменилось — шаг коммита просто пишет `no asset changes`.

## Структура

| Путь | Что это |
|---|---|
| `src/ds.css` | подмножество токенов LeadUp AI Design System v3, нужное картинкам (тёмная тема, Geist, teal `#00E5C7`) |
| `src/mark-m4.svg` | марка M4 в 32×32 grid (panel + chevron + caret), она же уезжает в `assets/logo/startupbase-mark.svg` |
| `src/mark-512.html` | обёртка: разворачивает M4 на весь холст 512×512, чтобы PNG вышел 1024×1024 из настоящего вектора (не апскейл) |
| `src/fig1..fig3.html`, `src/cover.html` | иллюстрации статьи 1440×810 (@2 → 2880×1620) |
| `src/og-article.html`, `src/og-blog.html` | OG-карточки 1200×630 (@2 → 2400×1260, потом даунскейл до 1200×630) |
| `src/logo-dark.html`, `src/logo-light.html` | лок-апы словаря 900×160, прозрачный фон, обрезка по ink |
| `src/appicon.html` | app icon 512×512 на `--bg-1` |
| `render.js` | таблица JOBS: шаблон → размер → имя PNG |
| `postprocess.py` | webp q90/88, PNG-даунскейл OG, contain-fit лок-апов 312×48, фавиконы/ico, apple-touch-icon |

## Что попадает в репозиторий (21 файл)

```
images/blog/<slug>/fig-1-architecture.webp   2880×1620
images/blog/<slug>/fig-2-terminal.webp       2880×1620
images/blog/<slug>/fig-3-benchmarks.webp     2880×1620
images/blog/<slug>/cover.webp                2880×1620
images/blog/<slug>/og.png                    1200×630
assets/og/default.png                        1200×630
assets/og/default@2x.png                     2400×1260
assets/og/article-default.png                1200×630
assets/og/article-default@2x.png             2400×1260
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

1. Скопировать `src/fig1.html` → `src/<что-то>.html` и поправить разметку/текст.
2. Добавить строку в `JOBS` в `render.js` (`['<что-то>.html', 1440, 810, 2, '<имя>.png', false]`).
3. Добавить вызов в `postprocess.py`:
   `webp('<имя>.png', f'{IMG}/<имя>.webp')`.
4. Запушить — workflow отрендерит и закоммитит; для другого slug запускать вручную
   с параметром `slug`.

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
