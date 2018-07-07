#!/usr/bin/env python3

import json
import re

import tweepy
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

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
print("We are following: ")
for twitter_id in config.users_to_follow:
    username = api.get_user(twitter_id)
    print(twitter_id + " - " + str(username.screen_name))
print("---------------------------")


class StdOutListener(StreamListener):
    def on_data(self, data):
        tweet = json.loads(data)
        # print("Tweet: " + str(data))
        submitter = str(tweet["user"]["id"])

        if submitter in config.users_to_follow:
            # print("First step - User: " + str(submitter))
            # Check if the tweet if retweeted or starts with "RT @"
            if not tweet["retweeted"] and 'RT @' not in tweet["text"]:
                # Get content of tweet

                # We want the whole tweet to be posted and not a truncated version
                if tweet["truncated"]:
                    message = tweet["extended_tweet"]["full_text"]
                    print("Truncated - Message: " + message)

                    # Discord makes link previews from URLs, we can hide those with < and > before and after URLs
                    # We do that with regular expression https://t.co/[a-zA-Z0-9]*
                    # \g<0>	- Insert entire match
                    message_cleaned = re.sub(r'https://t.co/[a-zA-Z0-9]*', '<\g<0>>', message, flags=re.MULTILINE)
                    # TODO: re.compile these ^

                    # Make webhook embed
                    embed = Webhook(config.url)

                    # Replace the webhook username with the Twitter username
                    embed.set_username(tweet["user"]["name"])

                    # Change the webhook avatar to the twitter avatar
                    embed.set_avatar(tweet["user"]["profile_image_url_https"])  # TODO: Make this higher quality

                    # Add the tweet but with <URL> that we made earlier
                    embed.set_content(message_cleaned)

                    # Post to channel
                    embed.post()
                else:
                    message = tweet["text"]
                    print("Message: " + message)

                    # Discord makes link previews from URLs, we can hide those with < and > before and after URLs
                    # We do that with regular expression https://t.co/[a-zA-Z0-9]*
                    # \g<0>	- Insert entire match
                    message_cleaned = re.sub(r'https://t.co/[a-zA-Z0-9]*', '<\g<0>>', message, flags=re.MULTILINE)

                    # Make webhook embed
                    embed = Webhook(config.url)

                    # Replace the webhook username with the Twitter username
                    embed.set_username(tweet["user"]["name"])

                    # Change the webhook avatar to the twitter avatar
                    embed.set_avatar(tweet["user"]["profile_image_url_https"])  # TODO: Make this higher quality

                    # Add the tweet but with <URL> that we made earlier
                    embed.set_content(message_cleaned)

                    # Post to channel
                    embed.post()

                    return True
            else:
                return
        else:
            return

    def on_error(self, status_code):
        if status_code == 401:
            print("401 Unauthorized - Missing or incorrect authentication credentials.\n"
                  "Did you fill out the config.py correctly?\n"
                  "Possible reasons: Invalid auth credentials, Time on computer is wrong or too many incorrect logins")

        if status_code == 413:
            print("413 Too long - More follow user IDs are sent than the user is allowed to follow.")

        if status_code == 420:
            print("420 Enhance Your Calm - We are being rate limited.\n"
                  "Possible reasons: Too many login attempts or running too many copies of the same "
                  "application authenticating with the same credentials")
            return False

        if status_code == 500:
            print("500 Internal Server Error - Something is broken.\n"
                  "This is usually a temporary error, for example in a high load situation or if an endpoint is "
                  "temporarily having issues.")

        if status_code == 502:
            print("502 Bad Gateway - Twitter is down, or being upgraded.")

        if status_code == 503:
            print("503 Service Unavailable - A streaming server is temporarily overloaded. Try again later.")

        print("Error: " + str(status_code))


listener = StdOutListener()
stream = Stream(auth, listener)

# Stream all tweets from users chosen in config.py
# Streams are only terminated if the connection is closed, blocking the thread.
# The async parameter makes the stream run on a new thread.
stream.filter(follow=config.users_to_follow, async=True)
