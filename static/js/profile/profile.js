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

    // 2. Accessible WAI-ARIA Profile Tabs (click + Left/Right/Home/End keyboard nav)
    const tabList = document.querySelector(".profile-tab-bar[role='tablist']");
    if (tabList) {
        const tabs = Array.from(tabList.querySelectorAll("[role='tab']"));
        const activateTab = (tab, moveFocus) => {
            tabs.forEach((t) => {
                const isSelected = t === tab;
                t.setAttribute("aria-selected", String(isSelected));
                t.setAttribute("tabindex", isSelected ? "0" : "-1");
                const panelId = t.getAttribute("aria-controls");
                const panel = panelId ? document.getElementById(panelId) : null;
                if (panel) {
                    panel.hidden = !isSelected;
                }
            });
            if (moveFocus) tab.focus();
        };

        tabs.forEach((tab, idx) => {
            tab.addEventListener("click", () => activateTab(tab, false));
            tab.addEventListener("keydown", (e) => {
                let nextIdx = null;
                if (e.key === "ArrowRight") nextIdx = (idx + 1) % tabs.length;
                else if (e.key === "ArrowLeft") nextIdx = (idx - 1 + tabs.length) % tabs.length;
                else if (e.key === "Home") nextIdx = 0;
                else if (e.key === "End") nextIdx = tabs.length - 1;
                if (nextIdx !== null) {
                    e.preventDefault();
                    activateTab(tabs[nextIdx], true);
                }
            });
        });
    }

    // 3. Form submission spinner
    const profileForm = document.getElementById("profileForm");
    const saveBtn = document.getElementById("saveProfileBtn");
    if (profileForm && saveBtn) {
        profileForm.addEventListener("submit", () => {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving changes...';
        });
    }
});
