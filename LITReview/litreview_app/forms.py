from django.forms import ModelForm
from .models import Ticket, Review, UserFollows
from django import forms
#from django.contrib.auth.models import User

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
    headline = forms.CharField()
    body = forms.CharField(widget=forms.Textarea, required=False)
    rating = forms.IntegerField(widget=forms.RadioSelect(choices=(
        (1, "- 1"),
        (2, "- 2"),
        (3, "- 3"),
        (4, "- 4"),
        (5, "- 5"))))
    class Meta:
        model = Review
        fields = ["headline", "rating", "body"]

class UserFollowsForm(ModelForm):
    user = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder": "Nom d\'utilisateur"}))
    class Meta:
        model = UserFollows
        fields = ['followed_user']
