import re

from discord_twitter_webhooks.settings import logger


def replace_hashtag_with_link(text: str) -> str:
    """Replace hashtag with link to Twitter search.

    Before: #Hello
    After: [#Hello](https://twitter.com/hashtag/Hello)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the hashtag replaced with a link
    """
    logger.debug(f"replace_hashtag_with_link: text={text}")
    new_text = re.sub(
        r"\B#(\w*)",
        r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        text,
        flags=re.MULTILINE,
    )
    logger.debug(f"replace_hashtag_with_link: new_text={new_text}")
    return new_text
