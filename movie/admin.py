from django.contrib import admin
from .models import Movie

# Register your models here.
admin.site.register(Movie)

# @admin.register(Movie)
# class MovieAdmin(admin.ModelAdmin):
#     list_display = ('title', 'release_date', 'rating')
#     list_filter = ('rating',)