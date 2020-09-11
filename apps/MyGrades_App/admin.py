from django.contrib import admin
from .models import *

# Register your models here.

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'mail')

class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_pago', 'institucion', 'paypal_email')

class ArchivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'archivo')

class TrabajoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'area', 'publicador', 'estado', 'trabajador', 'precio')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'orderID', 'trabajo', 'estado', 'precio_total')

class CustomerSupportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'email')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Cuenta_Bancaria, CuentaBancariaAdmin)
admin.site.register(Archivo, ArchivoAdmin)
admin.site.register(Trabajo, TrabajoAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(CustomerSupport, CustomerSupportAdmin)
