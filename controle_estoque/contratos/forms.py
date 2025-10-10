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

# ... (outros forms) ...

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # CAMPOS NOVOS ADICIONADOS À LISTA
        fields = ['empresa', 'cnpj', 'sistema', 'tecnico', 'validade', 'descricao', 'pdf_anexo']
        widgets = {
            'validade': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}), # Widget para campo de texto maior
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Não aplicar a classe em campos de data ou arquivo
            if field_name not in ['validade', 'pdf_anexo']:
                field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['tecnico'].empty_label = "Nenhum técnico selecionado"
        self.fields['cnpj'].widget.attrs['id'] = 'id_cnpj_mascara'