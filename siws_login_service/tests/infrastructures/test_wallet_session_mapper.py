"""Tests for WalletSessionDBMapper."""

from src.infrastructures.database.mappers.wallet_session_mapper import (
    WalletSessionDBMapper,
)


class TestWalletSessionDBMapper:
    """Test suite for WalletSessionDBMapper."""

    def test_correct_from_db_model(
        self,
        wallet_session_mapper_from_db_model,
        sample_db_wallet_session_model,
    ) -> None:
        """Test that from_database_model() correctly converts WalletSession to WalletSessionVO.

        Args:
            wallet_session_mapper_from_db_model: Fixture providing WalletSessionVO from DB model.
            sample_db_wallet_session_model: Fixture providing the original WalletSession DB model.
        """
        entity = wallet_session_mapper_from_db_model

        assert (
            entity.wallet_address.value == sample_db_wallet_session_model.wallet_address
        )
        assert entity.device_id == sample_db_wallet_session_model.device_id
        assert (
            entity.refresh_token_hash
            == sample_db_wallet_session_model.refresh_token_hash
        )
        assert entity.is_revoked == sample_db_wallet_session_model.is_revoked
        assert entity.created_at == sample_db_wallet_session_model.created_at

    def test_correct_to_db_model(
        self,
        wallet_session_db_model,
        sample_wallet_session_vo,
    ) -> None:
        """Test that to_database_model() correctly converts WalletSessionVO to WalletSession.

        Args:
            wallet_session_db_model: Fixture providing WalletSession from WalletSessionVO.
            sample_wallet_session_vo: Fixture providing the original WalletSessionVO.
        """
        db_model = wallet_session_db_model

        assert db_model.wallet_address == sample_wallet_session_vo.wallet_address.value
        assert db_model.device_id == sample_wallet_session_vo.device_id
        assert (
            db_model.refresh_token_hash == sample_wallet_session_vo.refresh_token_hash
        )
        assert db_model.is_revoked == sample_wallet_session_vo.is_revoked
        assert db_model.created_at == sample_wallet_session_vo.created_at

    def test_round_trip_conversion(
        self,
        sample_wallet_session_vo,
    ) -> None:
        """Test that converting entity -> DB model -> entity preserves all data.

        Args:
            sample_wallet_session_vo: Fixture providing a valid WalletSessionVO instance.
        """
        db_model = WalletSessionDBMapper.to_database_model(sample_wallet_session_vo)

        restored_entity = WalletSessionDBMapper.from_database_model(db_model)

        assert (
            restored_entity.wallet_address.value
            == sample_wallet_session_vo.wallet_address.value
        )
        assert restored_entity.device_id == sample_wallet_session_vo.device_id
        assert (
            restored_entity.refresh_token_hash
            == sample_wallet_session_vo.refresh_token_hash
        )
        assert restored_entity.is_revoked == sample_wallet_session_vo.is_revoked
        assert restored_entity.created_at == sample_wallet_session_vo.created_at
