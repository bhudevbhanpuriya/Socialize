from django.shortcuts import render
from .forms import UserRegistrationForm
from django.http import HttpResponse
from django.contrib.auth import login
from .utils.cloudinary import upload_image_to_cloudinary
from django_celery_beat.models import PeriodicTask, CrontabSchedule, ClockedSchedule, IntervalSchedule
from django.shortcuts import get_object_or_404,redirect
import json
from .models import Telegram,Reddit,RedditAccount
from .forms import TelegramForm,RedditForm
from django.shortcuts import redirect
from django.utils import timezone   
from Main.tasks import send_photo_from_url
import urllib.parse
import requests

from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    return render(request,"index.html")


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request,user)
            


     

    else:
        form = UserRegistrationForm()

    return render(request,'auth/register.html',{'form':form }
    )







@login_required
def telegram_create(request):
    user = request.user
    tele_entry = Telegram.objects.filter(user=user).last()

    if request.method == 'POST':
        form = TelegramForm(request.POST, request.FILES)
        action = request.POST.get("action")
       
        if form.is_valid():
            tele = form.save(commit=False)
            tele.user = user
            tele.status = "Pending" if action == "schedule" else "Not Scheduled"
            tele.save()

            image_url = request.build_absolute_uri(tele.photo.url) if tele.photo else None

            if action == "schedule":
                clocked_time = tele.scheduled_time
                clocked_schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)
                task_name = f"schedule_telegram_task_{timezone.now().strftime('%Y%m%d%H%M%S')}"

                PeriodicTask.objects.create(
                    clocked=clocked_schedule,
                    name=task_name,
                    task='Main.tasks.send_telegram_message',
                    args=json.dumps([tele.BOT_id,tele.chat_id, tele.content,image_url,tele.id]),
                    one_off=True,
                    enabled=True
                )
                return redirect("user")

            elif action == "preview":

                    return render(request, 'telegram_form.html', {
                        'form': form,
                        'tele_entry': tele  # Pass the unsaved or saved tele object here
                    })

    else:
        form = TelegramForm()

    return render(request, 'telegram_form.html', {'form': form, 'tele_entry': tele_entry})






@login_required
def reddit_create(request):
    user = request.user
    reddit_entry = Reddit.objects.filter(user=user).last()
    reddit_user = RedditAccount.objects.filter(user=user).first()
  

    if request.method == 'POST':
        form = RedditForm(request.POST, request.FILES)
        action = request.POST.get("action")

        if form.is_valid():
            reddit = form.save(commit=False)
            reddit.user = request.user
            reddit.status = "Pending" if action == "schedule" else "Not Scheduled"


            image_file = request.FILES.get('photo')
            if image_file:
                try:
                    result  = upload_image_to_cloudinary(image_file)
                    reddit.photo_url = result
                except Exception as e:
                    print("❌ Cloudinary upload failed:", e)


            reddit.save()

            if action =="schedule":
                clocked_time = reddit.scheduled_time

                    # Create clocked schedule entry
                clocked_schedule, created = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)

                # Unique task name
                task_name = f"schedule_reddit_task_{timezone.now().strftime('%Y%m%d%H%M%S')}"

                # Schedule one-off task
                PeriodicTask.objects.create(
                    clocked=clocked_schedule,
                    name=task_name,
                    task='Main.tasks.post_for_user',
                    args=json.dumps([reddit.user.id, reddit.subreddit_name,reddit.title,reddit.body,reddit.photo_url,reddit.id]),
                    one_off=True,
                    enabled=True
                )

                return redirect("user")
        

            elif action == "preview":
                     return render(request,
                          'reddit_form.html',{
                              'form':form,
                              'reddit_entry':reddit,
                              'reddit_user': reddit_user

                      })
    else:
        form = RedditForm()

    return render(request, 'reddit_form.html', {'form': form,'reddit_entry':reddit_entry,'reddit_user':reddit_user})






# def trigger_reddit_post(request):
#     schedule, created = CrontabSchedule.objects.get_or_create( hour='',minute='')  # runs every minute for testing

#     task_name = f"schedule_reddit_task_{timezone.now().strftime('%Y%m%d%H%M%S')}"  # ensures uniqueness

#     PeriodicTask.objects.create(
#         crontab=schedule,
#         name=task_name,
#         task='Main.tasks.post_to_reddit',
#         args=json.dumps(['test', 'Automated title', 'Hello from Celery']),
#         enabled=True
#     )

#     return HttpResponse("Reddit route is working.")






def schedule_telegram(request):
    schedule,created  = CrontabSchedule.objects.get_or_create(hour = '11', minute = '44')
    task_name = f"schedule_telegram_task_{timezone.now().strftime('%Y%m%d%H%M%S')}"

    task = PeriodicTask.objects.create(
        crontab=schedule ,
        name=task_name,
        task = 'Main.tasks.send_telegram_message',
        args=json.dumps([1131413850, "Scheduled message from Celery!"]),
        enabled=True )
    return HttpResponse("Done")



@login_required
def user_activity_view(request):
    user = request.user
    reddit_username = RedditAccount.objects.filter(user=user).first()

    telegram_posts = Telegram.objects.filter(user=user).exclude(status="Not Scheduled").order_by('-scheduled_time')
    reddit_posts = Reddit.objects.filter(user=user).exclude(status="Not Scheduled").order_by('-scheduled_time')


    context = {
        'telegram_posts': telegram_posts,
        'reddit_posts': reddit_posts,
        'reddit_username': reddit_username
   
    }
    return render(request, 'user_activity.html', context)


@login_required
def telegram_edit(request, telegram_id):
    tele = get_object_or_404(Telegram, pk=telegram_id , user = request.user)
    if request.method == 'POST':
        form = TelegramForm(request.POST, request.FILES, instance=tele)
        if form.is_valid():
            tele = form.save(commit=False)
            tele.user = request.user
            tele.save()
            return redirect('user')

    else:
        form = TelegramForm(instance=tele)
    return render (request, 'telegram_form.html',{'form':form})




@login_required
def telegram_delete(request,telegram_id):
    tele = get_object_or_404(Telegram,pk=telegram_id,user=request.user)
    if request.method == 'POST':
        tele.delete()
        return redirect('user')
    return render (request, 'telegram_delete.html',{'telegram':tele})


from django_celery_beat.models import PeriodicTask, ClockedSchedule
from django.utils import timezone
import json

@login_required
def reddit_edit(request, reddit_id):
    reddit = get_object_or_404(Reddit, pk=reddit_id, user=request.user)
    reddit_user = RedditAccount.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = RedditForm(request.POST, request.FILES, instance=reddit)
        if form.is_valid():
            reddit = form.save(commit=False)
            reddit.user = request.user
            reddit.save()

            # Check if a PeriodicTask exists for this post
            task_name_prefix = f"schedule_reddit_task_"
            tasks = PeriodicTask.objects.filter(name__startswith=task_name_prefix)

            for task in tasks:
                args = json.loads(task.args)
                if reddit.id in args:
                    # Update the existing task's args and clocked time
                    task.args = json.dumps([reddit.user.id, reddit.subreddit_name, reddit.title, reddit.body, reddit.id])

                    # Update clocked schedule if time was changed
                    clocked_time = reddit.scheduled_time
                    clocked_schedule, created = ClockedSchedule.objects.get_or_create(clocked_time=clocked_time)
                    task.clocked = clocked_schedule

                    task.save()

            return redirect('user')

    else:
        form = RedditForm(instance=reddit)

    return render(request, 'reddit_form.html', {'form': form, 'reddit_user': reddit_user})



@login_required
def reddit_delete(request, reddit_id):
    reddit = get_object_or_404(Reddit, pk=reddit_id, user = request.user)
    if request.method == 'POST':
        reddit.delete()
        return redirect('user')
    return render (request, 'reddit_delete.html',{'reddit':reddit, })



@login_required
def telegram_view(request, telegram_id):
    tele = get_object_or_404(Telegram,pk=telegram_id,user = request.user)
    return render (request,'telegram_view.html',{
        "tele":tele

    })






@login_required
def reddit_view(request, reddit_id):
    reddit_username = get_object_or_404(RedditAccount, user=request.user).username
    
    reddit = get_object_or_404(Reddit,pk=reddit_id,user = request.user)
    return render (request,'reddit_view.html',{
        "reddit":reddit,"reddit_username":reddit_username

    })



from django.conf import settings

def test_env(request):
    print("Client ID:", settings.REDDIT_CLIENT_ID)
    print("Client Secret:", settings.REDDIT_CLIENT_SECRET)
    return HttpResponse("Check your terminal or logs.")






















