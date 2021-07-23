import os

import tweepy
from dotenv import load_dotenv
from tweepy import OAuthHandler

# Parse the .env file and then load all the variables found as environment variables
load_dotenv(verbose=True)

# Environment variables
# https://developer.twitter.com/en/apps
consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

# https://tweeterid.com/
users_to_follow = os.environ["USERS_TO_FOLLOW"]
user_list_replies_to_our_tweet = os.getenv("USER_LIST_REPLIES_TO_OUR_TWEET")
user_list_replies_to_other_tweet = os.getenv("USER_LIST_REPLIES_TO_OTHERS_TWEET")
user_list_someone_retweets_our_tweet = os.getenv("USER_LIST_SOMEONE_RETWEETS_OUR_TWEET")
user_list_we_retweet_someone_elses_tweet = os.getenv("USER_LIST_WE_RETWEET_SOMEONE_ELSES_TWEET")

# Should we message when a tracked user retweets his own tweet? True or False
get_retweet_of_own_tweet = os.getenv("GET_RETWEET_OF_OWN_TWEET", default="False")

# https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
webhook_url = os.environ["WEBHOOK_URL"]

# Log severity. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG
log_level = os.getenv("LOG_LEVEL", default="INFO")

# Where https://github.com/TheLovinator1/twitter-image-collage-maker is running.
# You can run your own version or use the default https://twitter.lovinator.space/
# The only information I have about you are the images that are generated.
# Nothing (e.g IP address) is connected to those images.
# Email tlovinator@gmail.com or go to https://github.com/TheLovinator1/discord-twitter-webhooks#need-help
# and give me the id of the tweet if you want me to delete the image.
twitter_image_collage_maker = os.getenv("TWITTER_IMAGE_COLLAGE_API", default="https://twitter.lovinator.space/add")

# Authenticate to the Twitter API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

user_list_retweets_split = []
user_list_retweeted_split = []
user_list_replies_to_our_tweet_split = []
user_list_replies_to_other_tweet_split = []

if users_to_follow is not None:
    print("Users - Tweets:")
    user_list = [x.strip() for x in str(users_to_follow).split(",")]
    for twitter_id in user_list:
        username = api.get_user(user_id=twitter_id)
        print(f"\t{twitter_id} - {username.screen_name}")
else:
    print("It looks like USERS_TO_FOLLOW is empty. Did you forget to fill it out?")

if user_list_replies_to_our_tweet is not None:
    print("Users - Comment to us from other:")
    user_list_replies_to_our_tweet_split = [x.strip() for x in str(user_list_replies_to_our_tweet).split(",")]
    for twitter_id in user_list_replies_to_our_tweet_split:
        username_reply = api.get_user(user_id=twitter_id)
        print(f"\t{twitter_id} - {username_reply.screen_name}")
else:
    print("Found no users to get replies from.")

if user_list_replies_to_other_tweet is not None:
    print("Users - Comment from us to other:")
    user_list_replies_to_other_tweet_split = [x.strip() for x in str(user_list_replies_to_other_tweet).split(",")]
    for twitter_id in user_list_replies_to_other_tweet_split:
        username_reply = api.get_user(user_id=twitter_id)
        print(f"\t{twitter_id} - {username_reply.screen_name}")
else:
    print("Found no users to get replies to.")

if user_list_we_retweet_someone_elses_tweet is not None:
    print("Users - We retweet others tweet:")
    user_list_retweets_split = [x.strip() for x in str(user_list_we_retweet_someone_elses_tweet).split(",")]
    for twitter_id in user_list_retweets_split:
        username_reply = api.get_user(user_id=twitter_id)
        print(f"\t{twitter_id} - {username_reply.screen_name}")
else:
    print("Found no users were we track retweets.")

if user_list_someone_retweets_our_tweet is not None:
    print("Users - Other retweets our tweet:")
    user_list_retweeted_split = [x.strip() for x in str(user_list_someone_retweets_our_tweet).split(",")]
    for twitter_id in user_list_retweeted_split:
        username_reply = api.get_user(user_id=twitter_id)
        print(f"\t{twitter_id} - {username_reply.screen_name}")
else:
    print("Found no users were we track tweets that get retweeted.")


if __name__ == "__main__":
    print(f"Consumer key: {consumer_key}")
    print(f"Consumer secret: {consumer_secret}")
    print(f"Access Token: {access_token}")
    print(f"Access Token Secret: {access_token_secret}")
    print(f"Users to follow - tweets: {users_to_follow}")
    print(f"Users to follow - replies to our: {user_list_replies_to_our_tweet}")
    print(f"Users to follow - replies to others: {user_list_replies_to_our_tweet}")
    print(f"Users to follow - retweets: {user_list_we_retweet_someone_elses_tweet}")
    print(f"Users to follow - retweeted: {user_list_someone_retweets_our_tweet}")
    print(f"Get self retweets: {get_retweet_of_own_tweet}")
    print(f"Webhook url: {webhook_url}")
    print(f"Twitter collage maker: {twitter_image_collage_maker}")
