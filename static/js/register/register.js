// Register Feature JavaScript
document.addEventListener("DOMContentLoaded", () => {
    // 1. Eye Password Toggles
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

    // 2. Form Submit Feedback
    const registerForm = document.getElementById("registerForm");
    const registerBtn = document.getElementById("registerSubmitBtn");
    if (registerForm && registerBtn) {
        registerForm.addEventListener("submit", () => {
            registerBtn.disabled = true;
            registerBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating account...';
        });
    }
});
