from django import forms
from .models import Sistema, Tecnico, Cliente

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

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['empresa', 'cnpj', 'sistema', 'tecnico', 'validade']
        widgets = {
            'validade': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Opcional: Adicionar um item vazio para seleção
        self.fields['tecnico'].empty_label = "Nenhum técnico selecionado"

        # ADICIONADO AQUI: Um ID específico para o campo CNPJ
        self.fields['cnpj'].widget.attrs['id'] = 'id_cnpj_mascara'