from django.urls import path
from . import views

urlpatterns = [
    # O 'name'="listar_pedidos" é o "apelido" que o dashboard.html usa
    path('', views.listar_pedidos, name='listar_pedidos'),
]