import html
import json
import logging
import re

import requests
from bs4 import BeautifulSoup
from dhooks import Embed, Webhook
from tweepy import Stream

from discord_twitter_webhooks.settings import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret,
    get_retweet_of_own_tweet,
    log_level,
    twitter_image_collage_maker,
    user_list,
    user_list_replies_to_other_tweet_split,
    user_list_replies_to_our_tweet_split,
    user_list_retweeted_split,
    user_list_retweets_split,
    webhook_url,
)

logger = logging
logger.basicConfig(format="%(asctime)s - %(message)s", level=log_level)

level = logging.getLevelName(log_level)


def get_text(tweet) -> str:
    try:
        text = tweet.extended_tweet["full_text"]
        logger.debug(f"Tweet is extended: {text}")

    except AttributeError:
        text = tweet.text
        logger.debug(f"Tweet is not extended: {text}")
    return text


def get_media_links_and_remove_url(tweet, text: str) -> tuple:
    link_list = []

    logger.debug(f"Found image in: https://twitter.com/i/web/status/{tweet.id}")
    try:
        # Tweet is more than 140 characters
        for image in tweet.extended_tweet["extended_entities"]["media"]:
            link_list.append(image["media_url_https"])
            text = text.replace(image["url"], "")
    except KeyError:
        # Tweet has no links
        pass

    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for image in tweet.extended_entities["media"]:
                link_list.append(image["media_url_https"])
                text = text.replace(image["url"], "")
        except AttributeError:
            # Tweet has no links
            pass

    return link_list, text


def get_avatar_url(tweet) -> str:
    avatar_url = tweet.user.profile_image_url_https
    logger.debug(f"Avatar URL: {avatar_url}")
    return avatar_url.replace("_normal.jpg", ".jpg")


def get_urls(tweet) -> list:
    url_list = []
    try:
        for url in tweet.extended_tweet["entities"]["urls"]:
            url_list.append(url["expanded_url"])
    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for url in tweet.entities["urls"]:
                url_list.append(url["expanded_url"])
        except AttributeError:
            # Tweet has no links
            pass
    return url_list


def replace_tco_url_link_with_real_link(tweet, text: str) -> str:
    try:
        # Tweet is more than 140 characters
        for url in tweet.extended_tweet["entities"]["urls"]:
            text = text.replace(url["url"], url["expanded_url"])

    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for url in tweet.entities["urls"]:
                text = text.replace(url["url"], url["expanded_url"])
        except AttributeError:
            # Tweet has no links
            pass
    return text


def replace_username_with_link(text: str) -> str:
    # Replace @username with link
    return re.sub(
        r"\B@(\w*)",
        r"[\g<0>](https://twitter.com/\g<1>)",
        text,
        flags=re.MULTILINE,
    )


def replace_hashtag_with_link(text: str) -> str:
    # Replace #hashtag with link
    return re.sub(
        r"\B#(\w*)",
        r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        text,
        flags=re.MULTILINE,
    )


def remove_discord_link_previews(text: str) -> str:
    # Discord makes link previews, can fix this by changing to <url>
    return re.sub(
        r"(https://\S*)\)",
        r"<\g<1>>)",
        text,
        flags=re.MULTILINE,
    )


def change_subreddit_to_clickable_link(text: str) -> str:
    # Change /r/subreddit to clickable link
    return re.sub(
        r"(/r/)([^\s^\/]*)(/|)",
        r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        text,
        flags=re.MULTILINE,
    )


def change_reddit_username_to_link(text: str) -> str:
    # Change /u/user to clickable link
    return re.sub(
        r"(/u/|/user/)([^\s^\/]*)(/|)",
        r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
        text,
        flags=re.MULTILINE,
    )


def get_meta_image(url: str):
    try:
        r = requests.get(url[0])
        soup = BeautifulSoup(r.content, "html.parser")
        image_url = ""

        # TODO: Which one should be used if both are availabe?
        # <meta name="twitter:image" content="">
        twitter_image = soup.find_all("meta", attrs={"name": "twitter:image"})
        if twitter_image:
            image_url = twitter_image[0].get("content")

        # <meta property="og:image" content="">
        og_image = soup.find_all("meta", attrs={"property": "og:image"})
        if og_image:
            image_url = og_image[0].get("content")

        return image_url
    except Exception as e:
        logger.error(f"Error getting image url: {e}")


def send_text_webhook(text: str, webhook: str = webhook_url):
    logger.error(f"Webhook text: {text}")
    hook = Webhook(webhook)
    hook.send(text)


def send_embed_webhook(avatar: str, tweet, link_list, text: str, webhook: str = webhook_url, twitter_card_image=None):
    logger.debug(f"Tweet: {text}")
    hook = Webhook(webhook)

    embed = Embed(
        description=text,
        color=0x1E0F3,
        timestamp="now",
    )
    if len(link_list):
        if len(link_list) == 1:
            logger.debug(f"Found one image: {link_list[0]}")
            embed.set_image(link_list[0])

        elif len(link_list) > 1:
            logger.debug("Found more than one image")
            response = requests.get(url=twitter_image_collage_maker, params={"tweet_id": tweet.id})

            if response.status_code == 200:
                json_data = json.loads(response.text)
                print(f"json from {twitter_image_collage_maker}: {json_data}")
                embed.set_image(json_data["url"])
            else:
                logger.error(f"Failed to get response from {twitter_image_collage_maker}. Using first image instead.")
                embed.set_image(link_list[0])

    elif twitter_card_image:
        try:
            embed.set_image(twitter_card_image)
        except Exception as e:
            logger.error(f"Failed to set Twitter card image: {e}")
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
    media_links, text_media_links = get_media_links_and_remove_url(tweet, text)
    avatar = get_avatar_url(tweet)
    twitter_card_image = get_meta_image(get_urls(tweet))
    unescaped_text = html.unescape(text_media_links)
    text_url_links = replace_tco_url_link_with_real_link(tweet, unescaped_text)
    text_replace_username = replace_username_with_link(text_url_links)
    text_replace_hashtags = replace_hashtag_with_link(text_replace_username)
    text_discord_preview = remove_discord_link_previews(text_replace_hashtags)
    text_subreddit_to_link = change_subreddit_to_clickable_link(text_discord_preview)
    text_reddit_username_to_link = change_reddit_username_to_link(text_subreddit_to_link)

    send_embed_webhook(
        avatar=avatar,
        tweet=tweet,
        link_list=media_links,
        text=text_reddit_username_to_link,
        twitter_card_image=twitter_card_image,
    )


class MyStreamListener(Stream):
    def on_status(self, tweet):
        print(f"on_status: {tweet}")
        """Called when a new status arrives"""

        # Tweet is retweet
        if hasattr(tweet, "retweeted_status"):
            logger.info("Tweet is retweet")
            if tweet.user.id_str == tweet.retweeted_status.user.id_str and get_retweet_of_own_tweet.lower() == "true":
                logger.info("We replied to our self")
                main(tweet=tweet)
                return
            if tweet.retweeted_status.user.id_str in user_list_retweeted_split:
                logger.info("Someone retweeted our tweet")
                main(tweet=tweet)
            elif tweet.user.id_str in user_list_retweets_split:
                logger.info("We retweeted a tweet")
                main(tweet=tweet)
            else:
                logger.info("Retweets and retweeted are not active in the environment variables.")
        elif tweet.in_reply_to_user_id is not None:
            # FIXME: If somebody else responds to their own reply in our tweet this activates.
            # We need to check who the original tweet author is.
            #
            # if tweet.user.id_str == tweet.in_reply_to_user_id_str:
            #     logger.info("We replied to our self")
            #     main(tweet=tweet)
            #     return
            #
            if tweet.user.id_str in user_list_replies_to_other_tweet_split:
                logger.info("We replied to someone")
                main(tweet=tweet)
            elif tweet.in_reply_to_user_id_str in user_list_replies_to_our_tweet_split:
                logger.info("Someone replied to us")
                main(tweet=tweet)
            else:
                logger.info(
                    "We didn't reply to our self, someone else or someone replied to us. "
                    "Or it is not active in the environment variables."
                )
        else:
            main(tweet=tweet)

        return


def start():
    # Authenticate to the Twitter API
    stream = MyStreamListener(consumer_key, consumer_secret, access_token, access_token_secret)

    # Streams are only terminated if the connection is closed, blocking the thread.
    stream.filter(follow=user_list, stall_warnings=True)


if __name__ == "__main__":
    start()
