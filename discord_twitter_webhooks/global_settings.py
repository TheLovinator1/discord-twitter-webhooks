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
        elif global_tag[0] == "global_translator_instance":
            global_settings.translator_instance = str(global_tag[1])
        elif global_tag[0] == "global_send_errors_to_discord":
            global_settings.send_errors_to_discord = bool(global_tag[1])
        elif global_tag[0] == "global_send_errors_to_discord_webhook":
            global_settings.send_errors_to_discord_webhook = str(global_tag[1])
    return global_settings
