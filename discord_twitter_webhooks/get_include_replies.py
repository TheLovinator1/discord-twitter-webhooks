from flask import Request


def get_include_replies(request: Request) -> bool:
    value: str = request.form.get("include_replies", "false")

    if value == "true":
        return True
    return False
