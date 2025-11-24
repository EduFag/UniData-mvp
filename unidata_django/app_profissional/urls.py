from django.urls import path
from .views import login, logout, cadastro, dashboard

urlpatterns = [
    path("login/", login, name="login_profissional"),
    path("cadastro/", cadastro, name="cadastro_profissional"),
    path("logout/", logout, name="logout_profissional"),
    path("painel-medico/", dashboard, name="dashboard_profissional"),

]