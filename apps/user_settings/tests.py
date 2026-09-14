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
            "dark_mode": True,
            "email_notifications": True,
            "notify_on_new_resources": False,
            "preferred_category": "DONATION"
        })
        self.assertRedirects(response, reverse("user_settings:settings"))
        
        settings = UserSettings.objects.get(user=self.user)
        self.assertTrue(settings.dark_mode)
        self.assertTrue(settings.email_notifications)
        self.assertFalse(settings.notify_on_new_resources)
        self.assertEqual(settings.preferred_category, "DONATION")
