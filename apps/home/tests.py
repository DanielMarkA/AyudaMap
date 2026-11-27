from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.profile.models import Profile
from .models import Resource


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="Password123!",
            first_name="Juan",
            last_name="Dela Cruz",
        )
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.full_name = "Juan Dela Cruz"
        profile.is_volunteer = True
        profile.city = "Manila"
        profile.save()

        self.resource1 = Resource.objects.create(
            name="Manila City Clinic",
            category="MEDICAL",
            status="OPERATIONAL",
            urgency_level="CRITICAL",
            location="Manila City",
            operating_hours="24/7",
            contact_info="12345",
            is_verified=True,
            created_by=self.user,
        )
        self.resource2 = Resource.objects.create(
            name="Pasig Food Pantry",
            category="FOOD",
            status="FULL_CAPACITY",
            urgency_level="MEDIUM",
            location="Pasig City",
            operating_hours="8am-5pm",
            contact_info="67890",
            is_verified=True,
        )

    def test_landing_renders_for_guest_and_authenticated(self):
        guest_res = self.client.get(reverse("home:landing"))
        self.assertEqual(guest_res.status_code, 200)
        self.assertTemplateUsed(guest_res, "home/landing.html")
        self.assertContains(guest_res, "Open Live Aid Map")

        self.client.login(username="testuser", password="Password123!")
        auth_res = self.client.get(reverse("home:landing"))
        self.assertEqual(auth_res.status_code, 200)
        self.assertTemplateUsed(auth_res, "home/landing.html")
        self.assertContains(auth_res, "Go to Volunteer Dashboard")

    def test_public_map_accessible_to_guests_with_submitter_full_name(self):
        response = self.client.get(reverse("home:map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/map.html")
        self.assertContains(response, "Manila City Clinic")
        self.assertContains(response, "Pasig Food Pantry")
        self.assertContains(response, "Juan Dela Cruz")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("home:dashboard"))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('home:dashboard')}")

    def test_reports_requires_login(self):
        response = self.client.get(reverse("home:reports"))
        self.assertRedirects(response, f"{reverse('login:login')}?next={reverse('home:reports')}")

    def test_reports_view_authenticated(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:reports"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/reports.html")

    def test_dashboard_view_authenticated(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/home.html")
        self.assertContains(response, "Manila City Clinic")
        self.assertContains(response, "Pasig Food Pantry")

    def test_dashboard_filter_by_category(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:dashboard") + "?category=MEDICAL")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manila City Clinic")
        self.assertNotContains(response, "Pasig Food Pantry")

    def test_dashboard_filter_by_status(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:dashboard") + "?status=FULL_CAPACITY")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pasig Food Pantry")
        self.assertNotContains(response, "Manila City Clinic")

    def test_dashboard_search_by_query(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:dashboard") + "?q=Pasig")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pasig Food Pantry")
        self.assertNotContains(response, "Manila City Clinic")

    def test_add_resource_view(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.post(reverse("home:add_resource"), {
            "name": "New Shelter Center",
            "category": "SHELTER",
            "status": "OPERATIONAL",
            "urgency_level": "MEDIUM",
            "description": "Safe shelter for typhoon victims",
            "capacity_total": 100,
            "capacity_available": 80,
            "location": "Quezon City",
            "latitude": 14.65,
            "longitude": 121.05,
            "operating_hours": "24/7",
            "contact_info": "555-1234",
        })
        self.assertRedirects(response, reverse("home:dashboard"))
        res = Resource.objects.filter(name="New Shelter Center").first()
        self.assertIsNotNone(res)
        self.assertEqual(res.created_by, self.user)
        self.assertEqual(res.status, "OPERATIONAL")
