from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import AppUser, Book, Video, Tutorial, PodcastEpisode
from .models import Podcast, Channel


class AppUserCreationForm(UserCreationForm):
    
    class Meta:
        model = AppUser
        fields = ['username']


class AppUserChangeForm(UserChangeForm):
    
    class Meta:
        model = AppUser
        fields = ['email']


class BookCreateForm(forms.ModelForm):
    author = forms.CharField()
    link = forms.URLField()

    class Meta:
        model = Book
        fields = (
            'category',
            'title',
            'description',
            'author',
            'link',
            'tags'
        )


class VideoCreateForm(forms.ModelForm):
    channel = forms.ModelChoiceField(queryset=Channel.objects.all())
    link = forms.URLField()

    class Meta:
        model = Video
        fields = (
            'category',
            'title',
            'description',
            'link',
            'channel',
            'tags'
        )


class TutorialCreateForm(forms.ModelForm):
    author = forms.CharField()
    link = forms.URLField()

    class Meta:
        model = Tutorial
        fields = (
            'category',
            'title',
            'description',
            'channel',
            'link',
            'author',
            'tags'
        )


class PodcastEpisodeCreateForm(forms.ModelForm):
    podcast = forms.ModelChoiceField(queryset=Podcast.objects.all())
    link = forms.URLField()

    class Meta:
        model = PodcastEpisode
        fields = (
            'category',
            'title',
            'description',
            'link',
            'tags',
            'podcast'
        )

