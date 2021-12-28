from discord_twitter_webhooks.settings import logger


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
            logger.debug(f"Found url in: https://twitter.com/i/web/status/{tweet.id}: {url}")
    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for url in tweet.entities["urls"]:
                url_list.append(url["expanded_url"])
                logger.debug(f"Found url in: https://twitter.com/i/web/status/{tweet.id}: {url}")
        except AttributeError:
            logger.debug(f"No url in https://twitter.com/i/web/status/{tweet.id}")

    logger.debug(f"url_list: {url_list}")
    return url_list
