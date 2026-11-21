# AyudaMap User Guide

A short walkthrough for volunteers, coordinators, and anyone evaluating the application.

## Getting access

1. Open the app. If you are not signed in you will see **Login** and **Register** in the header.
2. Click **Register**, enter a username, email, password, and (optionally) your full name. Submitting creates your account together with an empty profile and a default settings record, and signs you in automatically.
3. To use the demo data instead, sign in with `admin` / `AdminAyuda2026!` (coordinator) or `juan_delacruz` / `AyudaPass123!` (volunteer). See the [README](../README.md#demo-accounts).

The header navigation changes after sign-in: **Home**, **Reports**, **Profile**, **Settings**, a theme toggle, and your avatar with a sign-out button.

## Home — the aid map (`/`)

The home page is the main operating view. It contains:

- **Summary cards** — total verified resources and how many are marked critical.
- **Filters** — a keyword search box plus dropdowns for **category**, **status**, and **urgency**. Changing a filter narrows both the list and the map pins. If you have not chosen a category, the app uses the preferred category from your Settings (unless it is `All`).
- **The map** — an interactive Leaflet map with CARTO basemaps. Pins are colour-coded by category: Medical (red), Food (amber), Shelter (blue), Government (purple), Donation (green). Click a pin for details such as operating hours, capacity, supplies needed, contact info, and verification count. The map follows your light/dark theme.
- **Location tools** — "locate me" centres the map on your device location; the coordinate picker lets you set latitude/longitude when adding a resource.
- **Resource list** — cards for each verified site, with status/urgency badges and action buttons.

### Adding a resource

1. Click the **Add Resource** / report-a-site button on the home page.
2. Fill in the name, category, status, urgency, description, supplies needed, total and available capacity, location, coordinates, operating hours, and contact info.
3. Submit. The new entry is marked verified, attributed to your account, and written to the audit log. A confirmation message appears.

### Confirming a site

Click **Confirm** on a resource card if you have checked that the site is still active. Each click increments its community confirmation count and creates a `CONFIRM_ACTIVE` log entry. This helps coordinators trust the data.

### Changing a status

Coordinators can update a site's operating status (**Operational**, **Full Capacity**, **Temporarily Closed**). Setting **Full Capacity** automatically sets available capacity to zero. Every change is recorded with the previous and new status.

## Reports (`/reports/`)

The Reports page summarises relief operations:

- **Totals** — number of centres, total and available capacity, total confirmations.
- **Utilisation rate** — percentage of total capacity currently used.
- **Breakdowns** — counts by category and by urgency level.
- **Critical resources** — sites marked `CRITICAL`, most recently updated first.
- **Field audit log** — the 15 most recent status updates, confirmations, and supply pledges, showing the resource, action, user, and timestamp.

> Reports are currently reachable even without signing in (see [ARCHITECTURE.md](ARCHITECTURE.md#url-map)). If that is not intended, restrict the view.

## Profile (`/profile/`)

- Edit your name, email, organization, volunteer flag, bio, phone number, city, and profile photo.
- See your own contributed resources, how many you have submitted, the total confirmations they have received, and your recent verification activity.
- If you set a full name but no first/last name, the app fills those in from the full name automatically.

## Settings (`/settings/`)

Two independent forms:

- **Preferences** — dark mode, email notifications, notifications about new resources, preferred resource category, default map latitude/longitude, and zoom level (5–18). These control the theme, the default home filter, and where the map starts.
- **Change password** — requires your current password; your session stays signed in after the change.

Use the header theme toggle for a one-click light/dark switch; it is remembered in your browser's local storage.

## Admin (`/admin/`)

Staff/superusers can manage `Resource` and `ResourceStatusLog` records through the Django admin, including filtering by category, status, urgency, and verification.

## Getting help / troubleshooting

| Symptom | What to check |
| --- | --- |
| Redirected to Login when opening Home | Home requires authentication — sign in first. |
| No pins on the map | The resource may be unverified, or no `DATABASE_URL` is set so you are seeing the local SQLite database rather than Supabase. Run `python seed_data.py`. |
| Map tiles do not load | CARTO tiles require an internet connection; check the browser console. |
| Wrong map centre | Adjust default latitude/longitude/zoom in Settings. |
| Uploaded photo missing | `MEDIA_ROOT` is `media/`; media is only served by Django when `DEBUG = True`. |
