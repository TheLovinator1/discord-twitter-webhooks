from loguru import logger
from reader import Reader


def set_send_only_link(reader: Reader, name: str, send_only_link: bool) -> None:  # noqa: FBT001
    """Set the send_only_link tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        send_only_link: Whether or not to send only a link.
    """
    logger.debug(f"Setting send_only_link for {name} to {send_only_link}")
    reader.set_tag((), f"{name}_send_only_link", send_only_link)  # type: ignore  # noqa: PGH003


def set_send_only_link_preview(reader: Reader, name: str, send_only_link_preview: bool) -> None:  # noqa: FBT001
    """Set the send_only_link_preview tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        send_only_link_preview: Whether or not to send only a link preview.
    """
    logger.debug(f"Setting send_only_link_preview for {name} to {send_only_link_preview}")
    reader.set_tag((), f"{name}_send_only_link_preview", send_only_link_preview)  # type: ignore  # noqa: PGH003
