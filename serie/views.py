from django.shortcuts import render

# Create your views here.
from .models import Serie


def list_serie(request):
    try:
        if Serie:
            serie = Serie.objects.all()[:5]
            return render(request, 'serie/list_serie.html', {'series': serie})
        else:
            return f'No movies found in the database'
    except Exception as e:
        print(f" error :{e}")


def detail_serie(request, pk):
    ''' get the movie object from the database using the movie_id parameter in the URL request.'''
    serie = Serie.objects.get(id=pk)
    return render(request,'serie/detail_serie.html', {'serie': serie})