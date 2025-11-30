# todo_project/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('tasks.urls')),
]

# Only add the admin URL when the admin app is installed
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    urlpatterns += [path('admin/', admin.site.urls)]
