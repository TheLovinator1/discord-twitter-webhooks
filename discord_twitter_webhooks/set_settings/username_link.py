from loguru import logger
from reader import Reader


def set_username_link_destination(reader: Reader, name: str, username_link_destination: str) -> None:
    """Set the username_link_destination tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        username_link_destination: The destination of the username link.
    """
    logger.debug(f"Setting username_link_destination for {name} to {username_link_destination}")
    reader.set_tag((), f"{name}_username_link_destination", username_link_destination)  # type: ignore  # noqa: PGH003
