from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventario import views
# --- IMPORTS ADICIONADOS AQUI ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.root_redirect, name='root_redirect'),

    # Autenticação e Dashboard
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro_usuario_view, name='cadastro'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Reset de Senha
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuario/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="usuario/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuario/password_reset_complete.html'), name='password_reset_complete'),

    # Gerenciamento de Usuário
    path('usuario/', views.gerenciamento_usuario, name='gerenciamento_usuario'),
    path('usuario/toggle-admin/<int:user_id>/', views.mudar_status_admin, name='mudar_status_admin'),
    path('usuario/toggle-ativo/<int:user_id>/', views.mudar_status_ativo, name='mudar_status_ativo'),
    path('usuario/excluir/<int:user_id>/', views.excluir_usuario, name='excluir_usuario'),

    # Seção de Contratos (agora inclui as URLs do novo app)
    path('contratos/', include('contratos.urls')),

    # Seção de Estoque
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produto/novo/', views.criar_produto, name='criar_produto'),
    path('produto/editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('produto/excluir/<int:pk>/', views.excluir_produto, name='excluir_produto'),
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categoria/nova/', views.criar_categoria, name='criar_categoria'),
    path('categoria/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categoria/excluir/<int:pk>/', views.excluir_categoria, name='excluir_categoria'),
    path('transacoes/', views.listar_transacao, name='listar_transacao'),
    path('transacao/nova/', views.criar_transacao, name='criar_transacao'),
    path('transacao/arquivar/<int:pk>/', views.arquivar_transacao, name='arquivar_transacao'),
    path('relatorios/', views.transacao_pdf_view, name='relatorio_transacoes'),
]

# --- BLOCO DE CÓDIGO ADICIONADO PARA SERVIR ARQUIVOS DE MÍDIA EM DESENVOLVIMENTO ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)