from flask import Request
from loguru import logger
from reader import Reader


def get_include_retweets(request: Request) -> bool:
    value: str = request.form.get("include_retweets", "false")

    if value == "true":
        return True
    return False


def set_include_retweets(reader: Reader, name: str, include_retweets: bool) -> None:  # noqa: FBT001
    logger.debug(f"Setting include_retweets for {name} to {include_retweets}")
    reader.set_tag((), f"{name}_include_retweets", include_retweets)  # type: ignore  # noqa: PGH003
