# todo_project/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from .views import health   # <-- import the project-level health view

urlpatterns = [
    path("", include("tasks.urls")),    # all your /, /create/, etc. from tasks app
    path("health/", health, name="health"),
    path("", include("django_prometheus.urls")),  # global health endpoint
]

# Only add the admin URL when the admin app is installed
if "django.contrib.admin" in settings.INSTALLED_APPS:
    urlpatterns += [path("admin/", admin.site.urls)]
