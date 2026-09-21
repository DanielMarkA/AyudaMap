// Home Feature JavaScript
document.addEventListener("DOMContentLoaded", () => {
    // 1. Parse JSON map data
    let resources = [];
    const mapDataEl = document.getElementById("mapDataJson");
    if (mapDataEl) {
        try {
            resources = JSON.parse(mapDataEl.textContent);
        } catch (e) {
            console.error("Error parsing map data JSON:", e);
        }
    }

    // 2. Initialize Leaflet Map
    const mapContainer = document.getElementById("ayudaMapViewport");
    let map = null;
    let clickPickerMarker = null;

    if (mapContainer && typeof L !== "undefined") {
        // Default center: Manila, Philippines [14.5995, 120.9842]
        const defaultCenter = resources.length > 0 && resources[0].lat 
            ? [resources[0].lat, resources[0].lng] 
            : [14.5995, 120.9842];

        map = L.map('ayudaMapViewport').setView(defaultCenter, 12);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        const markers = {};
        const group = [];

        // Category color mapper
        const getCategoryColor = (cat) => {
            switch(cat) {
                case 'MEDICAL': return '#ef4444';
                case 'FOOD': return '#f59e0b';
                case 'SHELTER': return '#3b82f6';
                case 'GOV': return '#8b5cf6';
                case 'DONATION': return '#10b981';
                default: return '#0d9488';
            }
        };

        // Status badge formatter
        const getStatusBadge = (status, statusDisplay) => {
            let bg = '#2e7d32';
            if (status === 'FULL_CAPACITY') bg = '#e65100';
            else if (status === 'TEMPORARILY_CLOSED') bg = '#c62828';
            return `<span style="display:inline-block; font-size: 10px; padding: 2px 6px; border-radius: 4px; background: ${bg}; color: white; font-weight: 600; margin-left: 4px;">${statusDisplay || status}</span>`;
        };

        // Add markers for all verified resources
        resources.forEach(res => {
            if (res.lat && res.lng) {
                const color = getCategoryColor(res.category_code);
                
                const customIcon = L.divIcon({
                    className: 'custom-map-pin',
                    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; color: white; font-size: 11px;"><i class="fa-solid fa-location-dot"></i></div>`,
                    iconSize: [24, 24],
                    iconAnchor: [12, 12]
                });

                const popupContent = `
                    <div style="font-family: system-ui, sans-serif; min-width: 200px; padding: 2px;">
                        <h4 style="margin: 0 0 4px 0; color: #0f172a; font-size: 14px; font-weight: 700;">${res.name}</h4>
                        <div style="margin-bottom: 6px;">
                            <span style="display:inline-block; font-size: 11px; padding: 2px 6px; border-radius: 4px; background: #e0f2fe; color: #0284c7; font-weight: 600;">${res.category}</span>
                            ${getStatusBadge(res.status, res.status_display)}
                        </div>
                        <p style="margin: 4px 0; font-size: 12px; color: #475569;">📍 ${res.location}</p>
                        <p style="margin: 4px 0; font-size: 12px; color: #475569;">🕒 ${res.operating_hours}</p>
                        ${res.contact_info ? `<p style="margin: 4px 0; font-size: 12px; color: #475569;">📞 ${res.contact_info}</p>` : ''}
                    </div>
                `;

                const marker = L.marker([res.lat, res.lng], { icon: customIcon })
                    .bindPopup(popupContent)
                    .addTo(map);

                markers[res.id] = marker;
                group.push([res.lat, res.lng]);
            }
        });

        // Fit map to markers bounds if multiple exist
        if (group.length > 1) {
            map.fitBounds(group, { padding: [30, 30] });
        }

        // Pan to pin buttons
        document.querySelectorAll(".pan-to-pin-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const lat = parseFloat(btn.dataset.lat);
                const lng = parseFloat(btn.dataset.lng);
                const id = btn.closest(".resource-card")?.dataset.id;

                if (!isNaN(lat) && !isNaN(lng)) {
                    map.flyTo([lat, lng], 15, { animate: true, duration: 1 });
                    if (id && markers[id]) {
                        setTimeout(() => markers[id].openPopup(), 1000);
                    }
                }
            });
        });

        // Map Click coordinate picker when adding resource
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
                            html: `<div style="background-color: #0d9488; width: 22px; height: 22px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 8px rgba(13,148,136,0.6); display: flex; align-items: center; justify-content: center; color: white; font-size: 10px;"><i class="fa-solid fa-crosshairs"></i></div>`,
                            iconSize: [22, 22],
                            iconAnchor: [11, 11]
                        })
                    }).addTo(map);
                }
            }
        });
    }

    // 3. Modal Dialog Handler
    const modal = document.getElementById("addResourceModal");
    const openBtn = document.getElementById("openAddModalBtn");
    const closeBtn = document.getElementById("closeAddModalBtn");
    const cancelBtn = document.getElementById("cancelAddModalBtn");

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
});
