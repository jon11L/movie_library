from django import forms
from .models import WatchList

class WatchListForm(forms.Form):
    """
    Form to add a media to the watchlist.
    """

    personal_note = forms.CharField(
        max_length=500,
        required=False,
        label="personal_note",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Add a personal note...",
                "class": "watchlist-note-form",
                "id": "id_watchlist_personal_note",
                "rows": 4,
                # "cols": 40,
                "style": "resize: none; padding-left: 0.5rem; padding-top: 0.5rem;", 
            },
        ),
    )

    status = forms.ChoiceField(
        choices=WatchList.Status.choices,
        initial='empty', # to avoid pre-selecting the first choice, and let the user select one.   
        required=False,
        label="status",
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "id_watchlist_status",
            "style": "background-color: black; border: 1px solid #ced4da; border-radius: 0.5em; color: silver;",
        }),
            )

    class Meta:

        model = WatchList
        fields = ['personal_note', 'status']
