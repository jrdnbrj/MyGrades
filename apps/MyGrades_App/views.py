from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import *

# Create your views here.

def landing_page(request):
    return render(request, 'home/landing_page.html', {})

def post_assigment(request):
    if request.method == 'POST':
        form = TrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            trabajo = form.save()
            return render(request, 'post/post_assignment_2.html', {'trabajo': trabajo})
        else:
            print(form.errors)
    return render(request, 'post/post_assignment.html', {})

#def post_assigment_2(request):
#    return render(request, 'post/post_assignment_2.html', {})

def register(request):
    try:
        contexto = {'email': request.GET['email']}
    except:
        contexto = {}
    if request.method == 'POST':
        if request.POST['password'] != request.POST['password-repeat']:
            print('---------------Password Error--------------------')
            return redirect('register')
        form = UsuarioForm(request.POST)
        if form.is_valid():
            #usuario = form.save()
            return render(request, 'home/register_verification.html', {})
        else:
            print(form.errors)
    return render(request, 'home/register.html', contexto)

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('landing_page')
        else:
            messages.error(request, 'Credenciales Incorrectas')
            print('Credenciales incorrectas')
    return render(request, 'home/signin.html', {})

def signout(request):
    logout(request)
    return redirect('landing_page')

def registrar_usuario(request):
    if request.method == 'POST':
        email = request.POST['mail']
        username = request.POST['username']
        password = request.POST['password']
        password_verify = request.POST['password_verify']
        if password == password_verify:
            user = User.objects.create_user(username, email, password)
            if user is None:
                messages.error(request, 'Error al registrar usuario')
            usuario = UsuarioForm(request.POST)
            if usuario.is_valid():
                usuario.save()
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    return redirect('landingPage')