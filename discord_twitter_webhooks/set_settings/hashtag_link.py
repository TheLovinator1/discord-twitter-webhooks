from loguru import logger
from reader import Reader


def set_hashtag_link_destination(reader: Reader, name: str, hashtag_destination: str) -> None:
    """Set the hashtag_link_destination tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        hashtag_destination: The destination of the hashtag link.
    """
    if hashtag_destination is None or not hashtag_destination:
        logger.error(
            "Hashtag link destination is None or empty when setting hashtag link destination. Keeping default.",
        )
        return

    logger.debug(f"Setting hashtag_destination for {name} to {hashtag_destination}")
    reader.set_tag((), f"{name}_hashtag_destination", hashtag_destination)  # type: ignore  # noqa: PGH003
