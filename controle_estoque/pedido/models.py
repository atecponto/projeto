from django.db import models
from decimal import Decimal
from contratos.models import Tecnico
from django.conf import settings
from django.utils import timezone

class CategoriaPedido(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        ordering = ['nome']
        verbose_name = "Categoria de Pedido"
        verbose_name_plural = "Categorias de Pedido"

    def __str__(self):
        return self.nome
    
class ClientePedido(models.Model):
    usuario_criador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, # Se o usuário for deletado, o campo fica nulo
        null=True, 
        blank=True,
        verbose_name="Usuário Criador"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data de Cadastro"
    )

    nome = models.CharField(max_length=200, verbose_name="Nome/Empresa")
    cnpj = models.CharField(max_length=18, verbose_name="CNPJ/CPF")
    email = models.EmailField(max_length=254, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    contato = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pessoa de Contato")

    endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name="Endereço")
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP") 
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado (UF)") 
    
    # Campo para o filtro
    categoria = models.ForeignKey(CategoriaPedido, on_delete=models.PROTECT, verbose_name="Categoria do Pedido", default=1) # Certifique-se que ID 1 existe
    tecnico = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Técnico Responsável")
    descricao_pedido = models.TextField(blank=True, null=True, verbose_name="Descrição do Pedido")
    

    valor_pedido = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Pedido", default=Decimal('0.00'))
 
    
    class Meta:
        ordering = ['nome']
        verbose_name = "Cliente (Pedido)"
        verbose_name_plural = "Clientes (Pedido)"

    # Atualizei o __str__ para ficar mais informativo
    def __str__(self):
        return f"{self.nome} ({self.cnpj})"