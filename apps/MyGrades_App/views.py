from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.core import serializers

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersGetRequest, OrdersAuthorizeRequest, OrdersCaptureRequest

from decimal import Decimal
from datetime import datetime
import sys
import json

from .forms import *
from .models import *


def landing_page(request): 
    print(datetime.now())
    return render(request, 'home/landing_page.html', {})

def register(request):
    print(request.user)
    if request.user.is_authenticated: return redirect('work_place')

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
            context['error'] = 'Incorrect username or password. Please try again.'
            context['username'] = username
    return render(request, 'home/signin.html', context)

@login_required
def signout(request):
    logout(request)
    return redirect('landing_page')

def about(request): return render(request, 'home/about.html')

def contact(request): return render(request, 'home/contact.html')

def terms_conditions(request): return render(request, 'home/terms&conditions.html')

#___________________________ERROR HANDLERS_____________________________

def handler404(request, *args, **argv): return render(request, 'error/404.html')

def handler500(request, *args, **argv): return render(request, 'error/500.html')

#___________________________POST ASSIGNMENT_____________________________

@login_required
def post_assignment(request):
    context = {}
    if request.method == 'POST':
        form = PostAssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            trabajo = form.save(commit=False)
            trabajo.publicador = Usuario.objects.get(username = request.user)
            trabajo.save()
            if 'files_from_validation' in request.POST:
                for archivo in trabajo.archivos.all():
                    trabajo.archivos.remove(archivo)
                    # pendiente por eliminar archivos del modelo
                for file in request.POST.getlist('files_from_validation'):
                    trabajo.archivos.add(Archivo.objects.get(id = file))

            if request.FILES:
                for archivo in trabajo.archivos.all():
                    trabajo.archivos.remove(archivo)
                    # pendiente por eliminar archivos del modelo

            for file in request.FILES.getlist('archivos'):
                if file.size < 10000000:
                    archivo = Archivo.objects.create(nombre=file.name, archivo=file)
                    trabajo.archivos.add(archivo)

            return redirect('post_assignment_payment', trabajo=trabajo.id)
        else:
            print(form.errors)
            context['form'] = form
            if 'files_from_validation' in request.POST:
                files = [ Archivo.objects.get(id=file) for file in request.POST.getlist('files_from_validation') ]
            else:
                files = []
                for file in request.FILES.getlist('archivos'):
                    if file.size < 10000000:
                        files += [Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file)]

            context['files'] = files
            
    return render(request, 'post/post_assignment.html', context)

@login_required
def post_assignment_payment(request, trabajo):
    trabajo = Trabajo.objects.get(id=trabajo)
    if str(trabajo.publicador) != str(request.user): raise Http404()

    if trabajo.estado == 'hidden':
        return render(request, 'post/post_assignment_payment.html', { 'trabajo': trabajo })
    else:
        return render(request, 'post/post_assignment_complete.html', { 'trabajo': trabajo })

#___________________________WORK PLACE_____________________________

@login_required
def work_place(request): 
    validate_time(Trabajo.objects.all())
    return render(request, 'work_place/work_place.html', {})

def wp_ajax(request):
    if request.is_ajax and request.method == "POST":
        print(request.POST['title'], request.POST['area'], request.POST['date_from'], request.POST['date_to'])
        
        trabajos = validate_time(Trabajo.objects.all())
        trabajos = trabajos.filter(estado='posted')
        
        if request.POST['title']:
            trabajos = trabajos.filter(Q(titulo__icontains=request.POST['title']) | Q(descripcion__icontains=request.POST['title']))
        if request.POST['area']:
            trabajos = trabajos.filter(area=request.POST['area'])
        if request.POST['date_from']:
            trabajos = trabajos.exclude(fecha_expiracion__lt=request.POST['date_from'])
        if request.POST['date_to']:
            trabajos = trabajos.exclude(fecha_publicacion__gt=request.POST['date_to'])
        trabajos = trabajos.order_by('-fecha_editado')

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
def work_place_2(request, pk): #preview
    trabajo = get_object_or_404(Trabajo, pk=pk)
    if trabajo.estado != 'posted': raise Http404()

    return render(request, 'work_place/work_place_2.html', { 'trabajo': trabajo })

@login_required
def work_place_3(request, id): #conditions
    trabajo = get_object_or_404(Trabajo, id=id)
    if trabajo.estado != 'posted' or str(trabajo.publicador) == str(request.user): 
        raise Http404()

    if request.method == 'POST':
        trabajo.trabajador = Usuario.objects.get(username = request.user)
        trabajo.estado = 'taken'
        trabajo.fecha_asignacion_trabajador = datetime.now()
        trabajo.save()
        return redirect('work_place_4', id=id)

    context = { 'fecha_expiracion': trabajo.fecha_expiracion, 'id': id }
    return render(request, 'work_place/work_place_3.html', context)

@login_required
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
    if str(trabajo.trabajador) != str(request.user): raise Http404()

    context = {
        'fecha_expiracion': trabajo.fecha_expiracion,
        'titulo': trabajo.titulo,
    }
    return render(request, 'work_place/work_place_4.html', context)

#___________________________USER PROFILE_____________________________

def user_and_payment(request):
    user = User.objects.get(username=request.user)
    usuario = Usuario.objects.get(username=request.user)
    payment = Cuenta_Bancaria.objects.filter(usuario__username=request.user).first()
    return user, usuario, payment

@login_required
def user_profile(request):
    _, usuario, payment = user_and_payment(request)
    return render(request, 'user/user_profile.html', {'usuario': usuario, 'payment': payment })

def public_profile(request, username):
    try: usuario = Usuario.objects.get(username=username)
    except: raise Http404()

    assignments = Trabajo.objects.filter(publicador__username=username) \
        .filter(Q(estado='posted') | Q(estado='taken')).order_by('-fecha_publicacion')
    context = {
        'usuario': usuario,
        'assignments': assignments
    }
    return render(request, 'user/public_profile.html', context)

@login_required
def user_profile_2(request, status):
    _, usuario, payment = user_and_payment(request)
    if status == 'edited':
        return render(request, 'user/user_profile_2.html', { 'usuario': usuario, 'payment': payment, 'edit': True })
    elif status == 'edit':
        return render(request, 'user/user_profile_2.html', { 'usuario': usuario, 'payment': payment })
    else: raise Http404()


@login_required
def edit_user(request):
    context = {}
    user, usuario, payment = user_and_payment(request)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            # user = User.objects.get(username=request.user)
            user.username = usuario.username
            user.email = usuario.mail
            user.save()
        else:
            print(form.errors)
            context['form1'] = form
            context['usuario'] = usuario
            context['payment'] = payment
            return render(request,'user/user_profile_2.html', context)
    
    return redirect('user_profile_2', status='edited')


@login_required
def edit_user_info(request):
    context = {}
    user, usuario, payment = user_and_payment(request)

    if request.method == 'POST':
        form = EditUserInfoForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.key_words = json.dumps(request.POST.getlist('key_words'))
            usuario.save()
        else:
            print(form.errors)
            context['form2'] = form
            context['key_words_error'] = request.POST.getlist('key_words')
            context['payment'] = payment
            context['usuario'] = usuario
            return render(request,'user/user_profile_2.html', context)

    return redirect('user_profile_2', status='edited')

@login_required
def edit_payment_method(request):
    print('user_payment_method')

    user, usuario, payment = user_and_payment(request)

    if request.method == 'POST' and request.POST['tipo_pago'] != '':

        if request.POST['tipo_pago'] == 'PayPal':
            form = PayPalEmailForm(request.POST, instance=payment)
        elif request.POST['tipo_pago'] == 'Bank':
            form = CuentaBancariaForm(request.POST, instance=payment)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.usuario = usuario
            payment.save()
        else:
            print(form.errors)
            return render(request, 'user/user_profile_2.html', { 'usuario': usuario, 'form3': form })

    elif request.POST['tipo_pago'] == '' and payment: payment.delete()

    return redirect('user_profile_2', status='edited')


@login_required
def edit_password(request):
    context = {}
    user, usuario, payment = user_and_payment(request)
    user = User.objects.get(username=request.user)
    usuario = Usuario.objects.get(username=user.username)

    if request.method == 'POST':
        form = EditPasswordForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            # usuario.password = user.password
            user.set_password(usuario.password)
            user.save(); usuario.save()
            return redirect('signin')
        else:
            print(form.errors)
            context['form4'] = form
            context['usuario'] = usuario
            context['payment'] = payment
            return render(request,'user/user_profile_2.html', context)

    return redirect('user_profile_2', status='edited')

def validate_time(assignments):
    for assignment in assignments:
        if assignment.estado == 'posted':
            if assignment.fecha_expiracion <= datetime.now():
                assignment.estado = 'closed'
                assignment.trabajador = None
                assignment.save()

    return assignments

@login_required
def user_assignments(request):
    user = Usuario.objects.get(username=request.user)
    posted_assignments = Trabajo.objects.filter(publicador__username=request.user).exclude(estado='deleted').exclude(estado='eliminated')
    taken_assignments = Trabajo.objects.filter(trabajador__username=request.user).exclude(estado='thrown').exclude(estado='eliminated')

    context = {
        'posted_assignments': validate_time(posted_assignments).order_by('-fecha_publicacion'),
        'taken_assignments': validate_time(taken_assignments).order_by('-fecha_publicacion'),
    }
    return render(request, 'user/user_assignments.html', context)

@login_required
def delete_assignment(request, id):
    trabajo = Trabajo.objects.get(id=id)
    if str(trabajo.publicador) != str(request.user) or trabajo.estado == 'taken' or trabajo.estado == 'rejected' or trabajo.estado == 'sent': 
        raise Http404()

    if request.method == 'POST': 
        if trabajo.estado == 'thrown': trabajo.estado = 'eliminated'
        else: trabajo.estado = 'deleted'
        trabajo.save()
    
    return redirect('user_assignments')

@login_required
def accept_reject(request, id):
    trabajo = Trabajo.objects.get(id=id)
    if str(trabajo.publicador) != str(request.user) or \
        not (trabajo.estado == 'sent' or (trabajo.estado == 'accepted' and trabajo.on_time()) or trabajo.estado == 'rejected'): 
        raise Http404()
    
    if request.method == 'POST':
        if request.POST['accept_reject'] == 'accept': trabajo.estado = 'accepted'
        elif request.POST['accept_reject'] == 'reject': trabajo.estado = 'rejected'
        trabajo.save()

    return redirect('user_assignments')

@login_required
def open_close(request, id):
    trabajo = Trabajo.objects.get(id=id)
    if str(trabajo.publicador) != str(request.user) or \
        not (trabajo.estado == 'posted' or trabajo.estado == 'closed' or (trabajo.estado == 'rejected' and trabajo.on_time())): 
        raise Http404()
    
    if request.method == 'POST':
        if request.POST['open_close'] == 'open': trabajo.estado = 'posted'
        elif request.POST['open_close'] == 'close': trabajo.estado = 'closed'
        trabajo.save()

    return redirect('user_assignments')

@login_required
def throw_assignment(request, id):
    trabajo = Trabajo.objects.get(id=id)
    if str(trabajo.trabajador) != str(request.user) or not (trabajo.estado == 'accepted' or trabajo.estado == 'deleted'): 
        raise Http404()

    if request.method == 'POST': 
        if trabajo.estado == 'deleted': trabajo.estado = 'eliminated'
        else: trabajo.estado = 'thrown'
        trabajo.save()

    return redirect('user_assignments')

@login_required
def take_assignment(request, id):
    trabajo = Trabajo.objects.get(id=id)
    if str(trabajo.trabajador) != str(request.user) or trabajo.estado != 'rejected': 
        raise Http404()

    if request.method == 'POST': trabajo.estado = 'taken'; trabajo.save()

    return redirect('user_assignments')

@login_required
def edit_post_assignment(request, id):
    context = { 'title': 'Edit' }

    trabajo = Trabajo.objects.get(id = id)
    if str(trabajo.publicador) != str(request.user) or trabajo.estado == 'sent' or trabajo.estado == 'accepted' or trabajo.estado == 'thown': 
        raise Http404()
    
    if request.method == 'POST':

        form = PostAssignmentForm(request.POST, status=trabajo.estado)
        if form.is_valid():
            trabajo = form.save(commit=False, instance=trabajo)
            trabajo.save()

            if 'files_from_validation' in request.POST:
                for archivo in trabajo.archivos.all():
                    trabajo.archivos.remove(archivo)
                    # pendiente por eliminar archivos del modelo
                for file in request.POST.getlist('files_from_validation'):
                    trabajo.archivos.add(Archivo.objects.get(id = file))

            if request.FILES:
                for archivo in trabajo.archivos.all():
                    trabajo.archivos.remove(archivo)
                    # pendiente por eliminar archivos del modelo

            for file in request.FILES.getlist('archivos'):
                if file.size < 10000000:
                    archivo = Archivo.objects.create(nombre=file.name, archivo=file)
                    trabajo.archivos.add(archivo)
            
            if trabajo.estado == 'hidden':
                return redirect('post_assignment_payment', trabajo=trabajo.id)
            else:
                return redirect('user_assignments')
        else:
            print(form.errors)
            context['form'] = form
            context['trabajo'] = trabajo

            if 'files_from_validation' in request.POST:
                files = [ Archivo.objects.get(id=file) for file in request.POST.getlist('files_from_validation') ]
            else:
                files = []
                for file in request.FILES.getlist('archivos'):
                    if file.size < 10000000:
                        files += [Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file)]

            context['files'] = files
            context['trabajo_id'] = trabajo.id
    else:
        options = {
            'Literature': 0, 'History': 1, 'Social Sciences': 2, 'Nature Sciences': 3, 'Biology': 4, 
            'Chemistry': 5, 'Mathematics': 6, 'Physics': 7, 'Engineering': 8, 'Languages': 9,
            'Economics': 10, 'Laws': 11, 'Arts': 12, 'Marketing and Publicity': 13,
            'Architecture and Design': 14, 'Business and Management': 15, 'Psychology': 16, 'Other': 17
        }
        context['trabajo'] = trabajo
        context['option'] = options[trabajo.area]

    return render(request, 'post/post_assignment.html', context)

@login_required
def send_assignment(request, id):
    trabajo = Trabajo.objects.get(id=id)

    if str(trabajo.trabajador) != str(request.user) or not (trabajo.estado == 'sent' or trabajo.estado == 'taken'): 
        raise Http404()

    if request.method == 'POST':
        
        if request.FILES:
            for archivo in trabajo.archivos_trabajador.all():
                trabajo.archivos_trabajador.remove(archivo)
                # pendiente por eliminar archivos del modelo
        
        for file in request.FILES.getlist('archivos'):
            if file.size < 10000000:
                archivo = Archivo.objects.create(nombre=file.name, archivo=file)
                trabajo.archivos_trabajador.add(archivo)

        if request.FILES:
            trabajo.estado = 'sent'
            trabajo.fecha_entrega = datetime.now()
            trabajo.save()

    return redirect('user_assignments')

@login_required
def return_assignment(request, id):
    trabajo = Trabajo.objects.get(id=id)
    if str(trabajo.trabajador) != str(request.user) or not (trabajo.estado == 'taken' and not trabajo.fifteen_minutes()): 
        raise Http404()

    if request.method == 'POST':
        trabajo.estado = 'posted'
        trabajo.trabajador = None
        trabajo.save()

    return redirect('user_assignments')

#___________________________CUSTOMER SUPPORT_____________________________

def customer_support(request):
    context = {}
    if request.method == 'POST':
        form = CustomerSupportForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            if request.user.is_authenticated:
                user = Usuario.objects.get(username=request.user)
                form.user = user
            form.save()

            if 'files_from_validation' in request.POST:
                for archivo in form.files.all():
                    form.files.remove(archivo)
                    # pendiente por eliminar archivos del modelo
                for file in request.POST.getlist('files_from_validation'):
                    form.files.add(Archivo.objects.get(id = file))

            if request.FILES:
                for archivo in form.files.all():
                    form.files.remove(archivo)
                    # pendiente por eliminar archivos del modelo

            for file in request.FILES.getlist('files'):
                if file.size < 10000000:
                    archivo = Archivo.objects.create(nombre=file.name, archivo=file)
                    form.files.add(archivo)

            context['response'] = 'success'
        else:
            print(form.errors)
            context['form'] = form
            if 'files_from_validation' in request.POST:
                files = [ Archivo.objects.get(id=file) for file in request.POST.getlist('files_from_validation') ]
            else:
                files = []
                for file in request.FILES.getlist('files'):
                    if file.size < 10000000:
                        files += [Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file)]
            context['files'] = files
    return render(request, 'home/customer_support.html', context)

#___________________________PAYPAL_____________________________

def payment_test(request): return render(request, 'payment_test.html')

@login_required
def paypal_create(request, id):
    print('Verificando ando...')
    if request.method == 'POST':
        trabajo = Trabajo.objects.get(id=id)
        request_body = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": str(trabajo.precio),
                        "breakdown": {
                            "item_total": {
                                "currency_code": "USD",
                                "value": str(trabajo.precio)
                            },
                        }
                    }
                }
            ]
        }
        order = CreateOrder().create_order(request_body)
        data = order.result.__dict__['_dict']
        return JsonResponse(data)

    return JsonResponse({ 'details': 'invalid request' })

@login_required
def paypal_capture(request, order_id, trabajo_id):
    print('Capturando ando')
    if request.method =="POST":
        trabajo = Trabajo.objects.get(id=trabajo_id)
        data = CaptureOrder().capture_order(order_id)
        order = data.result.__dict__['_dict']
        order_amount = order['purchase_units'][0]['payments']['captures'][0]['amount']['value']
        print('ORDER:', order)

        if Decimal(order_amount) == Decimal(trabajo.precio):
            try:
                new_order = Order(
                    orderID = order['id'],
                    trabajo = trabajo,
                    user = trabajo.publicador,
                    estado = order['status'],
                    precio_total = Decimal(order['purchase_units'][0]['payments']['captures'][0]['amount']['value']),
                    nombre = order['payer']['name']['given_name'],
                    apellido = order['payer']['name']['surname'],
                    full_name = order['purchase_units'][0]['shipping']['name']['full_name'],
                    capture_status = order['purchase_units'][0]['payments']['captures'][0]['status'],
                    capture_id = order['purchase_units'][0]['payments']['captures'][0]['id'],
                    payer_id = order['payer']['payer_id'],
                    create_time = order['purchase_units'][0]['payments']['captures'][0]['create_time'],
                    email = order['payer']['email_address'],
                    direccion = order['purchase_units'][0]['shipping']['address']['address_line_1'] + ', ' + order['purchase_units'][0]['shipping']['address']['country_code']
                )
                new_order.save()

                if new_order.estado == 'COMPLETED':
                    trabajo.estado = 'posted'
                    trabajo.save()
                return JsonResponse(order)
            except:
                return JsonResponse({ 
                    'details': "It seems that there was an error with the transaction. It is possible that the charge has been debited from your payment account, if you had any problems please contact us on the Customer Support." 
                })
        else:
            print('EL PRECIO PAGADO NO ES EL MISMO QUE EL DEL TRABAJO!!! PILAS WEY')
            print(Decimal(order_amount), Decimal(trabajo.precio))

    return JsonResponse({ 
        'details': "It seems that there was an error with the transaction. It is possible that the charge has been debited from your payment account, if you had any problems please contact us on the Customer Support." 
    })

class PayPalClient:
    def __init__(self):
        # Sandbox
        # self.client_id = "AWLMBI3BwXhtXFpMZw-BnZLMvw3NjS_52qMjdQPx-e7Oe7Q7_x33nyg4EXcMHVu9ZhdNw_0CNfpgOR2M"
        # self.client_secret = "EIAR_G5gIaS2A2ZDWATudaRzTooP_kkP8PTN4GP11v8RgQfhSiIEiRJNK-k-oESr2lf4cixIp6Tuudci"
        # Live
        self.client_id = "AUfE4lMYpalZDXKaXrU-OBU3EpQkEqK8TlpiYplZ3mdJAjtaeSkrt1iktz0GFlMgdPKviucsr5F8BD0G"
        self.client_secret = "EBGppM5pfBWp-VsvUWeV72-vQUNbvReUimfmPmYfzsqoWM8QpR-gUSTVHythyaXv8B--2ghja28Gu2xb"

        # self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.environment = LiveEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(self.environment)

class CreateOrder(PayPalClient):

    def create_order(self, request_body):
        request = OrdersCreateRequest()
        request.prefer('return=representation')
        request.request_body(request_body)
        response = self.client.execute(request)

        return response

class GetOrder(PayPalClient):
  
  def get_order(self, order_id):
    request = OrdersGetRequest(order_id)
    response = self.client.execute(request)
    return response

class CaptureOrder(PayPalClient):

  def capture_order(self, order_id):
    request = OrdersCaptureRequest(order_id)
    response = self.client.execute(request)
    return response
