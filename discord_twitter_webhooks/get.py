import re

import requests
from bs4 import BeautifulSoup
from tweepy import StreamResponse
from tweepy.streaming import StreamRule

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
        settings.logger.debug("Image: %s", image)

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
    url_list: list[str] = []

    for url in entities["urls"]:
        settings.logger.debug("url found in tweet: %s", url["expanded_url"])

        # We only want to add external links to the list and entities["urls"] has URLs for images, videos that are
        # uploaded with the tweet.
        if "status" in url:
            settings.logger.debug("%s has a HTTP status code - adding to tweet_urls", url["expanded_url"])
            url_list.append(url["expanded_url"])

    for url in url_list:
        settings.logger.debug("meta_image() - url in url_list: %s", url)
    if url_list:
        response: requests.Response = requests.get(url_list[0], timeout=5)
        settings.logger.debug("meta_image() - Response: %s", response)

        if not response.ok:
            settings.logger.error("meta_image() - Response not ok: %r", response)
            return image_url

        soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

        if og_image := soup.find_all("meta", attrs={"property": "og:image"}):
            image_url = og_image[0].get("content")
            settings.logger.debug("meta_image() - og_image: %s", og_image)

        if twitter_image := soup.find_all("meta", attrs={"name": "twitter:image"}):
            image_url = twitter_image[0].get("content")
            settings.logger.debug("meta_image() - twitter_image: %s", twitter_image)

        settings.logger.debug("meta_image() - image_url: %s", image_url)

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
        settings.logger.debug("Entities: %s", entities)
    return entities  # type: ignore


def get_webhook_url(response: StreamResponse) -> str:
    """Get the webhook url.

    We will check for a stream tag and match it with a webhook url.

    Args:
        response: The response from the stream.

    Returns:
        str: The webhook url.
    """
    webhook_url: str = settings.webhooks[0]
    if matching_rules := response.matching_rules:
        webhook_url = get_webhook_from_tag(matching_rules)
    else:
        data = response.data
        matching_rule_error: str = (
            f"discord-twitter-webhooks error: Failed to find matching rule for {matching_rules[0].tag!r}\n"
            f"Tweet was: <https://twitter.com/i/web/status/{data.id}>\n"
            "Contact TheLovinator#9276 if this keeps happening."
        )

        send_error_webhook(matching_rule_error)

    settings.logger.debug("webhook_url: %s", webhook_url)

    return webhook_url


def get_webhook_from_tag(matching_rules: list[StreamRule]) -> str:
    tag: str = matching_rules[0].tag

    # Get the number from the tag
    m: re.Match[str] | None = re.search(r"\d+$", tag)  # Get digits at the end of the string
    tag_number: int | None = int(m.group()) if m else None
    if tag_number is None:
        settings.logger.error(
            "I couldn't figure out what %s was when parsing %s. Contact TheLovinator if this should work."
            % (tag_number, tag),
        )
    settings.logger.debug("tag_number: %s for tag: %s", tag_number, tag)
    if tag_number is None:
        settings.logger.error("tag_number is None")
    return settings.webhooks.get(tag_number)  # type: ignore


def get_text(response: StreamResponse) -> str:
    """Get the text from the tweet.

    Args:
        response: The response from the stream.

    Returns:
        str: The text from the tweet.
    """
    data = response.data
    try:
        text: str = data.text
    except AttributeError:
        text = "*Failed to get text from tweet*"

        error_msg: str = f"No text found {data!r} for tweet {data.id}"
        send_error_webhook(error_msg)
    settings.logger.debug("Text: %s", text)
    return text


def get_avatar_and_username(response: StreamResponse) -> tuple[str, str]:
    """Get avatar and username, this is used for the embed avatar and name.

    Args:
        response: The response from the stream.

    Returns:
        tuple: The avatar and username.
    """
    users = [users.data for users in response.includes["users"]]
    for user in users:
        settings.logger.debug("User: %s", user)
    avatar: str = users[0]["profile_image_url"]
    user_name: str = users[0]["name"]
    return avatar, user_name
