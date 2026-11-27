from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPassword123!")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")

    def test_login_success(self):
        response = self.client.post(reverse("login:login"), {
            "username": "testuser",
            "password": "TestPassword123!"
        })
        self.assertRedirects(response, reverse("home:dashboard"))

    def test_login_failure(self):
        response = self.client.post(reverse("login:login"), {
            "username": "testuser",
            "password": "WrongPassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_logout(self):
        self.client.login(username="testuser", password="TestPassword123!")
        response = self.client.get(reverse("login:logout"))
        self.assertRedirects(response, reverse("login:login"))
