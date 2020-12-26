"""This program fetches tweets and writes them in Discord."""

import html
import logging.config
import os
import re

import requests
import tweepy
import urllib3
from dhooks import Embed, Webhook
from dotenv import load_dotenv
from tweepy import OAuthHandler, Stream

load_dotenv(verbose=True)

# Environment variables
consumer_key = os.getenv(key="CONSUMER_KEY")
consumer_secret = os.getenv(key="CONSUMER_SECRET")
access_token = os.getenv(key="ACCESS_TOKEN")
access_token_secret = os.getenv(key="ACCESS_TOKEN_SECRET")
users_to_follow = os.getenv(key="USERS_TO_FOLLOW", default="")
webhook_url_error = os.getenv(key="WEBHOOK_URL_ERROR")
webhook_url = os.getenv(key="WEBHOOK_URL")
log_level = os.getenv(key="LOG_LEVEL", default="INFO")

# Logger
formatter = logging.Formatter("%(asctime)s %(levelname)-12s %(message)s")
logger = logging.getLogger()
handler = logging.StreamHandler()

# Log to console
handler.setFormatter(formatter)
logger.addHandler(handler)

level = logging.getLevelName(log_level)
logger.setLevel(level)

# Authenticate to the Twitter API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
logger.info(f"API key belongs to {api.me().screen_name}")

logger.debug(f"Consumer key: {consumer_key}")
logger.debug(f"Consumer secret: {consumer_secret}")
logger.debug(f"Access Token: {access_token}")
logger.debug(f"Access Token Secret: {access_token_secret}")
logger.debug(f"Users to follow: {users_to_follow}")
logger.debug(f"Webhook url for errors: {webhook_url_error}")
logger.debug(f"Webhook url: {webhook_url}")

user_list = [x.strip() for x in users_to_follow.split(",")]
for twitter_id in user_list:
    """ Print users we follow. """
    username = api.get_user(twitter_id)
    print(f"{twitter_id} - {username.screen_name}")


def is_retweet(tweet):
    """ Skip retweets. """
    if tweet.retweeted or "RT @" in tweet.text:
        return True


def is_reply(tweet):
    """ Skip replies. """
    if tweet.in_reply_to_screen_name is not None:
        return True


def tweet_text(tweet):
    """Check if the tweet is truncated and get full tweet"""
    try:
        text = tweet.extended_tweet["full_text"]
        logger.debug(f"Tweet is extended:\n\t{text}")
        return text
    except AttributeError:
        text = tweet.text
        logger.debug(f"Tweet is not extended:\n\t{text}")
        return text


def tweet_media_links(tweet):
    link_list = []
    if "media" in tweet.entities:
        for media in tweet.extended_entities["media"]:
            logger.debug(f"Media: {media['media_url_https']}")
            link = media["media_url_https"]
            link_list.append(link)
            logger.debug(f"Link list: {link_list}")
        return link_list


def get_avatar_url(tweet):
    """Remove the "_normal.jpg" part in url to get higher quality"""
    avatar_hd = tweet.user.profile_image_url_https[:-11]
    extension = tweet.user.profile_image_url_https[-4:]
    avatar_url = f"{avatar_hd}{extension}"
    return avatar_url


def replace_tco_link_with_real_link(tweet, text):
    """Replace t.co url with real url"""
    try:
        for url in tweet.extended_tweet["entities"]["urls"]:
            text = text.replace(url["url"], url["expanded_url"])
        return text
    except AttributeError:
        for url in tweet.entities["urls"]:
            text = text.replace(url["url"], url["expanded_url"])
        return text


def _regex_substitutor(pattern: str, replacement: str, string: str) -> str:
    substitute = re.sub(
        r"{}".format(pattern), r"{}".format(replacement), string, flags=re.MULTILINE
    )
    return substitute


def twitter_regex(text):
    regex_dict = {  # I have no idea what I am doing so don't judge my regex lol
        # Replace @username with link
        r"@(\w*)": r"[\g<0>](https://twitter.com/\g<1>)",
        # Replace #hashtag with link
        r"#(\w*)": r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        # Discord makes link previews, can fix this by changing to <url>
        r"(https://\S*)\)": r"<\g<1>>)",
        # Change /r/subreddit to clickable link
        r".*?(/r/)([^\s^\/]*)(/|)": r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        # Change /u/user to clickable link
        r".*?(/u/|/user/)([^\s^\/]*)(/|)": r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
    }

    for pat, rep in regex_dict.items():
        text = _regex_substitutor(pattern=pat, replacement=rep, string=text)

    return text


def send_error_notification(error):
    """ Send error message webhook """
    logger.error(f"Error: {error}")
    hook = Webhook(webhook_url_error)
    hook.send(
        f"<@126462229892694018> I'm broken again "
        f"<:PepeHands:461899012136632320>\n{error}"
    )
    return False


def make_webhook(avatar, tweet, link_list, text):
    """Make webhook embed"""
    logger.debug(f"Tweet: {text}")
    hook = Webhook(webhook_url)
    embed = Embed(
        description=text,
        color=0x1E0F3,  # Light blue
        timestamp="now",  # Set the timestamp to current time
    )

    embed.set_author(
        icon_url=avatar,
        name=tweet.user.screen_name,
        url=f"https://twitter.com/i/web/status/{tweet.id}",
    )

    hook.send(embed=embed)

    # Add links under embed
    if link_list is not None:
        links = "\n".join([str(v) for v in link_list])
        if links:
            hook.send(f"I found some links:\n{links}")

    logger.info("Posted.")


def main(tweet):
    logger.debug(f"Raw tweet: {tweet}")

    # The text from the tweet
    text = tweet_text(tweet=tweet)

    # Change &amp; to &
    text_convert_safe_html_unicode = html.unescape(text)

    # Images from the tweet
    media_links = tweet_media_links(tweet=tweet)

    # Get user avatar
    avatar = get_avatar_url(tweet=tweet)

    # Replace t.co url with real url
    text_replaced = replace_tco_link_with_real_link(
        tweet=tweet, text=text_convert_safe_html_unicode
    )

    # Replace username, hashtag and subreddit with links
    regex = twitter_regex(text=text_replaced)

    # Send webhook to Discord
    make_webhook(avatar=avatar, tweet=tweet, text=regex, link_list=media_links)


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_status(self, tweet):
        """Called when a new status arrives"""
        try:
            if is_retweet(tweet=tweet):
                return
            if is_reply(tweet=tweet):
                return
            main(tweet=tweet)

        except Exception as error:
            send_error_notification(
                f"on_status failed!\n"
                f"{tweet.user.screen_name}: {tweet.text}\n"
                f"Error: {error}"
            )

    def on_error(self, error_code):
        if error_code == 420:
            send_error_notification(
                error="Can't connect to Twitter. Too many login attempts or running too many copies of the same "
                "credentials. "
            )
            return
        send_error_notification(error=error_code)

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        send_error_notification(
            error=f"Tweet from {user_id} \n{status_id} was deleted."
        )

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        send_error_notification(
            error=f"Called when an unhandled exception occurs:\n{exception}"
        )


if __name__ == "__main__":
    print("Bot started.")
    listener = MyStreamListener()
    stream = Stream(auth, listener)

    # Streams are only terminated if the connection is closed, blocking the
    # thread. The async parameter makes the stream run on a new thread.

    # Exceptions taken from https://github.com/NNTin/discord-twitter-bot/blob/master/bot/main.py#L112
    while True:
        try:
            stream.filter(follow=user_list, stall_warnings=True)
        except urllib3.exceptions.ProtocolError as e:
            send_error_notification(
                f"Raised when something unexpected happens mid-request/response:\n{e}"
            )

        except ConnectionResetError as e:
            send_error_notification(f"Connection reset:\n{e}")

        except ConnectionError as e:
            send_error_notification(f"Connection error:\n{e}")

        except requests.exceptions.ConnectionError as e:
            send_error_notification(f"A Connection error occurred:\n{e}")

        except Exception as e:
            send_error_notification(f"Unknown error:\n" f"{e}\n")
