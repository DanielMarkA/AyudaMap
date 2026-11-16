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

    const getTileUrl = (isDark) => {
        return isDark
            ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
            : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    };

    if (mapContainer && typeof L !== "undefined") {
        const isDark = document.documentElement.classList.contains("dark-mode");
        const defaultCenter = resources.length > 0 && resources[0].lat
            ? [resources[0].lat, resources[0].lng]
            : [10.3157, 123.8854];

        map = L.map('ayudaMapViewport').setView(defaultCenter, 12);

        tileLayer = L.tileLayer(getTileUrl(isDark), {
            maxZoom: 19,
            subdomains: 'abcd',
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }).addTo(map);

        window.addEventListener("themeChanged", (e) => {
            if (map && tileLayer) {
                map.removeLayer(tileLayer);
                tileLayer = L.tileLayer(getTileUrl(e.detail.isDark), {
                    maxZoom: 19,
                    subdomains: 'abcd',
                    attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
                }).addTo(map);
            }
        });

        const getCategoryColor = (cat) => {
            switch (cat) {
                case 'MEDICAL': return '#ef4444';
                case 'FOOD': return '#f59e0b';
                case 'SHELTER': return '#3b82f6';
                case 'GOV': return '#8b5cf6';
                case 'DONATION': return '#10b981';
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
            if (status === 'FULL_CAPACITY') bg = '#e65100';
            else if (status === 'TEMPORARILY_CLOSED') bg = '#c62828';
            return `<span style="display:inline-block; font-size: 10px; padding: 2px 6px; border-radius: 4px; background: ${bg}; color: white; font-weight: 700; margin-left: 4px;">${statusDisplay || status}</span>`;
        };

        resources.forEach(res => {
            if (res.lat && res.lng) {
                const color = getCategoryColor(res.category_code);
                const iconClass = getCategoryIconClass(res.category_code);
                const criticalClass = res.urgency === 'CRITICAL' ? 'pin-critical' : '';

                const customIcon = L.divIcon({
                    className: 'custom-map-pin',
                    html: `<div class="${criticalClass}" style="background-color: ${color}; width: 28px; height: 28px; border-radius: 50%; border: 2.5px solid white; box-shadow: 0 3px 8px rgba(0,0,0,0.38); display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; cursor: pointer;"><i class="fa-solid ${iconClass}"></i></div>`,
                    iconSize: [28, 28],
                    iconAnchor: [14, 14]
                });

                const suppliesHtml = res.supplies_needed
                    ? `<p style="margin: 4px 0; font-size: 11px; color: #b45309; font-weight: 600;"><i class="fa-solid fa-boxes-stacked"></i> Needed: ${res.supplies_needed}</p>`
                    : '';

                const popupContent = `
                    <div style="font-family: system-ui, sans-serif; min-width: 230px; padding: 4px;">
                        <h4 style="margin: 0 0 5px 0; font-size: 14px; font-weight: 700;">${res.name}</h4>
                        <div style="margin-bottom: 7px;">
                            <span style="display:inline-block; font-size: 11px; padding: 2px 6px; border-radius: 4px; background: #e0f2fe; color: #0284c7; font-weight: 600;">${res.category}</span>
                            ${getStatusBadge(res.status, res.status_display)}
                        </div>
                        <p style="margin: 4px 0; font-size: 12px; color: #334155;"><strong>Capacity:</strong> ${res.capacity_available} / ${res.capacity_total} slots</p>
                        ${suppliesHtml}
                        <p style="margin: 4px 0; font-size: 12px; color: #64748b;"><i class="fa-solid fa-location-dot"></i> ${res.location}</p>
                        <p style="margin: 4px 0; font-size: 12px; color: #64748b;"><i class="fa-solid fa-clock"></i> ${res.operating_hours}</p>
                        ${res.contact_info ? `<p style="margin: 4px 0; font-size: 12px; color: #64748b;"><i class="fa-solid fa-phone"></i> ${res.contact_info}</p>` : ''}
                        <p style="margin: 6px 0 0 0; font-size: 11px; color: #0d9488; font-weight: 600;"><i class="fa-solid fa-thumbs-up"></i> ${res.confirmations} community confirmations</p>
                    </div>
                `;

                const marker = L.marker([res.lat, res.lng], { icon: customIcon })
                    .bindPopup(popupContent)
                    .addTo(map);

                marker.on("click", () => {
                    const card = document.getElementById(`resource-card-${res.id}`);
                    if (card) {
                        document.querySelectorAll(".resource-card").forEach(c => c.classList.remove("card-highlighted"));
                        card.classList.add("card-highlighted");
                        card.scrollIntoView({ behavior: "smooth", block: "center" });
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
                    map.flyTo([lat, lng], 15, { animate: true, duration: 1 });
                    if (id && markers[id]) {
                        setTimeout(() => markers[id].openPopup(), 1000);
                    }
                }
            });
        });

        document.querySelectorAll(".resource-card").forEach(card => {
            card.addEventListener("click", () => {
                const lat = parseFloat(card.dataset.lat);
                const lng = parseFloat(card.dataset.lng);
                const id = card.dataset.id;

                document.querySelectorAll(".resource-card").forEach(c => c.classList.remove("card-highlighted"));
                card.classList.add("card-highlighted");

                if (!isNaN(lat) && !isNaN(lng)) {
                    map.flyTo([lat, lng], 14, { animate: true, duration: 0.8 });
                    if (id && markers[id]) {
                        setTimeout(() => markers[id].openPopup(), 850);
                    }
                }
            });
        });

        const locateBtn = document.getElementById("locateMeBtn");
        if (locateBtn && navigator.geolocation) {
            locateBtn.addEventListener("click", () => {
                locateBtn.disabled = true;
                locateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Locating...';

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const userLat = position.coords.latitude;
                        const userLng = position.coords.longitude;

                        map.flyTo([userLat, userLng], 14, { animate: true, duration: 1.2 });

                        if (userLocationMarker) {
                            userLocationMarker.setLatLng([userLat, userLng]);
                        } else {
                            const userIcon = L.divIcon({
                                className: 'user-location-pin',
                                html: `<div style="background-color: #0284c7; width: 22px; height: 22px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(2,132,199,0.8); display: flex; align-items: center; justify-content: center; color: white; font-size: 9px;"><i class="fa-solid fa-user"></i></div>`,
                                iconSize: [22, 22],
                                iconAnchor: [11, 11]
                            });

                            userLocationMarker = L.marker([userLat, userLng], { icon: userIcon })
                                .bindPopup("<div style='font-size: 13px; font-weight: bold;'>You Are Here</div>")
                                .addTo(map);
                        }

                        setTimeout(() => userLocationMarker.openPopup(), 1200);
                        locateBtn.disabled = false;
                        locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Located!';
                        setTimeout(() => {
                            locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Locate Me';
                        }, 3000);
                    },
                    () => {
                        alert("Could not access your location. Please check browser permissions.");
                        locateBtn.disabled = false;
                        locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Locate Me';
                    }
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
                            html: `<div style="background-color: #0d9488; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px rgba(13,148,136,0.8); display: flex; align-items: center; justify-content: center; color: white; font-size: 11px;"><i class="fa-solid fa-crosshairs"></i></div>`,
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

    if (modal && openBtn) {
        openBtn.addEventListener("click", () => {
            modal.style.display = "flex";
            if (map) {
                setTimeout(() => map.invalidateSize(), 200);
            }
        });

        const closeModal = () => {
            modal.style.display = "none";
            if (clickPickerMarker && map) {
                map.removeLayer(clickPickerMarker);
                clickPickerMarker = null;
            }
        };

        if (closeBtn) closeBtn.addEventListener("click", closeModal);
        if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

        window.addEventListener("click", (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    if (modalGpsBtn && navigator.geolocation) {
        modalGpsBtn.addEventListener("click", () => {
            modalGpsBtn.disabled = true;
            modalGpsBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Getting GPS coordinates...';

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const latInput = document.querySelector("#addResourceModal input[name='latitude']");
                    const lngInput = document.querySelector("#addResourceModal input[name='longitude']");
                    if (latInput && lngInput) {
                        latInput.value = pos.coords.latitude.toFixed(6);
                        lngInput.value = pos.coords.longitude.toFixed(6);
                    }
                    modalGpsBtn.disabled = false;
                    modalGpsBtn.innerHTML = '<i class="fa-solid fa-check"></i> GPS Coordinates Applied!';
                    setTimeout(() => {
                        modalGpsBtn.innerHTML = '<i class="fa-solid fa-location-arrow"></i> Use My Current GPS Coordinates';
                    }, 2500);
                },
                () => {
                    alert("Unable to get current GPS location.");
                    modalGpsBtn.disabled = false;
                    modalGpsBtn.innerHTML = '<i class="fa-solid fa-location-arrow"></i> Use My Current GPS Coordinates';
                }
            );
        });
    }
});