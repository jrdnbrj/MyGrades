from django.forms import ModelForm
from .models import *

class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

class TrabajoForm(ModelForm):
    class Meta:
        model = Trabajo
        fields = ['titulo', 'area', 'fecha_expiracion', 'descripcion', 'archivos',]