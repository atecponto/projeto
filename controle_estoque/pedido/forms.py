from django import forms
from .models import CategoriaPedido, ClientePedido

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

class ClientePedidoForm(forms.ModelForm):
    class Meta:
        model = ClientePedido
        fields = ['nome', 'cnpj', 'email', 'telefone', 'contato', 'categoria']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica classes Bootstrap
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Adiciona IDs 
        self.fields['cnpj'].widget.attrs.update({
            'id': 'id_cnpj_mascara_pedido', 
            'placeholder': '00.000.000/0000-00'
        })
        self.fields['telefone'].widget.attrs.update({
            'id': 'id_telefone_mascara_pedido', 
            'placeholder': '(00) 00000-0000'
        })
        
        self.fields['categoria'].empty_label = "Nenhuma categoria"