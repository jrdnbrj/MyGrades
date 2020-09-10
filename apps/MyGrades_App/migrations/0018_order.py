# Generated by Django 3.1 on 2020-09-10 04:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MyGrades_App', '0017_delete_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('orderID', models.CharField(max_length=150)),
                ('estado', models.CharField(max_length=150)),
                ('precio_total', models.DecimalField(decimal_places=2, max_digits=5)),
                ('nombre', models.CharField(max_length=150)),
                ('apellido', models.CharField(max_length=150)),
                ('full_name', models.CharField(max_length=250)),
                ('capture_status', models.CharField(max_length=150)),
                ('payer_id', models.CharField(max_length=30)),
                ('create_time', models.CharField(max_length=150)),
                ('email', models.CharField(max_length=150)),
                ('direccion', models.CharField(max_length=150)),
                ('fecha_editado', models.DateTimeField(auto_now=True)),
                ('trabajo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='MyGrades_App.trabajo')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='MyGrades_App.usuario')),
            ],
        ),
    ]
