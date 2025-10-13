from django.db import models

class Sistema(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nome

class Tecnico(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nome

class Cliente(models.Model):
    # Tipos de Cobrança
    MENSAL = 'M'
    ANUAL = 'A'
    TIPO_COBRANCA_CHOICES = [
        (MENSAL, 'Mensal'),
        (ANUAL, 'Anual'),
    ]

    # Campos existentes
    empresa = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    sistema = models.ForeignKey(Sistema, on_delete=models.PROTECT, verbose_name="Sistema")
    # GARANTINDO A PROTEÇÃO CONTRA EXCLUSÃO
    tecnico = models.ForeignKey(Tecnico, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Técnico")
    validade = models.DateField(verbose_name="Validade do Contrato")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    pdf_anexo = models.FileField(upload_to='contratos_pdfs/', blank=True, null=True, verbose_name="Anexo PDF")
    
    # Campos de Cobrança
    tipo_cobranca = models.CharField(max_length=1, choices=TIPO_COBRANCA_CHOICES, null=True, blank=True)
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    meses_contrato = models.IntegerField(default=12, null=True, blank=True)
    valor_anual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    bloqueado = models.BooleanField(default=False, verbose_name="Bloqueado")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        ordering = ['empresa']

    def __str__(self):
        return self.empresa
    
    @property
    def valor_total_calculado(self):
        if self.tipo_cobranca == self.MENSAL and self.valor_mensal and self.meses_contrato:
            return self.valor_mensal * self.meses_contrato
        return None