# Testing

## Running the suite

Set `DJANGO_DEBUG=True` and leave `DATABASE_URL` blank in your local configuration to run against SQLite. With a PostgreSQL URL configured, Django attempts to create a test database on that PostgreSQL server; never point the test runner at production.

```powershell
# All tests
python manage.py test

# Single app
python manage.py test apps.home

# Single test method
python manage.py test apps.home -k test_dashboard_filter_by_category

# Show more detail
python manage.py test -v 2
```

Django's test runner discovers `tests.py` in each feature app. With SQLite, it uses an in-memory test database. No pytest dependency is required.

## Test inventory

| App | File | Tests | What is covered |
| --- | --- | --- | --- |
| `home` | [`apps/home/tests.py`](../apps/home/tests.py) | 15 | Guest landing and public map; dashboard and reports access; filters and legacy city casing; resource creation and validation |
| `login` | [`apps/login/tests.py`](../apps/login/tests.py) | 4 | Login page renders; successful login; failed login; logout |
| `register` | [`apps/register/tests.py`](../apps/register/tests.py) | 4 | Registration creates profile and settings; required name and city validation |
| `profile` | [`apps/profile/tests.py`](../apps/profile/tests.py) | 3 | Login required; profile page renders; profile update |
| `user_settings` | [`apps/user_settings/tests.py`](../apps/user_settings/tests.py) | 5 | Login required; settings and password updates; map zoom validation |

## What is not yet covered

Be aware of these gaps when evaluating coverage:

- `confirm_resource_view` and `update_resource_status_view` (including the `F('confirmations') + 1` atomic increment and the `FULL_CAPACITY` side effect) have no direct tests.
- Reports access and rendering are covered; the aggregation and breakdown calculations are not directly asserted.
- The `ResourceStatusLog` audit entries written by home mutations are not asserted.
- Tests exercise the volunteer-network filter's results, but do not assert the generated SQL.
- No coverage tooling or CI configuration is present.

## Adding a test — conventions

1. Add a `TestCase` subclass to the owning app's `tests.py`.
2. Use `reverse('<app>:<name>')` instead of hard-coded URLs.
3. For authenticated views, create a user in `setUp()` and call `self.client.login(...)`.
4. Assert on `status_code`, `assertTemplateUsed`, `assertContains`, `assertRedirects`, and model state.

Example skeleton:

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.home.models import Resource

class ResourceStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('volunteer', password='Pass12345!')
        self.client.login(username='volunteer', password='Pass12345!')
        self.resource = Resource.objects.create(name='Test Shelter', location='QC')

    def test_confirm_increments_count(self):
        response = self.client.post(
            reverse('home:confirm_resource', args=[self.resource.id])
        )
        self.resource.refresh_from_db()
        self.assertRedirects(response, reverse('home:dashboard'))
        self.assertEqual(self.resource.confirmations, 2)
```

## Manual verification

The completed course demo used the dashboard and Reports to show JOINs, and the dashboard's **My local volunteers** filter to show a subquery. To reproduce the checks with your own staging data, create volunteer accounts and listings in matching and non-matching cities, turn the filter on, and check the result set. Print the generated SQL from the Django shell and verify the underlying `aid_resources`, `auth_user`, and `user_profiles` rows in the Supabase table editor.
