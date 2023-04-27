from loguru import logger
from reader import Reader


def set_include_retweets(reader: Reader, name: str, include_retweets: bool) -> None:  # noqa: FBT001
    """Set the include_retweets tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        include_retweets: Whether or not to include retweets.
    """
    logger.debug(f"Setting include_retweets for {name} to {include_retweets}")
    reader.set_tag((), f"{name}_include_retweets", include_retweets)  # type: ignore  # noqa: PGH003