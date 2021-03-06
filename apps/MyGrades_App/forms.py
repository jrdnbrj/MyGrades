from django import forms
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from .models import *

import datetime
import pytz

utc = pytz.UTC


class UsuarioForm(forms.Form):

    username = forms.CharField(min_length=3, max_length=50)
    mail = forms.EmailField(min_length=5, max_length=50)
    celular = forms.CharField(min_length=5, max_length=25, required=False)
    password = forms.CharField(min_length=8, max_length=24)
    password_repeat = forms.CharField(min_length=8, max_length=24)

    def clean_mail(self):
        mail = self.cleaned_data['mail']
        mail_taken = Usuario.objects.filter(mail=mail)

        if mail_taken:
            raise forms.ValidationError('The email already belongs to an account.')

        return mail
    
    def clean_username(self):
        username = self.cleaned_data['username']
        username_taken = Usuario.objects.filter(username=username)

        if username_taken:
            raise forms.ValidationError('A user with that username already exists.')

        return username

    def clean_celular(self):
        celular = self.cleaned_data['celular']

        if celular and not celular.isnumeric():
            raise forms.ValidationError("The input must be a valid phone number. Don't add special characters.")

        return celular

    def clean(self):
        data = super().clean()

        if 'password' in data and 'password_repeat' in data:
            password = data['password']
            password_repeat = data['password_repeat']

            if password != password_repeat:
                raise forms.ValidationError({ 'password_repeat': 'Passwords do not match.' })

        return data

    def save(self, commit=True):
        data = self.cleaned_data
        # data.pop('password')
        data.pop('password_repeat')
        usuario = Usuario.objects.create(**data)

        if commit: usuario.save()

        return usuario


class EditUserForm(forms.ModelForm):
    
    username = forms.CharField(min_length=3, max_length=50)
    mail = forms.EmailField(min_length=5, max_length=50)
    celular = forms.CharField(min_length=5, max_length=25, required=False)

    class Meta:
        model = Usuario
        fields = ('username', 'mail', 'celular')
    
    def clean_celular(self):
        celular = self.cleaned_data['celular']

        if celular and not celular.isnumeric():
            raise forms.ValidationError("The input must be a valid phone number. Don't add special characters.")

        return celular


class EditUserInfoForm(forms.ModelForm):

    class Meta:
        model = Usuario
        fields = ('foto', 'info_about')

class CuentaBancariaForm(forms.ModelForm):

    institucion = forms.CharField(max_length=100)
    tipo_cuenta = forms.CharField(max_length=20)
    nombre_apellido = forms.CharField(max_length=70)
    cedula_ruc = forms.CharField(max_length=15)
    numero_cuenta = forms.CharField(max_length=20)
    tipo_pago = forms.CharField(max_length=20)
    
    class Meta:
        model = Cuenta_Bancaria
        fields = ('institucion', 'tipo_cuenta', 'nombre_apellido', 'cedula_ruc', 'numero_cuenta', 'tipo_pago')

    def save(self, commit=True):

        if self.instance:
            self.instance.paypal_email = ''

            if commit:
                self.instance.save()

            return self.instance
        else:
            instance = Cuenta_Bancaria(**self.cleaned_data)

            if commit:
                instance.save()

            return instance


class PayPalEmailForm(forms.ModelForm):

    tipo_pago = forms.CharField(max_length=20)
    paypal_email = forms.EmailField(max_length=50)

    class Meta:
        model = Cuenta_Bancaria
        fields = ('paypal_email', 'tipo_pago')
    
    def save(self, commit=True):

        if self.instance:
            self.instance.institucion = ''
            self.instance.tipo_cuenta = ''
            self.instance.nombre_apellido = ''
            self.instance.cedula_ruc = ''
            self.instance.numero_cuenta = ''

            if commit:
                self.instance.save()

            return self.instance
        else:
            instance = Cuenta_Bancaria(**self.cleaned_data)

            if commit:
                instance.save()

            return instance

class EditPasswordForm(forms.ModelForm):
        
    actual_password = forms.CharField()
    password = forms.CharField(min_length=8, max_length=24)
    confirm_password = forms.CharField()

    class Meta:
        model = Usuario
        fields = ('password',)

    def clean_actual_password(self):
        actual_password_clean = self.cleaned_data['actual_password']

        if not self.instance.password == actual_password_clean:
            raise forms.ValidationError('Does not match current password.')

        # if not self.instance.check_password(actual_password_clean):
        #     raise forms.ValidationError('Does not match current password.')

        return actual_password_clean
    
    def clean(self):
        data = super().clean()

        if 'password' in data and 'confirm_password' in data:
            new_password = data['password']
            confirm_new_password = data['confirm_password']

            if new_password != confirm_new_password:
                raise forms.ValidationError({ 'password': 'Passwords do not match.' })

        return data


class PostAssignmentForm(forms.Form):

    titulo = forms.CharField(min_length=1, max_length=65)
    area = forms.CharField(min_length=1, max_length=50)
    descripcion = forms.CharField(min_length=0, max_length=10000)
    fecha_expiracion = forms.DateTimeField(
        input_formats = ['%Y-%m-%dT%H:%M'],
        widget = forms.DateTimeInput(attrs={ 'type': 'datetime-local' }, format='%Y-%m-%dT%H:%M')
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.status = kwargs.pop('status', 'hidden')
        
        super(PostAssignmentForm, self).__init__(*args, **kwargs)

        if self.status == 'hidden':
            self.fields['precio'] = forms.DecimalField(max_digits=8, decimal_places=4, min_value=3.00)

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo']
        user = self.user

        trabajo = Trabajo.objects.filter(Q(titulo__iexact=titulo), Q(publicador__username=user))

        if user and trabajo:
            raise forms.ValidationError('You have already created an Assignment with the same title.')

        return titulo

    def clean_fecha_expiracion(self):
        data = self.cleaned_data
        fecha_expiracion = data['fecha_expiracion']
        date_time = datetime.datetime.now()

        if fecha_expiracion <= date_time:
            raise forms.ValidationError('The Dead Line must be greater than '+ str(date_time)[:-10])

        return fecha_expiracion

    def save(self, instance=None, commit=False):
        
        if not instance: instance = Trabajo()
            
        post_assignment = self.cleaned_data
        instance.titulo = post_assignment['titulo']
        instance.area = post_assignment['area']
        instance.descripcion = post_assignment['descripcion']
        instance.fecha_expiracion = post_assignment['fecha_expiracion']
        if instance.estado == 'hidden': instance.precio = post_assignment['precio']
        
        if commit: instance.save()
            
        return instance


class CustomerSupportForm(forms.ModelForm):

    class Meta:
        model = CustomerSupport
        fields = ('title', 'name', 'email', 'phone_number', 'description')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']

        if phone_number and not phone_number.isnumeric():
            raise forms.ValidationError("The input must be a valid phone number. Don't add special characters.")

        return phone_number
