# Generated by Django 3.1 on 2020-09-07 20:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MyGrades_App', '0014_auto_20200907_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuenta_Bancaria',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_institucion', models.CharField(max_length=100, null=True)),
                ('tipo_cuenta', models.CharField(max_length=20, null=True)),
                ('nombre_apellido', models.CharField(max_length=70, null=True)),
                ('cedula_ruc', models.CharField(max_length=15, null=True)),
                ('numero_cuenta', models.CharField(max_length=20, null=True)),
                ('tipo_pago', models.CharField(max_length=20)),
                ('paypal_email', models.EmailField(max_length=50, null=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuario', to='MyGrades_App.usuario')),
            ],
        ),
    ]
