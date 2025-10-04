from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView   

urlpatterns = [
    path('admin/', admin.site.urls), # not used in this project, kept for possible future inprovements
    path('tasks/', include('tasks.urls')),     
    path('', RedirectView.as_view(               
        pattern_name='task_list',                
        permanent=False
    )),
]
