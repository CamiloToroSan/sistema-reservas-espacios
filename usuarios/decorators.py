from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(*roles_permitidos):
    """
    Decorador para vistas basadas en funciones.
    Uso: @rol_requerido('admin', 'operador')
    """
    def decorador(funcion):
        @wraps(funcion)
        def vista_envuelta(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            
            try:
                rol_usuario = request.user.perfil.rol
            except AttributeError:
                messages.error(request, 'No tienes un perfil asignado.')
                return redirect('usuarios:login')
            
            if rol_usuario not in roles_permitidos:
                messages.error(request, 'No tienes permisos para esta acción.')
                return redirect('dashboard:inicio')
            
            return funcion(request, *args, **kwargs)
        return vista_envuelta
    return decorador