import re


def replace_username_with_link(text: str) -> str:
    """Replace @username with link to their twitter profile.

    Before: @TheLovinator1
    After: [@TheLovinator1](https://twitter.com/TheLovinator1)

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the username replaced with a link
    """
    return re.sub(
        r"\B@(\w*)",
        r"[\g<0>](https://twitter.com/\g<1>)",
        text,
        flags=re.MULTILINE,
    )
