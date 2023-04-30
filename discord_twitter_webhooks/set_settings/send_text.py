from loguru import logger
from reader import Reader


def set_send_text(reader: Reader, name: str, send_text: bool) -> None:
    """Set the send_text tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        send_text: Whether or not to send text.
    """
    logger.debug(f"Setting send_text for {name} to {send_text}")
    reader.set_tag((), f"{name}_send_text", send_text)  # type: ignore  # noqa: PGH003
