from django.urls import path
from . import views

urlpatterns = [
    # URLs de Sistema
    path('sistemas/', views.listar_sistemas, name='listar_sistemas'),
    path('sistemas/novo/', views.criar_sistema, name='criar_sistema'),
    path('sistemas/editar/<int:pk>/', views.editar_sistema, name='editar_sistema'),
    path('sistemas/excluir/<int:pk>/', views.excluir_sistema, name='excluir_sistema'),

    # URLs de Técnico
    path('tecnicos/', views.listar_tecnicos, name='listar_tecnicos'),
    path('tecnicos/novo/', views.criar_tecnico, name='criar_tecnico'),
    path('tecnicos/editar/<int:pk>/', views.editar_tecnico, name='editar_tecnico'),
    path('tecnicos/excluir/<int:pk>/', views.excluir_tecnico, name='excluir_tecnico'),

    # ADICIONE AS URLs DE CLIENTE ABAIXO
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/novo/', views.criar_cliente, name='criar_cliente'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:pk>/', views.excluir_cliente, name='excluir_cliente'),

    path('clientes/toggle-bloqueado/<int:pk>/', views.toggle_bloqueado_cliente, name='toggle_bloqueado_cliente'),
]
