from loguru import logger
from reader import Reader


def set_append_usernames(reader: Reader, name: str, append_usernames: bool) -> None:
    """Set the append_usernames tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        append_usernames: Whether or not to append usernames.
    """
    logger.debug(f"Setting append_usernames for {name} to {append_usernames}")
    reader.set_tag((), f"{name}_append_usernames", append_usernames)  # type: ignore  # noqa: PGH003
