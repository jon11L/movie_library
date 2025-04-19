from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):

    body = forms.CharField(required=True,
                           widget=forms.widgets.Textarea(
                               attrs={
                                "placeholder": "Start a discussion...",
                                "class": "comment-form",
                                "rows": 4,
                                "cols": 40,
                                "style": "resize: none;",
                               }
                           ),
                           label="",
                           )
    
    class Meta:
        model = Comment
        fields = ('body',) 