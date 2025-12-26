from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WalletEntity: ...

