# Generated by Django 3.1 on 2020-09-04 01:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MyGrades_App', '0009_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usuario',
            options={},
        ),
        migrations.AlterField(
            model_name='trabajo',
            name='descripcion',
            field=models.TextField(max_length=5000),
        ),
        migrations.CreateModel(
            name='CustomerSupport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='sent', max_length=10)),
                ('title', models.CharField(max_length=60)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=25, null=True)),
                ('description', models.TextField(max_length=5000)),
                ('files', models.ManyToManyField(blank=True, to='MyGrades_App.Archivo')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='MyGrades_App.usuario')),
            ],
        ),
    ]