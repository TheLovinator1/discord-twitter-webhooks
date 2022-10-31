"""
media_links - Get media links from tweet.
meta_image - Get twitter:image meta tag from url.
tweet_urls - Get URLs in the tweet.
"""
import re
from typing import List

import requests
from bs4 import BeautifulSoup
from tweepy import StreamResponse

from discord_twitter_webhooks import settings
from discord_twitter_webhooks.send_webhook import send_error_webhook


def media_links(media: list[dict]) -> list[str]:
    """Get media links from tweet.

    Args:
        media: The media from the tweet, can be images, videos, gifs, etc.

    Returns:
        List of media links found in the tweet
    """
    link_list: list[str] = []
    for image in media:
        # Get the media links from the tweet
        if image["type"] == "photo":
            link_list.append(image["url"])
        elif image["type"] in ["animated_gif", "video"]:
            link_list.append(image["preview_image_url"])
            # TODO: Add actual .mp4 or add play button overlay so you can see that it's a video
        else:
            return []
        settings.logger.debug(f"Image: {image}")

    return link_list


def meta_image(entities) -> str:
    """Get twitter:image meta tag from url.

    Looks for <meta name="twitter:image" content=""> and
    <meta property="og:image" content=""> Right now og:image is prioritized
    over twitter:image.

    Args:
        entities: Entities from the tweet. This is used to get the URL.

    Returns:
        twitter:image found in url
    """
    image_url: str = ""
    url_list: List[str] = []

    for url in entities["urls"]:
        settings.logger.debug(f"url found in tweet: {url['expanded_url']}")

        # We only want to add external links to the list and entities["urls"] has URLs for images, videos that are
        # uploaded with the tweet.
        if "status" in url:
            settings.logger.debug(f"{url['expanded_url']} has a HTTP status code - adding to tweet_urls")
            url_list.append(url["expanded_url"])

    for url in url_list:
        settings.logger.debug(f"meta_image() - url in url_list: {url}")
    if url_list:
        response: requests.Response = requests.get(url_list[0])
        settings.logger.debug(f"meta_image() - Response: {response}")

        if not response.ok:
            settings.logger.error(f"meta_image() - Response not ok: {response!r}")
            return image_url

        soup = BeautifulSoup(response.content, "html.parser")

        if og_image := soup.find_all("meta", attrs={"property": "og:image"}):
            image_url = og_image[0].get("content")
            settings.logger.debug(f"meta_image() - og_image: {og_image}")

        if twitter_image := soup.find_all("meta", attrs={"name": "twitter:image"}):
            image_url = twitter_image[0].get("content")
            settings.logger.debug(f"meta_image() - twitter_image: {twitter_image}")

        settings.logger.debug(f"meta_image() - image_url: {image_url}")
    return image_url


def get_entities(response: StreamResponse) -> dict:
    """Get the entities from the tweet.

    Args:
        response: The response from the stream.

    Returns:
        dict: The entities from the tweet.
    """
    data = response.data
    entities = []
    if data["entities"]:
        entities = data.entities
        settings.logger.debug(f"Entities: {entities}")
    return entities


def get_webhook_url(response: StreamResponse) -> str:
    """Get the webhook url.

    We will check for a stream tag and match it with a webhook url.

    Args:
        response: The response from the stream.

    Returns:
        str: The webhook url.
    """
    data = response.data
    matching_rules = response.matching_rules
    matching_rule_error = (
        f"discord-twitter-webhooks error: Failed to find matching rule for {matching_rules[0].tag!r}\n"
        f"Tweet was: <https://twitter.com/i/web/status/{data.id}>\n"
        "Contact TheLovinator#9276 if this keeps happening.")

    webhook_url = settings.webhooks[0]
    if matching_rules:
        tag = matching_rules[0].tag

        # Get the number from the tag
        m = re.search(r'\d+$', tag)  # Get digits at the end of the string
        tag_number = int(m.group()) if m else None
        if tag_number is None:
            settings.logger.error(
                f"I couldn't figure out what {tag_number!r} was when parsing {tag}. Contact TheLovinator "
                "if this should work.")
        settings.logger.debug(f"tag_number: {tag_number} for tag: {tag}")
        webhook_url = settings.webhooks.get(tag_number)
    else:
        send_error_webhook(matching_rule_error)

    settings.logger.debug(f"webhook_url: {webhook_url}")
    return webhook_url


def get_text(response: StreamResponse) -> str:
    """Get the text from the tweet.

    Args:
        response: The response from the stream.

    Returns:
        str: The text from the tweet.
    """
    data = response.data
    try:
        text = data.text
    except AttributeError:
        text = "*Failed to get text from tweet*"

        error_msg = f"No text found {data!r} for tweet {data.id}"
        send_error_webhook(error_msg)
    settings.logger.debug(f"Text: {text}")
    return text


def get_avatar_and_username(response: StreamResponse) -> tuple:
    """Get avatar and username, this is used for the embed avatar and name.

    Args:
        response: The response from the stream.

    Returns:
        tuple: The avatar and username.
    """
    users = [users.data for users in response.includes["users"]]
    for user in users:
        settings.logger.debug(f"User: {user}")
    avatar = users[0]["profile_image_url"]
    user_name = users[0]["name"]
    return avatar, user_name
