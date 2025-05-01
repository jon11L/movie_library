from django.contrib import admin
from .models import Serie, Season, Episode

# Register your models here.
# admin.site.register(Serie)
# admin.site.register(Season)
# admin.site.register(Episode)



@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "season_number", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "episode_number", "season", "created_at", "updated_at")
    # Note: no prepopulated_fields for episodes by title because we handle slugs manually