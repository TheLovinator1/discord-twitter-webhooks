"""Stream tweets to Discord.

Tweepy(https://www.tweepy.org/) is used for connecting to the Twitter API and stream tweets to Discord.
Dhooks(https://github.com/kyb3r/dhooks) is used for sending tweets to Discord via webhooks.
BeautifulSoup(https://www.crummy.com/software/BeautifulSoup/) to get images from websites.
requests(https://requests.readthedocs.io/en/master/) to send images
to twitter-image-collage-maker(https://github.com/TheLovinator1/twitter-image-collage-maker)


Original GitHub: https://github.com/TheLovinator1/discord-twitter-webhooks

Don't be afraid to contact me if you have any questions or suggestions. I'm always happy to help or add new features.
Send a pull request or open an issue on GitHub if you want to help me improve this code.
"""

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
    """Get the text from the tweet.

    Tweets can be normal(less than 140 characters) or extended(more than 140 characters).

    Args:
        tweet ([type]): Tweet object

    Returns:
        str: Text from the tweet
    """
    try:
        text = tweet.extended_tweet["full_text"]
        logger.debug(f"Tweet is extended: {text}")

    except AttributeError:
        text = tweet.text
        logger.debug(f"Tweet is not extended: {text}")
    return text


def get_media_links_and_remove_url(tweet, text: str) -> tuple[list, str]:
    """Get the media links from the tweet and remove the links from the tweet text.

    Twitter adds a link at the end of the tweet if the tweet has image, video or gif.
    We will remove this as it is not needed.

    Args:
        tweet ([type]): Tweet object
        text (str): Text from the tweet

    Returns:
        tuple[list, str]:  Media links and text
    """
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


def get_urls(tweet) -> list[str]:
    """Get the URLs from the tweet and add them to a list.

    We use this to get the images from websites.

    Args:
        tweet ([type]): Tweet object

    Returns:
        list[str]: Urls from the tweet
    """
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
    """Replace the t.co url with the real url so users know where the link goes to.

    Before: https://t.co/1YC2hc8iUq
    After: https://www.youtube.com/

    Args:
        tweet ([type]): Tweet object
        text (str): Text from the tweet

    Returns:
        str: Text with the t.co url replaced with the real url
    """
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
    """Replace @username with link to their twitter profile.

    Before: @TheLovinator1
    After: [@TheLovinator1](https://twitter.com/TheLovinator1)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the username replaced with a link
    """
    return re.sub(
        r"\B@(\w*)",
        r"[\g<0>](https://twitter.com/\g<1>)",
        text,
        flags=re.MULTILINE,
    )


def replace_hashtag_with_link(text: str) -> str:
    """Replace hashtag with link to Twitter search.

    Before: #Hello
    After: [#Hello](https://twitter.com/hashtag/Hello)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the hashtag replaced with a link
    """
    # Replace #hashtag with link
    return re.sub(
        r"\B#(\w*)",
        r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        text,
        flags=re.MULTILINE,
    )


def remove_discord_link_previews(text: str) -> str:
    """Remove the discord link previews.

    We do this because Discord will add link previews after the message.
    This takes up too much space. We do this by appending a <> before and after the link.

    Before: https://www.example.com/
    After: <https://www.example.com/>

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the discord link previews removed
    """
    return re.sub(
        r"(https://\S*)\)",
        r"<\g<1>>)",
        text,
        flags=re.MULTILINE,
    )


def change_subreddit_to_clickable_link(text: str) -> str:
    """Change /r/subreddit to clickable link.

    Before: /r/sweden
    After: [r/sweden](https://www.reddit.com/r/sweden/)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the subreddit replaced with a clickable link
    """
    # Change /r/subreddit to clickable link
    return re.sub(
        r"(/r/)([^\s^\/]*)(/|)",
        r"[/r/\g<2>](https://reddit.com/r/\g<2>)",
        text,
        flags=re.MULTILINE,
    )


def change_reddit_username_to_link(text: str) -> str:
    """Change /u/username to clickable link.

    Before: /u/username
    After: [u/username](https://www.reddit.com/u/username/)

    Args:
        text (str): Text from the tweet
    Returns:
        str: Text with the username replaced with a clickable link
    """
    # Change /u/user to clickable link
    return re.sub(
        r"(/u/|/user/)([^\s^\/]*)(/|)",
        r"[/u/\g<2>](https://reddit.com/u/\g<2>)",
        text,
        flags=re.MULTILINE,
    )


def remove_utm_source(text: str) -> str:
    """Remove the utm_source parameter from the url.

    Before: https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter
    After: https://store.steampowered.com/app/457140/Oxygen_Not_Included/

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the utm_source parameter removed
    """
    return re.sub(
        r"(\?utm_source)\S*",
        r"",
        text,
        flags=re.MULTILINE,
    )


def get_meta_image(url: str) -> str:
    """Get twitter:image meta tag from url.

    Looks for <meta name="twitter:image" content=""> and <meta property="og:image" content="">
    Right now og:image is prioritized over twitter:image.

    Args:
        url (str): Url to get the meta image from

    Returns:
        [type]: twitter:image found in url
    """
    image_url = ""
    try:
        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")

        # TODO: Which one should be used if both are availabe?
        # <meta name="twitter:image" content="">
        twitter_image = soup.find_all("meta", attrs={"name": "twitter:image"})
        if twitter_image:
            image_url = twitter_image[0].get("content")

        # <meta property="og:image" content="">
        og_image = soup.find_all("meta", attrs={"property": "og:image"})
        if og_image:
            image_url = og_image[0].get("content")

    except Exception as exception:  # pylint: disable=broad-except
        logger.error(f"Error getting image url: {exception}")

    return image_url


def send_text_webhook(text: str, webhook: str = webhook_url) -> None:
    """Send text to webhook.

    Args:
        text (str): Text to send to webhook
        webhook (str, optional): Webhook URL. Defaults to environment variable WEBHOOK_URL.
    """
    logger.error(f"Webhook text: {text}")
    hook = Webhook(webhook)
    hook.send(text)


def send_embed_webhook(
    tweet, link_list: list[str], text: str, webhook: str = webhook_url, twitter_card_image: str = None
) -> None:
    """Send embed to Discord webhook.

    Args:
        avatar (str): Avatar URL
        tweet ([type]): Tweet object
        link_list (list[str]): List of links from the tweet
        text (str): Text from the tweet
        webhook (str, optional): Webhook URL. Defaults to environment variable WEBHOOK_URL.
        twitter_card_image (str, optional): Twitter meta image. Defaults to None.
    """
    logger.debug(f"Tweet: {text}")
    hook = Webhook(webhook)

    embed = Embed(
        description=text,
        color=0x1E0F3,
        timestamp="now",
    )
    # Only add image if there is one
    if len(link_list):
        if len(link_list) == 1:
            logger.debug(f"Found one image: {link_list[0]}")
            embed.set_image(link_list[0])

        elif len(link_list) > 1:
            # Send images to twitter-image-collage-maker(e.g https://twitter.lovinator.space/) and get a collage back.
            logger.debug("Found more than one image")
            response = requests.get(url=twitter_image_collage_maker, params={"tweet_id": tweet.id})

            if response.status_code == 200:
                json_data = json.loads(response.text)
                logger.debug(f"JSON from {twitter_image_collage_maker}: {json_data}")
                embed.set_image(json_data["url"])
            else:
                logger.error(f"Failed to get response from {twitter_image_collage_maker}. Using first image instead.")
                embed.set_image(link_list[0])

    elif twitter_card_image:
        try:
            embed.set_image(twitter_card_image)
        except Exception as exception:  # pylint: disable=broad-except
            logger.error(f"Failed to set Twitter card image: {exception}")

    avatar_url = tweet.user.profile_image_url_https
    logger.debug(f"Avatar URL: {avatar_url}")
    avatar_url = avatar_url.replace("_normal.jpg", ".jpg")

    embed.set_author(
        icon_url=avatar_url,
        name=tweet.user.screen_name,
        url=f"https://twitter.com/i/web/status/{tweet.id}",
    )

    hook.send(embed=embed)

    logger.info(f"Webhook posted for tweet https://twitter.com/i/web/status/{tweet.id}")


def main(tweet):
    """Don't be afraid to contact me if you have any questions about something here."""
    logger.debug(f"Raw tweet before any modifications: {tweet}")

    # Get tweet text.
    text = get_text(tweet)

    # Get media links and remove them from the text. We will use the media links to add images to the embed.
    media_links, text_media_links = get_media_links_and_remove_url(tweet, text)

    # Get image from website that we can use if no image is found in tweet
    urls_found = get_urls(tweet)
    twitter_card_image = get_meta_image(urls_found[0])

    # Unescape HTML entities. &gt; becomes > etc.
    unescaped_text = html.unescape(text_media_links)

    # Replace t.co links with clickable links
    text_url_links = replace_tco_url_link_with_real_link(tweet, unescaped_text)

    # Replace /u/username with clickable link
    text_replace_username = replace_username_with_link(text_url_links)

    # Replace hashtags with clickable links
    text_replace_hashtags = replace_hashtag_with_link(text_replace_username)

    # Add < and > to the beginning and end of URLs
    text_discord_preview = remove_discord_link_previews(text_replace_hashtags)

    # Change /r/subreddit to clickable link
    text_subreddit_to_link = change_subreddit_to_clickable_link(text_discord_preview)

    # Change /u/username to clickable link
    text_reddit_username_to_link = change_reddit_username_to_link(text_subreddit_to_link)

    # Remove ?utm_source in URLs
    text_remove_utm_source = remove_utm_source(text_reddit_username_to_link)

    # Send embed to Discord
    send_embed_webhook(
        tweet=tweet,
        link_list=media_links,
        text=text_remove_utm_source,
        twitter_card_image=twitter_card_image,
    )


class MyStreamListener(Stream):
    """https://docs.tweepy.org/en/latest/streaming.html

    Args:
        Stream ([type]): Stream tweets in realtime.
    """

    def on_status(self, status):
        """This is called when a new tweet is received.

        Args:
            status ([type]): Twitter status
        """
        # Tweet is retweet
        if hasattr(status, "retweeted_status"):
            logger.info("Tweet is retweet")
            if (
                status.user.id_str == status.retweeted_status.user.id_str
                and get_retweet_of_own_tweet.lower() == "true"
            ):
                logger.info("We replied to our self")
                main(tweet=status)
                return
            if status.retweeted_status.user.id_str in user_list_retweeted_split:
                logger.info("Someone retweeted our tweet")
                main(tweet=status)
            elif status.user.id_str in user_list_retweets_split:
                logger.info("We retweeted a tweet")
                main(tweet=status)
            else:
                logger.info("Retweets and retweeted are not active in the environment variables.")
        elif status.in_reply_to_user_id is not None:
            # FIXME: If somebody else responds to their own reply in our tweet this activates.
            # We need to check who the original tweet author is.
            #
            # if tweet.user.id_str == tweet.in_reply_to_user_id_str:
            #     logger.info("We replied to our self")
            #     main(tweet=tweet)
            #     return
            #
            if status.user.id_str in user_list_replies_to_other_tweet_split:
                logger.info("We replied to someone")
                main(tweet=status)
            elif status.in_reply_to_user_id_str in user_list_replies_to_our_tweet_split:
                logger.info("Someone replied to us")
                main(tweet=status)
            else:
                logger.info(
                    "We didn't reply to our self, someone else or someone replied to us. "
                    "Or it is not active in the environment variables."
                )
        else:
            main(tweet=status)

        return


def start():
    """Authenticate to the Twitter API and start the filter."""
    stream = MyStreamListener(consumer_key, consumer_secret, access_token, access_token_secret)

    # Streams are only terminated if the connection is closed, blocking the thread.
    stream.filter(follow=user_list, stall_warnings=True)


if __name__ == "__main__":
    start()
