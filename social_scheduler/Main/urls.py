from django.contrib import admin
from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static
from .utils import redirect

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path('test',views.test_env,name="test"),

    path("telegram",views.schedule_telegram, name="telegram"),
    # path("reddit",views.trigger_reddit_post, name="reddit"),
    path("telegram_form", views.telegram_create, name="tel_form"),
    path("reddit_form", views.reddit_create, name="red_form"),
    path("user_activity", views.user_activity_view, name="user"),
    # path("photo", views.my_view, name="userefeeffe"),
    path('<int:telegram_id>/edit/',views.telegram_edit, name='telegram_edit'),
    path('<int:telegram_id>/delete/',views.telegram_delete, name='telegram_delete'),
    path('<int:reddit_id>/reddit/edit/',views.reddit_edit, name='reddit_edit'),
    path('<int:reddit_id>/reddit/delete/',views.reddit_delete, name='reddit_delete'),
    path('<int:telegram_id>/telgram/view',views.telegram_view, name='telegram_view'),
     path('<int:reddit_id>/reddit/view',views.reddit_view, name='reddit_view'),
      path('reddit/connect/', redirect.reddit_auth_start, name='reddit_auth_start'),
      path('reddit/callback/', redirect.reddit_callback, name='reddit_callback'),  



]
