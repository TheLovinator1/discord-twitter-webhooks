from loguru import logger
from reader import Reader


def set_webhook_url(reader: Reader, name: str, webhook_value: str) -> None:
    """Set the webhook_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        webhook_value: The webhook_url value.
    """
    logger.debug(f"Setting webhook for {name} to {webhook_value}")
    reader.set_tag((), f"{name}_webhooks", webhook_value)  # type: ignore  # noqa: PGH003
