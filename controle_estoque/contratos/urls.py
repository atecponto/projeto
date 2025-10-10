from django.urls import path
from . import views

urlpatterns = [
    # URLs de Sistema
    path('sistemas/', views.listar_sistemas, name='listar_sistemas'),
    path('sistemas/novo/', views.criar_sistema, name='criar_sistema'),
    path('sistemas/editar/<int:pk>/', views.editar_sistema, name='editar_sistema'),
    path('sistemas/excluir/<int:pk>/', views.excluir_sistema, name='excluir_sistema'),

    # ADICIONE AS URLs DE TÉCNICO ABAIXO
    path('tecnicos/', views.listar_tecnicos, name='listar_tecnicos'),
    path('tecnicos/novo/', views.criar_tecnico, name='criar_tecnico'),
    path('tecnicos/editar/<int:pk>/', views.editar_tecnico, name='editar_tecnico'),
    path('tecnicos/excluir/<int:pk>/', views.excluir_tecnico, name='excluir_tecnico'),
]