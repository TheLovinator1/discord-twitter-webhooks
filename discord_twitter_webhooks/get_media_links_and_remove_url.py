from discord_twitter_webhooks.settings import logger


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
