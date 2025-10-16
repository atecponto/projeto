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
        fields = [
            'empresa', 'cnpj', 'sistema', 'tecnico', 'validade', 
            'descricao', 'pdf_anexo', 'tipo_cobranca', 'valor_mensal',
            'meses_contrato', 'valor_anual', 'bloqueado'
        ]
        widgets = {
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

# --- NOVO FORMULÁRIO DE RELATÓRIO ADICIONADO AQUI ---
class RelatorioContratosForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data de Início",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_fim = forms.DateField(
        label="Data de Fim",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    sistema = forms.ModelChoiceField(
        queryset=Sistema.objects.all(),
        required=False,
        label="Filtrar por Sistema",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tecnico = forms.ModelChoiceField(
        queryset=Tecnico.objects.all(),
        required=False,
        label="Filtrar por Técnico",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class RenovacaoForm(forms.Form):
    porcentagem_reajuste = forms.DecimalField(
        label='Porcentagem de Reajuste (%)',
        required=True,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2.50'})
    )
    nova_validade = forms.DateField(
        label='Nova Validade do Contrato',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    # Este campo guardará os IDs dos clientes selecionados, mas ficará oculto para o usuário.
    cliente_ids = forms.CharField(widget=forms.HiddenInput())