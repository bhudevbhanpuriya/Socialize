# social_scheduler/tasks.py

from celery import shared_task
from time import sleep
import requests
import logging
import praw
from .utils.reddit_client import get_access_token,schedule_post_to_reddit
from django.db import transaction
from .models import Telegram, Reddit,RedditAccount


@shared_task(bind=True)

def test_func(self):
    for i in range(10):
        sleep(1)
        print(i)
    return 'Done'

logger = logging.getLogger(__name__)


@shared_task
def send_telegram_message(BOT_id,chat_id, message, image_path_or_url=None, tele_id=None):
    bot_token = BOT_id

    success = False

    if image_path_or_url:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "caption": message,
            "parse_mode": "Markdown",
            "photo": image_path_or_url  # URL or direct string from view
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            logger.info(f"Image sent successfully to chat_id={chat_id}")
            success = True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send image to chat_id={chat_id}: {e}")

    else:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            logger.info(f"Text message sent successfully to chat_id={chat_id}")
            success = True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to chat_id={chat_id}: {e}")

    
    if success and tele_id:
        try:
            with transaction.atomic():
                telegram_obj = Telegram.objects.get(id=tele_id)
                telegram_obj.status = "Completed"
                telegram_obj.save()
                logger.info(f"Updated status to Completed for Telegram ID={tele_id}")
        except Telegram.DoesNotExist:
            logger.warning(f"Telegram object with ID={tele_id} does not exist.")
        except Exception as e:
            logger.error(f"Failed to update status for Telegram ID={tele_id}: {e}")
        
    elif not success and tele_id:
        try:
            with transaction.atomic():
                telegram_obj = Telegram.objects.get(id=tele_id)
                telegram_obj.status = "Error"
                telegram_obj.save()
                logger.info(f"Updated status to Error for Telegram ID={tele_id}")
        except Telegram.DoesNotExist:
            logger.warning(f"Telegram object with ID={tele_id} does not exist.")
        except Exception as e:
            logger.error(f"Failed to update status for Telegram ID={tele_id}: {e}")



    return response.json() if success else None






# @shared_task
# def post_to_reddit(username,password,subreddit_name, title, body, reddit_id = None):
#     success = False
#     try:

#         reddit = get_reddit_instance(username,password)
#         subreddit = reddit.subreddit(subreddit_name)
#         subreddit.submit(title, selftext=body)
#         return f"Posted to r/{subreddit_name}: {title}"
#     except Exception as e:
#         print(f"Reddit post failed: {e}")
#     except requests.exceptions.RequestException as e:
#     # This will catch errors in HTTP requests
#         print(f"HTTP error occurred: {e}")
#     except praw.exceptions.PRAWException as e:
#     # This will catch other PRAW exceptions
#         print(f"PRAW error occurred: {e}")


#     # Update Reddit status if succesful
#     if success and reddit_id:
#         try:
#             with transaction.atomic():
#                 reddit_obj = Reddit.objects.get(id=reddit_id)
#                 reddit_obj.status = "Completed"
#                 reddit_obj.save()
#                 print(f"Updated Status to Completed")
#         except Reddit.DoesNotExist:
#             print(f"Telegram Object does not exist.")
#         except Exception as e:
#             print(f"failed to update status for Reddit ID={reddit_id}:{e}")

#     elif not success and reddit_id:
#         try:
#             with transaction.atomic():
#                 reddit_obj = Reddit.objects.get(id=reddit_id)
#                 reddit_obj.status = "Error"
#                 reddit_obj.save()
#                 print(f"Updated Status to Completed")
#         except Reddit.DoesNotExist:
#             print(f"Telegram Object does not exist.")
#         except Exception as e:
#             print(f"failed to update status for Reddit ID={reddit_id}:{e}")

    

# @shared_task

# def post_to_reddit(username,password,subreddit_name, title, body):
#     try:

#         reddit = get_reddit_instance(username,password)
#         subreddit = reddit.subreddit(subreddit_name)
#         subreddit.submit(title, selftext=body)
#         return f"Posted to r/{subreddit_name}: {title}"
#     except Exception as e:
#         print(f"Reddit post failed: {e}")





from celery import shared_task
import requests

@shared_task
def send_photo_from_url():
    bot_token = "7527488282:AAF29ujLQXs3RTeNy2kPv5u6Qmn1pHUpPQ8"  # 🔁 Replace with your actual bot token
    chat_id = "1131413850"        # 🔁 Replace with the target chat ID
    image_url = "http://127.0.0.1:8000/media/photos/IMG20240202221515_oGzHjRr.jpg"  # 🔁 Replace with the actual image URL
    caption = "Here's a cool image from the internet!"

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        data = {
            'chat_id': chat_id,
            'photo': image_url,
            'caption': caption
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        return f"Success: {response.json()}"

    except requests.exceptions.RequestException as e:
        return f"Failed to send image: {str(e)}"
    


@shared_task
def post_for_user(user, subreddit, title, content,image_url, reddit_id=None):
    success = False
    try:

        reddit_account = RedditAccount.objects.get(user=user)
        
        access_token = get_access_token(reddit_account.refresh_token)

        if image_url:
             result = schedule_post_to_reddit(access_token, subreddit, title, kind="link", url = image_url)
             
        else:
            result = schedule_post_to_reddit(access_token, subreddit, title, kind="self", text=content)
            


        
       
        success = True
    except Exception as e:
        print(f"Reddit Post Failed: {e}")


    if success :
        try:
            with transaction.atomic():
                reedit_obj = Reddit.objects.get(id=reddit_id)
                reedit_obj.status = "Completed"
                reedit_obj.save()
                logger.info(f"Updated status to Completed for Reddit ID={reddit_id}")
        except Reddit.DoesNotExist:
            print(f"Reddit Object does not Exist")
        except Exception as e:
            print(f"Failed to update status : {e}")

    

    return result
