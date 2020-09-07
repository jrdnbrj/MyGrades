from django.db import models

import json


class Usuario(models.Model):
    id =            models.AutoField(primary_key=True)
    username =      models.CharField(max_length=50, unique=True)
    foto =          models.ImageField(upload_to='', max_length=None, null=True, blank=True)
    mail =          models.EmailField('Email', max_length=50, unique=True)
    password =      models.CharField(max_length=24)
    celular =       models.CharField(max_length=25, null=True, blank=True)
    key_words =     models.CharField(max_length=100, blank=True, default='["", "", ""]')
    info_about =    models.TextField(max_length=2000, blank=True)
    is_active =     models.BooleanField(default=True)
    fecha_editado = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "User"
    
    def __str__(self):
        return self.username
    
    def key_words_list(self):
        return json.loads(self.key_words)
    
    def key_words_comma(self):
        return ', '.join( [kw for kw in json.loads(self.key_words) if kw] )

class Cuenta_Bancaria(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, null=True, on_delete=models.CASCADE, related_name='usuario')
    nombre_institucion = models.CharField(max_length=100)
    tipo_cuenta = models.CharField(max_length=20)
    nombre_apellido = models.CharField(max_length=70)
    cedula_ruc = models.CharField(max_length=15)
    numero_cuenta = models.CharField(max_length=20)

    def __str__(self):
        return self.numero_cuenta

class Archivo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='', max_length=None)

    def __str__(self):
        return self.nombre

class Trabajo(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=60)
    area = models.CharField(max_length=50)
    publicador = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL, related_name='publicador')
    fecha_publicacion = models.DateTimeField(auto_now_add=True, editable=True)
    fecha_expiracion = models.DateTimeField(auto_now_add=False)
    fecha_asignacion_trabajador = models.DateTimeField( auto_now_add=False, null=True, blank=True)
    fecha_entrega = models.DateTimeField( auto_now_add=False, null=True, blank=True)
    estado = models.CharField(max_length=10, default='hidden')
    descripcion = models.TextField(max_length=5000)
    archivos = models.ManyToManyField(Archivo, blank=True, related_name='archivos')
    trabajador = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='trabajador')
    archivos_trabajador = models.ManyToManyField(Archivo, blank=True, related_name='archivos_trabajador')
    precio = models.DecimalField(decimal_places = 2, max_digits = 5, default=0.0)
    fecha_editado = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.titulo

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    orderID = models.CharField(max_length=150)
    trabajo = models.ForeignKey(Trabajo, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=150)
    codigo_estado = models.CharField(max_length=150)
    precio_total = models.DecimalField(decimal_places = 2, max_digits = 5)
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    direccion = models.CharField(max_length=150)
    fecha_editado = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.trabajo.titulo

class CustomerSupport(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='open')
    user = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=60)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=25, null=True, blank=True)
    description = models.TextField(max_length=5000)
    files = models.ManyToManyField(Archivo, blank=True)

    def __str__(self):
        return self.title
