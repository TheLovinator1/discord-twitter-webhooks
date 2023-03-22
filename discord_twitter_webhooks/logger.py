import sys

from loguru import logger

from discord_twitter_webhooks import get_settings


def setup_logger() -> None:
    log_format: str = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <level>{level: <5}</level> <white>{message}</white>"

    # Remove default logger
    logger.remove()

    # Add our logger with the correct settings
    log_level: str = get_settings.get_log_level()
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True,
        backtrace=False,
        diagnose=False,
        catch=True,
    )
