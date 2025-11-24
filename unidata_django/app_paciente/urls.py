from django.urls import path
from . import views

app_name = 'pessoas'

urlpatterns = [
    path('login/', views.paciente_login, name='login'),
    path('cadastro/', views.paciente_cadastro, name='cadastro'),
    path('dashboard/', views.paciente_dashboard, name='dashboard'),
    path('logout/', views.paciente_logout, name='logout'),
    path('pessoas/', views.listar_pessoas, name='listar_pessoas'),
    path('cadastrar/', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('gerar-carteira/', views.gerar_carteira_form, name='gerar_carteira_form'),
    path('gerar-carteira/<int:pessoa_id>/', views.gerar_carteira, name='gerar_carteira'),
]




