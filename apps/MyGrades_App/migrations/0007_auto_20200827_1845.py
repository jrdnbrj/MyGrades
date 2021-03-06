# Generated by Django 3.0.6 on 2020-08-27 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MyGrades_App', '0006_auto_20200707_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trabajo',
            name='archivos',
            field=models.ManyToManyField(blank=True, related_name='archivos', to='MyGrades_App.Archivo'),
        ),
        migrations.AlterField(
            model_name='trabajo',
            name='archivos_trabajador',
            field=models.ManyToManyField(blank=True, related_name='archivos_trabajador', to='MyGrades_App.Archivo'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_editado', models.DateTimeField(auto_now=True)),
                ('trabajo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='MyGrades_App.Usuario')),
            ],
        ),
    ]
