from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CategoriaPedido, ClientePedido
from .forms import CategoriaPedidoForm, ClientePedidoForm, ClientePedidoFilterForm
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Count, Sum
from datetime import datetime, time
from django.http import HttpResponse
from django.utils import timezone
from inventario.utils import render_to_pdf

@login_required
def listar_pedidos(request):
    """
    View para a página principal (lista) de pedidos.
    """
    context = {}
    return render(request, 'pedido/cliente/lista.html', context)

@login_required
def listar_categorias_pedido(request):
    """
    Lista e busca todas as categorias de pedido.
    """

    categorias_list = CategoriaPedido.objects.all()

    busca = request.GET.get('busca')
    if busca:
        categorias_list = categorias_list.filter(nome__icontains=busca)

    paginator = Paginator(categorias_list, 10) # 10 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'request': request # Para manter o termo de busca na paginação
    }
    return render(request, 'pedido/categoria/lista.html', context)

@login_required
def criar_categoria_pedido(request):
    """
    Cria uma nova categoria de pedido.
    """
    if request.method == 'POST':
        form = CategoriaPedidoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('pedido:listar_categorias_pedido')
    else:
        form = CategoriaPedidoForm()

    context = {
        'form': form,
        'titulo': 'Nova Categoria'
    }
    return render(request, 'pedido/categoria/form.html', context)

@login_required
def editar_categoria_pedido(request, pk):
    """
    Edita uma categoria de pedido existente.
    """
    categoria = get_object_or_404(CategoriaPedido, pk=pk)
    if request.method == 'POST':
        form = CategoriaPedidoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('pedido:listar_categorias_pedido')
    else:
        form = CategoriaPedidoForm(instance=categoria)

    context = {
        'form': form,
        'titulo': f'Editando Categoria: {categoria.nome}'
    }
    return render(request, 'pedido/categoria/form.html', context)

@login_required
def excluir_categoria_pedido(request, pk):
    """
    Exclui uma categoria de pedido.
    """
    categoria = get_object_or_404(CategoriaPedido, pk=pk)
    
    # Esta contagem não vai funcionar ainda, pois o modelo 'Pedido' não existe,
    pedidos_vinculados = getattr(categoria, 'pedidos', None)
    contagem_pedidos = pedidos_vinculados.count() if pedidos_vinculados else 0

    if request.method == 'POST':
        # Proteção para não excluir categoria em uso
        if contagem_pedidos > 0:
            messages.error(request, 'Não é possível excluir esta categoria, pois ela está vinculada a pedidos existentes.')
            return redirect('pedido:listar_categorias_pedido')
        
        try:
            nome_categoria = categoria.nome
            categoria.delete()
            messages.success(request, f'Categoria "{nome_categoria}" excluída com sucesso!')
        except ProtectedError:
            # Segurança extra caso o DB trave a exclusão
            messages.error(request, f'Não é possível excluir "{categoria.nome}", pois ela está em uso.')

        return redirect('pedido:listar_categorias_pedido')

    context = {
        'categoria': categoria,
        'contagem_pedidos': contagem_pedidos
    }
    return render(request, 'pedido/categoria/confirmar_exclusao.html', context)

@login_required
def listar_clientes_pedido(request):
    """
    Lista, busca (JS) e filtra os Clientes (do app Pedido).
    """
    clientes_list = ClientePedido.objects.select_related('categoria', 'usuario_criador', 'tecnico').all()
    
    if not request.user.is_superuser:
        clientes_list = clientes_list.filter(usuario_criador=request.user)
    
    filter_form = ClientePedidoFilterForm(request.GET or None)
    if not request.user.is_superuser:
        if 'tecnico' in filter_form.fields:
            del filter_form.fields['tecnico']

    # Aplica os filtros ANTES de calcular o sumário
    if filter_form.is_valid():
        categoria = filter_form.cleaned_data.get('categoria')
        if categoria:
            clientes_list = clientes_list.filter(categoria=categoria)
        
        if request.user.is_superuser:
            tecnico = filter_form.cleaned_data.get('tecnico')
            if tecnico:
                clientes_list = clientes_list.filter(tecnico=tecnico)
        
        if filter_form.cleaned_data.get('filtrar_por_data'):
            data_inicio = filter_form.cleaned_data.get('data_inicio')
            data_fim = filter_form.cleaned_data.get('data_fim')
            if data_inicio and data_fim:
                data_fim_com_hora = datetime.combine(data_fim, time.max)
                clientes_list = clientes_list.filter(data_criacao__range=[data_inicio, data_fim_com_hora])
    
    # --- NOVO SUMÁRIO FINANCEIRO (PÓS-FILTRO) ---
    # Calcula a soma de 'valor_pedido' para cada categoria,
    # baseado na lista já filtrada.
    financial_summary = clientes_list.filter(categoria__nome__isnull=False) \
                                  .values('categoria__nome') \
                                  .annotate(total_valor=Sum('valor_pedido')) \
                                  .order_by('categoria__nome')
    # ---------------------------------------------
        
    # Paginação (agora usa a lista 100% filtrada)
    paginator = Paginator(clientes_list, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form, 
        'request': request, 
        'financial_summary': financial_summary, # <-- Passa o novo sumário
        'total_clientes_encontrados': paginator.count # <-- Passa o total de clientes
    }
    return render(request, 'pedido/cliente/lista.html', context)

@login_required
def criar_cliente_pedido(request):
    """
    Cria um novo Cliente (do app Pedido).
    """
    if request.method == 'POST':
        form = ClientePedidoForm(request.POST)
        if form.is_valid():

            novo_pedido = form.save(commit=False) 

            novo_pedido.usuario_criador = request.user 

            novo_pedido.save() 

            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('pedido:listar_clientes_pedido')
    else:
        form = ClientePedidoForm()

    context = {
        'form': form,
        'titulo': 'Novo Cliente'
    }
    return render(request, 'pedido/cliente/form.html', context) 

@login_required
def editar_cliente_pedido(request, pk):
    """
    Edita um Cliente (do app Pedido) existente.
    """
    cliente = get_object_or_404(ClientePedido, pk=pk)


    if not request.user.is_superuser and cliente.usuario_criador != request.user:
        messages.error(request, 'Você não tem permissão para editar este registro.')
        return redirect('pedido:listar_clientes_pedido')

    if request.method == 'POST':
        form = ClientePedidoForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('pedido:listar_clientes_pedido')
    else:
        form = ClientePedidoForm(instance=cliente)

    context = {
        'form': form,
        'titulo': f'Editando Cliente: {cliente.nome}'
    }
    return render(request, 'pedido/cliente/form.html', context) 

@login_required
def excluir_cliente_pedido(request, pk):
    """
    Exclui um Cliente (do app Pedido).
    """
    cliente = get_object_or_404(ClientePedido, pk=pk)
    
    if not request.user.is_superuser and cliente.usuario_criador != request.user:
        messages.error(request, 'Você não tem permissão para excluir este registro.')
        return redirect('pedido:listar_clientes_pedido')

    if request.method == 'POST':
        try:
            nome_cliente = cliente.nome
            cliente.delete()
            messages.success(request, f'Cliente "{nome_cliente}" excluído com sucesso!')
        except ProtectedError:
            messages.error(request, f'Não é possível excluir "{cliente.nome}", pois ele está em uso.')
        return redirect('pedido:listar_clientes_pedido')

    context = {
        'cliente': cliente,
    }
    return render(request, 'pedido/cliente/excluir.html', context)

@login_required
def gerar_pdf_pedidos(request):
    """
    Gera um PDF da lista de pedidos filtrada.
    """
    # 1. Lógica de filtro (idêntica à sua view 'listar_clientes_pedido')
    clientes_list = ClientePedido.objects.select_related('categoria', 'usuario_criador', 'tecnico').all()
    
    if not request.user.is_superuser:
        clientes_list = clientes_list.filter(usuario_criador=request.user)
    
    filter_form = ClientePedidoFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        categoria = filter_form.cleaned_data.get('categoria')
        if categoria:
            clientes_list = clientes_list.filter(categoria=categoria)
        
        if request.user.is_superuser:
            tecnico = filter_form.cleaned_data.get('tecnico')
            if tecnico:
                clientes_list = clientes_list.filter(tecnico=tecnico)
        
        if filter_form.cleaned_data.get('filtrar_por_data'):
            data_inicio = filter_form.cleaned_data.get('data_inicio')
            data_fim = filter_form.cleaned_data.get('data_fim')
            if data_inicio and data_fim:
                data_fim_com_hora = datetime.combine(data_fim, time.max)
                clientes_list = clientes_list.filter(data_criacao__range=[data_inicio, data_fim_com_hora])
    
    # 2. Sumário Financeiro (Existente)
    financial_summary = clientes_list.filter(categoria__nome__isnull=False) \
                                  .values('categoria__nome') \
                                  .annotate(total_valor=Sum('valor_pedido')) \
                                  .order_by('categoria__nome')
                                  
    # --- 3. NOVO SUMÁRIO DE TÉCNICOS (como em image_d7d97a.png) ---
    # Calcula a contagem por técnico (apenas se for superuser)
    tecnico_summary = None
    if request.user.is_superuser:
        tecnico_summary = clientes_list.filter(tecnico__nome__isnull=False) \
                                    .values('tecnico__nome') \
                                    .annotate(total=Count('id')) \
                                    .order_by('tecnico__nome')
    # -----------------------------------------------------------
    
    # 4. Prepara o contexto para o PDF
    context = {
        'clientes': clientes_list,
        'filter_form': filter_form, 
        'financial_summary': financial_summary,
        'tecnico_summary': tecnico_summary, # <-- Passa o novo sumário
        'total_clientes_encontrados': clientes_list.count(),
        'data_geracao': timezone.now(),
        'user': request.user
    }
    
    # 5. Renderiza o PDF (Existente)
    pdf = render_to_pdf('pedido/pdf_pedido.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"relatorio_pedidos_{timezone.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    
    messages.error(request, "Ocorreu um erro ao gerar o PDF.")
    return redirect('pedido:listar_clientes_pedido')