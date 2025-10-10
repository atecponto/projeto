from django.urls import path
from . import views

urlpatterns = [
    path('sistemas/', views.listar_sistemas, name='listar_sistemas'),
    path('sistemas/novo/', views.criar_sistema, name='criar_sistema'),
    path('sistemas/editar/<int:pk>/', views.editar_sistema, name='editar_sistema'),
    path('sistemas/excluir/<int:pk>/', views.excluir_sistema, name='excluir_sistema'),
]