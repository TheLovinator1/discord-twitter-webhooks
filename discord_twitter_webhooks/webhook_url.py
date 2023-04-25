from loguru import logger
from reader import Reader


def set_webhook_url(reader: Reader, name: str, webhook_value: str) -> None:
    logger.debug(f"Setting webhook for {name} to {webhook_value}")
    reader.set_tag((), f"{name}_webhook", webhook_value)  # type: ignore  # noqa: PGH003
