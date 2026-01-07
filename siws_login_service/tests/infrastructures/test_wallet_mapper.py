"""Tests for WalletDBMapper."""

from src.infrastructures.database.mappers.wallet_mapper import WalletDBMapper


class TestWalletDBMapper:
    """Test suite for WalletDBMapper."""

    def test_correct_from_db_model(
        self,
        wallet_mapper_from_db_model,
        sample_db_wallet_model,
    ) -> None:
        """Test that from_database_model() correctly converts Wallet to WalletEntity.

        Args:
            wallet_mapper_from_db_model: Fixture providing WalletEntity from DB model.
            sample_db_wallet_model: Fixture providing the original Wallet DB model.
        """
        entity = wallet_mapper_from_db_model

        assert entity.uuid == sample_db_wallet_model.uuid
        assert entity.wallet_address.value == sample_db_wallet_model.wallet_address
        assert entity.last_active == sample_db_wallet_model.last_active
        assert entity.created_at == sample_db_wallet_model.created_at

    def test_correct_to_db_model(
        self,
        wallet_db_model,
        sample_wallet_entity,
    ) -> None:
        """Test that to_database_model() correctly converts WalletEntity to Wallet.

        Args:
            wallet_db_model: Fixture providing Wallet from WalletEntity.
            sample_wallet_entity: Fixture providing the original WalletEntity.
        """
        db_model = wallet_db_model

        assert db_model.uuid == sample_wallet_entity.uuid
        assert db_model.wallet_address == sample_wallet_entity.wallet_address.value
        assert db_model.last_active == sample_wallet_entity.last_active
        assert db_model.created_at == sample_wallet_entity.created_at

    def test_round_trip_conversion(
        self,
        sample_wallet_entity,
    ) -> None:
        """Test that converting entity -> DB model -> entity preserves all data.

        Args:
            sample_wallet_entity: Fixture providing a valid WalletEntity instance.
        """
        db_model = WalletDBMapper.to_database_model(sample_wallet_entity)

        restored_entity = WalletDBMapper.from_database_model(db_model)

        assert restored_entity.uuid == sample_wallet_entity.uuid
        assert (
            restored_entity.wallet_address.value
            == sample_wallet_entity.wallet_address.value
        )
        assert restored_entity.last_active == sample_wallet_entity.last_active
        assert restored_entity.created_at == sample_wallet_entity.created_at
