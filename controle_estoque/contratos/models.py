from django.db import models

class Sistema(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Tecnico(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

# --- ADICIONE O NOVO MODELO 'CLIENTE' ABAIXO ---
class Cliente(models.Model):
    empresa = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    sistema = models.ForeignKey(Sistema, on_delete=models.PROTECT, verbose_name="Sistema")
    tecnico = models.ForeignKey(Tecnico, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Técnico")
    validade = models.DateField(verbose_name="Validade do Contrato")

    class Meta:
        ordering = ['empresa']

    def __str__(self):
        return self.empresa