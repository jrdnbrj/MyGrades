# Generated by Django 3.0.7 on 2020-06-26 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyGrades_App', '0002_auto_20200619_0156'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trabajo',
            name='archivo_trabajador',
        ),
        migrations.AddField(
            model_name='trabajo',
            name='archivos_trabajador',
            field=models.ManyToManyField(related_name='archivos_trabajador', to='MyGrades_App.Archivo'),
        ),
        migrations.AlterField(
            model_name='trabajo',
            name='archivos',
            field=models.ManyToManyField(related_name='archivos', to='MyGrades_App.Archivo'),
        ),
    ]
