from flask import Request
from loguru import logger
from reader import Reader


def get_include_replies(request: Request) -> bool:
    """Return True if the include_replies checkbox is checked.

    Args:
        request: The request that was sent to the server. This is used to get the
            include_replies checkbox.

    Returns:
        bool: True if the include_replies checkbox is checked.
    """
    value: str = request.form.get("include_replies", "false")
    return value == "true"


def set_include_replies(reader: Reader, name: str, include_replies: bool) -> None:  # noqa: FBT001
    """Set the include_replies tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        include_replies: Whether or not to include replies.
    """
    logger.debug(f"Setting include_replies for {name} to {include_replies}")
    reader.set_tag((), f"{name}_include_replies", include_replies)  # type: ignore  # noqa: PGH003
