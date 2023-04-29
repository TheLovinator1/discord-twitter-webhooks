from loguru import logger
from reader import Reader


def set_remove_copyright_symbols(reader: Reader, name: str, remove_copyright: bool) -> None:
    """Set the remove_copyright tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        remove_copyright: The remove_utm value.
    """
    logger.debug(f"Setting remove_copyright for {name}")
    reader.set_tag((), f"{name}_remove_copyright", remove_copyright)  # type: ignore  # noqa: PGH003
