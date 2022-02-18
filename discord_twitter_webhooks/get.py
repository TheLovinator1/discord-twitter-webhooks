import requests
from bs4 import BeautifulSoup


def media_links_and_remove_url(tweet, text: str) -> tuple[list, str]:
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

    try:
        # Tweet is more than 140 characters
        for image in tweet.extended_tweet["extended_entities"]["media"]:
            link_list.append(image["media_url_https"])
            text = text.replace(image["url"], "")
    except KeyError:
        pass

    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for image in tweet.extended_entities["media"]:
                link_list.append(image["media_url_https"])
                text = text.replace(image["url"], "")
        except AttributeError:
            pass

    return link_list, text


def meta_image(url: str) -> str:
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
        # <meta property="og:image" content="">
        og_image = soup.find_all("meta", attrs={"property": "og:image"})
        if og_image:
            image_url = og_image[0].get("content")

        # <meta name="twitter:image" content="">
        twitter_image = soup.find_all("meta", attrs={"name": "twitter:image"})
        if twitter_image:
            image_url = twitter_image[0].get("content")

    except Exception:
        image_url = ""

    return image_url


def tweet_text(tweet) -> str:
    """Get the text from the tweet.

    Tweets can be normal(less than 140 characters) or extended(more than 140 characters).

    Args:
        tweet ([type]): Tweet object

    Returns:
        str: Text from the tweet
    """
    try:
        text = tweet.extended_tweet["full_text"]
    except AttributeError:
        text = tweet.text

    return text


def tweet_urls(tweet) -> list[str]:
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
            pass

    return url_list
