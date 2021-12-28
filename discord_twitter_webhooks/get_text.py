from discord_twitter_webhooks.settings import logger


def get_text(tweet) -> str:
    """Get the text from the tweet.

    Tweets can be normal(less than 140 characters) or extended(more than 140 characters).

    Args:
        tweet ([type]): Tweet object

    Returns:
        str: Text from the tweet
    """
    try:
        text = tweet.extended_tweet["full_text"]
        logger.debug(f"Tweet is extended: {text}")

    except AttributeError:
        text = tweet.text
        logger.debug(f"Tweet is not extended: {text}")
    return text
