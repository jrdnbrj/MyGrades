from django.db import models

# Create your models here.
class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    mail = models.EmailField(max_length=50)
    password = models.CharField(max_length=32)
    celular = models.CharField(max_length=15)

class Archivo(models.Model):
    nombre = models.CharField(max_length=32)
    formato = models.CharField(max_length=32)
    dato = models.FileField(upload_to='', max_length=None)
    tamaño = models.DecimalField(decimal_places = 2, max_digits = 5)

class Trabajo(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    publicador = models.ForeignKey(Usuario, null=True, on_delete=SET_NULL)
    fecha_publicacion = models.DateField( auto_now=False, auto_now_add=False)
    fecha_expiracion = models.DateField( auto_now=False, auto_now_add=False)
    fecha_asignacion_trabajador = models.DateField( auto_now=False, auto_now_add=False)
    fecha_entrega = models.DateField( auto_now=False, auto_now_add=False)
    estado = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=100)
    archivos = models.ManyToManyField(Archivo)
    trabajador = models.ForeignKey(Usuario, null=True, on_delete=SET_NULL)
    precio = models.DecimalField(decimal_places = 2, max_digits = 5)