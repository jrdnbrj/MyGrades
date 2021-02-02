from django.contrib import admin
from .models import *

# Register your models here.

def download_csv(modeladmin, request, queryset):
    import csv
    f = open('homework.csv', 'wb')
    writer = csv.writer(f)
    writer.writerow(["username", "username", "password", "celular", "key_words", "info_about"])
    for s in queryset:
        writer.writerow([s.username, s.username, s.password, s.celular, s.key_words, s.info_about])

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'mail')
    actions = [download_csv]

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
