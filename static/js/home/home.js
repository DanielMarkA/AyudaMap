document.addEventListener("DOMContentLoaded", () => {
    let resources = [];
    const mapDataEl = document.getElementById("mapDataJson");
    if (mapDataEl) {
        try {
            resources = JSON.parse(mapDataEl.textContent);
        } catch (e) {
            console.error("Error parsing map data JSON:", e);
        }
    }

    const mapContainer = document.getElementById("ayudaMapViewport");
    let map = null;
    let tileLayer = null;
    let userLocationMarker = null;
    let clickPickerMarker = null;
    const markers = {};
    const group = [];
    let userMapConfig = { lat: 10.3157, lng: 123.8854, zoom: 12 };
    
    const mapCfgEl = document.getElementById("userMapConfigJson");
    if (mapCfgEl) {
        try { userMapConfig = JSON.parse(mapCfgEl.textContent); } catch (e) {}
    }

    const escapeHtml = (value) => {
        if (value === null || value === undefined) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    };

    const prefersReducedMotion = () =>
        window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const statusLiveEl = document.getElementById("mapStatusLive");
    const announceMapStatus = (msg) => {
        if (statusLiveEl) {
            statusLiveEl.textContent = "";
            setTimeout(() => { statusLiveEl.textContent = msg; }, 50);
        }
    };

    const cartoApiKey = (userMapConfig.carto_api_key || '').trim();
    const createTileLayer = (isDark) => {
        if (cartoApiKey) {
            const base = isDark
                ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
                : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
            return L.tileLayer(`${base}?key=${encodeURIComponent(cartoApiKey)}`, {
                maxZoom: 19,
                subdomains: 'abcd',
                attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
            });
        }
        return L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        });
    };

    if (mapContainer && typeof L === "undefined") {
        mapContainer.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;padding:1.5rem;text-align:center;color:var(--text-muted);font-size:0.95rem;">Map tiles could not load (offline or CDN unavailable). You can still browse and update aid centers in the directory.</div>';
    }

    if (mapContainer && typeof L !== "undefined") {
        const isDark = document.documentElement.classList.contains("dark-mode");
        const defaultCenter = resources.length > 0 && resources[0].lat
            ? [resources[0].lat, resources[0].lng]
            : [userMapConfig.lat, userMapConfig.lng];

        mapContainer.classList.toggle('map-osm-fallback', !cartoApiKey);
        map = L.map('ayudaMapViewport').setView(defaultCenter, userMapConfig.zoom || 12);

        tileLayer = createTileLayer(isDark).addTo(map);

        if (cartoApiKey) {
            window.addEventListener("themeChanged", (e) => {
                if (map && tileLayer) {
                    map.removeLayer(tileLayer);
                    tileLayer = createTileLayer(e.detail.isDark).addTo(map);
                }
            });
        }

        const getCategoryColor = (cat) => {
            switch (cat) {
                case 'MEDICAL': return '#ef4444';
                case 'FOOD': return '#f59e0b';
                case 'SHELTER': return '#3b82f6';
                case 'GOV': return '#8b5cf6';
                case 'DONATION': return '#047857';
                default: return '#0d9488';
            }
        };

        const getCategoryIconClass = (cat) => {
            switch (cat) {
                case 'MEDICAL': return 'fa-hospital';
                case 'FOOD': return 'fa-bowl-food';
                case 'SHELTER': return 'fa-tents';
                case 'GOV': return 'fa-building-columns';
                case 'DONATION': return 'fa-hand-holding-dollar';
                default: return 'fa-location-dot';
            }
        };

        const getStatusBadge = (status, statusDisplay) => {
            let bg = '#2e7d32';
            if (status === 'LIMITED') bg = '#c2410c';
            else if (status === 'CLOSED') bg = '#c62828';
            return `<span class="ayuda-popup-status" style="background: ${bg};">${escapeHtml(statusDisplay || status)}</span>`;
        };

        resources.forEach(res => {
            if (res.lat && res.lng) {
                const color = getCategoryColor(res.category_code);
                const iconClass = getCategoryIconClass(res.category_code);

                const customIcon = L.divIcon({
                    className: 'custom-map-pin',
                    html: `<div class="ayuda-pin-circle" style="background-color: ${color};"><i class="fa-solid ${iconClass}"></i></div>`,
                    iconSize: [28, 28],
                    iconAnchor: [14, 14]
                });

                const services = Array.isArray(res.services) ? res.services : [];
                const servicesHtml = services.length
                    ? `<p style="margin: 4px 0; font-size: 0.8rem; color: var(--text-primary);"><strong>Available:</strong> ${escapeHtml(services.join(', '))}</p>`
                    : '';

                const hoursSuffix = res.is_auto_closed && res.opens_at_display
                    ? ` (Closed · Opens ${escapeHtml(res.opens_at_display)})`
                    : '';

                const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(res.lat)},${encodeURIComponent(res.lng)}`;

                const popupContent = `
                    <div style="font-family: system-ui, sans-serif; min-width: 230px; padding: 4px; color: var(--text-primary);">
                        <h4 style="margin: 0 0 5px 0; font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">${escapeHtml(res.name)}</h4>
                        <div style="margin-bottom: 7px;">
                            <span class="category-badge cat-${escapeHtml(String(res.category_code || '').toLowerCase())}">${escapeHtml(res.category)}</span>
                            ${getStatusBadge(res.status, res.status_display)}
                        </div>
                        ${servicesHtml}
                        <p style="margin: 4px 0; font-size: 0.85rem; color: var(--text-muted);"><i class="fa-solid fa-location-dot"></i> ${escapeHtml(res.location)}</p>
                        <p style="margin: 4px 0; font-size: 0.85rem; color: var(--text-muted);"><i class="fa-solid fa-clock"></i> ${escapeHtml(res.operating_hours)}${hoursSuffix}</p>
                        ${res.contact_info ? `<p style="margin: 4px 0; font-size: 0.85rem; color: var(--text-muted);"><i class="fa-solid fa-phone"></i> ${escapeHtml(res.contact_info)}</p>` : ''}
                        <p style="margin: 6px 0 6px 0; font-size: 0.8rem; color: var(--primary-text); font-weight: 600;"><i class="fa-solid fa-thumbs-up"></i> ${escapeHtml(res.confirmations)} community confirmations</p>
                        <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 5px; font-size: 0.82rem; font-weight: 600; color: var(--primary-text); text-decoration: none;"><i class="fa-solid fa-diamond-turn-right"></i> Get Directions &rarr;</a>
                    </div>
                `;

                const marker = L.marker([res.lat, res.lng], { icon: customIcon })
                    .bindPopup(popupContent)
                    .addTo(map);

                marker.on("click", () => {
                    const card = document.getElementById(`resource-card-${res.id}`);
                    if (card) {
                        document.querySelectorAll(".resource-card, .resource-row").forEach(c => c.classList.remove("card-highlighted"));
                        card.classList.add("card-highlighted");
                        if (card.tagName === "DETAILS") {
                            card.open = true;
                        }
                        card.scrollIntoView({ behavior: prefersReducedMotion() ? "auto" : "smooth", block: "center" });
                    }
                });

                markers[res.id] = marker;
                group.push([res.lat, res.lng]);
            }
        });

        if (group.length > 1) {
            map.fitBounds(group, { padding: [35, 35] });
        }

        document.querySelectorAll(".pan-to-pin-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const lat = parseFloat(btn.dataset.lat);
                const lng = parseFloat(btn.dataset.lng);
                const id = btn.dataset.id;

                if (!isNaN(lat) && !isNaN(lng)) {
                    const animate = !prefersReducedMotion();
                    map.flyTo([lat, lng], 15, { animate, duration: animate ? 0.8 : 0 });
                    if (id && markers[id]) {
                        setTimeout(() => markers[id].openPopup(), animate ? 820 : 50);
                    }
                }
            });
        });

        document.querySelectorAll(".resource-card, .resource-row").forEach(card => {
            const handleSelect = (e) => {
                if (e.target.closest("button, a, select, input, form, label")) {
                    return;
                }
                const lat = parseFloat(card.dataset.lat);
                const lng = parseFloat(card.dataset.lng);
                const id = card.dataset.id;

                document.querySelectorAll(".resource-card, .resource-row").forEach(c => c.classList.remove("card-highlighted"));
                card.classList.add("card-highlighted");

                if (!isNaN(lat) && !isNaN(lng)) {
                    const animate = !prefersReducedMotion();
                    map.flyTo([lat, lng], 14, { animate, duration: animate ? 0.7 : 0 });
                    if (id && markers[id]) {
                        setTimeout(() => markers[id].openPopup(), animate ? 720 : 50);
                    }
                }
            };
            card.addEventListener("click", handleSelect);
        });

        const locateBtn = document.getElementById("locateMeBtn");
        if (locateBtn && navigator.geolocation) {
            locateBtn.addEventListener("click", () => {
                locateBtn.disabled = true;
                locateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> Locating...';

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const userLat = position.coords.latitude;
                        const userLng = position.coords.longitude;

                        const animate = !prefersReducedMotion();
                        map.flyTo([userLat, userLng], 14, { animate, duration: animate ? 1.0 : 0 });

                        if (userLocationMarker) {
                            userLocationMarker.setLatLng([userLat, userLng]);
                        } else {
                            const userIcon = L.divIcon({
                                className: 'user-location-pin',
                                html: `<div class="ayuda-pin-user"><i class="fa-solid fa-user"></i></div>`,
                                iconSize: [22, 22],
                                iconAnchor: [11, 11]
                            });

                            userLocationMarker = L.marker([userLat, userLng], { icon: userIcon })
                                .bindPopup("<div style='font-size: 13px; font-weight: bold;'>You Are Here</div>")
                                .addTo(map);
                        }

                        setTimeout(() => userLocationMarker.openPopup(), 1200);
                        announceMapStatus("Map centered on your current location.");
                        locateBtn.disabled = false;
                        locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs" aria-hidden="true"></i> Located!';
                        setTimeout(() => {
                            locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs" aria-hidden="true"></i> Locate Me';
                        }, 3000);
                    },
                    () => {
                        announceMapStatus("Could not access your location. Please check browser permissions.");
                        locateBtn.disabled = false;
                        locateBtn.innerHTML = '<i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i> Location Denied';
                        setTimeout(() => {
                            locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs" aria-hidden="true"></i> Locate Me';
                        }, 3500);
                    },
                    { timeout: 10000 }
                );
            });
        }

        map.on('click', (e) => {
            const modal = document.getElementById("addResourceModal");
            const latInput = document.querySelector("#addResourceModal input[name='latitude']");
            const lngInput = document.querySelector("#addResourceModal input[name='longitude']");

            if (modal && modal.style.display === "flex" && latInput && lngInput) {
                latInput.value = e.latlng.lat.toFixed(6);
                lngInput.value = e.latlng.lng.toFixed(6);

                if (clickPickerMarker) {
                    clickPickerMarker.setLatLng(e.latlng);
                } else {
                    clickPickerMarker = L.marker(e.latlng, {
                        icon: L.divIcon({
                            className: 'picker-pin',
                            html: `<div class="ayuda-pin-picker"><i class="fa-solid fa-crosshairs"></i></div>`,
                            iconSize: [24, 24],
                            iconAnchor: [12, 12]
                        })
                    }).addTo(map);
                }
            }
        });
    }

    const modal = document.getElementById("addResourceModal");
    const openBtn = document.getElementById("openAddModalBtn");
    const closeBtn = document.getElementById("closeAddModalBtn");
    const cancelBtn = document.getElementById("cancelAddModalBtn");
    const modalGpsBtn = document.getElementById("modalGpsBtn");
    const addResourceForm = document.getElementById("addResourceForm");
    const saveResourceBtn = document.getElementById("saveResourceBtn");

    if (modal && openBtn) {
        let lastFocusedEl = null;

        const getFocusable = () => Array.from(
            modal.querySelectorAll('button:not([disabled]), [href], input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])')
        );

        const openModal = () => {
            lastFocusedEl = document.activeElement;
            modal.style.display = "flex";
            modal.setAttribute("aria-hidden", "false");
            if (map) {
                setTimeout(() => map.invalidateSize(), 200);
            }
            const firstInput = modal.querySelector("input:not([type='hidden']), select, textarea");
            if (firstInput) firstInput.focus();
        };

        const closeModal = () => {
            modal.style.display = "none";
            modal.setAttribute("aria-hidden", "true");
            if (clickPickerMarker && map) {
                map.removeLayer(clickPickerMarker);
                clickPickerMarker = null;
            }
            if (lastFocusedEl && typeof lastFocusedEl.focus === "function") {
                lastFocusedEl.focus();
            }
        };

        document.querySelectorAll("#openAddModalBtn, .btn-hero").forEach(btn => {
            btn.addEventListener("click", openModal);
        });
        if (closeBtn) closeBtn.addEventListener("click", closeModal);
        if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

        window.addEventListener("click", (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        document.addEventListener("keydown", (e) => {
            if (modal.style.display !== "flex") return;
            if (e.key === "Escape") {
                e.preventDefault();
                closeModal();
                return;
            }
            if (e.key === "Tab") {
                const focusable = getFocusable();
                if (!focusable.length) return;
                const first = focusable[0];
                const last = focusable[focusable.length - 1];
                if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                } else if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        });
    }

    if (addResourceForm && saveResourceBtn) {
        addResourceForm.addEventListener("submit", () => {
            saveResourceBtn.disabled = true;
            saveResourceBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> Saving...';
        });
    }

    const is247Checkbox = document.querySelector("#addResourceModal input[name='is_24_7']");
    const opensAtInput = document.querySelector("#addResourceModal input[name='opens_at']");
    const closesAtInput = document.querySelector("#addResourceModal input[name='closes_at']");
    if (is247Checkbox && opensAtInput && closesAtInput) {
        const syncHoursInputs = () => {
            const disabled = is247Checkbox.checked;
            opensAtInput.disabled = disabled;
            closesAtInput.disabled = disabled;
        };
        is247Checkbox.addEventListener("change", syncHoursInputs);
        syncHoursInputs();
    }

    const mapFilterMenu = document.getElementById("mapFilterMenu");
    if (mapFilterMenu) {
        document.addEventListener("click", (e) => {
            if (mapFilterMenu.open && !mapFilterMenu.contains(e.target)) {
                mapFilterMenu.removeAttribute("open");
            }
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && mapFilterMenu.open) {
                mapFilterMenu.removeAttribute("open");
                const summary = mapFilterMenu.querySelector("summary");
                if (summary) summary.focus();
            }
        });
    }

    const ledgerItems = Array.from(document.querySelectorAll(".ledger-item"));
    if (ledgerItems.length) {
        ledgerItems.forEach((item) => {
            item.addEventListener("toggle", () => {
                if (item.open) {
                    ledgerItems.forEach((other) => {
                        if (other !== item && other.open) other.removeAttribute("open");
                    });
                }
            });
        });
        document.addEventListener("click", (e) => {
            ledgerItems.forEach((item) => {
                if (item.open && !item.contains(e.target)) {
                    item.removeAttribute("open");
                }
            });
        });
        document.addEventListener("keydown", (e) => {
            if (e.key !== "Escape") return;
            const openItem = ledgerItems.find((item) => item.open);
            if (openItem) {
                openItem.removeAttribute("open");
                const summary = openItem.querySelector("summary");
                if (summary) summary.focus();
            }
        });
    }

    if (modalGpsBtn && navigator.geolocation) {
        modalGpsBtn.addEventListener("click", () => {
            modalGpsBtn.disabled = true;
            modalGpsBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i> Getting GPS coordinates...';

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const latInput = document.querySelector("#addResourceModal input[name='latitude']");
                    const lngInput = document.querySelector("#addResourceModal input[name='longitude']");
                    if (latInput && lngInput) {
                        latInput.value = pos.coords.latitude.toFixed(6);
                        lngInput.value = pos.coords.longitude.toFixed(6);
                    }
                    announceMapStatus("GPS coordinates filled into form.");
                    modalGpsBtn.disabled = false;
                    modalGpsBtn.innerHTML = '<i class="fa-solid fa-check" aria-hidden="true"></i> GPS Coordinates Applied!';
                    setTimeout(() => {
                        modalGpsBtn.innerHTML = '<i class="fa-solid fa-location-arrow" aria-hidden="true"></i> Use My Current GPS Coordinates';
                    }, 2500);
                },
                () => {
                    announceMapStatus("Unable to get current GPS location.");
                    modalGpsBtn.disabled = false;
                    modalGpsBtn.innerHTML = '<i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i> GPS Unavailable';
                    setTimeout(() => {
                        modalGpsBtn.innerHTML = '<i class="fa-solid fa-location-arrow" aria-hidden="true"></i> Use My Current GPS Coordinates';
                    }, 3500);
                },
                { timeout: 10000 }
            );
        });
    }
});