from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.urls import reverse

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersGetRequest, OrdersCaptureRequest

import datetime
import base64
import sys
import json

from .forms import *
from .models import *


def handler404(request, *args, **argv):
    return render(request, 'error/404.html')

def handler500(request, *args, **argv):
    return render(request, 'error/500.html')

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

@login_required
def signout(request):
    logout(request)
    return redirect('landing_page')

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

            return redirect('post_assignment_payment', trabajo=trabajo.titulo)
        else:
            print(form.errors)
            context['form'] = form
            if 'files_from_validation' in request.POST:
                files = [ Archivo.objects.get(id=file) for file in request.POST.getlist('files_from_validation') ]
            else:
                files = []
                for file in request.FILES.getlist('archivos'):
                    if file.size < 10000000:
                        files += Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file)
                # files = [ Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file) for file in request.FILES.getlist('archivos') ]
            context['files'] = files
            
    return render(request, 'post/post_assignment.html', context)

@login_required
def post_assignment_payment(request, trabajo):

    if request.method == 'POST':
        # validar si el pago se efectuo con exito
        print('Trabajo ID:', trabajo)
        trabajo = Trabajo.objects.get(id=trabajo)
        trabajo.estado = 'published'
        trabajo.save()
        return redirect('post_assignment_complete', trabajo=trabajo.id)
    else:
        # validar si el trabajo ya ha sido pagado o no
        print('Trabajo:', trabajo)
        trabajo = Trabajo.objects.get(Q(titulo=trabajo), Q(publicador__username=request.user))
        context = { 'precio': trabajo.precio, 'trabajo_id': trabajo.id }
        return render(request, 'post/post_assignment_payment.html', context)
    # return render(request, 'post/post_assignment_payment.html', context)

@login_required
def post_assignment_complete(request, trabajo):
    trabajo = Trabajo.objects.get(id=trabajo)
    return render(request, 'post/post_assignment_complete.html', { 'trabajo': trabajo })

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
    context = { 'title': 'Edit' }
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

            return redirect('post_assignment_payment', trabajo=trabajo.titulo)
        else:
            print(form.errors)
            context['form'] = form
            print(request.POST)
            if 'files_from_validation' in request.POST:
                files = [ Archivo.objects.get(id=file) for file in request.POST.getlist('files_from_validation') ]
            else:
                files = []
                for file in request.FILES.getlist('archivos'):
                    if file.size < 10000000:
                        files += Archivo.objects.create(nombre=file.name.replace('(', '').replace(')', ''), archivo=file)
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

#___________________________PAYPAL_____________________________

def verificar_pago(request):
    pass

def pago(request):
    trabajo = Trabajo.objects.get(pk=43)
    data = json.loads(request.body)
    order_id = data['orderID']
    
    detalle = GetOrder().get_order(order_id)
    detalle_precio = float(detalle.result.purchase_units[0].amount.value)
    print('detalle', detalle, detalle_precio)

    trx = CaptureOrder().capture_order(order_id, debug=True)
    # print('???????????????', detalle_precio == float(trabajo.precio), detalle_precio, float(trabajo.precio))
    if detalle_precio == float(trabajo.precio):
        order = Order(
            orderID = trx.result.id,
            trabajo = trabajo,
            estado = trx.result.status,
            codigo_estado = trx.status_code, 
            precio_total = trx.result.purchase_units[0].payments.captures[0].amount.value,
            nombre = trx.result.payer.name.given_name,
            apellido = trx.result.payer.name.surname,
            email = trx.result.payer.email_address,
            direccion = trx.result.purchase_units[0].shipping.address.address_line_1
        )
        order.save()

        data = {
            'id': f"{trx.result.id}",
            'nombre': f"{trx.result.payer.name.given_name}",
            'success': True,
            'message': "Succesful Transaction"
        }

        return JsonResponse(data)
    else:
        data = {
            'id': f"{trx.result.id}",
            'nombre': trx.result.payer.name.given_name,
            'success': False,
            'message': "Wrong Transaction"
        }
        return JsonResponse(data)


class PayPalClient:
    def __init__(self):
        self.client_id = "AWLMBI3BwXhtXFpMZw-BnZLMvw3NjS_52qMjdQPx-e7Oe7Q7_x33nyg4EXcMHVu9ZhdNw_0CNfpgOR2M"
        self.client_secret = "EIAR_G5gIaS2A2ZDWATudaRzTooP_kkP8PTN4GP11v8RgQfhSiIEiRJNK-k-oESr2lf4cixIp6Tuudci"

        """Set up and return PayPal Python SDK environment with PayPal access credentials.
           This sample uses SandboxEnvironment. In production, use LiveEnvironment."""

        self.environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)

        """ Returns PayPal HTTP client instance with environment that has access
            credentials context. Use this instance to invoke PayPal APIs, provided the
            credentials have access. """
        self.client = PayPalHttpClient(self.environment)

    def object_to_json(self, json_data):
        """
        Function to print all json data in an organized readable manner
        """
        result = {}
        if sys.version_info[0] < 3:
            itr = json_data.__dict__.iteritems()
        else:
            itr = json_data.__dict__.items()
        for key,value in itr:
            # Skip internal attributes.
            if key.startswith("__"):
                continue
            result[key] = self.array_to_json_array(value) if isinstance(value, list) else\
                        self.object_to_json(value) if not self.is_primittive(value) else\
                         value
        return result
    def array_to_json_array(self, json_array):
        result =[]
        if isinstance(json_array, list):
            for item in json_array:
                result.append(self.object_to_json(item) if  not self.is_primittive(item) \
                              else self.array_to_json_array(item) if isinstance(item, list) else item)
        return result

    def is_primittive(self, data):
        return isinstance(data, str) or isinstance(data, unicode) or isinstance(data, int)

class CreateOrder(PayPalClient):

    #2. Set up your server to receive a call from the client
    """ This is the sample function to create an order. It uses the
        JSON body returned by buildRequestBody() to create an order."""

    def create_order(self, debug=False):
        request = OrdersCreateRequest()
        request.prefer('return=representation')
        #3. Call PayPal to set up a transaction
        request.request_body(self.build_request_body())
        response = self.client.execute(request)
        if debug:
            print ('Status Code: ', response.status_code)
            print ('Status: ', response.result.status)
            print ('Order ID: ', response.result.id)
            print ('Intent: ', response.result.intent)
            print ('Links:')
        for link in response.result.links:
            print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
        print ('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                            response.result.purchase_units[0].amount.value))

        return response

        """Setting up the JSON request body for creating the order. Set the intent in the
        request body to "CAPTURE" for capture intent flow."""
    @staticmethod
    def build_request_body():
        """Method to create body with CAPTURE intent"""
        return {
            "intent": "CAPTURE",
            "application_context": {
                "brand_name": "EXAMPLE INC",
                "landing_page": "BILLING",
                "shipping_preference": "SET_PROVIDED_ADDRESS",
                "user_action": "CONTINUE"
            },
            "purchase_units": [
                {
                    "reference_id": "PUHF",
                    "description": "Sporting Goods",

                    "custom_id": "CUST-HighFashions",
                    "soft_descriptor": "HighFashions",
                    "amount": {
                        "currency_code": "USD",
                        "value": "230.00",
                        "breakdown": {
                            "item_total": {
                                "currency_code": "USD",
                                "value": "180.00"
                            },
                            "shipping": {
                                "currency_code": "USD",
                                "value": "30.00"
                            },
                            "handling": {
                                "currency_code": "USD",
                                "value": "10.00"
                            },
                            "tax_total": {
                                "currency_code": "USD",
                                "value": "20.00"
                            },
                            "shipping_discount": {
                                "currency_code": "USD",
                                "value": "10"
                            }
                        }
                        },
                        "items": [
                        {
                            "name": "T-Shirt",
                            "description": "Green XL",
                            "sku": "sku01",
                            "unit_amount": {
                                "currency_code": "USD",
                                "value": "90.00"
                            },
                            "tax": {
                                "currency_code": "USD",
                                "value": "10.00"
                            },
                            "quantity": "1",
                            "category": "PHYSICAL_GOODS"
                        },
                        {
                            "name": "Shoes",
                            "description": "Running, Size 10.5",
                            "sku": "sku02",
                            "unit_amount": {
                                "currency_code": "USD",
                                "value": "45.00"
                            },
                            "tax": {
                                "currency_code": "USD",
                                "value": "5.00"
                            },
                            "quantity": "2",
                            "category": "PHYSICAL_GOODS"
                        }
                        ],
                        "shipping": {
                        "method": "United States Postal Service",
                        "address": {
                            "name": {
                                "full_name":"John",
                                "surname":"Doe"
                            },
                            "address_line_1": "123 Townsend St",
                            "address_line_2": "Floor 6",
                            "admin_area_2": "San Francisco",
                            "admin_area_1": "CA",
                            "postal_code": "94107",
                            "country_code": "US"
                        }
                    }
                }
            ]
        }

class GetOrder(PayPalClient):

  #2. Set up your server to receive a call from the client
  """You can use this function to retrieve an order by passing order ID as an argument"""   
  def get_order(self, order_id):
    """Method to get order"""
    request = OrdersGetRequest(order_id)
    #3. Call PayPal to get the transaction
    response = self.client.execute(request)
    #4. Save the transaction in your database. Implement logic to save transaction to your database for future reference.
    print ('Status Code: ', response.status_code)
    print ('Status: ', response.result.status)
    print ('Order ID: ', response.result.id)
    print ('Intent: ', response.result.intent)
    print ('Links:')
    for link in response.result.links:
        print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
    print ('Gross Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code, response.result.purchase_units[0].amount.value))
    return response

class CaptureOrder(PayPalClient):

  #2. Set up your server to receive a call from the client
  """this sample function performs payment capture on the order.
  Approved order ID should be passed as an argument to this function"""

  def capture_order(self, order_id, debug=False):
    """Method to capture order using order_id"""
    request = OrdersCaptureRequest(order_id)
    #3. Call PayPal to capture an order
    response = self.client.execute(request)
    #4. Save the capture ID to your database. Implement logic to save capture to your database for future reference.
    if debug:
        print ('Status Code: ', response.status_code)
        print ('Status: ', response.result.status)
        print ('Order ID: ', response.result.id)
        print ('Links: ')
        for link in response.result.links:
            print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
        print ('Capture Ids: ')
        for purchase_unit in response.result.purchase_units:
            for capture in purchase_unit.payments.captures:
                print ('\t', capture.id)
        print ("Buyer:")
        # print ("\tEmail Address: {}\n\tName: {}\n\tPhone Number: {}".format(response.result.payer.email_address,
        #     response.result.payer.name.given_name + " " + response.result.payer.name.surname,
        #     response.result.payer.phone.phone_number.national_number))
    return response
