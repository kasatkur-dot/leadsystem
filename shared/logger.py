from loguru import logger
import sys

logger.remove()

logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[agent]}</cyan> | {message}",
    level="DEBUG",
    colorize=True,
)

logger.add(
    "logs/lead_engine.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[agent]} | {message}",
    level="INFO",
    rotation="1 week",
    retention="1 month",
    encoding="utf-8",
)


def get_logger(agent_name: str):
    return logger.bind(agent=agent_name)
