from django.contrib import admin
from .models import WatchList, WatchedContent, Like

# Register your models here.
admin.site.register(Like)

admin.site.register(WatchedContent)


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "__str__")
    # search_fields = ("user",)

    list_filter = ("created_at", "updated_at", "status")


# admin.site.register(WatchListAdmin)