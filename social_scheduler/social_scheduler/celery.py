# myproject/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_scheduler.settings')

app = Celery('social_scheduler')
app.conf.enable_utc = False


app.conf.update(timezone= 'Asia/Kolkata')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object(settings, namespace='CELERY')

# Load task modules from all registered Django app configs.

# Celery Beat Settings 
app.conf.beat_schedule ={
    'send_tel':{
        'task':'Main.tasks.send_telegram_message',
        'schedule': crontab(hour=2 , minute=45),
        'args': (1131413850, "hello from the other side")
    }


    
}
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
