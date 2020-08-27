from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers


import datetime
import base64

from .forms import *
from .models import *


def landing_page(request):
    return render(request, 'home/landing_page.html', {})

def register(request):

    try:
        context = {'email': request.GET['email']}
    except:
        context = {}

    if request.method == 'POST':
        usuario = UsuarioForm(request.POST)
        if usuario.is_valid():
            usuario = usuario.save()
            if not 'license_terms' in request.POST:
                context['license_error'] = 'License conditions must be accepted to continue.'
                context['form'] = usuario
                return render(request, 'home/register.html', context)
            user = User.objects.create_user(usuario.username, usuario.mail, usuario.password)
            if user is None:
                print('--------------Create User Error---------------')
            return redirect('signin')
        else:
            print(usuario.errors)
            if not 'license_terms' in request.POST:
                context['license_error'] = 'License conditions must be accepted to continue.'
            context['form'] = usuario
            print(usuario)
            return render(request, 'home/register.html', context)
    return render(request, 'home/register.html', context)

def signin(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('work_place')
        else:
            print('Credenciales incorrectas')
            context['error'] = 'Incorrect username or password.'
            context['username'] = username
    return render(request, 'home/signin.html', context)

def signout(request):
    logout(request)
    return redirect('landing_page')

#___________________________POST ASSIGNMENT_____________________________

@login_required
def post_assignment(request):
    context = {}
    if request.method == 'POST':
        form = PostAssignmentForm(request.POST)
        if form.is_valid():
            trabajo = form.save(commit=False)
            trabajo.publicador = Usuario.objects.get(username = request.user)
            trabajo.save()
            if 'files_from_validation' in request.POST:
                for file in request.POST.getlist('files_from_validation'):
                    trabajo.archivos.add(Archivo.objects.get(id = file))

            if request.FILES:
                for archivo in trabajo.archivos.all():
                    trabajo.archivos.remove(archivo)

            for file in request.FILES.getlist('archivos'):
                archivo = Archivo.objects.create(nombre=file.name, archivo=file)
                trabajo.archivos.add(archivo)

            request.session['id'] = trabajo.id
            print('id_pa1:',request.session['id'])
            return redirect('post_assignment_3')
        else:
            print(form.errors)
            context['form'] = form
            files = [Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file) for file in request.FILES.getlist('archivos')]
            context['files'] = files
            
    return render(request, 'post/post_assignment.html', context)

@login_required
def post_assignment_2(request):
    pass

@login_required
def post_assignment_3(request):
    context = {}
    if 'precio' in request.session:
        context['precio'] = request.session.pop('precio')

    if request.method == 'POST':
        #print(request.session['id'], request.POST['price'])
        print('id_pa3:', request.session['id'])
        trabajo = Trabajo.objects.get(id = request.session['id'])
        trabajo.precio = request.POST['price']
        trabajo.estado = 'published'
        trabajo.save()
        return redirect('post_assignment_4')
    return render(request, 'post/post_assignment_3.html', context)

@login_required
def post_assignment_4(request):
    trabajo = Trabajo.objects.get(id = request.session.pop('id'))
    return render(request, 'post/post_assignment_4.html', {'trabajo': trabajo})

#___________________________WORK PLACE_____________________________

@login_required
def work_place(request): 
    return render(request, 'work_place/work_place.html', {})

def wp_ajax(request):
    if request.is_ajax and request.method == "POST":
        print(request.POST['title'], request.POST['area'], request.POST['date_from'], request.POST['date_to'])

        trabajos = Trabajo.objects.filter(estado='published')
        if request.POST['title']:
            trabajos = trabajos.filter(Q(titulo__icontains=request.POST['title']) | Q(descripcion__icontains=request.POST['title']))
        if request.POST['area']:
            trabajos = trabajos.filter(area=request.POST['area'])
        if request.POST['date_from']:
            trabajos = trabajos.exclude(fecha_expiracion__lt=request.POST['date_from'])
        if request.POST['date_to']:
            trabajos = trabajos.exclude(fecha_publicacion__gt=request.POST['date_to'])
        trabajos = trabajos.order_by('fecha_expiracion')

        # len_trabajos = len(trabajos)
        page = request.POST['page']
        trabajos = Paginator(trabajos, 10)
        pags = {
            'page': page,
            'has_previous': trabajos.page(page).has_previous(),
            'has_next': trabajos.page(page).has_next(),
            'num_pages': trabajos.num_pages,
            'objects': serializers.serialize('json', trabajos.page(page).object_list)
        }
        
    return JsonResponse(data={'len': trabajos.count, 'pags': pags}, safe=False)

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
    path = str(path.replace(' ', '_'))
    #print('\npath', path)
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

#___________________________USER PROFILE_____________________________

@login_required
def user_profile(request):
    usuario = Usuario.objects.get(username = request.user)
    return render(request, 'user/user_profile.html', {'usuario': usuario})

@login_required
def user_profile_2(request):
    context = {}
    usuario = Usuario.objects.get(username = request.user)
    context['usuario'] = usuario
    return render(request, 'user/user_profile_2.html', context)

@login_required
def edit_user(request):
    context = {}
    user = Usuario.objects.get(username = request.user)
    context['usuario'] = user
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            usuario = form.save()
            user.username = usuario.username
            user.email = usuario.mail
            user.save()
        else:
            print(form.errors)
            context['form1'] = form
    return render(request,'user/user_profile_2.html', context)

@login_required
def edit_user_info(request):
    context = {}
    usuario = Usuario.objects.get(username = request.user)
    context['usuario'] = usuario
    if request.method == 'POST':
        
        form = EditUserInfoForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.key_words = ','.join(request.POST.getlist('key_words'))
            usuario.save()
        else:
            print(form.errors)
            context['form2'] = form
            context['key_words_error'] = request.POST.getlist('key_words')
            return render(request,'user/user_profile_2.html', context)
    return render(request,'user/user_profile_2.html', context)

@login_required
def edit_payment_method(request):
    print('user_payment_method')
    return redirect('user_profile_2')

@login_required
def edit_password(request):
    context = {}
    user = User.objects.get(username=request.user)
    usuario = Usuario.objects.get(username=user.username)
    context['usuario'] = usuario
    if request.method == 'POST':
        form = EditPasswordForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            usuario.password = user.password
            user.set_password(user.password)
            user.save(); usuario.save()
            return redirect('signin')
        else:
            print(form.errors)
            context['form4'] = form
    return render(request,'user/user_profile_2.html', context)

def verify_assigments(assignments):
    date_time = utc.localize(datetime.datetime.now())
    
    for assignment in assignments:
        if assignment.fecha_expiracion < date_time:
            assignment.estado = 'closed'
    return assigments

@login_required
def user_assignments(request):
    user = Usuario.objects.get(username=request.user)
    posted_assignments = Trabajo.objects.filter(publicador__username=request.user).exclude(estado='deleted')
    taken_assignments = Trabajo.objects.filter(trabajador__username=request.user).exclude(estado='deleted')

    context = {
        'posted_assignments': posted_assignments,
        'taken_assignments': taken_assignments,
    }
    return render(request, 'user/user_assignments.html', context)

@login_required
def edit_post_assignment(request, id):
    trabajo = Trabajo.objects.get(id = id)
    if request.method == 'POST':
        form = PostAssignmentForm(request.POST)
        if form.is_valid():
            trabajo = form.save(commit=False, instance=trabajo)
            trabajo.publicador = Usuario.objects.get(username = request.user)
            trabajo.save()
            if 'files_from_validation' in request.POST:
                for archivo in trabajo.archivos.all():
                    trabajo.archivos.remove(archivo)
                for file in request.POST.getlist('files_from_validation'):
                    trabajo.archivos.add(Archivo.objects.get(id = file))

            if request.FILES:
                for archivo in trabajo.archivos.all():
                    trabajo.archivos.remove(archivo)

            for file in request.FILES.getlist('archivos'):
                archivo = Archivo.objects.create(nombre=file.name, archivo=file)
                trabajo.archivos.add(archivo)

            request.session['id'] = trabajo.id
            request.session['precio'] = str(trabajo.precio)
            return redirect('post_assignment_3')
        else:
            print(form.errors)
            context = {}
            context['form'] = form
            files = [Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file) for file in request.FILES.getlist('archivos')]
            context['files'] = files
            context['trabajo_id'] = trabajo.id
    else:
        options = {
            'Literature': 0, 
            'History': 1, 
            'Social Sciences': 2, 
            'Nature Sciences': 3,
            'Biology': 4, 
            'Chemistry': 5, 
            'Mathematics': 6,
            'Physics': 7, 
            'Engineering': 8,
            'Languages': 9,
            'Economics': 10,
            'Laws': 11,
            'Arts': 12,
            'Marketing and Publicity': 13,
            'Architecture and Design': 14,
            'Business and Management': 15,
            'Psychology': 16,
            'Other...': 17
        }
        context = {'trabajo': trabajo, 'option': options[trabajo.area]}
    return render(request, 'post/post_assignment.html', context)

#___________________________SEND ASSIGNMENT_____________________________

def send_assignment(request):
    pk = request.POST['pk']
    trabajo = Trabajo.objects.get(pk=pk)
    if request.method == 'POST':
        
        if request.FILES:
            print('files')
            for archivo in trabajo.archivos_trabajador.all():
                trabajo.archivos_trabajador.remove(archivo)
        
        for file in request.FILES.getlist('archivos'):
            print('getlist')
            archivo = Archivo.objects.create(nombre=file.name, archivo=file)
            trabajo.archivos_trabajador.add(archivo)
            trabajo.estado = 'sent'
            trabajo.fecha_entrega = datetime.datetime.now()
            trabajo.save()
    return redirect('user_assignments')
