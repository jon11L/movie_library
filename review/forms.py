from django import forms
from .models import Review

class ReviewForm(forms.Form):
    """
    Form to review a media instance.
        - status: to select the current status of the media (e.g., "Watching", "Completed", etc.).
        - review: to write a textual review of the media.
        - rewatch: to indicate if the user would consider rewatching the media.
        - score: to give a numerical rating to the media (e.g., 1 to 10).
    """
    status = forms.ChoiceField(
        choices=Review.STATUS_CHOICES,
        initial='empty', # to avoid pre-selecting the first choice, and let the user select one.   
        required=False,
        label="status",
        widget=forms.Select(attrs={
            "class": "form-select",
            # "style": "width: 180px;",
            "style": "background-color: black; border: 1px solid #ced4da; border-radius: 0.5em; color: silver; max-width: fit-content;",
            }),
    )

    review = forms.CharField(
        max_length=2000,
        required=False,
        label="review",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Write a review..",
                "class": "review-input-form",
                "rows": 4,
                # "cols": 40,
                "style": "resize: none; padding-left: 0.5rem; padding-top: 0.5rem;", 
            },
        ),
    )

    rewatch = forms.ChoiceField(
        choices=Review.RewatchChoice.choices,
        initial='empty', # to avoid pre-selecting the first choice, and let the user select one.   
        required=False,
        label="status",
        widget=forms.Select(attrs={
            "class": "form-select",
            "style": "background-color: black; border: 1px solid #ced4da; border-radius: 0.5em; color: silver;",
            }),
    )

    score = forms.IntegerField(
        min_value=1,
        max_value=10,
        required=False,
        label="score",
        widget=forms.NumberInput(
            attrs={
                "placeholder": "1 - 10",
                "class": "form-control",
                "style": "background-color: black; border: 1px solid #ced4da; border-radius: 0.5em; color: silver;",
            },
        ),
    )


    class Meta:

        model = Review
        fields = ['status', 'review', 'rewatch', 'score']
