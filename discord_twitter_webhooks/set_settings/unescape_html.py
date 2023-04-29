from loguru import logger
from reader import Reader


def set_unescape_html(reader: Reader, name: str, unescape_html: bool) -> None:
    """Set the unescape_html tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        unescape_html: Whether or not to unescape HTML.
    """
    logger.debug(f"Setting unescape_html for {name} to {unescape_html}")
    reader.set_tag((), f"{name}_unescape_html", unescape_html)  # type: ignore  # noqa: PGH003
