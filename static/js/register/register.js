// Register Feature JavaScript (Vertical Slice: register)
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("registerForm");
    const submitBtn = document.getElementById("registerSubmitBtn");

    if (form && submitBtn) {
        form.addEventListener("submit", () => {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Creating account...';
        });
    }
});

