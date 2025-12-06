from django.urls import path
from monitoring import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("settings/", views.org_settings, name="org_settings"),
]
