/**
 * Client-side i18n: JSON dictionaries, localStorage, instant switch without reload.
 * Default language: Russian (ru). Add more languages by adding xx.json and using data-lang="xx".
 */
(function() {
    var STORAGE_KEY = 'safety-lab-lang';
    var DEFAULT_LANG = 'ru';

    function getLang() {
        var stored = localStorage.getItem(STORAGE_KEY);
        return stored === 'en' || stored === 'ru' ? stored : DEFAULT_LANG;
    }

    function setLang(lang) {
        localStorage.setItem(STORAGE_KEY, lang);
    }

    function getNested(obj, path) {
        var keys = path.split('.');
        var cur = obj;
        for (var i = 0; i < keys.length && cur != null; i++) cur = cur[keys[i]];
        return cur;
    }

    function getTranslationsBase() {
        var el = document.body || document.documentElement;
        var base = el.getAttribute('data-static-url') || '';
        if (base.length && base[base.length - 1] !== '/') base += '/';
        return base + 'translations/';
    }

    function loadTranslations(lang) {
        var base = getTranslationsBase();
        var url = base + lang + '.json';
        return fetch(url).then(function(r) {
            if (!r.ok) throw new Error('Translations failed: ' + lang);
            return r.json();
        });
    }

    function applyTranslations(t) {
        if (!t) return;
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var key = el.getAttribute('data-i18n');
            var value = getNested(t, key);
            if (value != null && typeof value === 'string') el.textContent = value;
        });
    }

    function updateLangButtons(lang) {
        document.documentElement.lang = lang === 'ru' ? 'ru' : 'en';
        document.querySelectorAll('.lang-btn').forEach(function(btn) {
            var isActive = btn.getAttribute('data-lang') === lang;
            btn.setAttribute('aria-pressed', isActive);
        });
    }

    function switchLanguage(lang) {
        setLang(lang);
        loadTranslations(lang).then(function(t) {
            applyTranslations(t);
            updateLangButtons(lang);
        }).catch(function() {
            updateLangButtons(lang);
        });
    }

    function init() {
        var lang = getLang();
        loadTranslations(lang).then(function(t) {
            applyTranslations(t);
            updateLangButtons(lang);
        }).catch(function() {
            updateLangButtons(lang);
        });

        document.querySelectorAll('.lang-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var newLang = this.getAttribute('data-lang');
                if (newLang) switchLanguage(newLang);
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
