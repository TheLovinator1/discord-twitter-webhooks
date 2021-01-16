"""This program fetches tweets and writes them in Discord."""

import html
import json
import logging.config
import re
import sys
import logging
import requests
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
    twitter_image_collage_maker,
)


def get_text(tweet) -> str:
    try:
        text = tweet.extended_tweet["full_text"]
        logger.debug(f"Tweet is extended: {text}")

    except AttributeError:
        text = tweet.text
        logger.debug(f"Tweet is not extended: {text}")

    return text


def get_media_links(tweet, text: str) -> tuple:
    link_list = []
    try:
        if "media" in tweet._json["extended_tweet"]["extended_entities"]:
            for image in tweet._json["extended_tweet"]["extended_entities"]["media"]:
                link_list.append(image["media_url_https"])
                text = text.replace(image["url"], "")
            logger.debug("Found image in extended_tweet-extended_entities-media")
    except KeyError:
        try:
            if "media" in tweet._json["extended_entities"]:
                for image in tweet._json["extended_entities"]["media"]:
                    link_list.append(image["media_url_https"])
                    text = text.replace(image["url"], "")
                logger.debug("Found image in extended_entities-media")
        except KeyError:
            logger.debug("Couldn't find any images in tweet")
    return link_list, text


def get_avatar_url(tweet) -> str:
    avatar_url = tweet.user.profile_image_url_https
    logger.debug(f"Avatar URL: {avatar_url}")
    return avatar_url.replace("_normal.jpg", ".jpg")


def replace_tco_url_link_with_real_link(tweet, text: str) -> str:
    try:
        if "urls" in tweet._json["extended_tweet"]["extended_entities"]:
            for url in tweet._json["extended_tweet"]["extended_entities"]["urls"]:
                text = text.replace(url["url"], url["expanded_url"])
            logger.debug("Found url in extended_tweet-extended_entities-urls")
    except KeyError:
        try:
            if "urls" in tweet._json["extended_entities"]:
                for url in tweet._json["extended_entities"]["urls"]:
                    text = text.replace(url["url"], url["expanded_url"])
                logger.debug("Found url in extended_entities-urls")
        except KeyError:
            if "urls" in tweet._json["entities"]:
                for url in tweet._json["entities"]["urls"]:
                    text = text.replace(url["url"], url["expanded_url"])
                logger.debug("Found url in entities-urls")
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
        color=0x1E0F3,
        timestamp="now",
    )
    if link_list is not None:
        if len(link_list) == 1:
            logger.debug("Found one image")
            embed.set_image(link_list[0])

        elif len(link_list) > 1:
            logger.debug("Found more than one image")
            response = requests.get(
                url=twitter_image_collage_maker, params={"tweet_id": tweet.id}
            )

            if response.status_code == 200:
                json_data = json.loads(response.text)
                print(f"json from {twitter_image_collage_maker}: {json_data}")
                embed.set_image(json_data["url"])
            else:
                logger.error(
                    f"Failed to get response from {twitter_image_collage_maker}. Using first image instead."
                )
                embed.set_image(link_list[0])

    embed.set_author(
        icon_url=avatar,
        name=tweet.user.screen_name,
        url=f"https://twitter.com/i/web/status/{tweet.id}",
    )

    hook.send(embed=embed)

    logger.info("Webhook posted.")


def main(tweet):
    logger.debug(f"Raw tweet before any modifications: {tweet}")
    text = get_text(tweet)
    media_links, text_media_links = get_media_links(tweet, text)
    avatar = get_avatar_url(tweet)

    unescaped_text = html.unescape(text_media_links)
    logger.debug(f"Safe HTML converted to unsafe HTML: {text}")

    text_url_links = replace_tco_url_link_with_real_link(tweet, unescaped_text)
    regex = twitter_regex(text_url_links)
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
            msg = (
                "Can't connect to Twitter. "
                "Too many login attempts or running too many copies of the same credentials."
            )
            logger.critical(msg)
            sys.exit(msg)
        logger.error(f"on_error: {error_code}")

    def on_delete(self, status_id: int, user_id: int):
        """Called when a delete notice arrives for a status"""
        send_text_webhook(
            f"[Tweet](https://twitter.com/i/web/status/{status_id}) "
            f"from {api.get_user(user_id).screen_name} was deleted."
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
    logger.debug(f"Twitter collage maker: {twitter_image_collage_maker}")

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
