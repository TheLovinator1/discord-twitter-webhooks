from loguru import logger
from reader import Reader


def set_translate(reader: Reader, name: str, translate: bool) -> None:
    """Set the translate tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        translate: Whether or not to translate.
    """
    if translate is None:
        logger.error("Translate is None when setting translate.")
        return

    logger.debug(f"Setting translate for {name} to {translate}")
    reader.set_tag((), f"{name}_translate", translate)  # type: ignore  # noqa: PGH003


def set_translate_to(reader: Reader, name: str, translate_to: str) -> None:
    """Set the translate_to tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        translate_to: The language to translate to.
    """
    if translate_to is None or not translate_to:
        logger.error("Translate to is None when setting translate to.")
        return

    logger.debug(f"Setting translate_to for {name} to {translate_to}")
    reader.set_tag((), f"{name}_translate_to", translate_to)  # type: ignore  # noqa: PGH003


def set_translate_from(reader: Reader, name: str, translate_from: str) -> None:
    """Set the translate_from tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        translate_from: The language to translate from.
    """
    if translate_from is None or not translate_from:
        logger.error("Translate from is None when setting translate from.")
        return

    logger.debug(f"Setting translate_from for {name} to {translate_from}")
    reader.set_tag((), f"{name}_translate_from", translate_from)  # type: ignore  # noqa: PGH003
