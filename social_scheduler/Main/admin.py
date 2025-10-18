from django.contrib import admin
from .models import ScheduledPost
from .models import Telegram,Reddit,RedditAccount

# Register your models here.


@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'platfrom',  'scheduled_time', 'status')


admin.site.register(Telegram)
admin.site.register(Reddit)
admin.site.register(RedditAccount)

