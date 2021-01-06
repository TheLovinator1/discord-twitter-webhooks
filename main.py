"""This program fetches tweets and writes them in Discord."""

import html
import logging.config
import re
import sys
import logging
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
    webhook_url,
)


def get_text(tweet) -> str:
    try:
        text = tweet.extended_tweet["full_text"]
        logger.debug(f"Tweet is extended:\n{text}")
        return text
    except AttributeError:
        text = tweet.text
        logger.debug(f"Tweet is not extended:\n{text}")
        return text


def get_media_links(tweet):
    link_list = []
    if "media" in tweet.entities:
        for media in tweet.extended_entities["media"]:
            logger.debug(f"Media: {media['media_url_https']}")
            link = media["media_url_https"]
            link_list.append(link)
            logger.debug(f"Links found in tweet: {link_list}")
        return link_list


def get_avatar_url(tweet) -> str:
    avatar_url = tweet.user.profile_image_url_https
    logger.debug(f"Avatar URL: {avatar_url}")
    return avatar_url.replace("_normal.jpg", ".jpg")


def replace_tco_link_with_real_link(tweet, text: str) -> str:
    # TODO: Make this work for images too
    try:
        for url in tweet.extended_tweet["entities"]["urls"]:
            text = text.replace(url["url"], url["expanded_url"])
        logger.debug(f"Replaced t.co URLs with real URLs: {text}")
        return text
    except AttributeError:
        for url in tweet.entities["urls"]:
            text = text.replace(url["url"], url["expanded_url"])
        logger.debug(f"Replaced t.co URLs with real URLs: {text}")
        return text


def _regex_substitutor(pattern: str, replacement: str, string: str) -> str:
    substitute = re.sub(
        r"{}".format(pattern), r"{}".format(replacement), string, flags=re.MULTILINE
    )
    return substitute


def twitter_regex(text: str) -> str:
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

    logger.debug(f"After we add links to tweet: {text}")
    return text


def send_text_webhook(text: str):
    logger.error(f"Webhook text: {text}")
    hook = Webhook(webhook_url)
    hook.send(text)


def send_embed_webhook(avatar: str, tweet, link_list, text: str):
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

    logger.info("Webhook posted.")


def main(tweet):
    logger.debug(f"Raw tweet before any modifications: {tweet}")

    media_links = get_media_links(tweet)
    avatar = get_avatar_url(tweet)

    text = get_text(tweet)
    unescaped_text = html.unescape(text)
    logger.debug(f"Safe HTML converted to unsafe HTML: {text}")
    text_with_links = replace_tco_link_with_real_link(tweet=tweet, text=unescaped_text)
    regex = twitter_regex(text_with_links)

    send_embed_webhook(avatar=avatar, tweet=tweet, link_list=media_links, text=regex)


class MyStreamListener(tweepy.StreamListener):
    def on_connect(self):
        print("I am now connected to the streaming API.")

    def on_status(self, tweet):
        """Called when a new status arrives"""
        if tweet.retweeted or "RT @" in tweet.text:
            return

        if tweet.in_reply_to_screen_name is not None:
            return

        main(tweet=tweet)

    def on_error(self, error_code: int):
        if error_code == 420:
            logger.critical(
                "Can't connect to Twitter. Too many login attempts or running too many copies of the same "
                "credentials. "
            )
            sys.exit(1)
        logger.error(f"on_error: {error_code}")

    def on_delete(self, status_id: int, user_id: int):
        """Called when a delete notice arrives for a status"""
        send_text_webhook(
            f"[Tweet](https://twitter.com/i/web/status/{status_id}) from {api.get_user(user_id).screen_name} was deleted."
        )

    def on_exception(self, exception):
        logger.error(f"Unhandled exception occured:\n{exception}")


if __name__ == "__main__":
    logger = logging
    logger.basicConfig(format="%(asctime)s - %(message)s", level=log_level)

    level = logging.getLevelName(log_level)

    logger.debug(f"Consumer key: {consumer_key}")
    logger.debug(f"Consumer secret: {consumer_secret}")
    logger.debug(f"Access Token: {access_token}")
    logger.debug(f"Access Token Secret: {access_token_secret}")
    logger.debug(f"Users to follow: {users_to_follow}")
    logger.debug(f"Webhook url: {webhook_url}")

    # Authenticate to the Twitter API
    api = tweepy.API(auth)
    listener = MyStreamListener()
    stream = Stream(auth, listener)

    logger.info(f"API key belongs to {api.me().screen_name}")

    user_list = [x.strip() for x in users_to_follow.split(",")]
    for twitter_id in user_list:
        # Print the users we have in our config file.
        username = api.get_user(twitter_id)
        print(f"{twitter_id} - {username.screen_name}")

    # Streams are only terminated if the connection is closed, blocking the
    # thread. The async parameter makes the stream run on a new thread.
    stream.filter(follow=user_list, stall_warnings=True, is_async=True)
