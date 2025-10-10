from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Sistema, Tecnico
from .forms import SistemaForm, TecnicoForm
from django.core.paginator import Paginator

# --- Views de Sistema (Adaptadas para seus nomes de arquivo) ---
@login_required
def listar_sistemas(request):
    busca = request.GET.get('busca')
    sistemas_list = Sistema.objects.all().order_by('nome')
    if busca:
        sistemas_list = sistemas_list.filter(nome__icontains=busca)
    
    paginator = Paginator(sistemas_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Apontando para 'listar_sistemas.html'
    return render(request, 'contratos/sistema/listar_sistemas.html', {'page_obj': page_obj})

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
    # Apontando para 'form_sistema.html'
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
    # Apontando para 'form_sistema.html'
    return render(request, 'contratos/sistema/form_sistema.html', context)

@login_required
def excluir_sistema(request, pk):
    sistema = get_object_or_404(Sistema, pk=pk)
    if request.method == 'POST':
        nome_sistema = sistema.nome
        sistema.delete()
        messages.success(request, f'Sistema "{nome_sistema}" excluído com sucesso!')
        return redirect('listar_sistemas')
    
    # Apontando para 'confirmar_exclusao_sistema.html'
    return render(request, 'contratos/sistema/confirmar_exclusao_sistema.html', {'sistema': sistema})


# --- Views de Técnico (Adaptadas para seus nomes de arquivo) ---
@login_required
def listar_tecnicos(request):
    busca = request.GET.get('busca')
    tecnicos_list = Tecnico.objects.all().order_by('nome')
    if busca:
        tecnicos_list = tecnicos_list.filter(nome__icontains=busca)
    
    paginator = Paginator(tecnicos_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Apontando para 'lista.html'
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
    
    context = {
        'form': form,
        'titulo': 'Cadastrar Novo Técnico'
    }
    # Apontando para 'form.html'
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
    
    context = {
        'form': form,
        'titulo': f'Editando Técnico: {tecnico.nome}'
    }
    # Apontando para 'form.html'
    return render(request, 'contratos/tecnicos/form.html', context)

@login_required
def excluir_tecnico(request, pk):
    tecnico = get_object_or_404(Tecnico, pk=pk)
    if request.method == 'POST':
        nome_tecnico = tecnico.nome
        tecnico.delete()
        messages.success(request, f'Técnico "{nome_tecnico}" excluído com sucesso!')
        return redirect('listar_tecnicos')
    
    # Apontando para 'excluir.html'
    return render(request, 'contratos/tecnicos/excluir.html', {'tecnico': tecnico})