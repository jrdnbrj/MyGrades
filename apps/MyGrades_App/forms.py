from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from .models import *

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
            raise forms.ValidationError('The email already belongs to an account')
        return mail
    
    def clean_username(self):
        username = self.cleaned_data['username']
        username_taken = Usuario.objects.filter(username=username)
        if username_taken:
            raise forms.ValidationError('A user with that username already exists')
        return username

    def clean(self):
        data = super().clean()
        if 'password' in data and 'password_repeat' in data:
            password = data['password']
            password_repeat = data['password_repeat']

            if password != password_repeat:
                raise forms.ValidationError({'password_repeat':'Passwords do not match.'})
        return data

    def save(self, commit=True):
        data = self.cleaned_data
        data.pop('password_repeat')
        usuario = Usuario.objects.create(**data)
        if commit:
            usuario.save()
        return usuario


class EditUserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'mail', 'celular')

    def clean_username(self):
        username = self.cleaned_data['username']
        usuario = User.objects.filter(username=username)
        if usuario and not self.instance.username == username:
            raise forms.ValidationError('User with this Username already exists.')
        return username

class EditUserInfoForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('foto', 'info_about')


class EditPasswordForm(forms.ModelForm):
        
    actual_password = forms.CharField()
    password = forms.CharField(min_length=8, max_length=24)
    confirm_password = forms.CharField()

    class Meta:
        model = Usuario
        fields = ('password',)

    def clean_actual_password(self):
        actual_password_clean = self.cleaned_data['actual_password']
        if not self.instance.check_password(actual_password_clean):
            raise forms.ValidationError('Does not match current password')
        return actual_password_clean
    
    def clean(self):
        data = super().clean()
        if 'password' in data and 'confirm_password' in data:
            new_password = data['password']
            confirm_new_password = data['confirm_password']

            if new_password != confirm_new_password:
                raise forms.ValidationError({'password':'Passwords do not match.'})
        return data

class PostAssignmentForm(forms.Form):

    titulo = forms.CharField(min_length=1, max_length=50)
    area = forms.CharField(min_length=1, max_length=17) # cambiar si se requiere al agregar nuevas áreas
    descripcion = forms.CharField(min_length=0, max_length=2000)
    fecha_expiracion = forms.DateTimeField(
        input_formats = ['%Y-%m-%dT%H:%M'],
        widget = forms.DateTimeInput( attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )

    def clean_fecha_expiracion(self):
        data = self.cleaned_data
        fecha_expiracion = data['fecha_expiracion']
        if timezone.now() >= fecha_expiracion:
            raise forms.ValidationError('The DeadLine must be greater than '+ str(timezone.now()))
        return fecha_expiracion

    def save(self, instance=None, commit=False):
        #instance = super(PostAssignmentForm, self).save(commit=False, *args, **kwargs)
        #print(*args, **kwargs)
        if not instance:
            instance = Trabajo()
        print('instance1:',instance)
        post_assignment = self.cleaned_data
        instance.titulo = post_assignment['titulo']
        instance.area = post_assignment['area']
        instance.descripcion = post_assignment['descripcion']
        instance.fecha_expiracion = post_assignment['fecha_expiracion']
        print('instance2:',instance)
        
        if commit:
            instance.save()
        return instance