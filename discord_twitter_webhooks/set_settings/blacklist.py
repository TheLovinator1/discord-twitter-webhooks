from loguru import logger
from reader import Reader


def set_blacklist_words(reader: Reader, name: str, blacklist_words: str) -> None:
    """Set the blacklist words tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        blacklist_words: The words we should blacklist.
    """
    logger.debug(f"Setting blacklist words for {name} to {blacklist_words}")
    reader.set_tag((), f"{name}_blacklist", blacklist_words)  # type: ignore  # noqa: PGH003


def set_blacklist_active(reader: Reader, name: str, blacklist_active: bool) -> None:  # noqa: FBT001
    """Set the blacklist active tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        blacklist_active: Whether or not to blacklist.
    """
    logger.debug(f"Setting blacklist active for {name} to {blacklist_active}")
    reader.set_tag((), f"{name}_blacklist_active", blacklist_active)  # type: ignore  # noqa: PGH003
