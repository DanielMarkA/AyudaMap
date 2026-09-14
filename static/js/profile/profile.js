// Profile Feature JavaScript (Vertical Slice: profile)
document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector('input[type="file"]');
    const avatarPreview = document.getElementById("avatarPreview");
    const avatarPlaceholder = document.getElementById("avatarPlaceholder");
    const avatarContainer = document.querySelector(".profile-avatar-container");

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith("image/")) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    if (avatarPreview) {
                        avatarPreview.src = event.target.result;
                    } else if (avatarPlaceholder && avatarContainer) {
                        avatarPlaceholder.remove();
                        const newImg = document.createElement("img");
                        newImg.src = event.target.result;
                        newImg.className = "profile-avatar";
                        newImg.id = "avatarPreview";
                        avatarContainer.appendChild(newImg);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    const form = document.getElementById("profileForm");
    const saveBtn = document.getElementById("saveProfileBtn");
    if (form && saveBtn) {
        form.addEventListener("submit", () => {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
        });
    }
});

