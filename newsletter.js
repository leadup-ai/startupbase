/* startupbase.uno · подписка на дайджест (n8n webhook)
   Простой POST `application/x-www-form-urlencoded` без кастомных заголовков —
   браузер отправляет его как simple request, без CORS-preflight.
   Endpoint, поля и состояния описаны в README.md, раздел «Подписка на дайджест». */
(function () {
  'use strict';

  if (!window.fetch || !window.URLSearchParams || !document.querySelector) return;

  var ENDPOINT = 'https://n8n.flowstudio.cloud/webhook/blog-newsletter-subscribe';
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var BANNER_CLASS = { ok: 'ns-success', err: 'ns-error' };
  var ICONS = {
    ok: '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M3.2 8.4l3 3 6.6-7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    err: '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 4.9v3.7M8 10.6v1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
  };

  function esc(value) {
    return String(value).replace(/[&<>"']/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  }

  /* Слаг страницы: «/» → index, «/category.html» → category, «/<slug>/» → <slug> */
  function pageSlug() {
    var path = location.pathname.replace(/\/+$/, '');
    var seg = path.substring(path.lastIndexOf('/') + 1).replace(/\.html$/, '');
    return seg || 'index';
  }

  /* Полный URL страницы: canonical, если он есть, иначе текущий адрес */
  function sourceUrl() {
    var canonical = document.querySelector('link[rel="canonical"]');
    if (canonical && canonical.href) return canonical.href;
    return location.origin + location.pathname;
  }

  function banner(kind, title, text) {
    return '<div class="ns-status ' + BANNER_CLASS[kind] + '">' +
      '<span class="ico">' + ICONS[kind] + '</span>' +
      '<span class="txt"><b>' + title + '</b><span>' + text + '</span></span>' +
      '</div>';
  }

  function bind(form) {
    var box = form.parentNode.querySelector('.nl-status');
    var fieldErr = form.parentNode.querySelector('.field-err');
    var input = form.querySelector('input[name="email"]') || form.querySelector('.input');
    var btn = form.querySelector('.btn');
    var btnLabel = btn ? btn.textContent : '';
    var busy = false;

    if (!box || !input) return;

    function showFieldError() {
      input.classList.add('err');
      if (fieldErr) fieldErr.hidden = false;
      box.innerHTML = '';
      input.focus();
    }

    function clearFieldError() {
      input.classList.remove('err');
      if (fieldErr) fieldErr.hidden = true;
    }

    function setBusy(state) {
      busy = state;
      if (!btn) return;
      btn.disabled = state;
      btn.textContent = state ? 'Отправляем…' : btnLabel;
    }

    function fail(message) {
      setBusy(false);
      box.innerHTML = banner('err', 'Не получилось подписать', message ||
        'Что-то пошло не так на нашей стороне. Попробуйте ещё раз через минуту или напишите <a href="mailto:hello@leadup.guru">hello@leadup.guru</a>.');
    }

    input.addEventListener('input', function () {
      if (busy) return;
      clearFieldError();
      box.innerHTML = '';
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (busy) return;

      var email = (input.value || '').trim();
      if (!EMAIL_RE.test(email)) {
        showFieldError();
        return;
      }

      clearFieldError();
      box.innerHTML = '';
      setBusy(true);

      fetch(ENDPOINT, {
        method: 'POST',
        body: new URLSearchParams({ email: email, slug: pageSlug(), source_url: sourceUrl() })
      }).then(function (response) {
        return response.text().then(function (raw) {
          try { return JSON.parse(raw); } catch (error) { return null; }
        });
      }).then(function (data) {
        if (data && data.status === 'ok') {
          box.innerHTML = banner('ok', 'Готово! Подписка оформлена',
            'Дайджест будет приходить на <strong>' + esc(email) + '</strong> — раз в неделю, без спама.');
          setBusy(false);
          form.hidden = true;
          return;
        }
        if (data && data.status === 'error' && data.message === 'invalid_email') {
          setBusy(false);
          showFieldError();
          return;
        }
        fail();
      }).catch(function () {
        fail();
      });
    });
  }

  function init() {
    var forms = document.querySelectorAll('.newsletter form.form');
    for (var i = 0; i < forms.length; i++) bind(forms[i]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
