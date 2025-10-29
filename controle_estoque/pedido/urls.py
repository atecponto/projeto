from django.urls import path
from . import views

app_name = 'pedido'

urlpatterns = [
    # O 'name'="listar_pedidos" é o "apelido" que o dashboard.html usa
    path('', views.listar_pedidos, name='listar_pedidos'),

    # categorias de pedido
    path('categorias/', views.listar_categorias_pedido, name='listar_categorias_pedido'),
    path('categorias/nova/', views.criar_categoria_pedido, name='criar_categoria_pedido'),
    path('categorias/editar/<int:pk>/', views.editar_categoria_pedido, name='editar_categoria_pedido'),
    path('categorias/excluir/<int:pk>/', views.excluir_categoria_pedido, name='excluir_categoria_pedido'),

    # clientes de pedido
    path('clientes/', views.listar_clientes_pedido, name='listar_clientes_pedido'),
    path('clientes/novo/', views.criar_cliente_pedido, name='criar_cliente_pedido'),
    path('clientes/editar/<int:pk>/', views.editar_cliente_pedido, name='editar_cliente_pedido'),
    path('clientes/excluir/<int:pk>/', views.excluir_cliente_pedido, name='excluir_cliente_pedido'),
]