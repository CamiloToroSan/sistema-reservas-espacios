from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'dashboard'

@login_required
def temp_inicio(request):
    return render(request, 'base.html')

urlpatterns = [
    path('', temp_inicio, name='inicio'),
]