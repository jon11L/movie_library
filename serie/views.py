from django.shortcuts import render

# Create your views here.
from .models import Serie


def serie_list(request):
    if Serie:
      series = Serie.objects.all()[:5]
    return render(request, 'serie/list_serie.html', {'series': series})