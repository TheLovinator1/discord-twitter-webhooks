#!/usr/bin/env python3
import re

import tweepy
from tweepy import OAuthHandler, Stream

# Import settings from config.py
import config
from discord_hooks import Webhook

# We need to be authenticated to use the Twitter API
auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_token_secret)

# Authenticate to the API
api = tweepy.API(auth)
print("API key belongs to " + api.me().screen_name)

print("---------------------------")
print("Following: ")
for twitter_id in config.users_to_follow:
    username = api.get_user(twitter_id)
    print(twitter_id + " - " + str(username.screen_name))
print("---------------------------")


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_status(self, status):
        print(status)
        try:
            # Skip retweets
            if status.retweeted or "RT @" in status.text:
                return

            # Don't get replies
            if status.in_reply_to_screen_name is not None:
                return

            # Skip PUBG tweets for Xbox
            if "Xbox players: " in status.text:
                return

            # Check if the tweet is extended and get content
            try:
                text = status.extended_tweet["full_text"]
            except AttributeError:
                text = status.text

            print(str(status.user.screen_name) + ": " + str(text))

            # Remove the "_normal.jpg" part in url
            avatar_hd = status.user.profile_image_url_https[:-11]
            extension = status.user.profile_image_url_https[-4:]

            # Discord makes link previews from URLs, we can hide those with < and > before and after URLs
            # We do that with regular expression https://t.co/[a-zA-Z0-9]*
            # \g<0>	- Insert entire match
            text_cleaned = re.sub(r'https://t.co/[a-zA-Z0-9]*', '<\g<0>>', text, flags=re.MULTILINE)

            # Make webhook embed
            embed = Webhook(config.url)

            # Replace the webhook username with the Twitter username
            embed.set_username(status.user.screen_name)

            # Change the webhook avatar to the twitter avatar
            embed.set_avatar(str(avatar_hd) + extension)

            # Message
            embed.set_content(
                    text_cleaned + "\n\n" + "[" + str(status.created_at) + "](https://twitter.com/statuses/"
                    + str(status.id) + ")")

            # Post to channel
            embed.post()
        except Exception as e:
            embed = Webhook(config.error_url)
            embed.set_content("<@126462229892694018> I'm broken again <:PepeHands:461899012136632320> \n" + str(e))

    def on_error(self, status_code):

        if status_code == 420:
            print("420 Enhance Your Calm - We are being rate limited.\n"
                  "Possible reasons: Too many login attempts or running too many copies of the same "
                  "application authenticating with the same credentials")
            return False  # returning False in on_error disconnects the stream

        print("Error: " + str(status_code))

        embed = Webhook(config.error_url)
        embed.set_content("Shits fucked\n" + str(status_code))


listener = MyStreamListener()
stream = Stream(auth, listener)

# Streams are only terminated if the connection is closed, blocking the thread.
# The async parameter makes the stream run on a new thread.
stream.filter(follow=config.users_to_follow, async=True)
