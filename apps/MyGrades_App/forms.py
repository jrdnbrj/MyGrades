from django.forms import ModelForm, DateTimeField, DateTimeInput
from .models import *

class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

class TrabajoForm(ModelForm):
    fecha_expiracion = DateTimeField( input_formats = ['%Y-%m-%dT%H:%M'], widget = DateTimeInput( attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'))

    class Meta:
        model = Trabajo
        fields = ['titulo', 'area', 'fecha_expiracion', 'descripcion', 'archivos',]