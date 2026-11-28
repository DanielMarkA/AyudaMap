# AyudaMap User Guide

A walkthrough for guests, field volunteers, and relief coordinators using AyudaMap.

## Getting access

1. Open the app. Guests see **Aid Map**, **Login**, and **Become a Volunteer** in the header.
2. Click **Become a Volunteer** (`/register/`) and enter a **username**, **email address**, **full name** (credited on aid hubs you submit), optional **city**, and **password**. Submitting creates your account with an active volunteer profile and default settings, and signs you in automatically.

After signing in, the header navigation updates to **Dashboard**, **Aid Map**, **Reports**, an **Account menu** dropdown (**Profile**, **Settings**, **Sign out**), and a one-click light/dark **theme toggle**.

## Public landing page (`/`) & live aid map (`/map/`)

Both the landing page and the full-viewport aid map are open to the public without signing in:

- **Landing page (`/`)** — Displays live relief coverage totals (verified hubs, currently open hubs, cities covered, community confirmations), a featured verified hub card, and active coverage by aid category.
- **Live Aid Map (`/map/`)** — Full-screen interactive Leaflet map powered by CARTO Voyager (light) and Dark Matter (dark) basemaps, with automatic OpenStreetMap fallback when no `CARTO_API_KEY` is configured.
  - **Search & filters** — Filter by category chip (`All`, `Medical`, `Food`, `Shelter`, `Govt Aid`, `Donation`), search by hub name, city, address, service (e.g., `Drinking Water`, `First Aid / Meds`), or volunteer name, and toggle the operating-status filter (`Operational / Open`, `Crowded / Limited`, `Closed`).
  - **Pin details** — Click any pin or list card to view offered services, operating hours (including automatic after-hours status), contact info, field confirmations, volunteer attribution, and a Google Maps **Directions** link.
  - **Map controls** — Toggle the color legend, fit all matching pins in view, or center on your current GPS location. On mobile, browse results in the expandable bottom sheet.

## Volunteer dashboard (`/dashboard/`)

Sign in to access the volunteer workbench (`/dashboard/`):

- **Interactive map & filters** — Filter in place without reloading the page using category chips (defaults to your Settings **Preferred Category** unless `All`), the **Operating Status** dropdown, and the **Local volunteers** checkbox (shows only verified hubs in your city reported by local volunteers). Active filters sync to shareable URLs.
- **Verified Relief Centers ledger** — Click any row to expand its description, service tags, operating hours, contact info, submitter name, and action buttons:
  - **View on Map** — Flies to the pin and opens its popup.
  - **Directions** — Opens Google Maps directions to the pin's coordinates.
  - **Verified (N)** — Confirms the hub is still active on site, incrementing its confirmation count and recording a `CONFIRM_ACTIVE` audit entry.
  - **Quick status dropdown** — Update the hub's operating status (`Operational / Open`, `Crowded / Limited`, `Closed`), writing a `STATUS_UPDATE` audit entry.

### Submitting a new aid hub

1. Click **Submit Aid Resource** on `/dashboard/`.
2. Fill in the **Resource / Safe Haven Name**, **Category**, **Operating Status**, **City** dropdown, and **Street / Barangay / Landmark**.
3. Optionally add a description, check available **Safe Haven Services & Amenities** (`Safe Shelter`, `Drinking Water`, `Hot Meals / Packs`, `First Aid / Meds`, `Power / Charging`, `Wi-Fi / Signal`, `PWD Accessible`, `Pet-Friendly`), and enter **Contact Info**.
4. Set coordinates by clicking directly on the background map, typing latitude/longitude, or clicking **Use My Current GPS Coordinates**.
5. Check **Open 24/7** or specify **Opens At** and **Closes At** times (`Asia/Manila`). Hubs outside their scheduled hours automatically show as `Closed` until they reopen.
6. Click **Save Resource**. The hub is immediately published and logged in the audit trail.

## Reports (`/reports/`)

Sign in to view operational analytics at `/reports/`:

- **KPI summary** — Verified aid hubs, currently open hubs (with open rate %), cities covered, and total community verifications.
- **Currently Open Havens by City** — Open now vs. total mapped centers per city/municipality.
- **Currently Open Havens by Service** — Count of currently open hubs offering each service.
- **Coverage by Aid Category** — Total centers, open now, and confirmations per category.
- **Recent Field Verification & Status Audit Log** — The 15 most recent status updates and on-site confirmations, showing the hub, action, note, volunteer, and relative time.

## Profile (`/profile/`)

Organized into three tabs:

- **Edit Profile** — Update first/last name, display/full name, email, affiliated organization (NGO/LGU), active volunteer status, phone number, city dropdown, bio, and profile photo (with live preview).
- **My Aid Hubs** — View every hub you submitted along with a **View on Map** shortcut.
- **Field Activity** — Review your 10 most recent status updates and confirmations.

## Settings (`/settings/`)

- **General & Alerts** — Toggle dark mode interface and stored notification flags *(note: outbound email delivery is not enabled in this deployment)*.
- **Map Defaults** — Set your default dashboard aid category filter, starting latitude/longitude, and zoom level (`5–18`).
- **Security & Password** — Update your password without signing out of your active session.

Use the header theme toggle at any time for an instant light/dark switch persisted in browser storage.

## Admin (`/admin/`)

Staff/superusers can manage `Resource` (including the internal `supplies_needed` coordinator note and `is_verified` flag) and `ResourceStatusLog` records through Django admin.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Redirected to Login when opening `/dashboard/` or `/reports/` | Sign in, or browse the public map at `/map/`. |
| No pins on the map | Reset active filters and verify the database contains `is_verified=True` resources. A fresh local SQLite database starts empty. |
| Map tiles show OpenStreetMap instead of CARTO, or fail offline | CARTO tiles require `CARTO_API_KEY` and internet access; blank keys automatically fall back to OpenStreetMap. |
| Wrong default map center | Adjust default latitude, longitude, and zoom in **Settings → Map Defaults**. |
| Uploaded profile photo missing in production | Ensure nginx/your proxy serves `/media/` from the same persistent directory configured in `DJANGO_MEDIA_ROOT`. |
