import sys

from loguru import logger


def setup_logger() -> None:
    """Set up the logger.

    This function is used to set up the logger.
    """
    log_format: str = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <level>{level: <5}</level> <white>{message}</white>"
    logger.remove()
    logger.add(
        sys.stderr,
        format=log_format,
        level="INFO",
        colorize=True,
        backtrace=False,
        diagnose=False,
        catch=True,
    )
