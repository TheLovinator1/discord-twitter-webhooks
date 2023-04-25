from flask import Request
from loguru import logger
from reader import Reader


def get_include_replies(request: Request) -> bool:
    value: str = request.form.get("include_replies", "false")

    if value == "true":
        return True
    return False


def set_include_replies(reader: Reader, name: str, include_replies: bool) -> None:  # noqa: FBT001
    logger.debug(f"Setting include_replies for {name} to {include_replies}")
    reader.set_tag((), f"{name}_include_replies", include_replies)  # type: ignore  # noqa: PGH003
