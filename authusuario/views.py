#importar los modelos del usuario y los formularios para registros
from .models import Perfil
from .forms import new_profile

from django.shortcuts import render, redirect

#Para mostrar mensajes de error
from django.contrib import messages
#Para verificar que la URL a redireccionar sea segura
from django.utils.http import is_safe_url

#Para manejar la información de los usuarios
from django.core.validators import validate_email #valida que el formato de email sea correcto
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

#Función que verifica si la redirección es aceptada, en caso contrario devolver a "home"
def check_redirect(request, next):
    if next and is_safe_url(url=next, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next)
    return redirect('home')

#Iniciar sesión
def login(request):
    #Si la sesión ya está iniciada abortar
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        valuenext= request.POST.get('next') #En caso que una página haya requerido inicio de sesión antes de continuar
        
        context={'is_error':False, 'data':request.POST, 'valuenext':valuenext}
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        remember_me=request.POST.get('remember-me',False)

        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            if user is not None:
                do_login(request, user)
                if not remember_me: #si la check-box no esta marcada ejecuta
                    request.session.set_expiry(0) #la sesion finaliza al cerrar el navegador
                return check_redirect(request, valuenext) #si detecta el valor /next/ para ir a otra pagina despues de logearse

            else:
                context['is_error']=True
        else:
            context['is_error']=True

        if context['is_error']:
            messages.add_message(request, messages.ERROR, 'Usuario o contraseña incorrecta.')
            return redirect("/login/"+"?next="+valuenext) #regresa la direccion con 'next'
    return render(request,'user/login.html')

#Cerrar sesión
def logout(request):
    if request.user.is_authenticated:
        do_logout(request)
    return redirect('home')
    
#Crear usuario
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    #Envía al formulario al cargar la página
    if request.method == "GET":
        context = {'form' : new_profile()}
    #Pide el formulario al usuario
    elif request.method=="POST":
        form = new_profile(request.POST) #Carga los campos del form en el HTML
        if form.is_valid():
            form=form.clean()
        context={'is_error':False, 'form':form}

        name = form['nombre']#request.POST.get('username').lower()
        lastname = form['apellido']
        email = form['email']
        fecha_nacimiento = form['fecha_nacimiento']
        rol = form['rol']
        password = form['password']
        repeat_password = form['repeat_password']

        if not name or not lastname or not email or not fecha_nacimiento or not rol or not password  or not repeat_password:
            messages.add_message(request, messages.ERROR, 'Complete todos los campos requeridos')
            context['is_error']=True

        if User.objects.filter(username=email).exists():
            messages.add_message(request, messages.ERROR, 'Ya hay una cuenta con este correo electrónico')
            context['is_error']=True

        if email:
            try:
                validate_email(email)
            except:
                messages.add_message(request, messages.ERROR, 'Ingrese un correo electrónico válido')
                context['is_error']=True

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR, 'El correo electrónico ya está registrado')
            context['is_error']=True

        if len(password)<8:
            messages.add_message(request, messages.ERROR, 'La contraseña debe tener más de 8 carácteres')
            context['is_error']=True

        if password!=repeat_password:
            messages.add_message(request, messages.ERROR, 'La contraseña no coincide')
            context['is_error']=True

        if context['is_error']:
            return render(request,'user/register.html',context) #si hay error devuelve a la pagina 'register' pero con los campos guardados

        user=User.objects.create_user(username=email,email=email,password=password)
        profile=Perfil(
            usuario=user,
            email=email,
            nombre=name,
            apellido=lastname,
            fecha_nacimiento=fecha_nacimiento,
            rol=rol)
        profile.save()
        return redirect('login')

    return render(request,'user/register.html', context)