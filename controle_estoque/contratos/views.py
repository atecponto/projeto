from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Sistema, Tecnico, Cliente
from .forms import SistemaForm, TecnicoForm, ClienteForm
from django.core.paginator import Paginator
from datetime import date # <--- ADICIONE ESTA LINHA DE IMPORTAÇÃO
from django.views.decorators.http import require_POST

# --- Views de Sistema ---
@login_required
def listar_sistemas(request):
    busca = request.GET.get('busca')
    sistemas_list = Sistema.objects.all().order_by('nome')
    if busca:
        sistemas_list = sistemas_list.filter(nome__icontains=busca)
    paginator = Paginator(sistemas_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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
    context = { 'form': form, 'titulo': 'Cadastrar Novo Sistema' }
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
    context = { 'form': form, 'titulo': f'Editando Sistema: {sistema.nome}' }
    return render(request, 'contratos/sistema/form_sistema.html', context)

@login_required
def excluir_sistema(request, pk):
    sistema = get_object_or_404(Sistema, pk=pk)
    if request.method == 'POST':
        sistema.delete()
        messages.success(request, f'Sistema "{sistema.nome}" excluído com sucesso!')
        return redirect('listar_sistemas')
    return render(request, 'contratos/sistema/confirmar_exclusao_sistema.html', {'sistema': sistema})

# --- Views de Técnico ---
@login_required
def listar_tecnicos(request):
    busca = request.GET.get('busca')
    tecnicos_list = Tecnico.objects.all().order_by('nome')
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
    if request.method == 'POST':
        tecnico.delete()
        messages.success(request, f'Técnico "{tecnico.nome}" excluído com sucesso!')
        return redirect('listar_tecnicos')
    return render(request, 'contratos/tecnicos/excluir.html', {'tecnico': tecnico})

# --- Views de Cliente ---
@login_required
def listar_clientes(request):
    clientes_list = Cliente.objects.select_related('sistema', 'tecnico').all()

    # Filtros existentes
    filtro_cnpj = request.GET.get('cnpj')
    filtro_sistema = request.GET.get('sistema')
    filtro_tecnico = request.GET.get('tecnico')
    # NOVO FILTRO
    mostrar_bloqueados = request.GET.get('mostrar_bloqueados')

    if filtro_cnpj:
        clientes_list = clientes_list.filter(cnpj__icontains=filtro_cnpj)
    if filtro_sistema:
        clientes_list = clientes_list.filter(sistema__id=filtro_sistema)
    if filtro_tecnico:
        clientes_list = clientes_list.filter(tecnico__id=filtro_tecnico)
    
    # LÓGICA DO NOVO FILTRO
    if mostrar_bloqueados == 'on':
        clientes_list = clientes_list.filter(bloqueado=True)
        
    paginator = Paginator(clientes_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'sistemas': Sistema.objects.all(),
        'tecnicos': Tecnico.objects.all(),
        'today': date.today(),
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

@require_POST # Garante que esta view só aceite requisições POST
@login_required
def toggle_bloqueado_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    # Inverte o status atual (se for True vira False, e vice-versa)
    cliente.bloqueado = not cliente.bloqueado
    cliente.save()
    
    status = "bloqueado" if cliente.bloqueado else "desbloqueado"
    messages.success(request, f'Cliente "{cliente.empresa}" foi {status} com sucesso.')
    
    return redirect('listar_clientes')