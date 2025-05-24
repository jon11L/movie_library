from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"Enter your email"}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter your first name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter your last name'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['last_name'].help_text = '<span class="form-text text-muted text-align:"><small>100 characters max. Letters and /-/ only for First and Last name .</small></span>'

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>(Field required). 150 characters max. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'



class EditProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['date_of_birth', 'phone', 'country', 'city', 'profile_picture', 'bio' ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].label = 'Date of Birth'
        self.fields['date_of_birth'].help_text = '<small>Please use the format YYYY-MM-DD.</small>'

        self.fields['phone'].label = 'Phone Number'
        self.fields['phone'].help_text = '<small>Enter a valid phone number with country code.</small>'

        self.fields['country'].label = 'Country'
        self.fields['country'].help_text = '<small>Your current country of residence.</small>'

        self.fields['city'].label = 'City'
        self.fields['city'].help_text = '<small>Your current city of residence.</small>'

        self.fields['profile_picture'].label = 'Profile Picture'
        self.fields['profile_picture'].help_text = '<small>Upload an image file for your profile.</small>'

        self.fields['bio'].label = 'Bio'
        self.fields['bio'].help_text = '<small>Write a short bio about yourself.</small>'


class UpdateUserForm(forms.ModelForm):
    
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"Enter your email"}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter your first name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Enter your last name'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'}),}

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

        self.fields['last_name'].help_text = '<span class="form-text text-muted text-align:"><small style="color:antiquewhite">100 characters max. Letters and /-/ only for First and Last name .</small></span>'

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small style="color:antiquewhite">(Field required). 150 characters max. Letters, digits and @/./+/-/_ only.</small></span>'
