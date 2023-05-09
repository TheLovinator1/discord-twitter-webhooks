from loguru import logger
from reader import Reader


def set_username_link_destination(reader: Reader, name: str, username_destination: str) -> None:
    """Set the username_link_destination tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        username_destination: The destination of the username link.
    """
    if username_destination is None or not username_destination:
        logger.error("Username link destination is None when setting username link destination.")
        return

    logger.debug(f"Setting username_destination for {name} to {username_destination}")
    reader.set_tag((), f"{name}_username_destination", username_destination)  # type: ignore  # noqa: PGH003
