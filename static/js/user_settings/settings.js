// Settings Feature JavaScript
document.addEventListener("DOMContentLoaded", () => {
    // 1. Dark Mode Toggle
    const darkModeToggle = document.getElementById("dark_mode_toggle");
    const htmlElement = document.documentElement;

    if (darkModeToggle) {
        darkModeToggle.checked = htmlElement.classList.contains("dark-mode");

        darkModeToggle.addEventListener("change", (e) => {
            if (e.target.checked) {
                htmlElement.classList.add("dark-mode");
                localStorage.setItem("ayuda_theme", "dark");
            } else {
                htmlElement.classList.remove("dark-mode");
                localStorage.setItem("ayuda_theme", "light");
            }
            window.dispatchEvent(new CustomEvent("themeChanged", { detail: { isDark: e.target.checked } }));
        });
    }

    // 2. Eye Password Toggles
    document.querySelectorAll(".eye-toggle-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const input = btn.parentElement.querySelector("input");
            const icon = btn.querySelector("i");
            if (input) {
                if (input.type === "password") {
                    input.type = "text";
                    icon.classList.remove("fa-eye");
                    icon.classList.add("fa-eye-slash");
                } else {
                    input.type = "password";
                    icon.classList.remove("fa-eye-slash");
                    icon.classList.add("fa-eye");
                }
            }
        });
    });

    // 3. Form submission button spinners
    const forms = document.querySelectorAll(".settings-form");
    forms.forEach(form => {
        form.addEventListener("submit", () => {
            const submitBtn = form.querySelector("button[type='submit']");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
            }
        });
    });
});
