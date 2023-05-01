from loguru import logger
from reader import Reader


def set_usernames(reader: Reader, name: str, usernames: str) -> None:
    """Set the usernames tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        usernames: The usernames to set.
    """
    logger.debug(f"Setting usernames for {name} to {usernames}")
    reader.set_tag((), f"{name}_usernames", usernames)  # type: ignore  # noqa: PGH003
