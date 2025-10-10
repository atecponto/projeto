from django import forms
from .models import Sistema, Tecnico # Adicione Tecnico aqui

class SistemaForm(forms.ModelForm):
    class Meta:
        model = Sistema
        fields = ['nome']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite o nome do sistema'
        })

# ADICIONE O CÓDIGO ABAIXO
class TecnicoForm(forms.ModelForm):
    class Meta:
        model = Tecnico
        fields = ['nome']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite o nome do técnico'
        })