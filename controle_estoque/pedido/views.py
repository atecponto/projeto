# No topo do arquivo, adicione estes imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CategoriaPedido, ClientePedido
from .forms import CategoriaPedidoForm, ClientePedidoForm
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.db.models import ProtectedError, Q

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
            # Redireciona para a lista usando o namespace 'pedido:listar_categorias_pedido'
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
    clientes_list = ClientePedido.objects.select_related('categoria').all()
    
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        clientes_list = clientes_list.filter(categoria_id=categoria_id)
        
    paginator = Paginator(clientes_list, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categorias': CategoriaPedido.objects.all(), 
        'request': request, 
    }
    # ATUALIZADO: Aponta para 'lista.html'
    return render(request, 'pedido/cliente/lista.html', context) 

@login_required
def criar_cliente_pedido(request):
    """
    Cria um novo Cliente (do app Pedido).
    """
    if request.method == 'POST':
        form = ClientePedidoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('pedido:listar_clientes_pedido')
    else:
        form = ClientePedidoForm()

    context = {
        'form': form,
        'titulo': 'Novo Cliente'
    }
    # ATUALIZADO: Aponta para 'form.html'
    return render(request, 'pedido/cliente/form.html', context) 

@login_required
def editar_cliente_pedido(request, pk):
    """
    Edita um Cliente (do app Pedido) existente.
    """
    cliente = get_object_or_404(ClientePedido, pk=pk)
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
    # ATUALIZADO: Aponta para 'form.html'
    return render(request, 'pedido/cliente/form.html', context) 

@login_required
def excluir_cliente_pedido(request, pk):
    """
    Exclui um Cliente (do app Pedido).
    """
    cliente = get_object_or_404(ClientePedido, pk=pk)
    
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
    # ATUALIZADO: Aponta para 'excluir.html'
    return render(request, 'pedido/cliente/excluir.html', context)