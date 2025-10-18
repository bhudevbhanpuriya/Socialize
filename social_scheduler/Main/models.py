from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.


class ScheduledPost(models.Model):
    PLATFORM_CHOICES = [
    ('TW','TWITTER'),
    ('TE','TELEGRAM'),
    ('IN','INSTAGRAM')
    ] 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts', blank=True, null=True)
    platfrom = models.CharField(choices=PLATFORM_CHOICES, max_length=2)
    scheduled_time = models.DateTimeField()
    status = models.CharField(default="Pending", max_length=10)

    def __str__(self):
        return f' {self.user.username}'
    

class Telegram(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    BOT_id = models.TextField()
    chat_id = models.TextField()
    content= models.TextField()
    scheduled_time = models.DateTimeField()
    photo  = models.ImageField(upload_to='photos/', blank=True, null=True)
    status = models.CharField(default="Pending", max_length=20)
  


class Reddit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subreddit_name = models.CharField(max_length=20)
    title= models.TextField()
    body = models.TextField(blank=True , null=True)
    photo  = models.ImageField(upload_to='reddit_photos/', blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(default="Pending", max_length=20)




class RedditAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.TextField(default="default_user")
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


