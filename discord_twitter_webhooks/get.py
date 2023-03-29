import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tweepy import StreamResponse
from tweepy.streaming import StreamRule

from discord_twitter_webhooks import settings
from discord_twitter_webhooks.send_webhook import send_error_webhook


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
        logger.debug("url found in tweet: {}", url)

        # We only want to add external links to the list and entities["urls"] has URLs for images, videos that are
        # uploaded with the tweet.
        if "status" in url:
            logger.debug("{} has a HTTP status code - adding to tweet_urls", url["expanded_url"])
            url_list.append(url["expanded_url"])

    for url in url_list:
        logger.debug("URL in url_list: {}", url)
    if url_list:
        try:
            response: requests.Response = requests.get(url_list[0], timeout=5)
        except requests.exceptions.RequestException:
            logger.error("RequestException: {}", url_list[0])
            return image_url

        logger.debug("Response: {}", response)

        if not response.ok:
            logger.error("Response not ok: {}", response)
            return image_url

        soup: BeautifulSoup = BeautifulSoup(response.content, "html.parser")

        if og_image := soup.find_all("meta", attrs={"property": "og:image"}):
            image_url = og_image[0].get("content")
            logger.debug("og_image: {}", og_image)

        if twitter_image := soup.find_all("meta", attrs={"name": "twitter:image"}):
            image_url = twitter_image[0].get("content")
            logger.debug("twitter_image: {}", twitter_image)

        logger.debug("image_url: {}", image_url)

    # Some URLs don't have a protocol, so we add it here.
    if image_url.startswith("//"):
        image_url = f"https:{image_url}"

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
        logger.debug("Entities: {entities}", entities=entities)
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
            f"discord-twitter-webhooks error: Failed to find matching rule for {matching_rules[0].tag}\n"
            f"Tweet was: <https://twitter.com/i/web/status/{data.id}>\n"
            "Contact TheLovinator#9276 if this keeps happening."
        )

        send_error_webhook(matching_rule_error)

    logger.debug("webhook_url: {}", webhook_url)

    return webhook_url


def get_webhook_from_tag(matching_rules: list[StreamRule]) -> str:
    our_webhooks: str = ""
    for rules in matching_rules:
        tag: str = rules.tag

        # Get digits at the end of the string
        m: re.Match[str] | None = re.search(r"\d+$", tag)

        # Convert the string to an int
        tag_number: int | None = int(m.group()) if m else None

        if tag_number is None:
            logger.error(
                "I couldn't figure out what {} was when parsing {}. Contact TheLovinator if this should work.",
                tag_number,
                tag,
            )
        logger.debug("tag_number: {} for tag: {}", tag_number, tag)

        if tag_number is not None:
            webhook: str | None = settings.webhooks.get(tag_number)

            if webhook is None:
                logger.error("webhook is None")

            # Add the webhook to the list
            our_webhooks = f"{our_webhooks}{webhook},"

    # Remove the last comma if there is one
    if our_webhooks[-1] == ",":
        our_webhooks = our_webhooks[:-1]

    # Convert the string to a list
    our_webhooks_list: list[str] = our_webhooks.split(",")

    # Remove duplicates and return the list as a string
    return ",".join(set(our_webhooks_list))


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

        error_msg: str = f"No text found {data} for tweet {data.id}"
        send_error_webhook(error_msg)
    logger.debug("Text: {}", text)
    return text


@dataclass
class UserInformation:
    """User information for the embed."""

    avatar_url: str
    display_name: str
    username: str


def get_user_information(response: StreamResponse) -> UserInformation:
    """Get avatar and username, this is used for the embed avatar and name.

    Args:
        response: The response from the stream.

    Returns:
        UserInformation: The user information. Avatar, display name and username.
    """
    users = [users.data for users in response.includes["users"]]
    for user in users:
        logger.debug("User: {}", user)

    # TODO: Check if this always is [0]
    avatar_url: str = users[0]["profile_image_url"]
    display_name: str = users[0]["name"]
    username = users[0]["username"]

    return UserInformation(avatar_url, display_name, username)
