from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Sistema
from .forms import SistemaForm

@login_required
def listar_sistemas(request):
    busca = request.GET.get('busca')
    if busca:
        sistemas = Sistema.objects.filter(nome__icontains=busca).order_by('nome')
    else:
        sistemas = Sistema.objects.all().order_by('nome')
    
    # Caminho do template corrigido para a nova subpasta 'sistema'
    return render(request, 'contratos/sistema/listar_sistemas.html', {'sistemas': sistemas})

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
    
    context = {
        'form': form,
        'titulo': 'Cadastrar Novo Sistema'
    }
    # Caminho do template corrigido para a nova subpasta 'sistema'
    return render(request, 'contratos/sistema/form_sistema.html', context)

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
    
    context = {
        'form': form,
        'titulo': f'Editando Sistema: {sistema.nome}'
    }
    # Caminho do template corrigido para a nova subpasta 'sistema'
    return render(request, 'contratos/sistema/form_sistema.html', context)

@login_required
def excluir_sistema(request, pk):
    sistema = get_object_or_404(Sistema, pk=pk)
    if request.method == 'POST':
        nome_sistema = sistema.nome
        sistema.delete()
        messages.success(request, f'Sistema "{nome_sistema}" excluído com sucesso!')
        return redirect('listar_sistemas')
    
    # Caminho do template corrigido para a nova subpasta 'sistema'
    return render(request, 'contratos/sistema/confirmar_exclusao_sistema.html', {'sistema': sistema})