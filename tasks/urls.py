from django.urls import path
from . import views as t

urlpatterns = [
    path('', t.task_list, name='task_list'),
    path('new/', t.task_create, name='task_create'),
    path('<int:pk>/edit/', t.task_update, name='task_update'),
    path('<int:pk>/delete/', t.task_delete, name='task_delete'),
    path('<int:pk>/toggle/', t.task_toggle, name='task_toggle'),
]
