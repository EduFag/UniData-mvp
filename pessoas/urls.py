from django.urls import path
from . import views

app_name = 'pessoas'

urlpatterns = [
    path('', views.listar_pessoas, name='listar_pessoas'),
    path('cadastrar/', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('gerar-carteira/', views.gerar_carteira_form, name='gerar_carteira_form'),
    path('gerar-carteira/<int:pessoa_id>/', views.gerar_carteira, name='gerar_carteira'),
]




