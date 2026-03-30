// Minimal JavaScript for basic interactions

document.addEventListener('DOMContentLoaded', function() {
    // Sticky header animation on scroll
    var header = document.querySelector('header');
    if (header) {
        var scrollThreshold = 24;
        function updateHeaderState() {
            if (window.scrollY > scrollThreshold) {
                header.classList.add('header-scrolled');
            } else {
                header.classList.remove('header-scrolled');
            }
        }
        window.addEventListener('scroll', updateHeaderState, { passive: true });
        updateHeaderState();
    }

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('translate-x-full');
        });
        if (mobileMenuClose) {
            mobileMenuClose.addEventListener('click', () => {
                mobileMenu.classList.add('translate-x-full');
            });
        }
        // close menu on clicking links
        mobileMenu.querySelectorAll('a').forEach(a => {
            a.addEventListener('click', () => {
                mobileMenu.classList.add('translate-x-full');
            });
        });
    }

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

