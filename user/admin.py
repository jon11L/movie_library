from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile

# unregister Group (not needed at the moment)
admin.site.unregister(Group)
admin.site.unregister(User)

# Mix profile info into the User info
class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('username', 'email', 'is_staff')
    # fields = ['username']
    inlines = [ProfileInline]


# re register the USer edited for admin display
admin.site.register(User, UserAdmin)
admin.site.register(Profile)

