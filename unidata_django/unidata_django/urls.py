"""
URL configuration for unidata project.
"""
from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    path('', home, name="home"),
    path('admin/', admin.site.urls),
    path('', include('app_paciente.urls')),
    path('', include('app_profissional.urls')),
]




