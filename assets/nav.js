/**
 * ScrollSpy and Navbar Active State Handler
 * Accurately tracks which of the 4 sections is in the viewport and updates the glowing active indicator.
 */
(function() {
    function initScrollSpy() {
        const navLinks = document.querySelectorAll('.nav-anchor-link');
        const sectionIds = ['procurement', 'production', 'inventory', 'costs', 'explainer'];
        const sections = sectionIds.map(id => document.getElementById(id)).filter(el => el !== null);

        if (navLinks.length === 0 || sections.length === 0) {
            setTimeout(initScrollSpy, 150);
            return;
        }

        function setActive(activeId) {
            navLinks.forEach(link => {
                const href = link.getAttribute('href') || '';
                const targetId = href.replace('#', '');
                if (targetId === activeId) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        // Click handler for instantaneous feedback
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href') || '';
                const targetId = href.replace('#', '');
                if (targetId) {
                    setActive(targetId);
                }
            });
        });

        // Scroll handler with viewport geometry calculation
        function updateActiveOnScroll() {
            const scrollY = window.scrollY;
            const windowHeight = window.innerHeight;
            const docHeight = document.documentElement.scrollHeight;

            // If at the very bottom of the page, activate the last section (explainer)
            if (scrollY + windowHeight >= docHeight - 80) {
                setActive('explainer');
                return;
            }

            // Trigger line: 200px below the top of the viewport
            const triggerLine = 200;
            let currentSection = sectionIds[0];

            for (let i = 0; i < sections.length; i++) {
                const sec = sections[i];
                const rect = sec.getBoundingClientRect();
                if (rect.top <= triggerLine) {
                    currentSection = sec.getAttribute('id');
                }
            }

            setActive(currentSection);
        }

        window.addEventListener('scroll', updateActiveOnScroll, { passive: true });
        // Initial run
        updateActiveOnScroll();
    }

    function initHorizontalScrollFallback() {
        const track = document.getElementById('machine-scroll-track');
        const strip = document.getElementById('machine-horizontal-strip');
        if (!track || !strip) {
            setTimeout(initHorizontalScrollFallback, 150);
            return;
        }

        // If native CSS scroll-driven animation is supported, let the browser GPU handle it directly!
        const supportsNativeScrollTimeline = (window.CSS && CSS.supports && (CSS.supports('animation-timeline', 'view()') || CSS.supports('animation-timeline', 'scroll()')));
        if (supportsNativeScrollTimeline) {
            return;
        }

        function updateHorizontalPosition() {
            const rect = track.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            const startY = 80;
            const totalDistance = track.offsetHeight - windowHeight + startY;
            if (totalDistance <= 0) return;

            const currentY = startY - rect.top;
            const progress = Math.max(0, Math.min(1, currentY / totalDistance));
            strip.style.transform = `translateX(-${progress * 75}%)`;
        }

        window.addEventListener('scroll', updateHorizontalPosition, { passive: true });
        updateHorizontalPosition();
    }

    function initTitleScaleFallback() {
        const titles = document.querySelectorAll('.interactive-title');
        if (!titles.length) {
            setTimeout(initTitleScaleFallback, 150);
            return;
        }

        const supportsNativeScrollTimeline = (window.CSS && CSS.supports && (CSS.supports('animation-timeline', 'view()') || CSS.supports('animation-timeline', 'scroll()')));
        if (supportsNativeScrollTimeline) {
            return;
        }

        function updateTitleScales() {
            const windowHeight = window.innerHeight;
            titles.forEach(title => {
                const rect = title.getBoundingClientRect();
                const progress = (windowHeight - rect.top) / (windowHeight + rect.height);
                if (progress >= 0 && progress <= 1) {
                    let scale = 0.85;
                    let opacity = 0.5;
                    if (progress >= 0.3 && progress <= 0.7) {
                        scale = 1.15;
                        opacity = 1.0;
                    } else if (progress < 0.3) {
                        const ratio = progress / 0.3;
                        scale = 0.85 + (1.15 - 0.85) * ratio;
                        opacity = 0.5 + 0.5 * ratio;
                    } else {
                        const ratio = (progress - 0.7) / 0.3;
                        scale = 1.15 - (1.15 - 0.88) * ratio;
                        opacity = 1.0 - 0.5 * ratio;
                    }
                    title.style.transform = `scale(${scale.toFixed(3)})`;
                    title.style.opacity = opacity.toFixed(2);
                }
            });
        }

        window.addEventListener('scroll', updateTitleScales, { passive: true });
        updateTitleScales();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initScrollSpy();
            initHorizontalScrollFallback();
            initTitleScaleFallback();
        });
    } else {
        initScrollSpy();
        initHorizontalScrollFallback();
        initTitleScaleFallback();
    }
})();
