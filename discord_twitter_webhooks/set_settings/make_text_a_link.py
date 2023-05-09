from loguru import logger
from reader import Reader


def set_make_text_a_link(reader: Reader, name: str, make_text_a_link: bool) -> None:
    """Set the make_text_a_link tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        make_text_a_link: Whether or not to make text a link.
    """
    if make_text_a_link is None:
        logger.error("Make text a link is None when setting make text a link.")
        return

    logger.debug(f"Setting make_text_a_link for {name} to {make_text_a_link}")
    reader.set_tag((), f"{name}_make_text_a_link", make_text_a_link)  # type: ignore  # noqa: PGH003


def set_make_text_a_link_preview(reader: Reader, name: str, make_text_a_link_preview: bool) -> None:
    """Set the make_text_a_link_preview tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        make_text_a_link_preview: Whether or not to make text a link preview.
    """
    if make_text_a_link_preview is None:
        logger.error("Make text a link preview is None when setting make text a link preview.")
        return

    logger.debug(f"Setting make_text_a_link_preview for {name} to {make_text_a_link_preview}")
    reader.set_tag((), f"{name}_make_text_a_link_preview", make_text_a_link_preview)  # type: ignore  # noqa: PGH003


def set_make_text_a_link_url(reader: Reader, name: str, make_text_a_link_url: str) -> None:
    """Set the make_text_a_link_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        make_text_a_link_url: The url to use for the link.
    """
    if make_text_a_link_url is None or not make_text_a_link_url:
        logger.error("Make text a link url is None when setting make text a link url.")
        return

    logger.debug(f"Setting make_text_a_link_url for {name} to {make_text_a_link_url}")
    reader.set_tag((), f"{name}_make_text_a_link_url", make_text_a_link_url)  # type: ignore  # noqa: PGH003