import sys

import tweepy

from discord_twitter_webhooks import settings


def check_rules(stream) -> None:
    """Check if we have any old rules and delete them if we do.

    Args:
        stream (_type_): The tweepy stream object
    """

    # Check Twitter app for rules that already have been created
    old_rules = stream.get_rules()
    settings.logger.debug(f"Old rules: {old_rules}")

    # Get rules and add to list so we can delete them later
    rules_to_delete = []
    if old_rules.data and len(old_rules.data) > 0:
        for old_rule in old_rules.data:
            settings.logger.debug(f"Added {old_rule.value} - {old_rule.id} for deletion")  # noqa: E501, pylint: disable=line-too-long
            rules_to_delete.append(old_rule.id)

    # TODO: Only remove rule if the user list has changed?
    # If the app already has rules, delete them first before adding our own
    if rules_to_delete:
        settings.logger.debug(f"Deleting rules: {rules_to_delete}")
        stream.delete_rules(rules_to_delete)
    else:
        settings.logger.debug("App had no rules to delete")


def add_new_rule(stream) -> None:
    """Add rule to Twitter. If error, exit."""
    # This is our user created rule
    print(f"Adding new rule: {settings.rule} ")
    rule_to_add = tweepy.StreamRule(value=settings.rule)

    # TODO: Add support for several rules and add support for writing to
    # different channels

    rule_response = stream.add_rules(add=rule_to_add)

    if rule_response.errors:
        for error in rule_response.errors:
            settings.logger.error(f"\nFound error for: {error['value']}")
            settings.logger.error(f"{error['title']} - Error details: {error['details'][0]}")  # noqa: E501, pylint: disable=line-too-long
        sys.exit(1)
