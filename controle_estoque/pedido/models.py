from django.db import models

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
    nome = models.CharField(max_length=200, verbose_name="Nome/Empresa")
    cnpj = models.CharField(max_length=18, verbose_name="CNPJ/CPF", unique=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    contato = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pessoa de Contato")
    
    # Campo para o filtro
    categoria = models.ForeignKey(CategoriaPedido, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria Padrão")

    class Meta:
        ordering = ['nome']
        verbose_name = "Cliente (Pedido)"
        verbose_name_plural = "Clientes (Pedido)"

    def __str__(self):
        return self.nome