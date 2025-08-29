from django.contrib import admin
from .models import Movie

# Register your models here.
# admin.site.register(Movie)

# @admin.register(Movie)
# class MovieAdmin(admin.ModelAdmin):
#     list_display = ('title', 'release_date', 'rating')
#     list_filter = ('rating',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "original_title", "tmdb_id")
    list_filter = ("created_at", "updated_at", "release_date")