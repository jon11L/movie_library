from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile

# unregister Group (not needed at the moment)
admin.site.unregister(Group)


# Mix profile info into the User info
# class UserMixin(admin.StackedInline):
#     model = Profile

# class UserAdmin(admin.ModelAdmin):
#     model = User
    # inlines = [UserMixin]


# Register your models here.
admin.site.register(Profile)

