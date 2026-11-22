// AyudaMap Guest Landing Page — Smooth Chapter Scroll Controller
document.addEventListener("DOMContentLoaded", () => {
    const chapters = Array.from(document.querySelectorAll(".landing-chapter"));
    if (!chapters.length) return;

    const dotButtons = Array.from(document.querySelectorAll(".chapter-dot-btn"));
    const header = document.querySelector(".app-header");
    const prefersReducedMotion = () =>
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let currentIndex = 0;
    let isLocked = false;
    let unlockTimer = null;

    const getHeaderHeight = () => (header ? header.offsetHeight : 64);

    const setActiveDot = (index) => {
        currentIndex = index;
        dotButtons.forEach((btn, i) => {
            const active = i === index;
            btn.classList.toggle("active", active);
            btn.setAttribute("aria-current", active ? "true" : "false");
        });
    };

    const detectCurrentChapter = () => {
        const scrollMid = window.scrollY + getHeaderHeight() + window.innerHeight * 0.35;
        let activeIdx = 0;
        chapters.forEach((section, idx) => {
            if (section.offsetTop <= scrollMid) {
                activeIdx = idx;
            }
        });
        return activeIdx;
    };

    const scrollToChapter = (index) => {
        const clamped = Math.max(0, Math.min(chapters.length - 1, index));
        const target = chapters[clamped];
        if (!target) return;

        isLocked = true;
        clearTimeout(unlockTimer);
        setActiveDot(clamped);

        const top =
            clamped === chapters.length - 1
                ? Math.max(0, document.documentElement.scrollHeight - window.innerHeight)
                : Math.max(0, target.offsetTop - getHeaderHeight());
        window.scrollTo({
            top,
            behavior: prefersReducedMotion() ? "auto" : "smooth",
        });

        unlockTimer = setTimeout(() => {
            isLocked = false;
        }, 650);
    };

    // Keep chapter dots synced when scrolling via scrollbar, anchor links, or touch
    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            (entries) => {
                if (isLocked) return;
                entries.forEach((entry) => {
                    if (entry.isIntersecting && entry.intersectionRatio >= 0.45) {
                        const idx = chapters.indexOf(entry.target);
                        if (idx !== -1) setActiveDot(idx);
                    }
                });
            },
            { threshold: [0.45, 0.7] }
        );
        chapters.forEach((ch) => observer.observe(ch));
    }

    // Dot rail click handlers
    dotButtons.forEach((btn, idx) => {
        btn.addEventListener("click", () => scrollToChapter(idx));
    });

    // Hero scroll-cue link
    const scrollCue = document.querySelector(".scroll-cue");
    if (scrollCue) {
        scrollCue.addEventListener("click", (e) => {
            e.preventDefault();
            scrollToChapter(1);
        });
    }

    // Wheel chapter-jump on desktop (> 768px) when reduced motion is off
    window.addEventListener(
        "wheel",
        (e) => {
            if (window.innerWidth <= 768 || prefersReducedMotion()) return;
            if (e.ctrlKey || e.metaKey) return; // Allow browser pinch/ctrl zoom

            const delta = e.deltaY;
            if (Math.abs(delta) < 10) return;

            const activeIdx = detectCurrentChapter();
            const activeEl = chapters[activeIdx];
            const headerH = getHeaderHeight();
            const viewportH = window.innerHeight - headerH;

            // If the current chapter is taller than the viewport, allow internal scrolling until its edge
            if (activeEl && activeEl.offsetHeight > viewportH + 40) {
                const rect = activeEl.getBoundingClientRect();
                if (delta > 0 && rect.bottom > window.innerHeight + 16) return;
                if (delta < 0 && rect.top < headerH - 16) return;
            }

            // Allow scrolling down past the last chapter to view the footer, and back up from the footer
            const atLastChapter = activeIdx === chapters.length - 1;
            const atFirstChapter = activeIdx === 0;
            if (delta > 0 && atLastChapter) return;
            if (delta < 0 && atFirstChapter && window.scrollY <= 4) return;

            e.preventDefault();
            if (isLocked) return;

            const nextIdx = delta > 0 ? activeIdx + 1 : activeIdx - 1;
            scrollToChapter(nextIdx);
        },
        { passive: false }
    );

    // Keyboard PageDown / PageUp chapter jumping
    window.addEventListener("keydown", (e) => {
        if (window.innerWidth <= 768) return;
        const tag = document.activeElement?.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

        if (e.key === "PageDown") {
            const activeIdx = detectCurrentChapter();
            if (activeIdx < chapters.length - 1) {
                e.preventDefault();
                scrollToChapter(activeIdx + 1);
            }
        } else if (e.key === "PageUp") {
            const activeIdx = detectCurrentChapter();
            if (activeIdx > 0) {
                e.preventDefault();
                scrollToChapter(activeIdx - 1);
            }
        }
    });
});
