from django.contrib import admin

from .models import Media
# Register your models here.

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "release_date", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("pk", "title", "original_title")
    list_filter = ("created_at", "updated_at", "release_date")