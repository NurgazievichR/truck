// Minimal JavaScript for basic interactions

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    const body = document.body;

    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            const isOpen = mainNav.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active', isOpen);
            mobileMenuToggle.setAttribute('aria-expanded', isOpen);
            body.classList.toggle('menu-open', isOpen);
        });

        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                mainNav.classList.remove('active');
                mobileMenuToggle.classList.remove('active');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                body.classList.remove('menu-open');
            });
        });
    }

    // FAQ accordion
    document.querySelectorAll('[data-faq-toggle]').forEach(button => {
        button.addEventListener('click', function() {
            const expanded = this.getAttribute('aria-expanded') === 'true';
            const targetId = this.getAttribute('aria-controls');
            const target = targetId ? document.getElementById(targetId) : null;
            this.setAttribute('aria-expanded', !expanded);
            if (target) target.hidden = expanded;
        });
    });

    // На главной: при прокрутке вниз хедер плавно становится белым
    const header = document.querySelector('header');
    if (header && body.classList.contains('page-index')) {
        const scrollThreshold = 50;
        function updateHeaderScroll() {
            if (window.scrollY > scrollThreshold) {
                header.classList.add('header-scrolled');
            } else {
                header.classList.remove('header-scrolled');
            }
        }
        window.addEventListener('scroll', updateHeaderScroll, { passive: true });
        updateHeaderScroll();
    }

    // Hero slideshow
    var slides = document.querySelectorAll('.hero-slide');
    var dotsContainer = document.querySelector('.hero-dots');
    if (slides.length > 1 && dotsContainer) {
        var currentSlide = 0;
        var dots = [];

        slides.forEach(function (_, i) {
            var dot = document.createElement('button');
            dot.className = 'hero-dot' + (i === 0 ? ' is-active' : '');
            dot.setAttribute('aria-label', 'Slide ' + (i + 1));
            dot.addEventListener('click', function () { goToSlide(i); });
            dotsContainer.appendChild(dot);
            dots.push(dot);
        });

        function goToSlide(n) {
            slides[currentSlide].classList.remove('is-active');
            dots[currentSlide].classList.remove('is-active');
            currentSlide = n;
            slides[currentSlide].classList.add('is-active');
            dots[currentSlide].classList.add('is-active');
        }

        setInterval(function () {
            goToSlide((currentSlide + 1) % slides.length);
        }, 5000);
    }
});

