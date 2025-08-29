from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from .models import Profile

# unregister Group (not needed at the moment)
admin.site.unregister(Group)

# Mix profile info into the User info
class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "email", "first_name", "last_name")
    search_fields = ("pk", "username", "first_name")
    list_filter = ("date_joined",)

    # fields = ['username']
    inlines = [ProfileInline]


admin.site.unregister(User)
# # re register the USer edited for admin display
admin.site.register(User, UserAdmin)
admin.site.register(Profile)

