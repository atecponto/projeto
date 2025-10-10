from django.db import models

# Create your models here.
from django.db import models

class Sistema(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome