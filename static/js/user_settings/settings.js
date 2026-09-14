// Settings Feature JavaScript (Vertical Slice: user_settings)
document.addEventListener("DOMContentLoaded", () => {
    const darkModeToggle = document.getElementById("dark_mode_toggle");
    const htmlElement = document.documentElement;

    if (darkModeToggle) {
        darkModeToggle.addEventListener("change", (e) => {
            if (e.target.checked) {
                htmlElement.classList.add("dark-mode");
            } else {
                htmlElement.classList.remove("dark-mode");
            }
        });
    }

    const form = document.getElementById("settingsForm");
    const saveBtn = document.getElementById("saveSettingsBtn");
    if (form && saveBtn) {
        form.addEventListener("submit", () => {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving preferences...';
        });
    }
});

