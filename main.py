"""This program fetches tweets and writes them in Discord."""

import logging.config
import os
import re
import sys

import tweepy
from dhooks import Embed, Webhook
from dotenv import load_dotenv
from tweepy import OAuthHandler, Stream

load_dotenv(verbose=True)


# Enviroment variables
consumer_key = os.getenv(key="CONSUMER_KEY")
consumer_secret = os.getenv(key="CONSUMER_SECRET")
access_token = os.getenv(key="ACCESS_TOKEN")
access_token_secret = os.getenv(key="ACCESS_TOKEN_SECRET")
users_to_follow = os.getenv(
    key="USERS_TO_FOLLOW", default=""  # Add default so user_list doesn't hate us
)
webhook_url_error = os.getenv(key="WEBHOOK_URL_ERROR")
webhook_url = os.getenv(key="WEBHOOK_URL")
log_level = os.getenv(  # CRITICAL, ERROR, WARNING, INFO, DEBUG
    key="LOG_LEVEL", default="INFO"
)


print(consumer_key)
print(consumer_secret)
print(access_token)
print(access_token_secret)
print(users_to_follow)
print(webhook_url_error)
print(webhook_url)

"""
# Check if the user has filled out the enviroment variables
if (
    consumer_key
    or consumer_secret
    or access_token
    or access_token_secret
    or users_to_follow
    or webhook_url_error
    or webhook_url is None
):
    print("Fill out the enviroment variables!")
    sys.exit()

"""


# Logger
formatter = logging.Formatter("%(asctime)s %(levelname)-12s %(message)s")
logger = logging.getLogger()
handler = logging.StreamHandler()

# Log to console
handler.setFormatter(formatter)
logger.addHandler(handler)

level = logging.getLevelName(log_level)  # CRITICAL, ERROR, WARNING, INFO, DEBUG
logger.setLevel(level)


# Authenticate to the Twitter API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
logger.info(f"API key belongs to {api.me().screen_name}")


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
        # Change /r/subreddit to clickable link # FIXME: Broken.
        # r"/?r/(\S{3,21})": r"[/r/\g<1>](https://reddit.com/r/\g<1>)",
        # Change /u/user to clickable link      # FIXME: Broken.
        # r"/?u/(\S{3,20})": r"[/u/\g<1>](https://reddit.com/u/\g<1>)",
    }

    for pat, rep in regex_dict.items():
        text = _regex_substitutor(pattern=pat, replacement=rep, string=text)

    return text


def send_error_notification(error):
    """ Send errror message webhook """
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
        url=f"https://twitter.com/statuses/{tweet.id}",
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

    text = tweet_text(tweet=tweet)
    media_links = tweet_media_links(tweet=tweet)
    avatar = get_avatar_url(tweet=tweet)
    text_replaced = replace_tco_link_with_real_link(tweet=tweet, text=text)
    regex = twitter_regex(text=text_replaced)
    make_webhook(avatar=avatar, tweet=tweet, text=regex, link_list=media_links)


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_status(self, tweet):
        """Called when an unhandled exception occurs."""
        try:
            if is_retweet(tweet=tweet):
                return
            if is_reply(tweet=tweet):
                return
            main(tweet=tweet)

        except Exception as e:
            send_error_notification(error=e)

    def on_error(self, error_code):
        if error_code == 420:
            msg = (
                "We are being rate limited. Too many login attempts or "
                "running too many copies of the same credentials"
            )
            send_error_notification(error=msg)
        send_error_notification(error=error_code)

    def on_direct_message(self, status):
        """Called when a new direct message arrives"""
        msg = f"on_direct_message:\n{status}"
        send_error_notification(error=msg)

    def on_warning(self, notice):
        """Called when a disconnection warning message arrives"""
        msg = f"on_warning:\n{notice}"
        send_error_notification(error=msg)

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice

        Disconnect codes are listed here:
        https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/streaming-message-types

        error_codes = {
            1: "Shutdown: The feed was shutdown (possibly a machine restart)",
            2: "Duplicate stream: The same endpoint was connected too many times.",
            4: "Stall: The client was reading too slowly and was disconnected by the server.",
            5: "Normal: The client appeared to have initiated a disconnect.",
            7: "Admin logout: The same credentials were used to connect a new stream and the oldest was disconnected.",
            9: "Max message limit: The stream connected with a negative count "
            + "parameter and was disconnected after all backfill was delivered.",
            10: "Stream exception: An internal issue disconnected the stream.",
            11: "Broker stall: An internal issue disconnected the stream.",
            12: "Shed load: The host the stream was connected to became"
            + " overloaded and streams were disconnected to balance load. Reconnect as usual.",
        }
        error_codes.get(notice, "on_disconnect - Unknown message")
        """
        msg = f"on_disconnect:\n{notice}"
        send_error_notification(error=msg)

    def on_timeout(self):
        """Called when stream connection times out"""
        msg = "on_timeout"
        send_error_notification(error=msg)

    def on_friends(self, friends):
        """Called when a friends list arrives."""
        msg = f"on_friends:\n{friends}"
        send_error_notification(error=msg)

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        msg = f"on_delete:\n{status_id}: {user_id}"
        send_error_notification(error=msg)

    def on_limit(self, track):
        """Called when a limitation notice arrives"""
        msg = f"on_limit:\n{track}"
        send_error_notification(error=msg)

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""
        msg = f"on_exception:\n{exception}"
        send_error_notification(error=msg)


listener = MyStreamListener()
stream = Stream(auth, listener)

# Streams are only terminated if the connection is closed, blocking the
# thread. The async parameter makes the stream run on a new thread.
stream.filter(follow=user_list, is_async=True, stall_warnings=True)
