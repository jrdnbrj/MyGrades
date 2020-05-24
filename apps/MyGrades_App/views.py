from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
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
        context = {'email': request.GET['email']}
    except:
        context = {}

    if request.method == 'POST':
        email = request.POST['mail']
        username = request.POST['username']
        password = request.POST['password']
        password_verify = request.POST['password-repeat']
        if password == password_verify:
            usuario = UsuarioForm(request.POST)
            if usuario.is_valid():
                usuario.save()
                user = User.objects.create_user(username, email, password)
                if user is None:
                    messages.error(request, 'Error al registrar usuario')
                    return redirect('register')
                return redirect('register_verification')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    return render(request, 'home/register.html', context)

def register_verification(request):
    if request.method == 'POST':
        pass
    else:
        import random
        import smtplib
        from email.message import EmailMessage

        sender = 'udla20202020@gmail.com'
        code = random.randint(100000, 999999)

        msg = EmailMessage()
        msg['Subject'] = "MyGrades Account Verification Code"
        msg['From'] = sender
        msg['To'] = 'www.jrdnbrj@gmail.com'
        msg.set_content(code)

        with smtplib.SMTP_SSL(server, port) as smtp:
            smtp.login(sender, "Anonimo2019")
            smtp.send_message(msg)
            print('Sent', code)

        return render(request, 'home/register_verification.html', {'code': code})



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