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

# ... (imports e outros forms) ...

# ... (imports e outros forms) ...

# ... (imports e outros forms) ...

# ... (imports e outros forms) ...

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'empresa', 'cnpj', 'sistema', 'tecnico', 'validade', 
            'descricao', 'pdf_anexo', 'tipo_cobranca', 'valor_mensal',
            'meses_contrato', 'valor_anual', 'bloqueado'
        ]
        widgets = {
            # FORMATO DA DATA CORRIGIDO AQUI
            'validade': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'tipo_cobranca': forms.RadioSelect(),
            'bloqueado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['validade', 'pdf_anexo', 'tipo_cobranca', 'bloqueado']:
                field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['tecnico'].empty_label = "Nenhum técnico selecionado"
        self.fields['cnpj'].widget.attrs['id'] = 'id_cnpj_mascara'
        self.fields['valor_mensal'].widget.attrs.update({'id': 'id_valor_mensal', 'placeholder': 'R$ 0,00', 'class': 'form-control form-control-sm'})
        self.fields['meses_contrato'].widget.attrs.update({'id': 'id_meses_contrato', 'class': 'form-control form-control-sm'})
        self.fields['valor_anual'].widget.attrs.update({'id': 'id_valor_anual', 'placeholder': 'R$ 0,00', 'class': 'form-control form-control-sm'})

    def clean(self):
        cleaned_data = super().clean()
        tipo_cobranca = cleaned_data.get("tipo_cobranca")
        valor_mensal = cleaned_data.get("valor_mensal")
        valor_anual = cleaned_data.get("valor_anual")

        if tipo_cobranca == 'M' and not valor_mensal:
            self.add_error('valor_mensal', 'Este campo é obrigatório para cobrança mensal.')
        
        if tipo_cobranca == 'A' and not valor_anual:
            self.add_error('valor_anual', 'Este campo é obrigatório para cobrança anual.')
            
        return cleaned_data