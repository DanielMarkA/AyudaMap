// AyudaMap Guest Landing Page — Smooth Scroll Cue
document.addEventListener("DOMContentLoaded", () => {
    const scrollCue = document.querySelector(".scroll-cue");
    const impactSection = document.getElementById("impact");
    if (!scrollCue || !impactSection) return;

    const header = document.querySelector(".app-header");
    const prefersReducedMotion = () =>
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    scrollCue.addEventListener("click", (e) => {
        e.preventDefault();
        const headerH = header ? header.offsetHeight : 64;
        const top = Math.max(0, impactSection.offsetTop - headerH);
        window.scrollTo({
            top,
            behavior: prefersReducedMotion() ? "auto" : "smooth",
        });
        const heading = document.getElementById("landing-impact-title") || impactSection;
        heading.setAttribute("tabindex", "-1");
        heading.focus({ preventScroll: true });
    });
});
