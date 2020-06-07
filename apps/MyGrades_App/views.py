from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
import datetime

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
        if password == password_verify:
            usuario = UsuarioForm(request.POST)
            if usuario.is_valid():
                request.session['email'] = email
                request.session['username'] = username
                request.session['password'] = password
                request.session['celular'] = celular
                request.method = 'GET'
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

#___________________________POST ASSIGNMENT_____________________________

@login_required
def post_assigment(request):
    if request.method == 'POST':
        print(request.POST)
        form = TrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            trabajo = form.save(commit=False)
            trabajo.publicador = Usuario.objects.get(username = request.user)
            trabajo.save()
            request.session['id'] = trabajo.id
            return redirect('post_assignment_3')
        else:
            print(form.errors)
    return render(request, 'post/post_assignment.html', {})

@login_required
def post_assignment_2(request):
    pass

@login_required
def post_assignment_3(request):
    if request.method == 'POST':
        print(request.session['id'], request.POST['price'])
        trabajo = Trabajo.objects.get(id = request.session.pop('id'))
        trabajo.precio = request.POST['price']
        trabajo.save()
        return redirect('work_place')
    return render(request, 'post/post_assignment_3.html', {})

#___________________________WORK PLACE_____________________________

@login_required
def work_place(request):
    trabajos = Trabajo.objects.filter(estado = 'publicado').order_by('fecha_expiracion')
    return render(request, 'work_place/work_place.html', {'trabajos': trabajos})

def wp_ajax(request):
    if request.is_ajax and request.method == "POST":
        print(request.POST['title'], request.POST['area'], request.POST['date_from'], request.POST['date_to'])
        title = request.POST['title']
        area = request.POST['area']
        date_from = request.POST['date_from']
        date_to = request.POST['date_to']

        trabajos = Trabajo.objects.filter(estado='published')

        if area:
            trabajos = trabajos.filter(area=area)
        if date_from:
            trabajos = trabajos.exclude(fecha_expiracion__lt=date_from)
        if date_to:
            trabajos = trabajos.exclude(fecha_publicacion__gt=date_to)
        if title:
            trabajos_title = trabajos.filter(titulo__icontains=title)
            trabajos_description = trabajos.filter(descripcion__icontains=title)
            trabajos = trabajos_title.union(trabajos_description)

        trabajos = trabajos.order_by('fecha_expiracion')

        long = len(trabajos)
        trabajos = serializers.serialize('json', trabajos)
    return JsonResponse(data={'trabajos': trabajos, 'len': long}, safe=False)

@login_required
def work_place_2(request, pk):
    trabajo = Trabajo.objects.get(pk = pk)
    return render(request, 'work_place/work_place_2.html', {'trabajo': trabajo})

@login_required
def work_place_3(request, id):
    trabajo = Trabajo.objects.get(id = id)
    fecha_expiracion = trabajo.fecha_expiracion

    context = {'fecha_expiracion': fecha_expiracion, 'id': id}
    return render(request, 'work_place/work_place_3.html', context)

def download_file(request, path):
    response = HttpResponse(open('media/' + path, 'rb').read())
    response['Content-Type'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename='+path
    return response

@login_required
def work_place_4(request, id):
    trabajo = Trabajo.objects.get(id = id)
    trabajo.trabajador = Usuario.objects.get(username = request.user.username)
    trabajo.estado = 'taken'
    trabajo.fecha_asignacion_trabajador = datetime.datetime.now()
    trabajo.save()

    context = {
        'fecha_expiracion': trabajo.fecha_expiracion,
        'titulo': trabajo.titulo,
    }
    return render(request, 'work_place/work_place_4.html', context)

#___________________________USER INTERFACE_____________________________

@login_required
def user_interface(request):
    user = Usuario.objects.get(username = request.user.username)
    posted_assignments = Trabajo.objects.filter(publicador = user.id)
    taken_assignments = Trabajo.objects.filter(trabajador = user.id)

    context = {
        'posted_assignments': posted_assignments,
        'taken_assignments': taken_assignments,
    }
    return render(request, 'user_interface/user_interface.html', context)

@login_required
def user_interface_2(request):
    return render(request, 'user_interface/user_interface_2.html', {})

@login_required
def user_interface_3(request):
    return render(request, 'user_interface/user_interface_3.html', {})