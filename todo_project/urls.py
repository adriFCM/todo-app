"""
URL configuration for todo_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views as t

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', t.task_list, name='task_list'),
    path('tasks/new/', t.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', t.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', t.task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle/', t.task_toggle, name='task_toggle'),
]