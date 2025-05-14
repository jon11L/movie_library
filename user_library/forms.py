from django import forms
from .models import WatchedContent, WatchList

class WatchListForm(forms.Form):
    """
    Form to add a movie or serie to the watchlist.
    """

    personal_note = forms.CharField(max_length=500, required=False, label="Personal Note", widget=forms.Textarea(attrs={'placeholder': 'Add a personal note...'}))
    status = forms.ChoiceField(choices=WatchList.Status.choices, required=False, label="Status", widget=forms.Select(attrs={'class': 'form-select'}))


    class Meta:
        
        model = WatchList
        fields = ['personal_note', 'status']


