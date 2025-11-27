from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Cliente, Carro
import re
from django.core import serializers
import json
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail

@login_required
def clientes(request):
    # A view `clientes` agora serve somente a listagem de clientes (GET)
    # Ordenação: ?order=name ou ?order=date
    order = request.GET.get('order', 'name')
    if order == 'date':
        clientes_qs = Cliente.objects.all().order_by('-id')
    else:
        clientes_qs = Cliente.objects.all().order_by('nome')

    # Paginação: ?page=1 & per_page=20
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(clientes_qs, per_page)
    try:
        clientes_page = paginator.page(page)
    except PageNotAnInteger:
        clientes_page = paginator.page(1)
    except EmptyPage:
        clientes_page = paginator.page(paginator.num_pages)

    return render(request, 'clientes.html', {'clientes': clientes_page, 'paginator': paginator, 'order': order, 'per_page': per_page})


@login_required
def novo_cliente(request):
    # Formulário separado para criação de cliente (GET) e criação (POST)
    if request.method == 'GET':
        return render(request, 'novo_cliente.html')

    # POST: criar cliente e carros enviados no formulário
    nome = request.POST.get('nome')
    sobrenome = request.POST.get('sobrenome')
    email = request.POST.get('email')
    cpf = request.POST.get('cpf')
    carros = request.POST.getlist('carro')
    placas = request.POST.getlist('placa')
    anos = request.POST.getlist('ano')

    cliente_qs = Cliente.objects.filter(cpf=cpf)

    if cliente_qs.exists():
        messages.error(request, 'Já existe um cliente com esse CPF.')
        return render(request, 'novo_cliente.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'carros': zip(carros, placas, anos)})

    if not re.fullmatch(re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'), email):
        messages.error(request, 'E-mail inválido.')
        return render(request, 'novo_cliente.html', {'nome': nome, 'sobrenome': sobrenome, 'cpf': cpf, 'carros': zip(carros, placas, anos)})

    cliente = Cliente(nome=nome, sobrenome=sobrenome, email=email, cpf=cpf)
    cliente.save()

    for carro, placa, ano in zip(carros, placas, anos):
        car = Carro(carro=carro, placa=placa, ano=ano or 0, cliente=cliente)
        car.save()

    messages.success(request, 'Cliente cadastrado com sucesso.')
    return redirect(reverse('clientes'))


@login_required
def att_cliente(request):
    id_cliente = request.POST.get('id_cliente')
    cliente = Cliente.objects.filter(id=id_cliente)
    carros = Carro.objects.filter(cliente=cliente[0])
    cliente_json = json.loads(serializers.serialize('json', cliente))[0]['fields']
    cliente_id = json.loads(serializers.serialize('json', cliente))[0]['pk']
    carros_json = json.loads(serializers.serialize('json', carros))
    carros_json = [{'fields': i['fields'], 'id': i['pk']} for i in carros_json]
    data = {'cliente': cliente_json, 'carros': carros_json, 'cliente_id': cliente_id}
    return JsonResponse(data)

@login_required
def excluir_carro(request, id):
    try:
        carro = Carro.objects.get(id=id)
        carro.delete()
        return redirect(reverse('clientes')+f'?aba=att_cliente&id_cliente={id}')
    except:
        return redirect(reverse('clientes')+f'?aba=att_cliente&id_cliente={id}')

@csrf_exempt
@login_required
def update_carro(request, id):
    nome_carro = request.POST.get('carro')
    placa = request.POST.get('placa')
    ano = request.POST.get('ano')

    carro = Carro.objects.get(id=id)
    list_carros = Carro.objects.exclude(id=id).filter(placa=placa)

    if list_carros.exists():
        return HttpResponse('Placa já existente') 
        
    carro.carro = nome_carro
    carro.placa = placa
    carro.ano = ano
    carro.save()

    return HttpResponse(id)


@csrf_exempt
@login_required
def criar_carro(request):
    # Cria um carro via AJAX para um cliente existente
    try:
        cliente_id = request.POST.get('cliente_id') or request.POST.get('cliente')
        carro = request.POST.get('carro')
        placa = request.POST.get('placa')
        ano = request.POST.get('ano')
        if not cliente_id:
            return JsonResponse({'status': '400', 'error': 'cliente_id required'})
        cliente = Cliente.objects.get(id=cliente_id)
        car = Carro.objects.create(carro=carro, placa=placa, ano=ano or 0, cliente=cliente)
        return JsonResponse({'status': '200', 'id': car.id, 'carro': car.carro, 'placa': car.placa, 'ano': car.ano})
    except Exception as e:
        return JsonResponse({'status': '500', 'error': str(e)})


@csrf_exempt
@login_required
def excluir_carro_ajax(request):
    # Exclui um carro via AJAX (POST com id)
    try:
        body = request.POST or request.GET
        carro_id = body.get('id')
        if not carro_id:
            return JsonResponse({'status': '400', 'error': 'id required'})
        carro = Carro.objects.get(id=carro_id)
        carro.delete()
        return JsonResponse({'status': '200'})
    except Carro.DoesNotExist:
        return JsonResponse({'status': '404', 'error': 'not found'})
    except Exception as e:
        return JsonResponse({'status': '500', 'error': str(e)})

@login_required
def update_cliente(request, id):
    body = json.loads(request.body)

    nome = body['nome']
    sobrenome = body['sobrenome']
    email = body['email']
    cpf = body['cpf']

    cliente = get_object_or_404(Cliente, id=id)
    try:
        cliente.nome = nome
        cliente.sobrenome = sobrenome
        cliente.email = email
        cliente.cpf = cpf
        cliente.save()
        return JsonResponse({'status': '200', 'nome': nome, 'sobrenome': sobrenome, 'email': email, 'cpf': cpf})
    except:
        return JsonResponse({'status': '500'})


@login_required
def excluir_cliente(request, id):
    try:
        cliente = Cliente.objects.get(id=id)
        cliente.delete()
        messages.success(request, 'Cliente removido com sucesso.')
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente não encontrado.')
    return redirect(reverse('clientes'))


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect(reverse('clientes'))
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos.', 'next': next_url})
    return render(request, 'login.html', {'next': next_url})


def logout_view(request):
    auth_logout(request)
    return redirect(reverse('login'))


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(reverse('clientes'))
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # use Django's built-in email flow
            form.save(request=request, use_https=False, email_template_name='password_reset_email.html')
            return render(request, 'password_reset_done.html')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

