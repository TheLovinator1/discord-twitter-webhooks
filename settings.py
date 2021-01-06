import os

from dotenv import load_dotenv
from tweepy import OAuthHandler

load_dotenv(verbose=True)

# Environment variables
# https://developer.twitter.com/en/apps
consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

# https://tweeterid.com/ Don't use spaces between commas
users_to_follow = os.environ["USERS_TO_FOLLOW"]

# https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
webhook_url = os.environ["WEBHOOK_URL"]

# Log severity. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG
log_level = os.getenv("LOG_LEVEL", default="INFO")

# Authenticate to the Twitter API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


if __name__ == "__main__":
    print(f"Consumer key: {consumer_key}")
    print(f"Consumer secret: {consumer_secret}")
    print(f"Access Token: {access_token}")
    print(f"Access Token Secret: {access_token_secret}")
    print(f"Users to follow: {users_to_follow}")
    print(f"Webhook url: {webhook_url}")
