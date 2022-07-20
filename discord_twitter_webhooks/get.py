from typing import List

import requests
from bs4 import BeautifulSoup

from discord_twitter_webhooks import settings


def media_links(media) -> list[str]:
    link_list = []
    for image in media:
        # Get the media links from the tweet
        if image["type"] == "photo":
            link_list.append(image["url"])
        elif image["type"] in ["animated_gif", "video"]:
            link_list.append(image["preview_image_url"])
            # TODO: Add actual .mp4 or add play button overlay so you
            # can see that it's a video
        else:
            return []
        settings.logger.debug(f"Image: {image}")

    return link_list


def meta_image(url: str) -> str:
    """Get twitter:image meta tag from url.

    Looks for <meta name="twitter:image" content=""> and
    <meta property="og:image" content=""> Right now og:image is prioritized
    over twitter:image.

    Args:
        url: Url to get the meta image from

    Returns:
        twitter:image found in url
    """
    image_url: str = ""

    response = requests.get(url)
    settings.logger.debug(f"Response: {response}")

    soup = BeautifulSoup(response.content, "html.parser")

    if og_image := soup.find_all("meta", attrs={"property": "og:image"}):
        image_url = og_image[0].get("content")
        settings.logger.debug(f"og_image: {og_image}")

    if twitter_image := soup.find_all("meta", attrs={"name": "twitter:image"}):
        image_url = twitter_image[0].get("content")
        settings.logger.debug(f"twitter_image: {twitter_image}")

    settings.logger.debug(f"image_url: {image_url}")
    return image_url


def tweet_urls(entities: dict) -> list[str]:
    """Get URLs in the tweet.

    Args:
        entities (_type_): __description__

    Returns:
        list[str]: List of URLs found in the tweet
    """
    url_list: List[str] = []

    for url in entities["urls"]:
        settings.logger.debug(f"url found in tweet: {url['expanded_url']}")

        # We only want to add external links to the list and
        # entities["urls"] has URLs for images, videos that are uploaded
        # with the tweet.
        if "status" in url:
            settings.logger.debug(f"{url['expanded_url']} has a HTTP status code - adding to tweet_urls")
            url_list.append(url["expanded_url"])

    settings.logger.debug(f"url_list: {url_list}")

    return url_list
