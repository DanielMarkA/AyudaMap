# Testing

## Running the suite

```powershell
# All tests
python manage.py test

# Single app
python manage.py test apps.home

# Single test method
python manage.py test apps.home.tests.HomeViewTests.test_home_filter_by_category

# Show more detail
python manage.py test -v 2
```

Django's test runner discovers `tests.py` in each feature app. Tests use Django's `TestCase` and an in-memory/test database, so they never touch your real Supabase data. No pytest dependency is required.

## Test inventory (19 tests)

| App | File | Tests | What is covered |
| --- | --- | --- | --- |
| `home` | [`apps/home/tests.py`](../apps/home/tests.py) | 6 | Login redirect on `/`; authenticated home page renders and lists resources; filter by category; filter by status; keyword search; adding a resource sets `created_by` and status |
| `login` | [`apps/login/tests.py`](../apps/login/tests.py) | 4 | Login page renders; successful login; failed login; logout |
| `register` | [`apps/register/tests.py`](../apps/register/tests.py) | 2 | Register page renders; registration creates both `Profile` and `UserSettings` |
| `profile` | [`apps/profile/tests.py`](../apps/profile/tests.py) | 3 | Login required; profile page renders; profile update |
| `user_settings` | [`apps/user_settings/tests.py`](../apps/user_settings/tests.py) | 4 | Login required; settings page renders; settings update; password change |

## What is not yet covered

Be aware of these gaps when evaluating coverage:

- `confirm_resource_view` and `update_resource_status_view` (including the `F('confirmations') + 1` atomic increment and the `FULL_CAPACITY` side effect) have no direct tests.
- `reports_view` has no tests, including its aggregates and category/urgency breakdowns.
- The `ResourceStatusLog` audit entries written by home mutations are not asserted.
- No tests exercise the generated SQL or result sets of the JOIN / SUBQUERY demo page (`/queries/`).
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
        self.assertRedirects(response, reverse('home:home'))
        self.assertEqual(self.resource.confirmations, 2)
```

## Manual verification

The course activity requires demonstrating JOIN and SUBQUERY behaviour in the running app and in the database. Open `/queries/` to show both result sets and their generated SQL, then verify the underlying `aid_resources`, `auth_user`, and `user_profiles` rows in the Supabase table editor.
