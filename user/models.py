from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", )
    # email = models.EmailField(unique=True)
    # password = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    bio = models.TextField(blank=True)


    def __str__(self):
        return self.user.username


    def calculate_age(self):
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


#  once user register first time, take user to complete-profile (complete your profile)

gender = ['male', 'female', 'transgender', '']