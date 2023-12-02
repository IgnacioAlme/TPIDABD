# Generated by Django 4.2.6 on 2023-12-01 02:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Permisos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': [('es_usuario_admin', 'Acceso a herramientas del sitio')],
            },
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.CharField(default='email@email.com', max_length=50)),
                ('nombre', models.CharField(default='Nombre', max_length=50)),
                ('apellido', models.CharField(default='Apellido', max_length=50)),
                ('fecha_nacimiento', models.DateField()),
                ('rol', models.CharField(choices=[('Cliente', 'Cliente'), ('Conductor', 'Conductor'), ('Admin', 'Admin')], default='Cliente', max_length=30)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]