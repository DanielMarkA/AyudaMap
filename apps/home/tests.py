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
            city="Manila",
            location="Sampaloc, Manila",
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
            city="Pasig",
            location="Ortigas Ave, Pasig",
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

    def test_map_json_escapes_html_characters(self):
        self.resource1.name = "Clinic <East> & West"
        self.resource1.save(update_fields=["name"])
        self.client.force_login(self.user)

        for route in ("home:map", "home:dashboard"):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, r'"Clinic \u003CEast\u003E \u0026 West"')

        response = self.client.get(reverse("home:map"), {"q": "<East> & West"})
        self.assertContains(response, r'"q": "\u003CEast\u003E \u0026 West"')

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

    def test_dashboard_local_volunteers_filter_without_profile(self):
        self.client.force_login(self.user)
        dashboard_url = reverse("home:dashboard")
        response = self.client.get(dashboard_url, {"local_volunteers": "1"})
        self.assertContains(response, "Manila City Clinic")
        self.assertNotContains(response, "Pasig Food Pantry")

        Profile.objects.filter(user=self.user).delete()
        response = self.client.get(dashboard_url, {"local_volunteers": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["resources"]), [])

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
            "city": "Quezon City",
            "location": "Maginhawa St, Teachers Village",
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
        self.assertEqual(res.city, "Quezon City")
        self.assertEqual(res.display_location, "Maginhawa St, Teachers Village, Quezon City")

    def test_add_resource_rejects_available_capacity_above_total(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("home:add_resource"), {
            "name": "New Shelter Center",
            "category": "SHELTER",
            "status": "OPERATIONAL",
            "urgency_level": "MEDIUM",
            "capacity_total": 10,
            "capacity_available": 20,
            "city": "Quezon City",
            "location": "Maginhawa St",
            "latitude": 14.65,
            "longitude": 121.05,
            "operating_hours": "24/7",
        }, follow=True)
        self.assertContains(response, "Available capacity cannot exceed total capacity.")
        self.assertFalse(Resource.objects.filter(name="New Shelter Center").exists())

    def test_add_resource_rejects_invalid_city(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("home:add_resource"), {
            "name": "Bad City Hub",
            "category": "SHELTER",
            "status": "OPERATIONAL",
            "urgency_level": "MEDIUM",
            "capacity_total": 10,
            "capacity_available": 5,
            "city": "quezon",
            "location": "Some Street",
            "latitude": 14.65,
            "longitude": 121.05,
            "operating_hours": "24/7",
        }, follow=True)
        self.assertFalse(Resource.objects.filter(name="Bad City Hub").exists())

    def test_local_volunteers_filter_is_case_insensitive_for_legacy_city_casing(self):
        peer = User.objects.create_user(username="qc_peer", password="Password123!")
        peer_profile, _ = Profile.objects.get_or_create(user=peer)
        peer_profile.is_volunteer = True
        peer_profile.city = "Quezon City"
        peer_profile.save()

        Resource.objects.create(
            name="QC Pantry",
            category="FOOD",
            status="OPERATIONAL",
            urgency_level="LOW",
            city="Quezon City",
            location="Maginhawa St",
            is_verified=True,
            created_by=peer,
        )

        # Simulate legacy lowercase/alias profile value on the logged-in user
        Profile.objects.filter(user=self.user).update(city="quezon city")
        self.client.force_login(self.user)
        response = self.client.get(reverse("home:dashboard"), {"local_volunteers": "1"})
        self.assertContains(response, "QC Pantry")
        self.assertNotContains(response, "Manila City Clinic")
