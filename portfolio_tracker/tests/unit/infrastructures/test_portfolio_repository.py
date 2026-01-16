from decimal import Decimal

import pytest

from domain.entities.portfolio_entity import PortfolioEntity
from domain.exceptions import RepositoryError
from sqlalchemy.exc import SQLAlchemyError


class TestPortfolioRepository:
    @pytest.mark.asyncio
    async def test_get_portfolio_total_value(
        self,
        sample_portfolio_entity,
        mock_result_obj,
        mock_async_session,
        mock_portfolio_repository,
        mock_portfolio_mapper,
    ) -> None:
        mock_result_obj.one_or_none.return_value = (sample_portfolio_entity, Decimal("100"))
        mock_async_session.execute.return_value = mock_result_obj
        mock_portfolio_mapper.from_database.return_value = sample_portfolio_entity

        result = await mock_portfolio_repository.get_portfolio_total_value("test_wallet_address")

        assert len(result) == 2
        assert isinstance(result[0], PortfolioEntity)
        assert isinstance(result[1], Decimal)
        assert result[1] == Decimal("100")
        mock_async_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_portfolio_with_assets_and_prices(
        self,
        mock_result_obj,
        mock_portfolio_mapper,
        mock_async_session,
        sample_portfolio_entity,
        mock_portfolio_repository,
    ):

        mock_result_obj.scalar_one_or_none.return_value = sample_portfolio_entity
        mock_async_session.execute.return_value = mock_result_obj
        mock_portfolio_mapper.from_database.return_value = sample_portfolio_entity

        result = await mock_portfolio_repository.get_portfolio_with_assets_and_prices(
            "test_wallet_address"
        )

        assert len(result.assets) == 1
        mock_async_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_portfolio_with_assets_count(
        self,
        sample_portfolio_entity,
        sample_portfolio_db_model,
        mock_result_obj,
        mock_async_session,
        mock_portfolio_mapper,
        mock_portfolio_repository,
    ):

        mock_result_obj.unique.return_value = mock_result_obj
        mock_result_obj.one_or_none.return_value = (sample_portfolio_db_model, 10)
        mock_async_session.execute.return_value = mock_result_obj
        mock_portfolio_mapper.from_database.return_value = sample_portfolio_entity

        result = await mock_portfolio_repository.get_portfolio_with_assets_count(
            wallet_address="test_wallet_addr"
        )

        assert result[1] == 10
        assert isinstance(result[0], PortfolioEntity)

    @pytest.mark.parametrize(
        "exception_, expected_exception",
        [(SQLAlchemyError, RepositoryError), (Exception, RepositoryError)],
    )
    @pytest.mark.asyncio
    async def test_get_portfolio_with_assets_count_raises_error(
        self, exception_, expected_exception, mock_async_session, mock_portfolio_repository
    ):

        mock_async_session.execute.side_effect = exception_

        with pytest.raises(expected_exception):
            await mock_portfolio_repository.get_portfolio_with_assets_count(
                wallet_address="test_wallet_addr"
            )
