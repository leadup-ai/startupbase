# startupbase.uno — блог

Статический блог на GitHub Pages, домен **https://blog.startupbase.uno**.

## Структура

| Путь | Назначение |
| --- | --- |
| `index.html` | главная страница блога |
| `category.html` | страница рубрики |
| `search.html` | поиск по статьям (клиентский, `noindex`) |
| `author.html` | страница автора |
| `404.html` | страница «не найдено» |
| `<slug>/index.html` | HTML-страница статьи (например `meta-muse-spark-open-weights-agents/`) |
| `content/posts/<slug>.md` | исходник статьи (markdown + frontmatter) |
| `colors_and_type.css`, `blog.css` | токены и стили из UI-кита дизайн-системы |

## Источник дизайна

Вёрстка собрана из UI-кита `ui_kits/blog/` репозитория `leadup-ai/LeadUp-AI-Design-System`
(LeadUp AI — Design System v3, D2 Cold Technical, акцент `--teal #00E5C7`).
Файл `colors_and_type.css` — дословная копия токенов дизайн-системы, `blog.css` — копия
`ui_kits/blog/blog.css` плюс блок дополнений для этого сайта.

## Правило публикации

Опубликованной считается статья, у которой есть и markdown-источник в `content/posts/`,
и HTML-страница в `<slug>/index.html`. Обновляй `sitemap.xml` при добавлении страницы.

## Публикация статьи

1. Текст статьи — `content/posts/<slug>.md` с YAML frontmatter (title, slug, locale, description, meta_title, meta_description, primary_keyword, secondary_keywords, category, author, reading_minutes, tags).
2. Канонический URL — `https://blog.startupbase.uno/<slug>/`; страница статьи лежит в `/<slug>/index.html`.
3. Заголовок H1 и все заголовки в списках берутся из `title` во frontmatter; `<title>`/`og:title` — из `meta_title`.
4. Картинки статьи — `images/blog/<slug>/` (cover.webp 16:9, fig-N-*.webp, og.png 1200×630).
5. OG-карточки — `assets/og/default.png` (страницы блога) и `images/blog/<slug>/og.png` (статья).
6. Иконки в корне — `favicon.svg`, `favicon.ico`, `favicon-32.png`, `apple-touch-icon.png`.
7. После публикации: добавить URL в `sitemap.xml` и обновить карточки в index.html / category.html / author.html / search.html / 404.html.
8. Бинарные ассеты пересобираются workflow `.github/workflows/render-assets.yml` из `tools/assets/`.
