"""This program fetches tweets and writes them in Discord."""

import html
import logging.config
import re
import sys

import tweepy
from dhooks import Embed, Webhook
from tweepy import Stream

from settings import (
    access_token,
    access_token_secret,
    auth,
    consumer_key,
    consumer_secret,
    users_to_follow,  # TODO: Add support for twitter usernames
    log_level,
    owner_id,
    webhook_url,
    webhook_url_error,
)

logger = logging
logger.basicConfig(format="%(asctime)s - %(message)s", level=log_level)

level = logging.getLevelName(log_level)

logger.debug(f"Consumer key: {consumer_key}")
logger.debug(f"Consumer secret: {consumer_secret}")
logger.debug(f"Access Token: {access_token}")
logger.debug(f"Access Token Secret: {access_token_secret}")
logger.debug(f"Users to follow: {users_to_follow}")
logger.debug(f"Webhook url for errors: {webhook_url_error}")
logger.debug(f"Webhook url: {owner_id}")
logger.debug(f"Discord owner ID: {webhook_url}")


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
    # TODO: Make this work for images too
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


def send_error_webhook(error):
    logger.error(f"Error: {error}")
    hook = Webhook(webhook_url_error)
    hook.send(
        f"<@{owner_id}> I'm broken again <:PepeHands:461899012136632320>\n{error}"
    )
    return False


def make_webhook_embed(avatar, tweet, link_list, text):
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
    logger.debug(f"Raw tweet before any modifications: {tweet}")

    # The text from the tweet
    text = tweet_text(tweet=tweet)
    logger.debug(f"Text extracted from the tweet: {text}")

    # Change &amp; to &
    text_convert_safe_html_unicode = html.unescape(text)
    logger.debug(f"Safe HTML converted to unsafe HTML: {text}")

    # Images from the tweet
    media_links = tweet_media_links(tweet=tweet)
    logger.debug(f"Media links found in tweet: {media_links}")

    # Get user avatar
    avatar = get_avatar_url(tweet=tweet)
    logger.debug(f"Avatar from tweeter: {avatar}")

    # Replace t.co URL with real URL
    text_replaced = replace_tco_link_with_real_link(
        tweet=tweet, text=text_convert_safe_html_unicode
    )
    logger.debug(f"Replaced t.co URLs with real URLs: {text_replaced}")

    # Replace username, hashtag and subreddit with links
    regex = twitter_regex(text=text_replaced)
    logger.debug("After we add links to tweet: " + str(regex))

    # Send webhook to Discord
    make_webhook_embed(avatar=avatar, tweet=tweet, text=regex, link_list=media_links)
    logger.debug("Sent webhook to Discord")


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_status(self, tweet):
        """Called when a new status arrives"""
        try:
            if tweet.retweeted or "RT @" in tweet.text:
                logger.debug(
                    f"Tweet(https://twitter.com/i/web/status/{tweet.id}) is retweet. Skipping"
                )
                return
            if tweet.in_reply_to_screen_name is not None:
                logger.debug(
                    f"Tweet(https://twitter.com/i/web/status/{tweet.id}) is reply. Skipping"
                )
                return
            main(tweet=tweet)

        except Exception as error:
            send_error_webhook(
                f"on_status failed!\n"
                f"[{tweet.user.screen_name}](https://twitter.com/i/web/status/{tweet.id}): {tweet.text}\n"
                f"Error: {error}"
            )

    def on_error(self, error_code):
        if error_code == 420:
            send_error_webhook(
                "Can't connect to Twitter. Too many login attempts or running too many copies of the same "
                "credentials. "
            )
            sys.exit(1)
        send_error_webhook(f"on_error: {error_code}")

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        send_error_webhook(
            f"[Tweet](https://twitter.com/i/web/status/{status_id}) from {api.get_user(user_id).screen_name} was deleted."
        )

    def on_exception(self, exception):
        send_error_webhook(f"Called when an unhandled exception occurs:\n{exception}")


if __name__ == "__main__":
    print("Bot started.")

    # Authenticate to the Twitter API
    api = tweepy.API(auth)
    listener = MyStreamListener()
    stream = Stream(auth, listener)

    logger.info(f"API key belongs to {api.me().screen_name}")

    user_list = [x.strip() for x in users_to_follow.split(",")]
    for twitter_id in user_list:
        """ Print users we follow. """
        username = api.get_user(twitter_id)
        print(f"{twitter_id} - {username.screen_name}")

    # Streams are only terminated if the connection is closed, blocking the
    # thread. The async parameter makes the stream run on a new thread.
    stream.filter(follow=user_list, stall_warnings=True, is_async=True)
