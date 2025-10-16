from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Sistema, Tecnico, Cliente, HistoricoRenovacao
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
from dateutil.relativedelta import relativedelta
from django.views.decorators.http import require_POST


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
            sistema_id = form.cleaned_data['sistema']
            tecnico_id = form.cleaned_data['tecnico']

            start_date = timezone.make_aware(datetime.combine(data_inicio, time.min))
            end_date = timezone.make_aware(datetime.combine(data_fim, time.max))
            
            clientes = Cliente.objects.filter(
                data_criacao__gte=start_date,
                data_criacao__lte=end_date
            )

            if sistema_id:
                clientes = clientes.filter(sistema=sistema_id)
            if tecnico_id:
                clientes = clientes.filter(tecnico=tecnico_id)
            
            # Usa os nomes de variáveis corretos que seu template espera
            resumo_por_sistema = clientes.values('sistema__nome').annotate(quantidade=Count('id')).order_by('-quantidade')
            
            # --- LÓGICA ADICIONADA ---
            resumo_por_tecnico = clientes.exclude(tecnico__isnull=True).values('tecnico__nome').annotate(quantidade=Count('id')).order_by('-quantidade')

            context = {
                'clientes': clientes.order_by('data_criacao'),
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                # Usa os nomes de variáveis corretos que seu template espera
                'sistema_filtrado': Sistema.objects.filter(pk=sistema_id).first() if sistema_id else None,
                'tecnico_filtrado': Tecnico.objects.filter(pk=tecnico_id).first() if tecnico_id else None,
                'data_geracao': timezone.now(),
                'resumo_por_sistema': resumo_por_sistema,
                'resumo_por_tecnico': resumo_por_tecnico, # Adiciona os novos dados ao contexto
            }
            
            pdf = render_to_pdf('contratos/relatorio/pdf_template.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = f"relatorio_clientes_{timezone.now().strftime('%Y%m%d')}.pdf"
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response
            
            messages.error(request, "Ocorreu um erro ao gerar o PDF.")
            return redirect('relatorio_contratos')
    else:
        form = RelatorioContratosForm()

    return render(request, 'contratos/relatorio/form.html', {'form': form})

@login_required
def renovacao_list(request):
    # Parâmetros de filtro
    cnpj = request.GET.get('cnpj')
    sistema_id = request.GET.get('sistema')
    tecnico_id = request.GET.get('tecnico')
    mostrar_vencidos = request.GET.get('mostrar_vencidos')
    mostrar_inativos = request.GET.get('mostrar_inativos')
    mostrar_bloqueados = request.GET.get('mostrar_bloqueados')

    # --- MUDANÇA AQUI: Adicionamos o prefetch_related para otimização ---
    clientes = Cliente.objects.all().prefetch_related('historico_renovacoes')

    # Lógica de filtro (permanece a mesma)
    if mostrar_inativos:
        clientes = clientes.filter(ativo=False)
    else:
        clientes = clientes.filter(ativo=True)

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
    
    clientes = clientes.order_by('empresa')
    
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
    if request.method == 'POST' and 'meses_a_adicionar' in request.POST:
        form = RenovacaoForm(request.POST)
        if form.is_valid():
            cliente_ids_str = form.cleaned_data['cliente_ids']
            cliente_ids = cliente_ids_str.split(',')
            meses_a_adicionar = form.cleaned_data['meses_a_adicionar']
            porcentagem_reajuste = form.cleaned_data['porcentagem_reajuste']

            clientes_atualizados = []
            clientes_com_erro = []

            for cliente_id in cliente_ids:
                try:
                    cliente = Cliente.objects.get(pk=int(cliente_id))
                    
                    # --- INÍCIO DO BLOCO DE CAPTURA DE DADOS ANTIGOS ---
                    validade_antiga = cliente.validade
                    valor_antigo = cliente.valor_mensal if cliente.tipo_cobranca == 'M' else cliente.valor_anual
                    # --- FIM DO BLOCO DE CAPTURA ---

                    fator_reajuste = Decimal(1) + (Decimal(porcentagem_reajuste) / Decimal(100))
                    
                    novo_valor_calculado = None
                    if cliente.valor_mensal:
                        cliente.valor_mensal *= fator_reajuste
                        novo_valor_calculado = cliente.valor_mensal
                    if cliente.valor_anual:
                        cliente.valor_anual *= fator_reajuste
                        novo_valor_calculado = cliente.valor_anual

                    nova_validade_calculada = cliente.validade + relativedelta(months=meses_a_adicionar)
                    cliente.validade = nova_validade_calculada
                    
                    cliente.save() # Salva as alterações no cliente

                    # --- INÍCIO DO BLOCO DE CRIAÇÃO DO HISTÓRICO ---
                    HistoricoRenovacao.objects.create(
                        cliente=cliente,
                        validade_anterior=validade_antiga,
                        nova_validade=nova_validade_calculada,
                        valor_anterior=valor_antigo,
                        porcentagem_reajuste=porcentagem_reajuste,
                        novo_valor=novo_valor_calculado,
                        usuario_responsavel=request.user
                    )
                    # --- FIM DO BLOCO DE CRIAÇÃO ---

                    clientes_atualizados.append(cliente.empresa)
                except Cliente.DoesNotExist:
                    clientes_com_erro.append(cliente_id)

            if clientes_atualizados:
                messages.success(request, f"Contratos renovados com sucesso para: {', '.join(clientes_atualizados)}.")
            if clientes_com_erro:
                messages.error(request, f"Não foi possível encontrar os clientes com IDs: {', '.join(clientes_com_erro)}.")
            
            return redirect('renovacao_list')
        
        else: # O resto da função continua igual...
            cliente_ids_str = request.POST.get('cliente_ids', '')
            cliente_ids = cliente_ids_str.split(',') if cliente_ids_str else []
            clientes_selecionados = Cliente.objects.filter(pk__in=cliente_ids)
            context = {
                'form': form,
                'clientes_selecionados': clientes_selecionados,
                'titulo': 'Aplicar Renovação de Contratos'
            }
            return render(request, 'contratos/renovacao_form.html', context)

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
            'titulo': 'Aplicar Renovação de Contratos'
        }
        return render(request, 'contratos/renovacao_form.html', context)

    return redirect('renovacao_list')

@login_required
@require_POST # Garante que esta view só pode ser chamada com um método POST, por segurança
def excluir_historico_renovacao(request, pk):
    # Encontra o registro de histórico específico ou retorna um erro 404 se não existir
    historico = get_object_or_404(HistoricoRenovacao, pk=pk)
    
    # Guarda o ID do cliente para saber para qual página voltar
    cliente_id = historico.cliente.id
    
    # Deleta o registro do banco de dados
    historico.delete()
    
    messages.success(request, "Registro de histórico excluído com sucesso.")
    
    # Redireciona de volta para a lista de clientes
    return redirect('listar_clientes')