// Profile Feature JavaScript
document.addEventListener("DOMContentLoaded", () => {
    // 1. Live Profile Photo Preview
    const imageInput = document.querySelector("input[type='file'][name='profile_image']");
    const avatarContainer = document.querySelector(".profile-avatar-container");
    const placeholder = document.getElementById("avatarPlaceholder");

    if (imageInput && avatarContainer) {
        imageInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file && file.type && file.type.startsWith("image/")) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    let previewImg = document.getElementById("avatarPreview");
                    if (!previewImg) {
                        previewImg = document.createElement("img");
                        previewImg.id = "avatarPreview";
                        previewImg.className = "profile-avatar";
                        previewImg.alt = "Profile photo preview";
                        avatarContainer.appendChild(previewImg);
                    }
                    previewImg.src = e.target.result;
                    previewImg.style.display = "block";
                    if (placeholder) {
                        placeholder.style.display = "none";
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 2. Form submission spinner
    const profileForm = document.getElementById("profileForm");
    const saveBtn = document.getElementById("saveProfileBtn");
    if (profileForm && saveBtn) {
        profileForm.addEventListener("submit", () => {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving changes...';
        });
    }
});
