from unittest.mock import AsyncMock, MagicMock
import pytest

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.domain.entities.nonce_entity import NonceEntity
from src.infrastructures.database.repositories.nonce_repository import SQLAlchemyNonceRepository
from src.infrastructures.database.mappers.nonce_mapper import NonceDBMapper
from src.infrastructures.database.models.nonce_model import Nonce
from src.infrastructures.exceptions import FailedToSaveNonceError


class TestNonceRepository:
    """Test suite for SQLAlchemyNonceRepository."""

    @pytest.mark.asyncio
    async def test_find_active_nonce_by_wallet_returns_entity_when_found(
        self,
        nonce_db_model: Nonce,
        sample_nonce_entity: NonceEntity,
        mock_result_obj: MagicMock,
        mock_async_session: AsyncMock,
        mock_nonce_repository: SQLAlchemyNonceRepository,
        mock_nonce_mapper: MagicMock,
    ) -> None:
        """Test that find_active_nonce_by_wallet returns entity when active nonce is found.

        Args:
            nonce_db_model: Sample nonce database model fixture.
            sample_nonce_entity: Sample nonce entity fixture.
            mock_result_obj: Mocked scalar result object.
            mock_async_session: Mocked async database session.
            mock_nonce_repository: Mocked nonce repository instance.
            mock_nonce_mapper: Mocked nonce mapper instance.
        """
        mock_result_obj.first.return_value = nonce_db_model
        mock_async_session.scalars.return_value = mock_result_obj
        mock_nonce_mapper.from_database_model.return_value = sample_nonce_entity

        result = await mock_nonce_repository.find_active_nonce_by_wallet("testbase58pubkey")

        assert result == sample_nonce_entity
        assert result.used_at is None
        mock_async_session.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_active_nonce_by_wallet_returns_none_when_not_found(
        self,
        nonce_db_model: Nonce,
        sample_nonce_entity: NonceEntity,
        mock_result_obj: MagicMock,
        mock_async_session: AsyncMock,
        mock_nonce_repository: SQLAlchemyNonceRepository,
        mock_nonce_mapper: MagicMock,
    ) -> None:
        """Test that find_active_nonce_by_wallet returns None when no active nonce is found.

        Args:
            nonce_db_model: Sample nonce database model fixture.
            sample_nonce_entity: Sample nonce entity fixture.
            mock_result_obj: Mocked scalar result object.
            mock_async_session: Mocked async database session.
            mock_nonce_repository: Mocked nonce repository instance.
            mock_nonce_mapper: Mocked nonce mapper instance.
        """
        mock_result_obj.first.return_value = None
        mock_async_session.scalars.return_value = mock_result_obj

        result = await mock_nonce_repository.find_active_nonce_by_wallet("testbase58pubkey")

        assert result is None
        mock_async_session.scalars.assert_called_once()
        mock_nonce_mapper.from_database_model.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_nonce_saves_to_database(
        self,
        mock_nonce_mapper: MagicMock,
        nonce_db_model: Nonce,
        sample_nonce_entity: NonceEntity,
        mock_nonce_repository: SQLAlchemyNonceRepository,
        mock_async_session: AsyncMock,
    ) -> None:
        """Test that create_nonce saves entity to database and commits transaction.

        Args:
            mock_nonce_mapper: Mocked nonce mapper instance.
            nonce_db_model: Sample nonce database model fixture.
            sample_nonce_entity: Sample nonce entity fixture.
            mock_nonce_repository: Mocked nonce repository instance.
            mock_async_session: Mocked async database session.
        """
        mock_nonce_mapper.to_database_model.return_value = nonce_db_model
        mock_nonce_mapper.from_database_model.return_value = sample_nonce_entity

        result = await mock_nonce_repository.create_nonce(sample_nonce_entity)

        assert result == sample_nonce_entity
        mock_async_session.add.assert_called_once()
        mock_async_session.commit.assert_called_once()
        mock_async_session.rollback.assert_not_called()

    @pytest.mark.parametrize(
        "exception_",
        [
            SQLAlchemyError,
            IntegrityError(statement="", params=None, orig=None),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_nonce_raises_error(
        self,
        mock_async_session: AsyncMock,
        exception_: type[Exception] | Exception,
        mock_nonce_repository: SQLAlchemyNonceRepository,
        sample_nonce_entity: NonceEntity,
    ) -> None:
        """Test that create_nonce raises FailedToSaveNonceError on database exceptions.

        Args:
            mock_async_session: Mocked async database session.
            exception_: Exception type or instance to raise (SQLAlchemyError or IntegrityError).
            mock_nonce_repository: Mocked nonce repository instance.
            sample_nonce_entity: Sample nonce entity fixture.
        """
        mock_async_session.add.side_effect = exception_

        with pytest.raises(FailedToSaveNonceError):
            await mock_nonce_repository.create_nonce(sample_nonce_entity)

        mock_async_session.rollback.assert_called_once()
        mock_async_session.commit.assert_not_called()


