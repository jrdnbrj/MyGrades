from django.forms import ModelForm
from .models import *

class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

class ArchivoForm(ModelForm):
    class Meta:
        model = Archivo
        fields = '__all__'

class TrabajoForm(ModelForm):
    class Meta:
        model = Trabajo
        fields = '__all__'