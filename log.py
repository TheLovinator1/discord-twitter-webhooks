import logging.config
import config

# Logger
formatter = logging.Formatter("%(asctime)s %(levelname)-12s %(message)s")
logger = logging.getLogger()
handler = logging.StreamHandler()

# Log to file
if config.parser.getboolean("logging", "log_to_file"):
    file_handler = logging.FileHandler(config.parser.get("logging", "log_name"))
    level = logging.getLevelName(config.log_level_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Log to console
handler.setFormatter(formatter)
logger.addHandler(handler)

# CRITICAL, ERROR, WARNING, INFO, DEBUG
level = logging.getLevelName(config.log_level)
logger.setLevel(level)
