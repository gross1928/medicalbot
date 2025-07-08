"""
Telegram Bot модуль
"""

from .handlers import setup_handlers
from .bot import MedicalBot

__all__ = [
    "setup_handlers",
    "MedicalBot",
] 