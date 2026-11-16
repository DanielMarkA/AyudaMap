from django.urls import path
from .views import (
    home_view,
    add_resource_view,
    confirm_resource_view,
    update_resource_status_view,
    reports_view,
)

app_name = "home"

urlpatterns = [
    path("", home_view, name="home"),
    path("reports/", reports_view, name="reports"),
    path("add/", add_resource_view, name="add_resource"),
    path("<int:resource_id>/confirm/", confirm_resource_view, name="confirm_resource"),
    path("<int:resource_id>/status/", update_resource_status_view, name="update_status"),
]