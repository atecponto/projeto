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
        label='Data de Início',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    data_fim = forms.DateField(
        label='Data de Fim',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    sistema = forms.ModelChoiceField(
        queryset=Sistema.objects.all(),
        required=False,
        label='Filtrar por Sistema',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # --- INÍCIO DA NOVA SEÇÃO ---
    STATUS_CHOICES = [
        ('', 'Todos os Status'),
        ('ativos', 'Apenas Ativos'),
        ('inativos', 'Apenas Inativos'),
        ('bloqueados', 'Apenas Bloqueados'),
        ('vencidos', 'Apenas Vencidos'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label='Filtrar por Status',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # --- FIM DA NOVA SEÇÃO ---
    tecnico = forms.ModelChoiceField(
        queryset=Tecnico.objects.all(),
        required=False,
        label='Filtrar por Técnico',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class RenovacaoForm(forms.Form):
    porcentagem_reajuste = forms.DecimalField(
        label='Porcentagem de Reajuste (%)',
        required=True,
        # --- INÍCIO DAS LINHAS ADICIONADAS/MODIFICADAS ---
        max_digits=5,      # Define o total de dígitos permitidos (ex: 999.99)
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2.50'}),
        error_messages={   # Define a mensagem de erro personalizada
            'max_digits': 'Certifique-se de que não tenha mais de 5 dígitos no total.'
        }
        # --- FIM DAS LINHAS ADICIONADAS/MODIFICADAS ---
    )
    meses_a_adicionar = forms.IntegerField(
        label='Adicionar Meses ao Contrato',
        required=True,
        min_value=1,
        initial=12, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    cliente_ids = forms.CharField(widget=forms.HiddenInput())

class RenovacaoListFilterForm(forms.Form):
    # Campos de filtro existentes que já estão no seu HTML
    cnpj = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite para buscar...'}))
    sistema = forms.ModelChoiceField(queryset=Sistema.objects.all(), required=False, empty_label="Todos os Sistemas", widget=forms.Select(attrs={'class': 'form-select'}))
    tecnico = forms.ModelChoiceField(queryset=Tecnico.objects.all(), required=False, empty_label="Todos os Técnicos", widget=forms.Select(attrs={'class': 'form-select'}))
    mostrar_vencidos = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    mostrar_inativos = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    mostrar_bloqueados = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # Novos campos para o filtro de período
    filtrar_por_data = forms.BooleanField(required=False, label="Período", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    data_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    data_fim = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        filtrar = cleaned_data.get('filtrar_por_data')
        inicio = cleaned_data.get('data_inicio')
        fim = cleaned_data.get('data_fim')

        if filtrar:
            if not inicio or not fim:
                raise forms.ValidationError("Se a opção 'Período' estiver marcada, as datas de início e fim são obrigatórias.")
            if inicio > fim:
                raise forms.ValidationError("A data de início não pode ser maior que a data de fim.")
            # Validação de 2 anos (731 dias para incluir anos bissextos)
            if (fim - inicio).days > 731:
                raise forms.ValidationError("O período máximo de seleção de data é de 2 anos.")
        
        return cleaned_data