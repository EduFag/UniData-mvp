from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login_paciente'),
    path('dashboard/', views.dashboard, name='dashboard_paciente'),
    path('logout/', views.logout, name='logout_paciente'),
    path('cadastro/', views.cadastro, name='cadastro_paciente'),
]




