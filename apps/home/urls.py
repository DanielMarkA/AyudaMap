from django.urls import path
from .views import (
    landing_view,
    map_view,
    dashboard_view,
    add_resource_view,
    confirm_resource_view,
    update_resource_status_view,
    reports_view,
)

app_name = "home"

urlpatterns = [
    path("", landing_view, name="landing"),
    path("map/", map_view, name="map"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("reports/", reports_view, name="reports"),
    path("add/", add_resource_view, name="add_resource"),
    path("<int:resource_id>/confirm/", confirm_resource_view, name="confirm_resource"),
    path("<int:resource_id>/status/", update_resource_status_view, name="update_status"),
]
