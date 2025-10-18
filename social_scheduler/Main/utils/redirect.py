
from django.shortcuts import get_object_or_404,redirect
import requests
import urllib.parse
from django.http import HttpResponse
from ..models import Telegram,Reddit,RedditAccount
from ..forms import TelegramForm,RedditForm
from requests.auth import HTTPBasicAuth
from django.conf import settings

client_id = settings.REDDIT_CLIENT_ID
client_secret = settings.REDDIT_CLIENT_SECRET



CLIENT_ID = client_id
REDIRECT_URI = "https://socialize-xjdy.onrender.com/schedule/reddit/callback/"
CLIENT_SECRET = client_secret
SCOPES = "identity submit read"
STATE = "random_secure_token"





def reddit_auth_start(request):
    url = (
        f"https://www.reddit.com/api/v1/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&state={STATE}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&duration=permanent&scope={SCOPES}"
    )
    return redirect(url)





def reddit_callback(request):
  try:
     
        code = request.GET.get("code")
        if not code:
            return HttpResponse("No Code Recieved")

        auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
        headers = {"User-Agent": "script:myapp:v1.0 (by u/Possible_Cry2426)"}

        r = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)

        print("Status Code:", r.status_code)
        print("Response Text:", r.text)
        

        try:
            token_data = r.json()
            print("coverted to JSON")
        except ValueError:
            return HttpResponse("Reddit response was not JSON: " + r.text)
        
        refresh_token = token_data.get("refresh_token")
        access_token = token_data.get("access_token")


        if not refresh_token:
            return HttpResponse("No refresh token received.")
        
        print("working Till Now")


        reddit_username =None

        # Use access token to get username
        try:
            headers = {
            "User-Agent": "web:myapp:v1.0 (by u/Possible_Cry2426)",  # Use your actual Reddit username
            "Authorization": f"bearer {access_token}"
                }  # ← lowercase!
            r2 = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
            print("User Info Status:", r2.status_code)
            print("User Info JSON:", r2.json())
            reddit_username = r2.json().get("name")
            print(reddit_username)
        except Exception as e:
            print("Exception:", str(e))

        if not reddit_username:
            return HttpResponse("Reddit username not found in user info response.")






        RedditAccount.objects.update_or_create(
            user=request.user,
            defaults={"username":reddit_username,"refresh_token": refresh_token, }
        )

        return redirect("red_form")
  except Exception as e:
      return HttpResponse(f"{e}")
        
  
