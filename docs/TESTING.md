# Testing

## Running the suite

Run tests against an isolated in-memory SQLite database by leaving `DATABASE_URL` blank and `DJANGO_DEBUG=True`. If your `.env` file sets `DATABASE_URL` for Supabase PostgreSQL, override it in your shell before running tests so Django does not attempt to create `test_postgres` on the cloud server:

```powershell
# PowerShell (safe override when .env sets DATABASE_URL)
$env:DATABASE_URL=" "; $env:DJANGO_DEBUG="True"
python manage.py test

# Single app
python manage.py test apps.home

# Single test method
python manage.py test apps.home -k test_dashboard_filter_by_category

# Verbose output
python manage.py test -v 2
```

Django's test runner discovers `tests.py` across all five feature apps (`home`, `login`, `register`, `profile`, `user_settings`) and runs against an in-memory SQLite database with no pytest dependency required.

## Test inventory (37 tests)

| App | File | Tests | What is covered |
| --- | --- | --- | --- |
| `home` | [`apps/home/tests.py`](../apps/home/tests.py) | 21 | Guest landing and public map; `json_script` XSS escaping; dashboard & reports auth guards; category, effective status, after-hours/overnight auto-closing, and legacy-casing local-volunteer filters; AJAX `X-Dashboard-Filters` partial responses; `add_resource`, `confirm_resource`, and `update_status` mutations + `ResourceStatusLog` creation; `supplies_needed` exclusion; reports breakdowns by city/service/category |
| `login` | [`apps/login/tests.py`](../apps/login/tests.py) | 4 | Login page renders; successful login; failed login; logout |
| `register` | [`apps/register/tests.py`](../apps/register/tests.py) | 4 | Registration page renders; creates volunteer `Profile` and `UserSettings`; required `full_name` and canonical `city` validation |
| `profile` | [`apps/profile/tests.py`](../apps/profile/tests.py) | 3 | Login required; profile page renders; profile update including canonical city |
| `user_settings` | [`apps/user_settings/tests.py`](../apps/user_settings/tests.py) | 5 | Login required; authenticated render (and SQLite cloud-pill guard); preferences update; map zoom `5–18` validation; password change |

## What is not yet covered

Be aware of these remaining gaps when evaluating coverage:

- `reports_view` total-aggregation edge cases (`_get_impact_summary` with zero resources, `recent_logs` 15-item truncation) and `profile_view` submitted-hubs/activity counts are not directly asserted.
- The **Local volunteers** filter (`Profile` `Subquery`) is verified functionally on results, rather than asserting exact SQL query plans.
- Client-side JavaScript (`static/js/home/home.js`, `map.js`, `profile.js`, `settings.js`) has no automated browser test runner (Playwright/Jest).
- No coverage reporting tool or CI workflow is configured in the repository.

## Adding a test — conventions

1. Add a `TestCase` subclass to the owning app's `tests.py`.
2. Use `reverse('<app>:<name>')` instead of hard-coded URLs.
3. For authenticated views, create a user in `setUp()` and call `self.client.login(...)` or `self.client.force_login(...)`.
4. Assert on `status_code`, `assertTemplateUsed`, `assertContains`, `assertRedirects`, and model state.

Example skeleton:

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.home.models import Resource, ResourceStatusLog


class ResourceStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('volunteer', password='Pass12345!')
        self.client.force_login(self.user)
        self.resource = Resource.objects.create(
            name='Test Shelter',
            category='SHELTER',
            status='OPERATIONAL',
            city='Quezon City',
            location='Maginhawa St',
            is_24_7=True,
        )

    def test_confirm_increments_count_and_logs(self):
        response = self.client.post(
            reverse('home:confirm_resource', args=[self.resource.id])
        )
        self.resource.refresh_from_db()
        self.assertRedirects(response, reverse('home:dashboard'))
        self.assertEqual(self.resource.confirmations, 2)
        self.assertTrue(
            ResourceStatusLog.objects.filter(
                resource=self.resource, action_type='CONFIRM_ACTIVE'
            ).exists()
        )
```

## Manual SQL / Supabase verification

The completed course demo used the dashboard and Reports to demonstrate SQL JOINs (`select_related('created_by', 'created_by__profile')`) and the dashboard's **Local volunteers** filter to demonstrate a SQL `Subquery` across `aid_resources`, `auth_user`, and `user_profiles`. To reproduce those checks against staging data, create volunteer accounts and aid hubs in matching and non-matching cities, toggle **Local volunteers**, and inspect the generated SQL from `django.db.connection.queries` or the Supabase table editor.
