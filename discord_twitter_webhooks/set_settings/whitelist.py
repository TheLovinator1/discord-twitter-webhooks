from loguru import logger
from reader import Reader


def set_whitelist(reader: Reader, name: str, whitelist_words: str) -> None:
    """Set the whitelist words tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        whitelist_words: The words we should whitelist.
    """
    logger.debug(f"Setting whitelist words for {name} to {whitelist_words}")
    reader.set_tag((), f"{name}_whitelist", whitelist_words)  # type: ignore  # noqa: PGH003


def set_whitelist_active(reader: Reader, name: str, whitelist_active: bool) -> None:
    """Set the whitelist active tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        whitelist_active: Whether or not to whitelist.
    """
    logger.debug(f"Setting whitelist active for {name} to {whitelist_active}")
    reader.set_tag((), f"{name}_whitelist_active", whitelist_active)  # type: ignore  # noqa: PGH003
