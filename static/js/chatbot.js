/**
 * Safety Lab — Scripted chatbot widget
 * No external dependencies. Reads language from localStorage (same key as i18n.js).
 * Sends lead form via AJAX POST to /contacts/ using Django CSRF token.
 */
(function () {
    'use strict';

    var LANG_KEY = 'safety-lab-lang';
    var T = {};  // filled after translation file loads

    /* ── Built-in fallback translations (used if JSON fetch fails / cached) ── */
    var FALLBACK = {
        ru: {
            toggleTitle: 'Чат с нами', headerTitle: 'Safety Lab',
            headerSubtitle: 'Обычно отвечаем сразу',
            welcome: 'Здравствуйте! 👋 Я помогу узнать о наших услугах или записаться на консультацию.',
            menuPrompt: 'Выберите, что вас интересует:',
            btnServices: 'Узнать про услуги', btnConsult: 'Получить консультацию',
            btnFaq: 'Частые вопросы', btnBack: '← Назад', btnContact: 'Связаться',
            servicesPrompt: 'Выберите услугу:',
            ifta: 'IFTA & Fuel Tax', iftaDesc: 'Квартальные отчёты по топливному налогу (IFTA), регистрация и соответствие во всех юрисдикциях.',
            irp: 'IRP & Registration', irpDesc: 'Пропорциональная регистрация, продления и оформление прицепов для межштатных перевозок.',
            ucr: 'UCR & Permits', ucrDesc: 'Единая регистрация перевозчиков (UCR) и разрешения штатов — всегда в срок.',
            fmcsa: 'FMCSA & Safety', fmcsaDesc: 'Соответствие по безопасности, поддержка CSA и готовность к аудиту DOT.',
            consultPrompt: 'Оставьте контакты — мы свяжемся в течение 24 часов.',
            labelName: 'Ваше имя *', labelEmail: 'Email *',
            placeholderName: 'Иван Иванов', placeholderEmail: 'ivan@company.com',
            btnSend: 'Отправить', sending: 'Отправляем…',
            successMsg: 'Спасибо! Мы скоро свяжемся с вами. ✅',
            errorMsg: 'Ошибка. Напишите на SafetyHazel@gmail.com',
            errorFill: 'Пожалуйста, заполните имя и email.',
            faqPrompt: 'Выберите вопрос:',
            faqQ1: 'Сколько стоят услуги?', faqA1: 'Стоимость зависит от размера парка. Оставьте заявку — подготовим индивидуальное предложение.',
            faqQ2: 'Как быстро начнёте работу?', faqA2: 'Большинство клиентов подключаются за 1–2 рабочих дня после консультации.',
            faqQ3: 'Работаете во всех 50 штатах?', faqA3: 'Да, лицензированы в каждом штате по IFTA, IRP, UCR и разрешениям.',
            faqQ4: 'Что если пропущу дедлайн?', faqA4: 'Напоминания и мониторинг 24/7 — 99,8% заявок сданы в срок.',
            btnTelegram: '💬 Написать в Telegram',
            minimize: 'Свернуть'
        },
        en: {
            toggleTitle: 'Chat with us', headerTitle: 'Safety Lab',
            headerSubtitle: 'We usually reply instantly',
            welcome: 'Hello! 👋 I can help you learn about our services or schedule a consultation.',
            menuPrompt: 'What would you like to do?',
            btnServices: 'Learn about services', btnConsult: 'Get a consultation',
            btnFaq: 'FAQ', btnBack: '← Back', btnContact: 'Contact us',
            servicesPrompt: 'Choose a service:',
            ifta: 'IFTA & Fuel Tax', iftaDesc: 'Quarterly IFTA fuel tax reporting, registration and compliance across all jurisdictions.',
            irp: 'IRP & Registration', irpDesc: 'Apportioned registration, renewals, and trailer titling for interstate operations.',
            ucr: 'UCR & Permits', ucrDesc: 'Unified Carrier Registration and state permit filings, on time every time.',
            fmcsa: 'FMCSA & Safety', fmcsaDesc: 'Safety compliance, CSA support, and audit readiness for DOT requirements.',
            consultPrompt: 'Leave your details and we\'ll reach out within 24 hours.',
            labelName: 'Your name *', labelEmail: 'Email *',
            placeholderName: 'John Smith', placeholderEmail: 'john@company.com',
            btnSend: 'Send', sending: 'Sending…',
            successMsg: 'Thank you! We\'ll be in touch soon. ✅',
            errorMsg: 'Error. Please email SafetyHazel@gmail.com',
            errorFill: 'Please fill in your name and email.',
            faqPrompt: 'Choose a question:',
            faqQ1: 'How much do services cost?', faqA1: 'Pricing depends on fleet size. Submit a request and we\'ll prepare a custom quote.',
            faqQ2: 'How quickly can you start?', faqA2: 'Most clients are onboarded within 1–2 business days after consultation.',
            faqQ3: 'Do you work in all 50 states?', faqA3: 'Yes, licensed in every state for IFTA, IRP, UCR, and permits.',
            faqQ4: 'What if I miss a deadline?', faqA4: 'Reminders and 24/7 monitoring — 99.8% of filings are on time.',
            btnTelegram: '💬 Write on Telegram',
            minimize: 'Minimize'
        }
    };

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

    function getTgUrl() {
        var handle = (document.body || document.documentElement).getAttribute('data-tg-handle') || 'SafetyHazel';
        handle = handle.replace(/^@/, '');
        return 'https://t.me/' + handle;
    }

    function getCsrfToken() {
        var m = document.cookie.match(/csrftoken=([^;]+)/);
        return m ? m[1] : '';
    }

    /* ── Load translations ───────────────────────────────── */

    function applyFallback(lang) {
        T = FALLBACK[lang] || FALLBACK['ru'];
    }

    function loadTranslations(lang, cb) {
        applyFallback(lang);  // always set fallback first so t() never returns a key
        var url = getStaticBase() + 'translations/' + lang + '.json?v=6';
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.chatbot && Object.keys(data.chatbot).length > 0) {
                    T = data.chatbot;
                }
                cb();
            })
            .catch(function () {
                cb();
            });
    }

    function t(key) {
        return T[key] || (FALLBACK[getLang()] || FALLBACK['ru'])[key] || key;
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
            var el;
            if (btn.href) {
                // External link button (e.g. Telegram)
                el = document.createElement('a');
                el.className = 'chatbot-qr-btn chatbot-qr-btn--link';
                el.href = btn.href;
                el.target = '_blank';
                el.rel = 'noopener noreferrer';
                el.textContent = btn.label;
            } else {
                el = document.createElement('button');
                el.className = 'chatbot-qr-btn';
                el.textContent = btn.label;
                el.addEventListener('click', function () {
                    addMsg(btn.label, 'user');
                    clearReplies();
                    showTyping(btn.action);
                });
            }
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
                { label: t('btnTelegram'), href: getTgUrl()         },
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

        var leadUrl = window.location.origin + '/chatbot-lead/';

        fetch(leadUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken() },
            body: formData
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.ok) {
                clearReplies();
                addMsg(t('successMsg'), 'bot');
                showReplies([{ label: t('btnBack'), action: showMainMenu }]);
            } else {
                throw new Error(data.error || 'server error');
            }
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
