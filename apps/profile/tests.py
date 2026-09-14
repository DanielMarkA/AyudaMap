from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testprofileuser", password="Password123!")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile:profile"))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('profile:profile')}")

    def test_profile_view_authenticated(self):
        self.client.login(username="testprofileuser", password="Password123!")
        response = self.client.get(reverse("profile:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile/profile.html")
        self.assertContains(response, "testprofileuser")

    def test_profile_update(self):
        self.client.login(username="testprofileuser", password="Password123!")
        response = self.client.post(reverse("profile:profile"), {
            "first_name": "Maria",
            "last_name": "Santos",
            "email": "maria.santos@test.com",
            "full_name": "Maria Santos",
            "bio": "Volunteering for relief packing operations.",
            "phone_number": "+63 912 345 6789",
            "city": "Cebu City"
        })
        self.assertRedirects(response, reverse("profile:profile"))
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Maria")
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.full_name, "Maria Santos")
        self.assertEqual(profile.city, "Cebu City")

