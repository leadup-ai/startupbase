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
