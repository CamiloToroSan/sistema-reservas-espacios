from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import Espacio, TipoEspacio
from .forms import EspacioForm, TipoEspacioForm
from usuarios.mixins import RolRequeridoMixin

# Create your views here.

# ─── ESPACIOS ───

class EspacioListView(LoginRequiredMixin, ListView):
    model = Espacio
    template_name = 'espacios/lista.html'
    context_object_name = 'espacios'
    paginate_by = 12

    def get_queryset(self):
        queryset = Espacio.objects.select_related('tipo').all()

        busqueda = self.request.GET.get('q', '').strip()
        tipo_id = self.request.GET.get('tipo')
        estado = self.request.GET.get('estado')

        if busqueda:
            queryset = queryset.filter(nombre__icontains=busqueda)
        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = TipoEspacio.objects.all()
        context['busqueda'] = self.request.GET.get('q', '')
        context['tipo_seleccionado'] = self.request.GET.get('tipo', '')
        context['estado_seleccionado'] = self.request.GET.get('estado', '')
        return context
    
class EspacioDetailView(LoginRequiredMixin, DetailView):
    model = Espacio
    template_name = 'espacios/detalle.html'
    context_object_name = 'espacio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservas_recientes'] = self.object.reservas.select_related('usuario').order_by('-fecha', '-hora_inicio')[:5]
        return context 
    
class EspacioCreateView(LoginRequiredMixin, RolRequeridoMixin, SuccessMessageMixin, CreateView):
    model = Espacio
    form_class = EspacioForm
    template_name = 'espacios/formulario.html'
    success_url = reverse_lazy('espacios:lista')
    success_message = 'Espacio creado correctamente.'
    roles_permitidos = ['admin', 'operador']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo espacio'
        context['accion'] = 'Crear'
        return context
    
class EspacioUpdateView(LoginRequiredMixin, RolRequeridoMixin, SuccessMessageMixin, UpdateView):
    model = Espacio
    form_class = EspacioForm
    template_name = 'espacios/formulario.html'
    success_url = reverse_lazy('espacios:lista')
    success_message = 'Espacio actualizado correctamente.'
    roles_permitidos = ['admin', 'operador']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar espacio'
        context['accion'] = 'Actualizar'
        return context
    
class EspacioDeleteView(LoginRequiredMixin, RolRequeridoMixin, DeleteView):
    model = Espacio
    template_name = 'espacios/eliminar.html'
    success_url = reverse_lazy('espacios:lista')
    roles_permitidos = ['admin']

# ─── TIPOS ───

class TipoEspacioListView(LoginRequiredMixin, RolRequeridoMixin, ListView):
    model = TipoEspacio
    template_name = 'espacios/tipos_lista.html'
    context_object_name = 'tipos'
    roles_permitidos = ['admin']


class TipoEspacioCreateView(LoginRequiredMixin, RolRequeridoMixin, SuccessMessageMixin, CreateView):
    model = TipoEspacio
    form_class = TipoEspacioForm
    template_name = 'espacios/tipo_formulario.html'
    success_url = reverse_lazy('espacios:tipos_lista')
    success_message = 'Tipo creado correctamente.'
    roles_permitidos = ['admin']
