from reader import Reader

from discord_twitter_webhooks.dataclasses import GlobalSettings


def get_global_settings(reader: Reader) -> GlobalSettings:
    """Get the global settings.

    Args:
        reader: The reader that has the global settings.

    Returns:
        The global settings.
    """
    global_settings = GlobalSettings()
    global_tags = list(reader.get_tags(()))
    for global_tag in global_tags:
        if global_tag[0] == "global_nitter_instance":
            global_settings.nitter_instance = str(global_tag[1])
        if global_tag[0] == "global_translator_instance":
            global_settings.translator_instance = str(global_tag[1])
        if global_tag[0] == "global_send_errors_to_discord":
            global_settings.send_errors_to_discord = bool(global_tag[1])
        if global_tag[0] == "global_error_webhook":
            global_settings.error_webhook = str(global_tag[1])
    return global_settings


def save_global_settings(reader: Reader, global_settings: GlobalSettings) -> None:
    """Save the global settings to the reader.

    Args:
        reader: The reader to use to save the settings to.
        global_settings: The global settings to save.
    """
    reader.set_tag((), "global_nitter_instance", global_settings.nitter_instance)  # type: ignore  # noqa: PGH003
    reader.set_tag((), "global_translator_instance", global_settings.translator_instance)  # type: ignore  # noqa: PGH003, E501
    reader.set_tag((), "global_send_errors_to_discord", global_settings.send_errors_to_discord)  # type: ignore  # noqa: PGH003, E501
    reader.set_tag((), "global_error_webhook", global_settings.error_webhook)  # type: ignore  # noqa: PGH003
