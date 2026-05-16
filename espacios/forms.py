from django import forms
from .models import Espacio, TipoEspacio

class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['codigo', 'nombre', 'tipo', 'capacidad', 'descripcion', 'equipamiento', 'estado', 'foto']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'equipamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Proyector, tablero, aire acondicionado...'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo','').upper().strip()
        if not codigo:
            raise forms.ValidationError('El codigo es obligatorio')
        return codigo
    
    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad and capacidad < 1:
            raise forms.ValidationError('La capacidad debe ser al menos 1')
        if capacidad and capacidad >500:
            raise forms.ValidationError('La capacidada parace demasiado alta. Verifica el valor')
        return capacidad
    
class TipoEspacioForm(forms.ModelForm):
    class Meta:
        model = TipoEspacio
        fields = ['nombre', 'descripcion', 'icono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'icono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-building'}),
        }