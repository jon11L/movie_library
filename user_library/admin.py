from django.contrib import admin
from .models import WatchList, LikedMovie, LikedSerie, WatchedMovie

# Register your models here.
admin.site.register(LikedMovie)
admin.site.register(LikedSerie)
admin.site.register(WatchList)
admin.site.register(WatchedMovie)