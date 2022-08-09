"""
media_links - Get media links from tweet.
meta_image - Get twitter:image meta tag from url.
tweet_urls - Get URLs in the tweet.
"""
from typing import List

import requests
from bs4 import BeautifulSoup

from discord_twitter_webhooks import settings


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
