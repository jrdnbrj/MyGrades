# Generated by Django 3.0.6 on 2020-06-03 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MyGrades_App', '0008_delete_cuenta_bancaria'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuenta_Bancaria',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('numero_cuenta', models.CharField(max_length=20)),
                ('nombre_completo', models.CharField(max_length=70)),
                ('numero_cedula', models.CharField(blank=True, max_length=15, null=True)),
                ('nombre_banco', models.CharField(max_length=40)),
                ('tipo_cuenta', models.CharField(max_length=20)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuario', to='MyGrades_App.Usuario')),
            ],
        ),
    ]