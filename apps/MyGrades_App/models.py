from django.db import models

# Create your models here.
class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=10)
    mail = models.EmailField(max_length=50)
    password = models.CharField(max_length=32)
    celular = models.CharField(max_length=15)

class Archivo(models.Model):
    nombre = models.CharField(max_length=50)
    formato = models.CharField(max_length=15)
    dato = models.FileField(upload_to='', max_length=None)
    tamaño = models.DecimalField(decimal_places = 3, max_digits = 10)

class Trabajo(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=30)
    area = models.CharField(max_length=50)
    publicador = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL, related_name='publicador')
    fecha_publicacion = models.DateTimeField(auto_now=True)
    fecha_expiracion = models.DateTimeField(auto_now_add=False)
    fecha_asignacion_trabajador = models.DateTimeField( auto_now_add=False, null=True)
    fecha_entrega = models.DateTimeField( auto_now_add=False, null=True)
    estado = models.CharField(max_length=10, default='publicado')
    descripcion = models.TextField(max_length=None)
    archivos = models.FileField(upload_to='', max_length=None, null=True)
    trabajador = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL, related_name='trabajador')
    precio = models.DecimalField(decimal_places = 2, max_digits = 5, null=True)