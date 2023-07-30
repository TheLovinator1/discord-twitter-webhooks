from typing import TYPE_CHECKING

import deepl
from loguru import logger

from discord_twitter_webhooks._dataclasses import get_app_settings
from discord_twitter_webhooks.reader_settings import get_reader

if TYPE_CHECKING:
    from deepl.translator import TextResult

_languages: dict[str, str] = {
    "bg": "Bulgarian",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "es": "Spanish",
    "et": "Estonian",
    "fi": "Finnish",
    "fr": "French",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "nb": "Norwegian",
    "nl": "Dutch",
    "pl": "Polish",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sv": "Swedish",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "zh": "Chinese",
}

languages_from: dict[str, str] = _languages.copy()
languages_from["auto"] = "Automatic"
languages_from["en"] = "English"
languages_from["pt"] = "Portuguese"

languages_to: dict[str, str] = _languages.copy()
languages_to["en-GB"] = "English (British)"
languages_to["en-US"] = "English (American)"
languages_to["pt-BR"] = "Portuguese (Brazilian)"
languages_to["pt-PT"] = "Portuguese (European)"


def translate_html(html: str, translate_from: str | None = "auto", translate_to: str = "en") -> str:
    """Translate HTML text to another language."""
    if translate_from == "auto":
        logger.debug("Auto-detecting language when translating.")
        translate_from = None

    auth_key: str = get_app_settings(get_reader()).deepl_auth_key
    if not auth_key:
        logger.error("No DeepL auth key set. Not translating.")
        return html

    try:
        translator = deepl.Translator(auth_key)
        result: TextResult | list[TextResult] = translator.translate_text(
            html,
            target_lang=translate_to,
            source_lang=translate_from,
            tag_handling="html",
        )
    except deepl.exceptions.DeepLException as e:
        logger.error("Error while translating: {}", e)
        return html

    if isinstance(result, list):
        return "\n".join([r.text for r in result])

    return result.text
