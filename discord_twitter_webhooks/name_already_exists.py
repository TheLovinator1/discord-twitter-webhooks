from reader import Reader


def name_already_exists(reader: Reader, name: str) -> bool:
    """Return True if the name already exists."""
    global_tags = reader.get_tags(())
    return any(global_tag[0].startswith(f"{name}_") for global_tag in global_tags)
