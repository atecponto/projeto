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