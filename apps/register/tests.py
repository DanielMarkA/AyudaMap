from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.profile.models import Profile
from apps.user_settings.models import UserSettings

class RegisterViewTests(TestCase):
    def test_register_page_renders(self):
        response = self.client.get(reverse("register:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register/register.html")

    def test_register_user_creates_profile_and_settings(self):
        response = self.client.post(reverse("register:register"), {
            "username": "newvolunteer",
            "email": "volunteer@test.com",
            "full_name": "New Volunteer",
            "password1": "SecurePass2026!",
            "password2": "SecurePass2026!"
        })
        self.assertRedirects(response, reverse("home:home"))
        
        user = User.objects.get(username="newvolunteer")
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "Volunteer")
        
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.full_name, "New Volunteer")
        
        self.assertTrue(UserSettings.objects.filter(user=user).exists())
