from loguru import logger
from reader import Reader


def set_include_replies(reader: Reader, name: str, include_replies: bool) -> None:
    """Set the include_replies tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        include_replies: Whether or not to include replies.
    """
    logger.debug(f"Setting include_replies for {name} to {include_replies}")
    reader.set_tag((), f"{name}_include_replies", include_replies)  # type: ignore  # noqa: PGH003
