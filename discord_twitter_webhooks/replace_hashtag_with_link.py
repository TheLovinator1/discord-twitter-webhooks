import re


def replace_hashtag_with_link(text: str) -> str:
    """Replace hashtag with link to Twitter search.

    Before: #Hello
    After: [#Hello](https://twitter.com/hashtag/Hello)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the hashtag replaced with a link
    """
    # Replace #hashtag with link
    return re.sub(
        r"\B#(\w*)",
        r"[\g<0>](https://twitter.com/hashtag/\g<1>)",
        text,
        flags=re.MULTILINE,
    )
