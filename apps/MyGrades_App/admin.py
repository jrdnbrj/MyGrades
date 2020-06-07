from django.contrib import admin
from .models import *

# Register your models here.

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'mail')

class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre_completo', 'nombre_banco', 'numero_cuenta')

class TrabajoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'area', 'publicador', 'estado', 'trabajador', 'precio')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Cuenta_Bancaria, CuentaBancariaAdmin)
admin.site.register(Trabajo, TrabajoAdmin)