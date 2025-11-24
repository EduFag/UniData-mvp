from django.urls import path
from .views import login, logout, cadastro, dashboard, buscar_paciente, ver_prontuario

urlpatterns = [
    path("login/", login, name="login_profissional"),
    path("cadastro/", cadastro, name="cadastro_profissional"),
    path("logout/", logout, name="logout_profissional"),
    path("painel-medico/", dashboard, name="dashboard_profissional"),
    path("buscar-paciente/", buscar_paciente, name="buscar_paciente"),
    path("prontuario/<int:paciente_id>/", ver_prontuario, name="ver_prontuario"),
]