from enum import Enum
from typing import final


@final
class ChannelEnum(Enum):
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"