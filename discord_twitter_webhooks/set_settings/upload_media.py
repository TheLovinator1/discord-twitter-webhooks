from loguru import logger
from reader import Reader


def set_upload_media(reader: Reader, name: str, upload_media: bool) -> None:  # noqa: FBT001
    """Set the upload_media tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        upload_media: Whether or not to upload media.
    """
    logger.debug(f"Setting upload_media for {name} to {upload_media}")
    reader.set_tag((), f"{name}_upload_media", upload_media)  # type: ignore  # noqa: PGH003
