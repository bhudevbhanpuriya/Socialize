# utils/reddit_client.py
import praw
import requests
from requests.auth import HTTPBasicAuth


from django.conf import settings

client_id = settings.REDDIT_CLIENT_ID
client_secret = settings.REDDIT_CLIENT_SECRET


# def get_reddit_instance(username,password,refresh_token):
#     return praw.Reddit(
#         client_id= 'vb_yhocQD_JyCSujpSPXxA',
#         client_secret='moIUVAEWT6EkfsxtnVTwHy-kQI0G4Q',
#         user_agent='script:myapp:v1.0 (by u/{username})',
#         username=username,
#         password=password,
#         refresh_token=refresh_token,
#     )



CLIENT_ID = client_id
REDIRECT_URI = "https://socialize-xjdy.onrender.com/schedule/reddit/callback/"
CLIENT_SECRET = client_secret
SCOPES = "identity submit read"
STATE = "random_secure_token"




def get_access_token(refresh_token):
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        "User-Agent": "web:myapp:v1.0 (by u/Possible_Cry2426)"  # Update to your Reddit bot username
    }

    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
    token_data = response.json()
    return token_data.get("access_token")





def schedule_post_to_reddit(access_token, subreddit, title, kind="self", text=None, url=None):
    headers = {
        "Authorization": f"bearer {access_token}",
        "User-Agent": "web:myapp:v1.0 (by u/yourbotusername)"
    }

    data = {
        "sr": subreddit,
        "title": title,
        "kind": kind,
        "resubmit": True,
        "api_type": "json"
    }

    # Add content depending on the type of post
    if kind == "self" and text:
        data["text"] = text
    elif kind == "link" and url:
        data["url"] = url

    response = requests.post("https://oauth.reddit.com/api/submit", headers=headers, data=data)

    print("Status:", response.status_code)
    print("Text:", response.text)
    
    try:
        return response.json()
    except ValueError:
        print("❌ Could not parse JSON response.")
        return {"error": "Invalid JSON", "status_code": response.status_code, "text": response.text}


# def get_reddit_instance(username,password):
#     return praw.Reddit(
#         client_id= 'HHlb40ez7SZSRw2XE2d1LA',
#         client_secret='4dsDEwlPKL0XTsXBBFjFFpRnrS-Gqg',
#         user_agent='script:myapp:v1.0 (by u/Possible_Cry2426)',
#         username="Possible_Cry2426",
#         password="Ssbcc@2005"
#     )

