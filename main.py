#!/usr/bin/env python3
import logging.config
import os
import re
import sys
from configparser import ConfigParser

import tweepy
from dhooks import Embed, Webhook
from tweepy import OAuthHandler, Stream

# TODO: Fix gifs
# TODO: Fix polls

config = ConfigParser()

config["discord"] = {
    "webhook_url": "webhook_url",
    "webhook_error_url": "webhook_error_url",
}

config["twitter"] = {
    "consumer_key": "consumer_key",
    "consumer_secret": "consumer_secret",
    "access_token": "access_token",
    "access_token_secret": "access_token_secret",
    "users_to_follow": "user1, user2, user3",
}

config["logging"] = {
    "log_level": "INFO",
    "log_to_file": False,
    "log_level_file": "INFO",
    "log_name": "log.txt",
    "sensitive_logs": False
}

# Check if config file exists before creating one
if not os.path.isfile("config.ini"):
    with open("config.ini", "w") as f:
        config.write(f)

parser = ConfigParser()
parser.read("config.ini")

if parser.get("discord", "webhook_url") == "webhook_url":
    print("Please fill out the config file!")
    sys.exit(0)

webhook_url = parser.get("discord", "webhook_url")
webhook_error_url = parser.get("discord", "webhook_error_url")

consumer_key = parser.get("twitter", "consumer_key")
consumer_secret = parser.get("twitter", "consumer_secret")
access_token = parser.get("twitter", "access_token")
access_token_secret = parser.get("twitter", "access_token_secret")

users_to_follow = parser.get("twitter", "users_to_follow")
user_list = [x.strip() for x in users_to_follow.split(',')]

log_level_file = parser.get("logging", "log_level_file")
log_level = parser.get("logging", "log_level")
log_name = parser.get("logging", "log_name")
sensitive_logs = parser.get("logging", "sensitive_logs")

# Logger
formatter = logging.Formatter('%(asctime)s %(levelname)-12s %(message)s')
logger = logging.getLogger()
handler = logging.StreamHandler()

# Log to file
if parser.getboolean("logging", "log_to_file"):
    file_handler = logging.FileHandler(parser.get("logging", "log_name"))
    level = logging.getLevelName(log_level_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Log to console
handler.setFormatter(formatter)
logger.addHandler(handler)

# CRITICAL, ERROR, WARNING, INFO, DEBUG
level = logging.getLevelName(log_level)
logger.setLevel(level)

# We need to be authenticated to use the Twitter API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Authenticate to the API
api = tweepy.API(auth)
logger.info("API key belongs to " + api.me().screen_name)

# TODO: Fix this
# if parser.getboolean("logging", "sensitive_logs"):
#     config_keys = [webhook_url,
#                    webhook_error_url,
#                    consumer_key,
#                    consumer_secret,
#                    access_token,
#                    access_token_secret,
#                    users_to_follow]
#
#     for key in range(len(config_keys)):
#         logger.debug(key)

# Print users we follow
for twitter_id in user_list:
    username = api.get_user(twitter_id)
    print(twitter_id + " - " + str(username.screen_name))


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_status(self, tweet):
        link_list = []
        try:
            logger.debug("Raw tweet: " + str(tweet))
            # Skip retweets
            if tweet.retweeted or "RT @" in tweet.text:
                # logger.debug("Tweet is retweet")
                return

            # Don't get replies
            if tweet.in_reply_to_screen_name is not None:
                # logger.debug("Tweet is reply")
                return

            # Skip PUBG tweets for Xbox
            if "Xbox players: " in tweet.text:
                # logger.debug("Tweet is for xbox")
                return

            # Check if the tweet is extended and get content
            try:
                text = tweet.extended_tweet["full_text"]
                logger.debug(f"Tweet is extended:")
                logger.debug(f"{text}")
            except AttributeError:
                text = tweet.text
                logger.debug(f"Tweet is not extended:")
                logger.debug(f"{text}")

            # Get media link
            if 'media' in tweet.entities:
                for media in tweet.extended_entities['media']:
                    logger.debug(f"Media: {media['media_url_https']}")
                    link = media['media_url_https']
                    link_list.append(link)
                    logger.debug(f"Media link: {link}")

            # Only print link list if not empty
            if link_list:
                logger.debug("Link List:")
                logger.debug(*link_list)

            # Remove the "_normal.jpg" part in url
            avatar_hd = tweet.user.profile_image_url_https[:-11]
            extension = tweet.user.profile_image_url_https[-4:]
            logger.debug(f"Avatar: {avatar_hd}{extension}")

            # Replace username with link
            text_profile_link = re.sub(r"@(\w*)", "[\g<0>](https://twitter.com/\g<1>/)", text, flags=re.MULTILINE)
            logger.debug(f"Text - profile links: {text_profile_link}")

            # Replace hashtag with link
            text_hashtag_link = re.sub(r"#(\w*)", "[\g<0>](https://twitter.com/hashtag/\g<1>/)", text_profile_link,
                                       flags=re.MULTILINE)
            logger.debug(f"Text - hashtags: {text_hashtag_link}")

            # Discord makes link previews from URLs, we can hide those with < and > before and after URLs
            text_link_preview = re.sub(r"(https://\S*[^\s^.)])", "<\g<0>>", text_hashtag_link, flags=re.MULTILINE)
            logger.debug(f"Text - link preview: {text_link_preview}")

            # Change /r/subreddit to clickable link
            text_reddit_subreddit_link = re.sub(r"/?r/(\S{3,21})", "[/r/\g<1>](https://www.reddit.com/r/\g<1>)",
                                                text_link_preview, flags=re.MULTILINE)
            logger.debug(f"Text - reddit subreddit: {text_reddit_subreddit_link}")

            # Change /u/user to clickable link
            text_reddit_user_link = re.sub(r"/?u/(\S{3,20})", "[/u/\g<1>](https://www.reddit.com/user/\g<1>)",
                                           text_reddit_subreddit_link, flags=re.MULTILINE)
            logger.debug(f"Text - reddit user: {text_reddit_user_link}")

            # Append media so Discords link preview picks them up
            links = '\n'.join([str(v) for v in link_list])
            logger.debug(f"Links: {links}")

            # Final message that we send
            message = text_reddit_user_link + links + "\n"
            logger.debug(f"Message: {message}")

            # Make webhook embed
            hook = Webhook(webhook_url)

            embed = Embed(
                    description=message,
                    color=0x1e0f3,  # Light blue
                    timestamp=True  # Set the timestamp to current time
            )

            # Change webhook avatar to twitter avatar and replace webhook username with Twitter username
            embed.set_author(icon_url=str(avatar_hd) + extension,
                             name=tweet.user.screen_name,
                             url="https://twitter.com/statuses/" + str(tweet.id))

            if link_list:
                first_image = link_list[0]
                embed.set_image(first_image)  # TODO: Change to highest quality
                logger.debug(f"First image: {first_image}")

            # Post to channel
            hook.send(embeds=embed)

            logger.info("Posted.")

        except Exception as e:
            logger.error(f"Error: {e}")
            hook = Webhook(webhook_error_url)
            hook.send(f"<@126462229892694018> I'm broken again <:PepeHands:461899012136632320>\n{e}")

    def on_error(self, error_code):
        if error_code == 420:
            logger.error("420 Enhance Your Calm - We are being rate limited."
                         "Possible reasons: Too many login attempts or running too many copies of the same "
                         "application authenticating with the same credentials")
            return False  # returning False in on_error disconnects the stream

        logger.error(f"Error: {error_code}")
        hook = Webhook(webhook_error_url)
        hook.send(f"<@126462229892694018> I'm broken again <:PepeHands:461899012136632320>\n{error_code}")


listener = MyStreamListener()
stream = Stream(auth, listener)

# Streams are only terminated if the connection is closed, blocking the thread.
# The async parameter makes the stream run on a new thread.
stream.filter(follow=user_list, is_async=True)
