from dhooks import Webhook

from discord_twitter_webhooks.settings import logger, webhook_url


def send_text_webhook(text: str, webhook: str = webhook_url) -> None:
    """Send text to webhook.

    Args:
        text (str): Text to send to webhook
        webhook (str, optional): Webhook URL. Defaults to environment variable WEBHOOK_URL.
    """
    logger.debug(f"Webhook text: {text} sent to {webhook}")
    hook = Webhook(webhook)
    hook.send(text)
