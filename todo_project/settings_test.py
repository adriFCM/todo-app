from .settings import *  # import your normal settings
# Temporarily remove the Django admin app to bypass the AdminSite error
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django.contrib.admin"]
