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
                #usuario.save()
                #user = User.objects.create_user(username, email, password)
                #if user is None:
                #    messages.error(request, 'Error al registrar usuario')
                #    return redirect('register')
                #return render(request, 'home/register_verification.html', {})
                return register_verification(request)
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
        #try:
        import random
        import smtplib
        from email.message import EmailMessage

        sender = 'udla20202020@gmail.com'
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
            smtp.login(sender, "Anonimo2019")
            print('login')
            smtp.send_message(msg)
            request.session['code'] = code
            print('Sent', code, 'hola')
        #except:
        #    print('---------------Email Error------------')
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