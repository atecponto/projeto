from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CategoriaPedido, ClientePedido
from .forms import CategoriaPedidoForm, ClientePedidoForm, ClientePedidoFilterForm
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.db.models import ProtectedError, Q
from datetime import datetime, time

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
            messages.success(request, 'Categoria atualizada com sucesso!')
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
    # Query base (sem alterações)
    clientes_list = ClientePedido.objects.select_related('categoria', 'usuario_criador').all()
    
    # Lógica de permissão (sem alterações)
    if not request.user.is_superuser:
        clientes_list = clientes_list.filter(usuario_criador=request.user)
    
    # --- LÓGICA DE FILTRO ATUALIZADA ---
    # Instancia o formulário de filtro com os dados do GET
    filter_form = ClientePedidoFilterForm(request.GET or None)

    # Aplica os filtros se o formulário for válido (e tiver dados)
    if filter_form.is_valid():
        categoria = filter_form.cleaned_data.get('categoria')
        if categoria:
            clientes_list = clientes_list.filter(categoria=categoria)
        
        # Filtro de Data (novo)
        if filter_form.cleaned_data.get('filtrar_por_data'):
            data_inicio = filter_form.cleaned_data.get('data_inicio')
            data_fim = filter_form.cleaned_data.get('data_fim')
            
            if data_inicio and data_fim:
                # Converte a data final para o fim do dia (23:59:59)
                data_fim_com_hora = datetime.combine(data_fim, time.max)
                # Filtra pelo campo 'data_criacao' no range
                clientes_list = clientes_list.filter(data_criacao__range=[data_inicio, data_fim_com_hora])
    # ------------------------------------
        
    # Paginação (sem alterações)
    paginator = Paginator(clientes_list, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'request': request, 
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