from django.db import models
from django.contrib.auth.models import User
from datetime import datetime



# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", )
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    bio = models.TextField(max_length=2000, blank=True)


    def __str__(self):
        return self.user.username


    def render_age(self):
        '''Return user's age.'''
        if self.date_of_birth:
            today = datetime.today().date()
            birthdate = self.date_of_birth

            # handle leap years
            age = today.year - birthdate.year
            if today.month < birthdate.month and today.day < birthdate.day:
                age -= 1

                return age
        else:
            return None
