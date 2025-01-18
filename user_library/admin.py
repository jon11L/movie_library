from django.contrib import admin
from .models import WatchList, WatchedMovie, Like

# Register your models here.
admin.site.register(Like)

admin.site.register(WatchList)
admin.site.register(WatchedMovie)