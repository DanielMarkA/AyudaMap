document.addEventListener("DOMContentLoaded", () => {
    let allResources = [];
    const dataEl = document.getElementById("publicMapDataJson");
    if (dataEl && dataEl.textContent.trim()) {
        try {
            allResources = JSON.parse(dataEl.textContent);
        } catch (e) {
            console.error("Failed to parse map data:", e);
        }
    }

    let mapConfig = { lat: 10.3157, lng: 123.8854, zoom: 12 };
    const cfgEl = document.getElementById("publicMapConfigJson");
    if (cfgEl && cfgEl.textContent.trim()) {
        try {
            mapConfig = JSON.parse(cfgEl.textContent);
        } catch (e) {}
    }

    let filters = { q: "", category: "", status: "" };
    const initFiltersEl = document.getElementById("publicInitialFiltersJson");
    if (initFiltersEl && initFiltersEl.textContent.trim()) {
        try {
            filters = { ...filters, ...JSON.parse(initFiltersEl.textContent) };
        } catch (e) {}
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

    const isMobileViewport = () => window.matchMedia("(max-width: 768px)").matches;

    const mapShell = document.getElementById("mapShell");
    const mapContainer = document.getElementById("publicMapViewport");
    const statusLiveEl = document.getElementById("publicMapStatusLive");
    const searchInput = document.getElementById("mapSearchInput");
    const clearSearchBtn = document.getElementById("mapClearSearchBtn");
    const filterToggleBtn = document.getElementById("mapFilterToggleBtn");
    const filterPanel = document.getElementById("mapFilterPanel");
    const filterActiveDot = document.getElementById("filterActiveDot");
    const statusFilter = document.getElementById("mapStatusFilter");
    const resetFiltersBtn = document.getElementById("mapResetFiltersBtn");
    const categoryChips = Array.from(document.querySelectorAll(".map-cat-chip"));

    const resultsListEl = document.getElementById("mapResultsList");
    const resultCountEl = document.getElementById("drawerResultCount");
    const sheetHandleBtn = document.getElementById("sheetHandleBtn");
    const sheetSummaryText = document.getElementById("sheetSummaryText");
    const drawerCollapseBtn = document.getElementById("drawerCollapseBtn");

    const listViewEl = document.getElementById("drawerListView");
    const detailViewEl = document.getElementById("drawerDetailView");
    const detailContentEl = document.getElementById("detailContent");
    const detailBackBtn = document.getElementById("detailBackBtn");
    const detailCloseBtn = document.getElementById("detailCloseBtn");

    const fitAllBtn = document.getElementById("publicFitAllBtn");
    const locateBtn = document.getElementById("publicLocateBtn");
    const legendBtn = document.getElementById("publicLegendBtn");
    const legendPanel = document.getElementById("publicMapLegend");

    const announce = (msg) => {
        if (!statusLiveEl) return;
        statusLiveEl.textContent = "";
        setTimeout(() => { statusLiveEl.textContent = msg; }, 50);
    };

    const cartoApiKey = (mapConfig.carto_api_key || "").trim();
    const createTileLayer = (isDark) => {
        if (cartoApiKey) {
            const base = isDark
                ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                : "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
            return L.tileLayer(`${base}?key=${encodeURIComponent(cartoApiKey)}`, {
                maxZoom: 19,
                subdomains: "abcd",
                attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
            });
        }
        return L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "&copy; OpenStreetMap contributors",
        });
    };

    const getCategoryColor = (cat) => {
        switch (cat) {
            case "MEDICAL": return "#ef4444";
            case "FOOD": return "#f59e0b";
            case "SHELTER": return "#3b82f6";
            case "GOV": return "#8b5cf6";
            case "DONATION": return "#047857";
            default: return "#0d9488";
        }
    };

    const getCategoryIconClass = (cat) => {
        switch (cat) {
            case "MEDICAL": return "fa-hospital";
            case "FOOD": return "fa-bowl-food";
            case "SHELTER": return "fa-tents";
            case "GOV": return "fa-building-columns";
            case "DONATION": return "fa-hand-holding-dollar";
            default: return "fa-location-dot";
        }
    };

    const getStatusMeta = (status) => {
        if (status === "LIMITED") return { cls: "status-full", short: "Limited", icon: "fa-circle-exclamation" };
        if (status === "CLOSED") return { cls: "status-closed", short: "Closed", icon: "fa-circle-xmark" };
        return { cls: "status-open", short: "Open", icon: "fa-circle-check" };
    };

    let map = null;
    let tileLayer = null;
    let markerLayerGroup = null;
    let userLocationMarker = null;
    let markersById = {};
    let selectedResourceId = null;
    let currentFiltered = allResources.slice();

    if (mapContainer && typeof L === "undefined") {
        mapContainer.innerHTML =
            '<div class="map-offline-fallback">Map tiles could not load (offline or CDN unavailable). You can still browse verified aid centers in the panel.</div>';
    }

    if (mapContainer && typeof L !== "undefined") {
        const isDark = document.documentElement.classList.contains("dark-mode");
        const initialCenter =
            allResources.length > 0 && allResources[0].lat
                ? [allResources[0].lat, allResources[0].lng]
                : [mapConfig.lat, mapConfig.lng];

        mapContainer.classList.toggle("map-osm-fallback", !cartoApiKey);
        map = L.map("publicMapViewport", { zoomControl: false }).setView(initialCenter, mapConfig.zoom || 12);
        L.control.zoom({ position: "bottomright" }).addTo(map);

        tileLayer = createTileLayer(isDark).addTo(map);

        markerLayerGroup = L.layerGroup().addTo(map);

        if (cartoApiKey) {
            window.addEventListener("themeChanged", (e) => {
                if (map && tileLayer) {
                    map.removeLayer(tileLayer);
                    tileLayer = createTileLayer(e.detail.isDark).addTo(map);
                }
            });
        }
    }

    const drawerInnerSections = Array.from(
        document.querySelectorAll(".drawer-search-bar, .drawer-filter-panel, #drawerBody, .drawer-footer")
    );

    const syncDrawerInert = () => {
        if (!mapShell) return;
        const hiddenOffscreen = isMobileViewport()
            ? !mapShell.classList.contains("sheet-expanded")
            : mapShell.classList.contains("drawer-collapsed");
        drawerInnerSections.forEach((el) => {
            el.inert = hiddenOffscreen;
        });
    };

    const openDrawer = () => {
        if (!mapShell) return;
        if (isMobileViewport()) {
            mapShell.classList.add("sheet-expanded");
            if (sheetHandleBtn) sheetHandleBtn.setAttribute("aria-expanded", "true");
        } else {
            mapShell.classList.remove("drawer-collapsed");
            if (drawerCollapseBtn) {
                drawerCollapseBtn.setAttribute("aria-expanded", "true");
                drawerCollapseBtn.setAttribute("aria-label", "Collapse side panel");
                drawerCollapseBtn.setAttribute("title", "Collapse side panel");
            }
        }
        syncDrawerInert();
    };

    const showListView = (restoreFocus = false) => {
        const previousId = selectedResourceId;
        selectedResourceId = null;
        if (detailViewEl) detailViewEl.hidden = true;
        if (listViewEl) listViewEl.hidden = false;
        document.querySelectorAll(".map-result-item.is-selected").forEach((el) => el.classList.remove("is-selected"));
        if (restoreFocus && previousId != null) {
            const prevBtn = resultsListEl && resultsListEl.querySelector(`.map-result-item[data-id="${previousId}"]`);
            if (prevBtn) prevBtn.focus();
        }
    };

    const showDetailView = (resource, panMap = true) => {
        if (!resource || !detailContentEl) return;
        selectedResourceId = resource.id;
        openDrawer();

        const st = getStatusMeta(resource.status);
        const catClass = `cat-${String(resource.category_code || "").toLowerCase()}`;
        const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(resource.lat)},${encodeURIComponent(resource.lng)}`;

        const services = Array.isArray(resource.services) ? resource.services : [];
        const servicesBlock = services.length
            ? `<div class="detail-services-box">
                   <div class="detail-services-title"><i class="fa-solid fa-shield-heart" aria-hidden="true"></i> Available at this Haven</div>
                   <div class="detail-services-list">
                       ${services.map((svc) => `<span class="haven-service-tag"><i class="fa-solid fa-check" aria-hidden="true"></i> ${escapeHtml(svc)}</span>`).join("")}
                   </div>
               </div>`
            : "";

        const hoursText = resource.is_auto_closed && resource.opens_at_display
            ? `${escapeHtml(resource.operating_hours)} <span class="detail-hours-note">(Closed after hours &middot; Opens ${escapeHtml(resource.opens_at_display)})</span>`
            : escapeHtml(resource.operating_hours);

        const descBlock = resource.description
            ? `<p class="detail-desc">${escapeHtml(resource.description)}</p>`
            : "";

        const contactRow = resource.contact_info
            ? `<div class="detail-info-row"><i class="fa-solid fa-phone" aria-hidden="true"></i><span>${escapeHtml(resource.contact_info)}</span></div>`
            : "";

        const orgLine = resource.posted_by_org
            ? `<span class="detail-volunteer-org">${escapeHtml(resource.posted_by_org)}</span>`
            : "";

        detailContentEl.innerHTML = `
            <div>
                <h2 class="detail-title">${escapeHtml(resource.name)}</h2>
                <div class="detail-badges">
                    <span class="status-pill ${st.cls}"><i class="fa-solid ${st.icon}" aria-hidden="true"></i> ${escapeHtml(resource.status_display)}</span>
                    <span class="category-badge ${escapeHtml(catClass)}">${escapeHtml(resource.category)}</span>
                </div>
            </div>
            ${descBlock}
            ${servicesBlock}
            <div class="detail-info-list">
                <div class="detail-info-row"><i class="fa-solid fa-location-dot" aria-hidden="true"></i><span>${escapeHtml(resource.location)}</span></div>
                <div class="detail-info-row"><i class="fa-solid fa-clock" aria-hidden="true"></i><span>${hoursText}</span></div>
                ${contactRow}
                <div class="detail-info-row"><i class="fa-solid fa-thumbs-up" aria-hidden="true"></i><span><strong>${escapeHtml(resource.confirmations)}</strong> field confirmations</span></div>
            </div>
            <div class="detail-volunteer-card">
                <span class="detail-volunteer-icon" aria-hidden="true"><i class="fa-solid fa-user-shield"></i></span>
                <div class="detail-volunteer-text">
                    <span class="detail-volunteer-label">Added by volunteer</span>
                    <span class="detail-volunteer-name">${escapeHtml(resource.posted_by)}</span>
                    ${orgLine}
                </div>
            </div>
            <div class="detail-actions">
                <button type="button" class="btn btn-sm btn-outline" id="detailCenterPinBtn">
                    <i class="fa-solid fa-crosshairs" aria-hidden="true"></i> Center Pin
                </button>
                <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-primary">
                    <i class="fa-solid fa-diamond-turn-right" aria-hidden="true"></i> Directions
                </a>
            </div>
        `;

        if (listViewEl) listViewEl.hidden = true;
        if (detailViewEl) detailViewEl.hidden = false;
        if (detailBackBtn) detailBackBtn.focus();

        const centerBtn = document.getElementById("detailCenterPinBtn");
        if (centerBtn && map) {
            centerBtn.addEventListener("click", () => {
                const animate = !prefersReducedMotion();
                map.flyTo([resource.lat, resource.lng], 15, { animate, duration: animate ? 0.65 : 0 });
            });
        }

        if (panMap && map && resource.lat && resource.lng) {
            const animate = !prefersReducedMotion();
            map.flyTo([resource.lat, resource.lng], 15, { animate, duration: animate ? 0.7 : 0 });
        }

        announce(`Showing details for ${resource.name}, added by ${resource.posted_by}.`);
    };

    const fitVisibleMarkers = (animate = false) => {
        if (!map) return;
        const coords = currentFiltered
            .filter((r) => r.lat && r.lng)
            .map((r) => [r.lat, r.lng]);

        if (coords.length > 1) {
            const leftPad = !isMobileViewport() && !mapShell.classList.contains("drawer-collapsed") ? 410 : 40;
            map.fitBounds(coords, {
                paddingTopLeft: [leftPad, 72],
                paddingBottomRight: [56, 48],
                animate,
            });
        } else if (coords.length === 1) {
            map.flyTo(coords[0], 14, { animate, duration: animate ? 0.6 : 0 });
        }
    };

    const renderMarkers = (items) => {
        if (!map || !markerLayerGroup) return;
        markerLayerGroup.clearLayers();
        markersById = {};

        items.forEach((res) => {
            if (!res.lat || !res.lng) return;
            const color = getCategoryColor(res.category_code);
            const iconClass = getCategoryIconClass(res.category_code);

            const icon = L.divIcon({
                className: "custom-map-pin",
                html: `<div style="background-color: ${color}; width: 32px; height: 32px; border-radius: 50%; border: 2.5px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.35); display: flex; align-items: center; justify-content: center; color: white; font-size: 0.85rem; cursor: pointer;"><i class="fa-solid ${iconClass}"></i></div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16],
            });

            const marker = L.marker([res.lat, res.lng], { icon, title: res.name }).addTo(markerLayerGroup);
            marker.bindTooltip(`${escapeHtml(res.name)}`, { direction: "top", offset: [0, -14] });
            marker.on("click", () => {
                showDetailView(res, true);
            });
            markersById[res.id] = marker;
        });
    };

    const renderList = (items) => {
        const count = items.length;
        const plural = count === 1 ? "" : "s";

        if (resultCountEl) {
            resultCountEl.textContent = `${count} verified hub${plural}`;
        }
        if (sheetSummaryText) {
            sheetSummaryText.innerHTML = `<strong>${count}</strong> verified aid hub${plural} &middot; Tap to browse`;
        }

        if (!resultsListEl) return;
        if (count === 0) {
            resultsListEl.innerHTML = `
                <div class="drawer-empty">
                    <i class="fa-solid fa-compass" aria-hidden="true"></i>
                    <p>No verified aid centers match these filters.</p>
                </div>
            `;
            return;
        }

        resultsListEl.innerHTML = items
            .map((res) => {
                const st = getStatusMeta(res.status);
                const catClass = `cat-${String(res.category_code || "").toLowerCase()}`;
                const selectedCls = res.id === selectedResourceId ? "is-selected" : "";
                const services = Array.isArray(res.services) ? res.services.slice(0, 3) : [];
                const servicesRow = services.length
                    ? `<div class="result-item-services">${services.map((s) => `<span class="result-service-pill">${escapeHtml(s)}</span>`).join("")}</div>`
                    : "";
                return `
                    <button type="button" class="map-result-item ${selectedCls}" data-id="${escapeHtml(res.id)}">
                        <div class="result-item-top">
                            <span class="result-item-title">${escapeHtml(res.name)}</span>
                            <span class="status-pill ${st.cls}">${st.short}</span>
                        </div>
                        <div class="result-item-badges">
                            <span class="category-badge ${escapeHtml(catClass)}">${escapeHtml(res.category)}</span>
                        </div>
                        ${servicesRow}
                        <div class="result-item-meta">
                            <span><i class="fa-solid fa-location-dot" aria-hidden="true"></i> ${escapeHtml(res.location)}</span>
                            <span class="num-cell"><i class="fa-solid fa-clock" aria-hidden="true"></i> ${escapeHtml(res.operating_hours)}</span>
                        </div>
                        <div class="result-item-volunteer">
                            <i class="fa-solid fa-user-shield" aria-hidden="true"></i> Added by ${escapeHtml(res.posted_by)}
                        </div>
                    </button>
                `;
            })
            .join("");

        resultsListEl.querySelectorAll(".map-result-item").forEach((btn) => {
            btn.addEventListener("click", () => {
                const id = Number(btn.dataset.id);
                const found = currentFiltered.find((r) => r.id === id);
                if (found) showDetailView(found, true);
            });
        });
    };

    const syncUrlParams = () => {
        const params = new URLSearchParams();
        if (filters.q) params.set("q", filters.q);
        if (filters.category) params.set("category", filters.category);
        if (filters.status) params.set("status", filters.status);
        const queryStr = params.toString();
        const nextUrl = queryStr ? `${window.location.pathname}?${queryStr}` : window.location.pathname;
        window.history.replaceState({}, "", nextUrl);
    };

    const applyFilters = () => {
        const q = (filters.q || "").trim().toLowerCase();
        currentFiltered = allResources.filter((r) => {
            if (filters.category && r.category_code !== filters.category) return false;
            if (filters.status && r.status !== filters.status) return false;
            if (q) {
                const haystack = [
                    r.name,
                    r.description,
                    r.city,
                    r.location,
                    Array.isArray(r.services) ? r.services.join(" ") : "",
                    r.posted_by,
                    r.category,
                ]
                    .join(" ")
                    .toLowerCase();
                if (!haystack.includes(q)) return false;
            }
            return true;
        });

        if (clearSearchBtn) clearSearchBtn.hidden = !filters.q;
        if (filterActiveDot) filterActiveDot.hidden = !filters.status;

        categoryChips.forEach((chip) => {
            chip.classList.toggle("active", (chip.dataset.category || "") === (filters.category || ""));
        });

        renderList(currentFiltered);
        renderMarkers(currentFiltered);

        if (selectedResourceId && !currentFiltered.some((r) => r.id === selectedResourceId)) {
            showListView();
        }

        if (fitAllBtn) fitAllBtn.disabled = !Object.keys(markersById).length;

        syncUrlParams();
    };

    // Event Wiring
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            filters.q = searchInput.value;
            showListView();
            applyFilters();
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener("click", () => {
            filters.q = "";
            if (searchInput) {
                searchInput.value = "";
                searchInput.focus();
            }
            showListView();
            applyFilters();
        });
    }

    if (filterToggleBtn && filterPanel) {
        const closeFilterPanel = (restoreFocus = false) => {
            if (filterPanel.hidden) return;
            filterPanel.hidden = true;
            filterToggleBtn.setAttribute("aria-expanded", "false");
            if (restoreFocus) filterToggleBtn.focus();
        };

        filterToggleBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            const willOpen = filterPanel.hidden;
            filterPanel.hidden = !willOpen;
            filterToggleBtn.setAttribute("aria-expanded", String(willOpen));
        });

        document.addEventListener("click", (e) => {
            if (!filterPanel.hidden && !filterPanel.contains(e.target) && !filterToggleBtn.contains(e.target)) {
                closeFilterPanel(false);
            }
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && !filterPanel.hidden) {
                closeFilterPanel(true);
            }
        });
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", () => {
            filters.status = statusFilter.value;
            showListView();
            applyFilters();
        });
    }

    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener("click", () => {
            filters = { q: "", category: "", status: "" };
            if (searchInput) searchInput.value = "";
            if (statusFilter) statusFilter.value = "";
            showListView();
            applyFilters();
        });
    }

    categoryChips.forEach((chip) => {
        chip.addEventListener("click", () => {
            filters.category = chip.dataset.category || "";
            showListView();
            applyFilters();
        });
    });

    if (detailBackBtn) detailBackBtn.addEventListener("click", () => showListView(true));
    if (detailCloseBtn) detailCloseBtn.addEventListener("click", () => showListView(true));

    if (drawerCollapseBtn && mapShell) {
        drawerCollapseBtn.addEventListener("click", () => {
            const willCollapse = !mapShell.classList.contains("drawer-collapsed");
            mapShell.classList.toggle("drawer-collapsed", willCollapse);
            drawerCollapseBtn.setAttribute("aria-expanded", String(!willCollapse));
            drawerCollapseBtn.setAttribute("aria-label", willCollapse ? "Expand side panel" : "Collapse side panel");
            drawerCollapseBtn.setAttribute("title", willCollapse ? "Expand side panel" : "Collapse side panel");
            syncDrawerInert();
            if (map) {
                setTimeout(() => map.invalidateSize(), 240);
            }
        });
    }

    if (sheetHandleBtn && mapShell) {
        sheetHandleBtn.addEventListener("click", () => {
            const expanded = mapShell.classList.toggle("sheet-expanded");
            sheetHandleBtn.setAttribute("aria-expanded", String(expanded));
            syncDrawerInert();
        });
    }

    window.addEventListener("resize", syncDrawerInert);
    syncDrawerInert();

    if (fitAllBtn) {
        fitAllBtn.addEventListener("click", () => {
            fitVisibleMarkers(!prefersReducedMotion());
            announce("Map centered on all matching aid pins.");
        });
    }

    if (legendBtn && legendPanel) {
        legendBtn.addEventListener("click", () => {
            const willOpen = legendPanel.hidden;
            legendPanel.hidden = !willOpen;
            legendBtn.setAttribute("aria-expanded", String(willOpen));
        });
    }

    if (locateBtn && navigator.geolocation && map) {
        locateBtn.addEventListener("click", () => {
            locateBtn.disabled = true;
            locateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin" aria-hidden="true"></i>';

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const userLat = pos.coords.latitude;
                    const userLng = pos.coords.longitude;
                    const animate = !prefersReducedMotion();
                    map.flyTo([userLat, userLng], 14, { animate, duration: animate ? 0.9 : 0 });

                    if (userLocationMarker) {
                        userLocationMarker.setLatLng([userLat, userLng]);
                    } else {
                        const userIcon = L.divIcon({
                            className: "user-location-pin",
                            html: `<div style="background-color: #0284c7; width: 22px; height: 22px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(2,132,199,0.8); display: flex; align-items: center; justify-content: center; color: white; font-size: 0.8rem;"><i class="fa-solid fa-user"></i></div>`,
                            iconSize: [22, 22],
                            iconAnchor: [11, 11],
                        });
                        userLocationMarker = L.marker([userLat, userLng], { icon: userIcon })
                            .bindTooltip("You are here", { direction: "top" })
                            .addTo(map);
                    }

                    announce("Map centered on your current location.");
                    locateBtn.disabled = false;
                    locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs" aria-hidden="true"></i>';
                },
                () => {
                    announce("Could not access your location.");
                    locateBtn.disabled = false;
                    locateBtn.innerHTML = '<i class="fa-solid fa-location-crosshairs" aria-hidden="true"></i>';
                },
                { timeout: 10000 }
            );
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key !== "Escape") return;
        if (detailViewEl && !detailViewEl.hidden) {
            showListView(true);
        } else if (filterPanel && !filterPanel.hidden) {
            filterPanel.hidden = true;
            if (filterToggleBtn) filterToggleBtn.setAttribute("aria-expanded", "false");
        } else if (legendPanel && !legendPanel.hidden) {
            legendPanel.hidden = true;
            if (legendBtn) legendBtn.setAttribute("aria-expanded", "false");
        }
    });

    // Initial render & bounds fit
    applyFilters();
    fitVisibleMarkers();

    // If URL pre-filtered to a single exact match (e.g., from Profile "View on Map"), open its detail sheet directly
    if (filters.q && currentFiltered.length === 1) {
        showDetailView(currentFiltered[0], true);
    }
});
