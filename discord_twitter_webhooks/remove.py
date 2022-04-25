import re


def discord_link_previews(text: str) -> str:
    """Remove the Discord link previews.

    We do this because Discord will add link previews after the message.
    This takes up too much space. We do this by appending a <> before
    and after the link.

    Before: https://www.example.com/
    After: <https://www.example.com/>

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the Discord link previews removed
    """
    return re.sub(
        r"(^(https:|http:|www\.)\S*)",
        r"<\g<1>>",
        text,
    )


def utm_source(text: str) -> str:
    """Remove the utm_source parameter from the url.

    Before: https://store.steampowered.com/app/457140/Oxygen_Not_Included/?utm_source=Steam&utm_campaign=Sale&utm_medium=Twitter # noqa, pylint: disable=line-too-long

    After: https://store.steampowered.com/app/457140/Oxygen_Not_Included/

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the utm_source parameter removed
    """
    return re.sub(
        r"(\?utm_source)\S*",
        r"",
        text,
    )


def copyright_symbols(text: str) -> str:
    """Remove ®, ™ and © symbols.

    Args:
        text (str): Text from the tweet

    Returns:
        str: Text with the copyright symbols removed
    """
    text = text.replace("®", "")
    text = text.replace("™", "")
    text = text.replace("©", "")
    return text
