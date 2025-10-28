from django import forms
from .models import CategoriaPedido

class CategoriaPedidoForm(forms.ModelForm):
    class Meta:
        model = CategoriaPedido
        fields = ['nome', 'descricao'] 
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['descricao'].widget.attrs.update({'class': 'form-control'})