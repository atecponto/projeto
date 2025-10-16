from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Sistema, Tecnico, Cliente
from .forms import SistemaForm, TecnicoForm, ClienteForm, RenovacaoForm, RelatorioContratosForm
from django.core.paginator import Paginator
from datetime import date
from django.db.models import ProtectedError
from django.db.models import Count
from .forms import RelatorioContratosForm
from inventario.utils import render_to_pdf # Reutilizando a função de PDF do seu outro app
from django.utils import timezone
import calendar
from django.http import HttpResponse
from django.db.models import Sum
from datetime import date, datetime, time
from decimal import Decimal

# --- Views de Sistema (sem alterações) ---
@login_required
def listar_sistemas(request):
    # Adicionamos .annotate() para contar os clientes de cada sistema
    sistemas_list = Sistema.objects.annotate(
        num_clientes=Count('cliente')
    ).order_by('nome')

    busca = request.GET.get('busca')
    if busca:
        sistemas_list = sistemas_list.filter(nome__icontains=busca)
    
    paginator = Paginator(sistemas_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'contratos/sistema/lista.html', {'page_obj': page_obj})

@login_required
def criar_sistema(request):
    if request.method == 'POST':
        form = SistemaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sistema cadastrado com sucesso!')
            return redirect('listar_sistemas')
    else:
        form = SistemaForm()
    
    context = { 'form': form, 'titulo': 'Cadastrar Novo Sistema' }
    # Caminho atualizado para 'form.html'
    return render(request, 'contratos/sistema/form.html', context)

@login_required
def editar_sistema(request, pk):
    sistema = get_object_or_404(Sistema, pk=pk)
    if request.method == 'POST':
        form = SistemaForm(request.POST, instance=sistema)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sistema atualizado com sucesso!')
            return redirect('listar_sistemas')
    else:
        form = SistemaForm(instance=sistema)
    
    context = { 'form': form, 'titulo': f'Editando Sistema: {sistema.nome}' }
    # Caminho atualizado para 'form.html'
    return render(request, 'contratos/sistema/form.html', context)

@login_required
def excluir_sistema(request, pk):
    sistema = get_object_or_404(Sistema, pk=pk)
    
    # Agora apenas verificamos se existe algum cliente vinculado (True ou False)
    em_uso = sistema.cliente_set.exists()
    
    if request.method == 'POST':
        if em_uso:
            messages.error(request, 'Este sistema não pode ser excluído pois está em uso.')
            return redirect('listar_sistemas')
        try:
            nome_sistema = sistema.nome
            sistema.delete()
            messages.success(request, f'Sistema "{nome_sistema}" excluído com sucesso!')
            return redirect('listar_sistemas')
        except ProtectedError: # Apenas como uma segurança extra
            messages.error(request, f'Não foi possível excluir o sistema "{sistema.nome}" pois ele está vinculado a um ou mais clientes.')
            return redirect('listar_sistemas')

    context = {
        'sistema': sistema,
        'em_uso': em_uso, # Enviamos a variável booleana para o template
    }
    return render(request, 'contratos/sistema/excluir.html', context)


# --- Views de Técnico (sem alterações) ---
@login_required
def listar_tecnicos(request):
    # CÁLCULO CORRIGIDO: Agora conta os 'clientes' vinculados
    tecnicos_list = Tecnico.objects.annotate(
        num_clientes=Count('cliente')
    ).order_by('nome')

    busca = request.GET.get('busca')
    if busca:
        tecnicos_list = tecnicos_list.filter(nome__icontains=busca)
    
    paginator = Paginator(tecnicos_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'contratos/tecnicos/lista.html', {'page_obj': page_obj})

@login_required
def criar_tecnico(request):
    if request.method == 'POST':
        form = TecnicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Técnico cadastrado com sucesso!')
            return redirect('listar_tecnicos')
    else:
        form = TecnicoForm()
    context = { 'form': form, 'titulo': 'Cadastrar Novo Técnico' }
    return render(request, 'contratos/tecnicos/form.html', context)

@login_required
def editar_tecnico(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    if request.method == 'POST':
        form = TecnicoForm(request.POST, instance=tecnico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Técnico atualizado com sucesso!')
            return redirect('listar_tecnicos')
    else:
        form = TecnicoForm(instance=tecnico)
    context = { 'form': form, 'titulo': f'Editando Técnico: {tecnico.nome}' }
    return render(request, 'contratos/tecnicos/form.html', context)

@login_required
def excluir_tecnico(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    em_uso = tecnico.cliente_set.exists()
    
    if request.method == 'POST':
        # Adicionamos o bloco try...except para capturar o ProtectedError
        try:
            nome_tecnico = tecnico.nome
            tecnico.delete()
            messages.success(request, f'Técnico "{nome_tecnico}" excluído com sucesso!')
            return redirect('listar_tecnicos')
        except ProtectedError:
            messages.error(request, f'Não foi possível excluir o técnico "{tecnico.nome}" pois ele está vinculado a um ou mais clientes.')
            return redirect('listar_tecnicos')

    context = {
        'tecnico': tecnico,
        'em_uso': em_uso,
    }
    return render(request, 'contratos/tecnicos/excluir.html', context)


# --- Views de Cliente ---
@login_required
def listar_clientes(request):
    clientes_list = Cliente.objects.select_related('sistema', 'tecnico').all()

    filtro_cnpj = request.GET.get('cnpj')
    filtro_sistema = request.GET.get('sistema')
    filtro_tecnico = request.GET.get('tecnico')
    mostrar_bloqueados = request.GET.get('mostrar_bloqueados')
    mostrar_inativos = request.GET.get('mostrar_inativos')
    mostrar_vencidos = request.GET.get('mostrar_vencidos')

    if mostrar_inativos == 'on':
        clientes_list = clientes_list.filter(ativo=False)
    else:
        clientes_list = clientes_list.filter(ativo=True)
    
    if filtro_cnpj:
        clientes_list = clientes_list.filter(cnpj__icontains=filtro_cnpj)
    if filtro_sistema:
        clientes_list = clientes_list.filter(sistema__id=filtro_sistema)
    if filtro_tecnico:
        clientes_list = clientes_list.filter(tecnico__id=filtro_tecnico)
    if mostrar_bloqueados == 'on':
        clientes_list = clientes_list.filter(bloqueado=True)
    if mostrar_vencidos == 'on':
        clientes_list = clientes_list.filter(validade__lt=date.today())
        
    paginator = Paginator(clientes_list.order_by('empresa'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- CÁLCULO DAS ESTATÍSTICAS ADICIONADO AQUI ---
    total_ativos = Cliente.objects.filter(ativo=True).count()
    total_inativos = Cliente.objects.filter(ativo=False).count()
    # Contamos apenas clientes ativos que também estão bloqueados/vencidos
    total_bloqueados = Cliente.objects.filter(ativo=True, bloqueado=True).count()
    total_vencidos = Cliente.objects.filter(ativo=True, validade__lt=date.today()).count()

    context = {
        'page_obj': page_obj,
        'sistemas': Sistema.objects.all(),
        'tecnicos': Tecnico.objects.all(),
        'today': date.today(),
        # NOVAS VARIÁVEIS ENVIADAS PARA O TEMPLATE
        'total_ativos': total_ativos,
        'total_inativos': total_inativos,
        'total_bloqueados': total_bloqueados,
        'total_vencidos': total_vencidos,
    }
    return render(request, 'contratos/cliente/lista.html', context)

@login_required
def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    context = {'form': form, 'titulo': 'Cadastrar Novo Cliente'}
    return render(request, 'contratos/cliente/form.html', context)

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm(instance=cliente)
    context = {'form': form, 'titulo': f'Editando Cliente: {cliente.empresa}'}
    return render(request, 'contratos/cliente/form.html', context)

@login_required
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        if cliente.pdf_anexo:
            cliente.pdf_anexo.delete()
        cliente.delete()
        messages.success(request, f'Cliente "{cliente.empresa}" excluído com sucesso!')
        return redirect('listar_clientes')
    return render(request, 'contratos/cliente/excluir.html', {'cliente': cliente})


@require_POST
@login_required
def toggle_bloqueado_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.bloqueado = not cliente.bloqueado
    cliente.save()
    status = "bloqueado" if cliente.bloqueado else "desbloqueado"
    messages.success(request, f'Cliente "{cliente.empresa}" foi {status} com sucesso.')
    return redirect('listar_clientes')

# --- ESTA É A FUNÇÃO RESPONSÁVEL PELA AÇÃO DE INATIVAR ---
@require_POST
@login_required
def toggle_ativo_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.ativo = not cliente.ativo # Inverte o status
    cliente.save()
    status = "ativado" if cliente.ativo else "inativado"
    messages.success(request, f'Cliente "{cliente.empresa}" foi {status} com sucesso.')
    
    # Redireciona para a lista, onde o cliente inativo ficará oculto
    return redirect('listar_clientes')

@login_required
def relatorio_contratos(request):
    if request.method == 'POST':
        form = RelatorioContratosForm(request.POST)
        if form.is_valid():
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']
            sistema = form.cleaned_data['sistema']
            tecnico = form.cleaned_data['tecnico']

            start_datetime = timezone.make_aware(datetime.combine(data_inicio, time.min))
            end_datetime = timezone.make_aware(datetime.combine(data_fim, time.max))
            
            clientes = Cliente.objects.filter(
                data_criacao__range=[start_datetime, end_datetime]
            )

            if sistema:
                clientes = clientes.filter(sistema=sistema)
            if tecnico:
                clientes = clientes.filter(tecnico=tecnico)
            
            resumo_por_sistema = clientes.values('sistema__nome').annotate(
                quantidade=Count('id')
            ).order_by('sistema__nome')

            context = {
                'clientes': clientes.order_by('data_criacao'),
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'sistema_filtrado': sistema,
                'tecnico_filtrado': tecnico,
                'data_geracao': timezone.now(),
                'resumo_por_sistema': resumo_por_sistema,
            }
            
            pdf = render_to_pdf('contratos/relatorio/pdf_template.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = f"relatorio_clientes_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            return HttpResponse("Erro ao gerar o PDF.", status=500)
    else:
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        _, last_day_of_month = calendar.monthrange(today.year, today.month)
        end_of_month = today.replace(day=last_day_of_month)
        
        form = RelatorioContratosForm(initial={
            'data_inicio': start_of_month,
            'data_fim': end_of_month
        })

    # A CORREÇÃO FOI FEITA NA LINHA ABAIXO
    return render(request, 'contratos/relatorio/form.html', {'form': form})

@login_required
def renovacao_list(request):
    # Obtém os parâmetros de filtro da URL
    cnpj = request.GET.get('cnpj')
    sistema_id = request.GET.get('sistema')
    tecnico_id = request.GET.get('tecnico')
    mostrar_vencidos = request.GET.get('mostrar_vencidos')
    mostrar_inativos = request.GET.get('mostrar_inativos')
    mostrar_bloqueados = request.GET.get('mostrar_bloqueados')

    # ---- LÓGICA DE FILTRO CORRIGIDA ----
    # Começa com todos os clientes. A filtragem de ativos/inativos é tratada abaixo.
    clientes = Cliente.objects.all()

    # Filtra por inativos: se a caixa estiver marcada, mostra SÓ os inativos.
    # Senão, mostra SÓ os ativos (comportamento padrão).
    if mostrar_inativos:
        clientes = clientes.filter(ativo=False)
    else:
        clientes = clientes.filter(ativo=True)

    # Aplica os outros filtros sobre o resultado anterior
    if cnpj:
        clientes = clientes.filter(cnpj__icontains=cnpj)
    if sistema_id:
        clientes = clientes.filter(sistema_id=sistema_id)
    if tecnico_id:
        clientes = clientes.filter(tecnico_id=tecnico_id)
    if mostrar_vencidos:
        clientes = clientes.filter(validade__lt=date.today())
    if mostrar_bloqueados:
        clientes = clientes.filter(bloqueado=True)
    
    # Ordena o resultado final
    clientes = clientes.order_by('empresa')
    
    # Prepara a lista de IDs para a funcionalidade "Marcar Todos"
    all_client_ids = list(clientes.values_list('pk', flat=True))
    all_client_ids_str = ','.join(map(str, all_client_ids))
    
    context = {
        'clientes': clientes, 
        'sistemas': Sistema.objects.all(),
        'tecnicos': Tecnico.objects.all(),
        'today': date.today(),
        'total_clientes_filtrados': clientes.count(),
        'all_client_ids_str': all_client_ids_str,
    }
    return render(request, 'contratos/renovacao/lista.html', context)

@login_required
def renovar_contratos(request):
    # Este 'if' trata o envio do formulário final com a porcentagem e a nova data.
    if request.method == 'POST' and 'porcentagem_reajuste' in request.POST:
        form = RenovacaoForm(request.POST)
        if form.is_valid():
            cliente_ids_str = form.cleaned_data['cliente_ids']
            cliente_ids = cliente_ids_str.split(',')
            nova_validade = form.cleaned_data['nova_validade']
            porcentagem_reajuste = form.cleaned_data['porcentagem_reajuste']

            clientes_atualizados = []
            clientes_com_erro = []

            for cliente_id in cliente_ids:
                try:
                    cliente = Cliente.objects.get(pk=int(cliente_id))
                    
                    fator_reajuste = Decimal(1) + (Decimal(porcentagem_reajuste) / Decimal(100))
                    
                    if cliente.valor_mensal:
                        cliente.valor_mensal *= fator_reajuste
                    
                    if cliente.valor_anual:
                        cliente.valor_anual *= fator_reajuste

                    cliente.validade = nova_validade
                    cliente.save()
                    clientes_atualizados.append(cliente.empresa)
                except Cliente.DoesNotExist:
                    clientes_com_erro.append(cliente_id)

            if clientes_atualizados:
                messages.success(request, f"Contratos renovados com sucesso para: {', '.join(clientes_atualizados)}.")
            if clientes_com_erro:
                messages.error(request, f"Não foi possível encontrar os clientes com os seguintes IDs: {', '.join(clientes_com_erro)}.")
            
            return redirect('renovacao_list')
        
        else:
            cliente_ids_str = request.POST.get('cliente_ids', '')
            cliente_ids = cliente_ids_str.split(',') if cliente_ids_str else []
            clientes_selecionados = Cliente.objects.filter(pk__in=cliente_ids)
            context = {
                'form': form,
                'clientes_selecionados': clientes_selecionados,
                'titulo': 'Renovar Contratos Selecionados'
            }
            # ALTERAÇÃO AQUI
            return render(request, 'contratos/renovacao_form.html', context)

    # Este 'if' trata o envio da lista de clientes selecionados.
    elif request.method == 'POST':
        cliente_ids = request.POST.getlist('cliente_ids')
        if not cliente_ids:
            messages.error(request, "Nenhum cliente foi selecionado.")
            return redirect('renovacao_list')

        form = RenovacaoForm(initial={'cliente_ids': ','.join(cliente_ids)})
        clientes_selecionados = Cliente.objects.filter(pk__in=cliente_ids)
        
        context = {
            'form': form,
            'clientes_selecionados': clientes_selecionados,
            'titulo': 'Renovar Contratos Selecionados'
        }
        # E ALTERAÇÃO AQUI TAMBÉM
        return render(request, 'contratos/renovacao_form.html', context)

    return redirect('renovacao_list')