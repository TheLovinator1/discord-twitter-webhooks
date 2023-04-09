from loguru import logger


def send_error_webhook(message: str) -> None:
    """Send a webhook to the error webhook URL.

    Args:
        message: The message to send.
    """
    logger.error(message)
