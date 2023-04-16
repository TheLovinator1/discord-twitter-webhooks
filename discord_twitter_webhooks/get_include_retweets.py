from flask import Request


def get_include_retweets(request: Request) -> bool:
    value: str = request.form.get("include_retweets", "false")

    if value == "true":
        return True
    return False
