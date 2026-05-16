from django.shortcuts import redirect
from django.contrib import messages


class RolRequeridoMixin:
    """
    Mixin para vistas basadas en clases.
    Uso:
        class MiVista(RolRequeridoMixin, CreateView):
            roles_permitidos = ['admin']
    """
    roles_permitidos = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        try:
            rol_usuario = request.user.perfil.rol
        except AttributeError:
            return redirect('usuarios:login')
        
        if rol_usuario not in self.roles_permitidos:
            messages.error(request, 'No tienes permisos para esta acción.')
            return redirect('dashboard:inicio')
        
        return super().dispatch(request, *args, **kwargs)