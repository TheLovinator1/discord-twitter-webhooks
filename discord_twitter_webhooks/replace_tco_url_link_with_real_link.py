from discord_twitter_webhooks.settings import logger


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
            logger.debug(f"Found url in: https://twitter.com/i/web/status/{tweet.id}: {url}")

    except AttributeError:
        # Tweet is less than 140 characters
        try:
            for url in tweet.entities["urls"]:
                text = text.replace(url["url"], url["expanded_url"])
                logger.debug(f"Found url in: https://twitter.com/i/web/status/{tweet.id}: {url}")
        except AttributeError:
            logger.debug(f"No url in https://twitter.com/i/web/status/{tweet.id}")

    logger.debug(f"replace_tco_url_link_with_real_link: text={text}")
    return text
