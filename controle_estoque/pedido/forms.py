from django import forms
from .models import CategoriaPedido, ClientePedido
from contratos.models import Tecnico

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
        fields = ['nome', 'cnpj', 'email', 'telefone', 'contato', 'categoria', 
                  'endereco', 'cep', 'cidade', 'estado', 'valor_pedido', 'tecnico', 'descricao_pedido'] 
        widgets = {
            'descricao_pedido': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica classes Bootstrap e IDs
        for field_name, field in self.fields.items():
            if field_name == 'categoria':
                 field.label_attrs = {'style': 'font-weight: bold;'}
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, (forms.NumberInput, forms.Textarea)): 
                 field.widget.attrs.update({'class': 'form-control'})
                 if isinstance(field.widget, forms.NumberInput):
                      field.widget.attrs.update({'step': '0.01'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Adiciona IDs e Placeholders
        self.fields['cnpj'].widget.attrs.update({
            'id': 'id_cnpj_mascara_pedido', 
            'placeholder': '00.000.000/0000-00 ou 000.000.000-00' 
        })
        self.fields['telefone'].widget.attrs.update({
            'id': 'id_telefone_mascara_pedido', 
            'placeholder': '(00) 00000-0000'
        })
        self.fields['cep'].widget.attrs.update({
            'id': 'id_cep_mascara_pedido', 
            'placeholder': '00000-000'
        })
        self.fields['estado'].widget.attrs.update({
            'placeholder': 'UF'
        })
        self.fields['valor_pedido'].widget.attrs.update({
             'placeholder': 'R$ 0,00'
        })
        if self.fields['tecnico'].required == False: 
            self.fields['tecnico'].empty_label = "Nenhum técnico"

class ClientePedidoFilterForm(forms.Form):
    categoria = forms.ModelChoiceField(
        queryset=CategoriaPedido.objects.all(),
        required=False,
        label='Filtrar por Categoria',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Filtro de Data 
    filtrar_por_data = forms.BooleanField(
        required=False, 
        label="Período", 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    data_inicio = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}) # Placeholder 'dd/mm/aaaa' é automático do 'date'
    )
    data_fim = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}) # Placeholder 'dd/mm/aaaa' é automático
    )

    # Validação (copiada do seu form de Renovação)
    def clean(self):
        cleaned_data = super().clean()
        filtrar = cleaned_data.get('filtrar_por_data')
        inicio = cleaned_data.get('data_inicio')
        fim = cleaned_data.get('data_fim')

        if filtrar:
            if not inicio or not fim:
                raise forms.ValidationError("Se 'Período' estiver marcado, as datas de início e fim são obrigatórias.")
            if inicio > fim:
                raise forms.ValidationError("A data de início não pode ser maior que a data de fim.")
        return cleaned_data
