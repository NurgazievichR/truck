/**
 * Safety Lab — Scripted chatbot widget
 * No external dependencies. Reads language from localStorage (same key as i18n.js).
 * Sends lead form via AJAX POST to /contacts/ using Django CSRF token.
 */
(function () {
    'use strict';

    var LANG_KEY = 'safety-lab-lang';
    var T = {};  // filled after translation file loads

    /* ── Helpers ─────────────────────────────────────────── */

    function getLang() {
        var l = localStorage.getItem(LANG_KEY);
        return l === 'en' || l === 'ru' ? l : 'ru';
    }

    function getStaticBase() {
        var el = document.body || document.documentElement;
        var base = el.getAttribute('data-static-url') || '';
        if (base.length && base[base.length - 1] !== '/') base += '/';
        return base;
    }

    function getCsrfToken() {
        var m = document.cookie.match(/csrftoken=([^;]+)/);
        return m ? m[1] : '';
    }

    /* ── Load translations ───────────────────────────────── */

    function loadTranslations(lang, cb) {
        var url = getStaticBase() + 'translations/' + lang + '.json';
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                T = data.chatbot || {};
                cb();
            })
            .catch(function () {
                T = {};
                cb();
            });
    }

    function t(key) {
        return T[key] || key;
    }

    /* ── Build DOM ───────────────────────────────────────── */

    var toggleBtn, window_, messagesEl, quickRepliesEl, formEl;

    function buildWidget() {
        // Toggle button
        toggleBtn = document.createElement('button');
        toggleBtn.className = 'chatbot-toggle has-notification';
        toggleBtn.setAttribute('aria-label', t('toggleTitle'));
        toggleBtn.setAttribute('title', t('toggleTitle'));
        toggleBtn.innerHTML =
            '<svg class="icon-chat" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>' +
            '<svg class="icon-close" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';

        // Window
        window_ = document.createElement('div');
        window_.className = 'chatbot-window';
        window_.setAttribute('role', 'dialog');
        window_.setAttribute('aria-label', t('headerTitle'));
        window_.innerHTML =
            '<div class="chatbot-header">' +
            '  <div class="chatbot-header-avatar">💬</div>' +
            '  <div class="chatbot-header-info">' +
            '    <div class="chatbot-header-name">' + t('headerTitle') + '</div>' +
            '    <div class="chatbot-header-status">' + t('headerSubtitle') + '</div>' +
            '  </div>' +
            '</div>' +
            '<div class="chatbot-messages"></div>' +
            '<div class="chatbot-quick-replies"></div>';

        messagesEl = window_.querySelector('.chatbot-messages');
        quickRepliesEl = window_.querySelector('.chatbot-quick-replies');

        document.body.appendChild(toggleBtn);
        document.body.appendChild(window_);

        toggleBtn.addEventListener('click', toggleWidget);
    }

    /* ── Open / Close ────────────────────────────────────── */

    var isOpen = false;

    function toggleWidget() {
        isOpen ? closeWidget() : openWidget();
    }

    function openWidget() {
        isOpen = true;
        toggleBtn.classList.add('is-open');
        toggleBtn.classList.remove('has-notification');
        window_.classList.add('is-open');
        if (messagesEl.children.length === 0) startConversation();
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function closeWidget() {
        isOpen = false;
        toggleBtn.classList.remove('is-open');
        window_.classList.remove('is-open');
    }

    /* ── Messaging ───────────────────────────────────────── */

    function addMsg(text, who) {
        var el = document.createElement('div');
        el.className = 'chatbot-msg chatbot-msg--' + who;
        el.textContent = text;
        messagesEl.appendChild(el);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return el;
    }

    function showTyping(cb) {
        var dots = document.createElement('div');
        dots.className = 'chatbot-typing';
        dots.innerHTML = '<span></span><span></span><span></span>';
        messagesEl.appendChild(dots);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        setTimeout(function () {
            messagesEl.removeChild(dots);
            cb();
        }, 700);
    }

    function clearReplies() {
        quickRepliesEl.innerHTML = '';
        if (formEl && formEl.parentNode) formEl.parentNode.removeChild(formEl);
        formEl = null;
    }

    function showReplies(buttons) {
        clearReplies();
        buttons.forEach(function (btn) {
            var el = document.createElement('button');
            el.className = 'chatbot-qr-btn';
            el.textContent = btn.label;
            el.addEventListener('click', function () {
                addMsg(btn.label, 'user');
                clearReplies();
                showTyping(btn.action);
            });
            quickRepliesEl.appendChild(el);
        });
    }

    /* ── Scenarios ───────────────────────────────────────── */

    function startConversation() {
        showTyping(function () {
            addMsg(t('welcome'), 'bot');
            showMainMenu();
        });
    }

    function showMainMenu() {
        showTyping(function () {
            addMsg(t('menuPrompt'), 'bot');
            showReplies([
                { label: t('btnServices'), action: showServicesMenu },
                { label: t('btnConsult'),  action: showConsultForm  },
                { label: t('btnFaq'),      action: showFaqMenu      },
            ]);
        });
    }

    /* Services sub-menu */
    function showServicesMenu() {
        addMsg(t('servicesPrompt'), 'bot');
        showReplies([
            { label: t('ifta'),  action: function () { showServiceDetail('ifta');  } },
            { label: t('irp'),   action: function () { showServiceDetail('irp');   } },
            { label: t('ucr'),   action: function () { showServiceDetail('ucr');   } },
            { label: t('fmcsa'), action: function () { showServiceDetail('fmcsa'); } },
            { label: t('btnBack'), action: showMainMenu },
        ]);
    }

    function showServiceDetail(key) {
        addMsg(t(key + 'Desc'), 'bot');
        showReplies([
            { label: t('btnContact'), action: showConsultForm },
            { label: t('btnBack'),    action: showServicesMenu },
        ]);
    }

    /* FAQ sub-menu */
    function showFaqMenu() {
        addMsg(t('faqPrompt'), 'bot');
        showReplies([
            { label: t('faqQ1'), action: function () { showFaqAnswer('faqA1'); } },
            { label: t('faqQ2'), action: function () { showFaqAnswer('faqA2'); } },
            { label: t('faqQ3'), action: function () { showFaqAnswer('faqA3'); } },
            { label: t('faqQ4'), action: function () { showFaqAnswer('faqA4'); } },
            { label: t('btnBack'), action: showMainMenu },
        ]);
    }

    function showFaqAnswer(key) {
        addMsg(t(key), 'bot');
        showReplies([
            { label: t('btnConsult'), action: showConsultForm },
            { label: t('btnBack'),    action: showFaqMenu     },
        ]);
    }

    /* Consultation lead form */
    function showConsultForm() {
        addMsg(t('consultPrompt'), 'bot');
        clearReplies();

        formEl = document.createElement('div');
        formEl.className = 'chatbot-form';
        formEl.innerHTML =
            '<div class="chatbot-form-row">' +
            '  <label>' + t('labelName') + '</label>' +
            '  <input type="text" name="cb-name" placeholder="' + t('placeholderName') + '" autocomplete="name">' +
            '</div>' +
            '<div class="chatbot-form-row">' +
            '  <label>' + t('labelEmail') + '</label>' +
            '  <input type="email" name="cb-email" placeholder="' + t('placeholderEmail') + '" autocomplete="email">' +
            '</div>' +
            '<button class="chatbot-form-submit" type="button">' + t('btnSend') + '</button>';

        window_.appendChild(formEl);
        messagesEl.scrollTop = messagesEl.scrollHeight;

        var submitBtn = formEl.querySelector('.chatbot-form-submit');
        submitBtn.addEventListener('click', submitLead);
    }

    function submitLead() {
        var nameInput  = formEl.querySelector('[name="cb-name"]');
        var emailInput = formEl.querySelector('[name="cb-email"]');
        var submitBtn  = formEl.querySelector('.chatbot-form-submit');

        var name  = nameInput.value.trim();
        var email = emailInput.value.trim();

        if (!name || !email) {
            addMsg(t('errorFill'), 'bot');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = t('sending');

        var formData = new FormData();
        formData.append('name', name);
        formData.append('email', email);
        formData.append('description', getLang() === 'ru'
            ? 'Заявка через чат-бот'
            : 'Request via chatbot');

        // Get the contacts URL from the page's origin
        var contactsUrl = window.location.origin + '/contacts/';

        fetch(contactsUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken() },
            body: formData,
            redirect: 'manual'
        })
        .then(function () {
            clearReplies();
            addMsg(t('successMsg'), 'bot');
            showReplies([{ label: t('btnBack'), action: showMainMenu }]);
        })
        .catch(function () {
            submitBtn.disabled = false;
            submitBtn.textContent = t('btnSend');
            addMsg(t('errorMsg'), 'bot');
        });
    }

    /* ── Init ────────────────────────────────────────────── */

    function init() {
        loadTranslations(getLang(), function () {
            buildWidget();

            // Auto-open notification dot after 4s
            setTimeout(function () {
                if (!isOpen) toggleBtn.classList.add('has-notification');
            }, 4000);

            // Re-translate when language switch happens (storage event from i18n.js)
            window.addEventListener('storage', function (e) {
                if (e.key === LANG_KEY) {
                    loadTranslations(getLang(), function () {
                        // Update header texts
                        var nameEl = window_.querySelector('.chatbot-header-name');
                        var statusEl = window_.querySelector('.chatbot-header-status');
                        if (nameEl) nameEl.textContent = t('headerTitle');
                        if (statusEl) statusEl.textContent = t('headerSubtitle');
                    });
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
