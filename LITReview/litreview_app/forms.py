from .models import Ticket, Review, UserFollows
from django import forms

class TicketForm(forms.ModelForm):
    title = forms.CharField(min_length=2)
    description = forms.CharField(widget=forms.Textarea, required=False)
    image = forms.ImageField(
        label="Télécharger une image",
        required=False,
        widget=forms.FileInput)
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image', 'user']

class ReviewForm(forms.ModelForm):
    """Form for creating reviews"""

    class Meta:
        model = Review
        fields = ['ticket', 'rating', 'headline', 'body', 'user']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'form-check-inline'},
                                        choices=[(0, ' 0'),
                                                 (1, ' 1'),
                                                 (2, ' 2'),
                                                 (3, ' 3'),
                                                 (4, ' 4'),
                                                 (5, ' 5')]),
        }



class UserFollowsForm(forms.ModelForm):
    """Form to follow other user"""
    class Meta:
        model = UserFollows
        fields = ['user', 'followed_user']
        widgets = {
            'followed_user': forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur'})
        }
