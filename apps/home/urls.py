from django.urls import path
from .views import home_view, add_resource_view

app_name = "home"

urlpatterns = [
    path("", home_view, name="home"),
    path("add/", add_resource_view, name="add_resource"),
]