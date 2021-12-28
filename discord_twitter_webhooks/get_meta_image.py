import requests
from bs4 import BeautifulSoup

from discord_twitter_webhooks.settings import logger


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
        logger.debug(f"Response {response.status_code} from {url}")

        soup = BeautifulSoup(response.content, "html.parser")

        # TODO: Which one should be used if both are availabe?
        # <meta property="og:image" content="">
        og_image = soup.find_all("meta", attrs={"property": "og:image"})
        logger.debug(f"og_image: {og_image}")
        if og_image:
            image_url = og_image[0].get("content")

        # <meta name="twitter:image" content="">
        twitter_image = soup.find_all("meta", attrs={"name": "twitter:image"})
        logger.debug(f"twitter_image: {twitter_image}")
        if twitter_image:
            image_url = twitter_image[0].get("content")

    except Exception as exception:  # pylint: disable=broad-except
        logger.error(f"Error getting image url: {exception}")

    logger.debug(f"image_url: {image_url}")
    return image_url
