from dataclasses import dataclass
from typing import final

from src.domain.value_objects.wallet_session_vo import WalletSessionVO
from src.domain.value_objects.wallet_vo import WalletAddressVO
from src.infrastructures.database.models.wallet_model import WalletSession


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class WalletSessionDBMapper:
    @staticmethod
    def to_database_model(value_object: WalletSessionVO) -> WalletSession:
        return WalletSession(
            wallet_address=value_object.wallet_address.value,
            device_id=value_object.device_id,
            refresh_token_hash=value_object.refresh_token_hash,
            is_revoked=value_object.is_revoked,
            created_at=value_object.created_at,
        )

    @staticmethod
    def from_database_model(wallet_session: WalletSession) -> WalletSessionVO:
        return WalletSessionVO(
            wallet_address=WalletAddressVO.from_string(wallet_session.wallet_address),
            device_id=wallet_session.device_id,
            refresh_token_hash=wallet_session.refresh_token_hash,
            is_revoked=wallet_session.is_revoked,
            created_at=wallet_session.created_at,
        )
