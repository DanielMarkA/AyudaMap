from datetime import datetime, time
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from apps.profile.models import Profile
from .models import Resource, ResourceStatusLog

MANILA_TZ = ZoneInfo("Asia/Manila")


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
            city="Manila",
            location="Sampaloc, Manila",
            is_24_7=True,
            opens_at=None,
            closes_at=None,
            services_offered=["MEDICAL", "WATER"],
            supplies_needed="Internal Bandage Stock",
            contact_info="12345",
            is_verified=True,
            created_by=self.user,
        )
        self.resource2 = Resource.objects.create(
            name="Pasig Food Pantry",
            category="FOOD",
            status="LIMITED",
            city="Pasig",
            location="Ortigas Ave, Pasig",
            is_24_7=False,
            opens_at=time(8, 0),
            closes_at=time(17, 0),
            services_offered=["FOOD"],
            supplies_needed="Drinking Water",
            contact_info="67890",
            is_verified=True,
        )

    def test_landing_renders_for_guest_and_authenticated(self):
        guest_res = self.client.get(reverse("home:landing"))
        self.assertEqual(guest_res.status_code, 200)
        self.assertTemplateUsed(guest_res, "home/landing.html")
        self.assertContains(guest_res, "Open Live Aid Map")
        self.assertContains(guest_res, "Open Right Now")
        self.assertNotContains(guest_res, "Critical Priority")

        self.client.login(username="testuser", password="Password123!")
        auth_res = self.client.get(reverse("home:landing"))
        self.assertEqual(auth_res.status_code, 200)
        self.assertTemplateUsed(auth_res, "home/landing.html")
        self.assertContains(auth_res, "Go to Volunteer Dashboard")

    def test_public_map_accessible_to_guests_without_urgency_or_supplies_needed(self):
        response = self.client.get(reverse("home:map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/map.html")
        self.assertContains(response, "Manila City Clinic")
        self.assertContains(response, "Pasig Food Pantry")
        self.assertContains(response, "Juan Dela Cruz")
        self.assertContains(response, "Drinking Water")
        self.assertContains(response, "First Aid / Meds")
        self.assertNotContains(response, "Internal Bandage Stock")
        self.assertNotContains(response, "mapUrgencyFilter")
        self.assertNotContains(response, "drawerCriticalBadge")

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

    def test_reports_view_shows_open_havens_by_city_and_service(self):
        self.client.login(username="testuser", password="Password123!")
        evening = datetime(2026, 11, 28, 19, 30, tzinfo=MANILA_TZ)
        with patch("apps.home.models.timezone.localtime", return_value=evening):
            response = self.client.get(reverse("home:reports"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/reports.html")
        self.assertContains(response, "Currently Open Havens by City")
        self.assertContains(response, "Currently Open Havens by Service")
        self.assertContains(response, "Coverage by Aid Category")
        self.assertNotContains(response, "Priority &amp; Urgency Breakdown")

        city_map = {row["city"]: row for row in response.context["city_stats"]}
        self.assertEqual(city_map["Manila"]["open_count"], 1)
        self.assertEqual(city_map["Pasig"]["open_count"], 0)

        svc_map = {row["code"]: row["open_count"] for row in response.context["service_stats"]}
        self.assertEqual(svc_map["WATER"], 1)
        self.assertEqual(svc_map["MEDICAL"], 1)
        self.assertEqual(svc_map["FOOD"], 0)

    def test_dashboard_view_authenticated_with_directions(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/home.html")
        self.assertContains(response, "Manila City Clinic")
        self.assertContains(response, "Pasig Food Pantry")
        self.assertContains(response, "https://www.google.com/maps/dir/?api=1&destination=")
        self.assertNotContains(response, "urgencySelect")
        self.assertNotContains(response, "Internal Bandage Stock")

    def test_dashboard_filter_by_category(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:dashboard") + "?category=MEDICAL")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manila City Clinic")
        self.assertNotContains(response, "Pasig Food Pantry")

    def test_dashboard_filter_request_returns_matching_rows_and_pins(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("home:dashboard"),
            {"category": "MEDICAL", "local_volunteers": "1"},
            headers={"X-Dashboard-Filters": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Dashboard-Filters", response.headers["Vary"])
        data = response.json()
        self.assertIn("Manila City Clinic", data["results"])
        self.assertIn('name="csrfmiddlewaretoken"', data["results"])
        self.assertNotIn("Pasig Food Pantry", data["results"])
        self.assertNotIn("ayudaMapViewport", data["results"])
        self.assertEqual([item["id"] for item in data["map_data"]], [self.resource1.pk])
        self.assertEqual((data["operational_count"], data["total_count"]), (1, 1))

    def test_dashboard_filter_by_effective_status_during_and_after_hours(self):
        self.client.login(username="testuser", password="Password123!")

        midday = datetime(2026, 11, 28, 12, 0, tzinfo=MANILA_TZ)
        with patch("apps.home.models.timezone.localtime", return_value=midday):
            response = self.client.get(reverse("home:dashboard") + "?status=LIMITED")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Pasig Food Pantry")
            self.assertNotContains(response, "Manila City Clinic")

        evening = datetime(2026, 11, 28, 19, 30, tzinfo=MANILA_TZ)
        with patch("apps.home.models.timezone.localtime", return_value=evening):
            closed_res = self.client.get(reverse("home:dashboard") + "?status=CLOSED")
            self.assertContains(closed_res, "Pasig Food Pantry")
            self.assertNotContains(closed_res, "Manila City Clinic")

            limited_res = self.client.get(reverse("home:dashboard") + "?status=LIMITED")
            self.assertNotContains(limited_res, "Pasig Food Pantry")

    def test_overnight_operating_hours_auto_close(self):
        night_shelter = Resource.objects.create(
            name="Night Safe Haven",
            category="SHELTER",
            status="OPERATIONAL",
            city="Manila",
            location="Taft Ave",
            is_24_7=False,
            opens_at=time(18, 0),
            closes_at=time(6, 0),
            is_verified=True,
        )
        late_night = datetime(2026, 11, 28, 22, 0, tzinfo=MANILA_TZ)
        early_morning = datetime(2026, 11, 28, 3, 0, tzinfo=MANILA_TZ)
        noon = datetime(2026, 11, 28, 12, 0, tzinfo=MANILA_TZ)

        self.assertTrue(night_shelter.is_within_operating_hours(now=late_night))
        self.assertTrue(night_shelter.is_within_operating_hours(now=early_morning))
        self.assertFalse(night_shelter.is_within_operating_hours(now=noon))

    def test_dashboard_does_not_render_search_input(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.get(reverse("home:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="q"')

    def test_public_map_preserves_query_param_without_exposing_supplies_needed(self):
        response = self.client.get(reverse("home:map"), {"q": "Pasig"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"q": "Pasig"')
        self.assertNotContains(response, "Internal Bandage Stock")

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

    def test_add_resource_view_with_services_and_24_7(self):
        self.client.login(username="testuser", password="Password123!")
        response = self.client.post(reverse("home:add_resource"), {
            "name": "New Shelter Haven",
            "category": "SHELTER",
            "status": "OPERATIONAL",
            "description": "Safe shelter for typhoon victims",
            "services_offered": ["SHELTER", "WATER", "POWER"],
            "city": "Quezon City",
            "location": "Maginhawa St, Teachers Village",
            "latitude": 14.65,
            "longitude": 121.05,
            "is_24_7": "on",
            "contact_info": "555-1234",
        })
        self.assertRedirects(response, reverse("home:dashboard"))
        res = Resource.objects.filter(name="New Shelter Haven").first()
        self.assertIsNotNone(res)
        self.assertEqual(res.created_by, self.user)
        self.assertEqual(res.status, "OPERATIONAL")
        self.assertTrue(res.is_24_7)
        self.assertEqual(res.operating_hours_display, "24/7")
        self.assertEqual(res.services_offered, ["SHELTER", "WATER", "POWER"])
        self.assertEqual(res.city, "Quezon City")
        self.assertEqual(res.display_location, "Maginhawa St, Teachers Village, Quezon City")
        log = ResourceStatusLog.objects.filter(resource=res).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action_type, "STATUS_UPDATE")
        self.assertEqual(log.new_status, "OPERATIONAL")
        self.assertEqual(log.updated_by, self.user)

    def test_confirm_resource_increments_count_and_creates_log(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("home:confirm_resource", args=[self.resource1.id]))
        self.assertRedirects(response, reverse("home:dashboard"))
        self.resource1.refresh_from_db()
        self.assertEqual(self.resource1.confirmations, 2)
        log = ResourceStatusLog.objects.filter(resource=self.resource1, action_type="CONFIRM_ACTIVE").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.updated_by, self.user)

    def test_update_resource_status_updates_status_and_creates_log(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("home:update_status", args=[self.resource1.id]),
            {"status": "LIMITED"},
        )
        self.assertRedirects(response, reverse("home:dashboard"))
        self.resource1.refresh_from_db()
        self.assertEqual(self.resource1.status, "LIMITED")
        log = ResourceStatusLog.objects.filter(resource=self.resource1, action_type="STATUS_UPDATE").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.previous_status, "OPERATIONAL")
        self.assertEqual(log.new_status, "LIMITED")
        self.assertEqual(log.updated_by, self.user)

    def test_update_resource_status_ignores_invalid_or_unchanged_status(self):
        self.client.force_login(self.user)
        for bad_status in ("BOGUS", "OPERATIONAL"):
            with self.subTest(status=bad_status):
                response = self.client.post(
                    reverse("home:update_status", args=[self.resource1.id]),
                    {"status": bad_status},
                )
                self.assertRedirects(response, reverse("home:dashboard"))
                self.resource1.refresh_from_db()
                self.assertEqual(self.resource1.status, "OPERATIONAL")
                self.assertFalse(ResourceStatusLog.objects.filter(resource=self.resource1).exists())

    def test_add_resource_rejects_identical_open_and_close_times(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("home:add_resource"), {
            "name": "Bad Hours Haven",
            "category": "SHELTER",
            "status": "OPERATIONAL",
            "city": "Quezon City",
            "location": "Maginhawa St",
            "latitude": 14.65,
            "longitude": 121.05,
            "opens_at": "08:00",
            "closes_at": "08:00",
        }, follow=True)
        self.assertContains(response, "Closing time must differ from opening time")
        self.assertFalse(Resource.objects.filter(name="Bad Hours Haven").exists())

    def test_add_resource_rejects_invalid_city(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("home:add_resource"), {
            "name": "Bad City Hub",
            "category": "SHELTER",
            "status": "OPERATIONAL",
            "city": "quezon",
            "location": "Some Street",
            "latitude": 14.65,
            "longitude": 121.05,
            "is_24_7": "on",
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
