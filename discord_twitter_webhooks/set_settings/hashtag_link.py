from loguru import logger
from reader import Reader


def set_hashtag_link(reader: Reader, name: str, hashtag_link: bool) -> None:
    """Set the hashtag_link tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        hashtag_link: Whether or not to hashtag link.
    """
    logger.debug(f"Setting hashtag_link for {name} to {hashtag_link}")
    reader.set_tag((), f"{name}_hashtag_link", hashtag_link)  # type: ignore  # noqa: PGH003


def set_hashtag_link_destination(reader: Reader, name: str, hashtag_link_destination: str) -> None:
    """Set the hashtag_link_destination tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        hashtag_link_destination: The destination of the hashtag link.
    """
    logger.debug(f"Setting hashtag_link_destination for {name} to {hashtag_link_destination}")
    reader.set_tag((), f"{name}_hashtag_link_destination", hashtag_link_destination)  # type: ignore  # noqa: PGH003
