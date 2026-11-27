from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserSettings

class UserSettingsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testsettingsuser", password="Password123!")

    def test_settings_requires_login(self):
        response = self.client.get(reverse("user_settings:settings"))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('user_settings:settings')}")

    def test_settings_view_authenticated(self):
        self.client.login(username="testsettingsuser", password="Password123!")
        response = self.client.get(reverse("user_settings:settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_settings/settings.html")

    def test_settings_update(self):
        self.client.login(username="testsettingsuser", password="Password123!")
        response = self.client.post(reverse("user_settings:settings"), {
            "action": "save_settings",
            "dark_mode": True,
            "email_notifications": True,
            "notify_on_new_resources": False,
            "default_latitude": 14.65,
            "default_longitude": 121.05,
            "default_zoom": 18,
        })
        self.assertRedirects(response, reverse("user_settings:settings"))
        
        settings = UserSettings.objects.get(user=self.user)
        self.assertTrue(settings.dark_mode)
        self.assertTrue(settings.email_notifications)
        self.assertFalse(settings.notify_on_new_resources)
        self.assertEqual(settings.default_zoom, 18)

    def test_settings_rejects_zoom_outside_supported_range(self):
        self.client.force_login(self.user)
        for zoom in (4, 19):
            with self.subTest(zoom=zoom):
                response = self.client.post(reverse("user_settings:settings"), {
                    "action": "save_settings",
                    "default_latitude": 14.65,
                    "default_longitude": 121.05,
                    "default_zoom": zoom,
                })
                self.assertEqual(response.status_code, 200)
                self.assertIn("default_zoom", response.context["form"].errors)
                self.assertEqual(UserSettings.objects.get(user=self.user).default_zoom, 12)

    def test_change_password(self):
        self.client.login(username="testsettingsuser", password="Password123!")
        response = self.client.post(reverse("user_settings:settings"), {
            "action": "change_password",
            "old_password": "Password123!",
            "new_password1": "BrandNewPass2026!",
            "new_password2": "BrandNewPass2026!",
        })
        self.assertRedirects(response, reverse("user_settings:settings"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNewPass2026!"))
