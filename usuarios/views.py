from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .forms import LoginForm, RegistroForm, PerfilForm


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:inicio')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido {user.get_full_name() or user.username}')
            return redirect('dashboard:inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:inicio')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('dashboard:inicio')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('usuarios:login')


@login_required
def perfil_view(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user.perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=request.user.perfil)
    
    return render(request, 'usuarios/perfil.html', {'form': form})