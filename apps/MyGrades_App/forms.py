from django import forms
from .models import *

class UsuarioForm(forms.Form):

    username = forms.CharField(min_length=3, max_length=50)
    mail = forms.EmailField(min_length=5, max_length=50)
    password = forms.CharField(min_length=8, max_length=24)
    password_repeat = forms.CharField(min_length=8, max_length=24)

    def clean_username(self):
        username = self.cleaned_data['username']
        username_taken = Usuario.objects.filter(username=username)
        if username_taken:
            raise forms.ValidationError('Username is already in use.')
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

class TrabajoForm(forms.ModelForm):

    fecha_expiracion = forms.DateTimeField(
        input_formats = ['%Y-%m-%dT%H:%M'],
        widget = forms.DateTimeInput( attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    )

    class Meta:
        model = Trabajo
        fields = ['titulo', 'area', 'fecha_expiracion', 'descripcion', 'archivos',]