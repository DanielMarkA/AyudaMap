// Login Feature JavaScript
document.addEventListener("DOMContentLoaded", () => {
    // 1. Eye Password Toggle
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


    // 3. Form Submit Feedback
    const loginForm = document.getElementById("loginForm");
    const loginBtn = document.getElementById("loginSubmitBtn");
    if (loginForm && loginBtn) {
        loginForm.addEventListener("submit", () => {
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Signing in...';
        });
    }
});
