from django.contrib import admin
from .models import WatchList, WatchedContent, Like

# Register your models here.
admin.site.register(Like)

admin.site.register(WatchList)
admin.site.register(WatchedContent)