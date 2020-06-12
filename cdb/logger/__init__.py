import os
from .message import bot

# Shared logging import for both client and default.py (for headless)
CDB_LOG_LEVEL = os.environ.get("CDB_LOG_LEVEL", "INFO")
CDB_LOG_LEVELS = ["DEBUG", "CRITICAL", "ERROR", "WARNING", "INFO", "QUIET", "FATAL"]
if CDB_LOG_LEVEL not in CDB_LOG_LEVELS:
    CDB_LOG_LEVEL = "INFO"
