import pytest
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from unittest.mock import AsyncMock, MagicMock

from infrastructures.exceptions import FailedToSaveWalletError
from infrastructures.database.repositories.wallet_repository import SQLAlchemyWalletRepository
from domain.entities.wallet_entity import WalletEntity
from infrastructures.database.models.wallet_model import Wallet


class TestWalletRepository:
    """Test suite for SQLAlchemyWalletRepository."""

    @pytest.mark.asyncio
    async def test_get_wallet_by_address_returns_entity_when_found(
        self,
        mock_result_obj: MagicMock,
        mock_wallet_repository: SQLAlchemyWalletRepository,
        sample_wallet_entity: WalletEntity,
        mock_async_session: AsyncMock,
        mock_wallet_mapper: MagicMock,
    ) -> None:
        """Test that get_wallet_by_address returns entity when wallet is found.

        Args:
            mock_result_obj: Mocked scalar result object.
            mock_wallet_repository: Mocked wallet repository instance.
            sample_wallet_entity: Sample wallet entity fixture.
            mock_async_session: Mocked async database session.
            mock_wallet_mapper: Mocked wallet mapper instance.
        """
        mock_result_obj.first.return_value = sample_wallet_entity

        mock_async_session.scalars.return_value = mock_result_obj
        mock_wallet_mapper.from_database_model.return_value = sample_wallet_entity

        res = await mock_wallet_repository.get_wallet_by_address("wallet")

        assert res == sample_wallet_entity

    @pytest.mark.asyncio
    async def test_get_wallet_by_address_returns_none_when_not_found(
        self,
        mock_result_obj: MagicMock,
        mock_async_session: AsyncMock,
        mock_wallet_repository: SQLAlchemyWalletRepository,
    ) -> None:
        """Test that get_wallet_by_address returns None when wallet is not found.

        Args:
            mock_result_obj: Mocked scalar result object.
            mock_async_session: Mocked async database session.
            mock_wallet_repository: Mocked wallet repository instance.
        """
        mock_result_obj.first.return_value = None
        mock_async_session.scalars.return_value = mock_result_obj

        res = await mock_wallet_repository.get_wallet_by_address("wallet")

        assert res is None

    @pytest.mark.asyncio
    async def test_create_wallet_saves_to_database(
        self,
        sample_wallet_entity: WalletEntity,
        wallet_db_model: Wallet,
        mock_wallet_repository: SQLAlchemyWalletRepository,
        mock_wallet_mapper: MagicMock,
        mock_async_session: AsyncMock,
    ) -> None:
        """Test that create_wallet saves entity to database and commits transaction.

        Args:
            sample_wallet_entity: Sample wallet entity fixture.
            wallet_db_model: Sample wallet database model fixture.
            mock_wallet_repository: Mocked wallet repository instance.
            mock_wallet_mapper: Mocked wallet mapper instance.
            mock_async_session: Mocked async database session.
        """
        mock_wallet_mapper.to_database_model.return_value = wallet_db_model
        mock_wallet_mapper.from_database_model.return_value = sample_wallet_entity

        result = await mock_wallet_repository.create_wallet(sample_wallet_entity)

        assert result == sample_wallet_entity
        mock_async_session.commit.assert_called_once()
        mock_async_session.add.assert_called_with(wallet_db_model)

    @pytest.mark.parametrize(
        "exception_",
        [
            IntegrityError(params=None, statement="", orig=None),
            SQLAlchemyError,
        ],
    )
    @pytest.mark.asyncio
    async def test_create_wallet_raises_error_on_database_exception(
        self,
        mock_async_session: AsyncMock,
        exception_: type[Exception],
        mock_wallet_repository: SQLAlchemyWalletRepository,
        sample_wallet_entity: WalletEntity,
    ) -> None:
        """Test that create_wallet raises FailedToSaveWalletError on database exceptions.

        Args:
            mock_async_session: Mocked async database session.
            exception_: Exception type to raise (IntegrityError or SQLAlchemyError).
            mock_wallet_repository: Mocked wallet repository instance.
            sample_wallet_entity: Sample wallet entity fixture.
        """
        mock_async_session.add.side_effect = exception_

        with pytest.raises(FailedToSaveWalletError):
            await mock_wallet_repository.create_wallet(sample_wallet_entity)

        mock_async_session.rollback.assert_called_once()
        mock_async_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_values_updates_wallet_successfully(
        self,
        mock_async_session: AsyncMock,
        mock_wallet_repository: SQLAlchemyWalletRepository,
        sample_wallet_entity: WalletEntity,
        mock_result_obj: MagicMock,
        wallet_db_model: Wallet,
        mock_wallet_mapper: MagicMock,
    ) -> None:
        """Test that update_values updates wallet entity and commits transaction.

        Args:
            mock_async_session: Mocked async database session.
            mock_wallet_repository: Mocked wallet repository instance.
            sample_wallet_entity: Sample wallet entity fixture.
            mock_result_obj: Mocked result object from execute.
            wallet_db_model: Sample wallet database model fixture.
            mock_wallet_mapper: Mocked wallet mapper instance.
        """
        mock_result_obj.scalar_one_or_none.return_value = wallet_db_model
        mock_async_session.execute.return_value = mock_result_obj
        mock_wallet_mapper.from_database_model.return_value = sample_wallet_entity

        result = await mock_wallet_repository.update_values(
            wallet_address="5cRypRAdKEUtMCyFdqtEifWER5GMCfVnhZ8EUtcB7Sc3",
            wallet_entity=sample_wallet_entity,
        )

        assert result == sample_wallet_entity
        mock_async_session.execute.assert_called_once()
        mock_async_session.commit.assert_called_once()
