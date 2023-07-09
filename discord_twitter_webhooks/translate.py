import deepl
from loguru import logger

from _dataclasses import get_app_settings
from reader_settings import get_reader

_languages = {
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

languages_from = _languages.copy()
languages_from["auto"] = "Automatic"
languages_from["en"] = "English"
languages_from["pt"] = "Portuguese"

languages_to = _languages.copy()
languages_to["en-GB"] = "English (British)"
languages_to["en-US"] = "English (American)"
languages_to["pt-BR"] = "Portuguese (Brazilian)"
languages_to["pt-PT"] = "Portuguese (European)"


def translate_html(html: str, translate_from: str = "auto", translate_to: languages_to = "en") -> str:
    """Translate HTML text to another language."""
    auth_key = get_app_settings(get_reader()).deepl_auth_key
    if not auth_key:
        logger.warning("No DeepL auth key set. Not translating.")
        return html

    translator = deepl.Translator(auth_key)
    result = translator.translate_text(html, target_lang=translate_to, source_lang=translate_from, tag_handling="html")
    return result.text
