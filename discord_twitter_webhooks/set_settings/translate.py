from loguru import logger
from reader import Reader


def set_translate(reader: Reader, name: str, translate: bool) -> None:  # noqa: FBT001
    """Set the translate tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        translate: Whether or not to translate.
    """
    logger.debug(f"Setting translate for {name} to {translate}")
    reader.set_tag((), f"{name}_translate", translate)  # type: ignore  # noqa: PGH003


def set_translate_to(reader: Reader, name: str, translate_to: str) -> None:
    """Set the translate_to tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        translate_to: The language to translate to.
    """
    logger.debug(f"Setting translate_to for {name} to {translate_to}")
    reader.set_tag((), f"{name}_translate_to", translate_to)  # type: ignore  # noqa: PGH003


def set_translate_from(reader: Reader, name: str, translate_from: str) -> None:
    """Set the translate_from tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        translate_from: The language to translate from.
    """
    logger.debug(f"Setting translate_from for {name} to {translate_from}")
    reader.set_tag((), f"{name}_translate_from", translate_from)  # type: ignore  # noqa: PGH003
