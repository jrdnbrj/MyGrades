from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.http import JsonResponse
import json

from .forms import *
from .models import *

# Create your views here.

def landing_page(request):
    return render(request, 'home/landing_page.html', {})

def register(request):

    try:
        context = {'email': request.GET['email']}
    except:
        context = {}

    if request.method == 'POST':
        email = request.POST['mail']
        username = request.POST['username']
        celular = request.POST['celular']
        password = request.POST['password']
        password_verify = request.POST['password-repeat']
        print(email, username, password, password_verify)
        if password == password_verify:
            print('-----------------REQUEST-----------------')
            print(request.POST)
            print('-----------------REQUEST-----------------')
            usuario = UsuarioForm(request.POST)
            if usuario.is_valid():
                request.session['email'] = email
                request.session['username'] = username
                request.session['password'] = password
                request.session['celular'] = celular
                request.method = 'GET'
                print(request.method, 'method')
                return register_verification(request)
            else:
                print(usuario.errors)
        else:
            messages.error(request, 'Las contraseñas no coinciden')
            print('---------Password Error---------------')
    return render(request, 'home/register.html', context)

def register_verification(request):
    if request.method == 'POST':
        print(request.session['code'], request.POST['code'], request.session['email'])
        if int(request.POST['code']) == int(request.session['code']):
            print('Codigo verificado')
            data = request.POST.copy()
            data['mail'] = request.session['email']
            data['username'] = request.session['username']
            data['password'] = request.session['password']
            data['celular'] = request.session['celular']
            form = UsuarioForm(data)
            if form.is_valid():
                form.save()
                user = User.objects.create_user(request.session['username'], request.session['email'], request.session['password'])
                if user is None:
                    messages.error(request, 'Error al registrar usuario')
                    print('--------------Create User Error---------------')
            else:
                print('------------User Error--------------')
                print(form.errors)
        else:
            print('Codigo incorrecto')
        return redirect('landing_page')
    else:
        try:
            import random
            import smtplib
            from email.message import EmailMessage

            sender = 'contact.mygrades@gmail.com'
            code = random.randint(100000, 999999)
            print('code: ', code)

            msg = EmailMessage()
            msg['Subject'] = "MyGrades Account Verification Code"
            msg['From'] = sender
            msg['To'] = request.session['email']
            print('Before content')
            msg.set_content('Code: ' + str(code))
            print('After content')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender, "mygrades123")
                print('login')
                smtp.send_message(msg)
                request.session['code'] = code
                print('Sent', code)
        except:
            print('---------------Email Error------------')
            return redirect('register')
        return render(request, 'home/register_verification.html', {})

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

def post_assigment(request):
    if request.method == 'POST':
        form = TrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            trabajo = form.save()
            trabajo.publicador = Usuario.objects.get(username = request.user)
            trabajo.save()
            return render(request, 'post/post_assignment_2.html', {'trabajo': trabajo})
            #request.method = 'GET'
            #return post_assignment_2(request)
        else:
            print(form.errors)
    return render(request, 'post/post_assignment.html', {})

def post_assignment_2(request):
    if request.method == 'POST':
        print(request.session['archivos'])
    else:
        context = {
            'area': request.POST['area'],
            'titulo': request.POST['titulo'],
            'fecha': request.POST['fecha_expiracion'],
            'descripcion': request.POST['descripcion'],
            'archivos': request.FILES['archivos'],
        }
        request.session['archivos'] = request.FILES['archivos']
        return render(request, 'post/post_assignment_2.html', context)

def post_assigment_3(request):
    return render(request, 'post/post_assignment_3.html', context)

def pa_ajax(request):
    if request.is_ajax:
        pass
    return JsonResponse(data={}, safe=False)

def work_place(request):
    trabajos = Trabajo.objects.filter(estado = 'publicado').order_by('fecha_expiracion')
    return render(request, 'work_place/work_place.html', {'trabajos': trabajos})

def requestAjax(request):
    data = {
        'is_valid': False,}
    if request.is_ajax():
        message = request.POST.get('message')
        if message == 'I want an AJAX response':
            data.update(is_valid=True)
            data.update(response= 'This is the response you wanted')
    return JsonResponse(data)

def wp_ajax(request):
    if request.is_ajax and request.method == "POST":
        print(request.POST['title'], request.POST['area'], request.POST['date_from'], request.POST['date_to'])
        title = request.POST['title']
        area = request.POST['area']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']

        trabajos = Trabajo.objects.filter(estado = 'publicado').order_by('fecha_expiracion')
        if title:
            trabajos = trabajos.filter(titulo__icontains = title)
        if area:
            trabajos = trabajos.filter(area = area)
        if date_from:
            trabajos = trabajos.exclude(fecha_expiracion__lt=date_from)
        if date_to:
            trabajos = trabajos.exclude(fecha_publicacion__gt=date_to)
        print(len(trabajos), trabajos)
        long = len(trabajos)
        trabajos = serializers.serialize('json', trabajos)
    return JsonResponse(data={'trabajos': trabajos, 'len': long}, safe=False)