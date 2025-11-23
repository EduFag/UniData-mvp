from django.urls import path
from .views import login, logout, cadastro

urlpatterns = [
    path("login/", login, name="login"),
    path("cadastro/", cadastro, name="cadastro"),
    path("logout/", logout, name="logout"),
]