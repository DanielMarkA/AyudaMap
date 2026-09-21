from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Resource

class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="Password123!")
        self.resource1 = Resource.objects.create(
            name="Manila City Clinic",
            category="MEDICAL",
            status="OPERATIONAL",
            location="Manila City",
            operating_hours="24/7",
            contact_info="12345",
            is_verified=True,
            created_by=self.user
        )
        self.resource2 = Resource.objects.create(
            name="Pasig Food Pantry",
            category="FOOD",
            status="FULL_CAPACITY",
            location="Pasig City",
            operating_hours="8am-5pm",
            contact_info="67890",
            is_verified=True
        )

    def test_home_requires_login(self):
        response = self.client.get(reverse("home:home"))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('home:home')}")

    def test_home_view_authenticated(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/home.html")
        self.assertContains(response, "Manila City Clinic")
        self.assertContains(response, "Pasig Food Pantry")

    def test_home_filter_by_category(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:home") + "?category=MEDICAL")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manila City Clinic")
        self.assertNotContains(response, "Pasig Food Pantry")

    def test_home_filter_by_status(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:home") + "?status=FULL_CAPACITY")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pasig Food Pantry")
        self.assertNotContains(response, "Manila City Clinic")

    def test_home_search_by_query(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:home") + "?q=Pasig")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pasig Food Pantry")
        self.assertNotContains(response, "Manila City Clinic")

    def test_add_resource_view(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.post(reverse("home:add_resource"), {
            "name": "New Shelter Center",
            "category": "SHELTER",
            "status": "OPERATIONAL",
            "description": "Safe shelter for typhoon victims",
            "location": "Quezon City",
            "latitude": 14.65,
            "longitude": 121.05,
            "operating_hours": "24/7",
            "contact_info": "555-1234"
        })
        self.assertRedirects(response, reverse("home:home"))
        res = Resource.objects.filter(name="New Shelter Center").first()
        self.assertIsNotNone(res)
        self.assertEqual(res.created_by, self.user)
        self.assertEqual(res.status, "OPERATIONAL")
