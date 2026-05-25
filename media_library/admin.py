from django.contrib import admin

from .models import Media, Movie, Serie, Season, Episode
# Register your models here.

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "release_date", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("pk", "title", "original_title")
    list_filter = ("created_at", "updated_at", "release_date")


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "release_date", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("pk", "title", "original_title", "tmdb_id")
    list_filter = ("created_at", "updated_at", "release_date")



# Serie part, also connect with season and episode inlines
class SeasonInline(admin.StackedInline):
    model = Season

class EpisodeInline(admin.StackedInline):
    model = Episode


@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("pk", "title", "original_title", "slug", "tmdb_id")
    list_filter = ("created_at", "updated_at", "first_air_date", "last_air_date")

    inlines = [SeasonInline]


admin.site.unregister(Serie)
admin.site.register(Serie, SerieAdmin)

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug", "season_number", "serie", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug", "tmdb_id")

    inlines = [EpisodeInline]

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "tmdb_id","slug", "episode_number", "season", "created_at", "updated_at")
    search_fields = ("title", "slug", "tmdb_id")
