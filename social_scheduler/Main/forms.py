from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Telegram,Reddit





class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username','email', 'password1','password2')



class TelegramForm(forms.ModelForm):
    class Meta:
        model = Telegram
        fields = ('BOT_id','chat_id','photo','content', 'scheduled_time',)
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            })
        }



class RedditForm(forms.ModelForm):
    class Meta:
        model = Reddit
        fields= ('subreddit_name','title','body','photo','scheduled_time')
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            })
        }

        

