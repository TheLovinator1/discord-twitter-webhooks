from loguru import logger
from reader import Reader


def set_remove_utm(reader: Reader, name: str, remove_utm_value: bool) -> None:
    """Set the remove_utm tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        remove_utm_value: The remove_utm value.
    """
    logger.debug(f"Setting remove_utm for {name} to {remove_utm_value}")
    reader.set_tag((), f"{name}_remove_utm", remove_utm_value)  # type: ignore  # noqa: PGH003
