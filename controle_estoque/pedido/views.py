from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def listar_pedidos(request):
    """
    View para a página principal (lista) de pedidos.
    """
    context = {}
    
    # ATUALIZAÇÃO: O caminho do template foi alterado aqui
    # para corresponder à sua nova estrutura de pastas.
    return render(request, 'pedido/cliente/lista.html', context)