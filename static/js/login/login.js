// Login Feature JavaScript (Vertical Slice: login)
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const submitBtn = document.getElementById("loginSubmitBtn");

    if (form && submitBtn) {
        form.addEventListener("submit", () => {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing in...';
        });
    }
});

