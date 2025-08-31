from django.contrib import admin
from .models import Serie, Season, Episode

# Register your models here.
# admin.site.register(Serie)
# admin.site.register(Season)
# admin.site.register(Episode)

class SeasonInline(admin.StackedInline):
    model = Season


@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "original_title", "slug", "tmdb_id")
    list_filter = ("created_at", "updated_at", "first_air_date")

    inlines = [SeasonInline]


admin.site.unregister(Serie)
# # re register the USer edited for admin display
admin.site.register(Serie, SerieAdmin)

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug", "season_number", "serie", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug", "tmdb_id")


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "episode_number", "season", "created_at", "updated_at")
    search_fields = ("title", "slug", "tmdb_id")

    # Note: no prepopulated_fields for episodes by title because we handle slugs manually