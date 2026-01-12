from decimal import Decimal

import pytest

from infrastructures.database.models.asset import Asset
from infrastructures.database.models.cryptoprice import CryptoPrice
from infrastructures.database.mappers.asset_db_mapper import AssetDBMapper
from domain.entities.portfolio_entity import PortfolioEntity


class TestPortfolioRepository:
    @pytest.mark.asyncio
    async def test_get_portfolio_with_assets_and_prices(
        self,
        integration_portfolio_entity,
        portfolio_repository_for_transactions,
        fill_integration_base_fields,
        async_session,
    ):
        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)
        await async_session.commit()

        portfolio = (
            await portfolio_repository_for_transactions.get_portfolio_with_assets_and_prices(
                wallet_address=integration_portfolio_entity.wallet_address
            )
        )

        assert isinstance(portfolio, PortfolioEntity)

    @pytest.mark.asyncio
    async def test_calculate_and_update_portfolio_total_value(
        self,
        integration_portfolio_entity,
        portfolio_repository_for_transactions,
        fill_integration_base_fields,
        async_session,
    ):
        """Integration test confirms that calculation total value & updating portfolio works correct"""
        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)
        await async_session.commit()

        portfolio, calculated_total_value = (
            await portfolio_repository_for_transactions.get_portfolio_total_value(
                wallet_address=integration_portfolio_entity.wallet_address
            )
        )

        assert isinstance(portfolio, PortfolioEntity)
        assert isinstance(calculated_total_value, Decimal)

        portfolio_with_total_value = portfolio.set_total_value(total_value=calculated_total_value)
        updated_portfolio = await portfolio_repository_for_transactions.update_portfolio(
            portfolio_with_total_value
        )

        assert isinstance(updated_portfolio, PortfolioEntity)
        assert updated_portfolio.total_value is not None

    @pytest.mark.asyncio
    async def test_get_counted_assets_and_update(
        self,
        portfolio_repository_for_transactions,
        integration_empty_portfolio_entity,
        fill_integration_base_fields,
        async_session,
    ):
        await portfolio_repository_for_transactions.save_portfolio(
            integration_empty_portfolio_entity
        )
        await async_session.commit()

        portfolio, assets_counted = (
            await portfolio_repository_for_transactions.get_portfolio_with_assets_count(
                wallet_address=integration_empty_portfolio_entity.wallet_address
            )
        )

        with_counted = portfolio.set_counted_assets(assets_counted)
        result = await portfolio_repository_for_transactions.update_portfolio(with_counted)

        await async_session.commit()

        assert result is not None
        assert result.assets_count == 1

    @pytest.mark.asyncio
    async def test_portfolio_saves_correctly(
        self,
        async_session,
        integration_portfolio_entity,
        portfolio_repository_for_transactions,
        add_asset_and_crypto_price_for_portfolio,
    ):
        portfolio_to_save = await portfolio_repository_for_transactions.save_portfolio(
            integration_portfolio_entity
        )
        not_saved = (
            await portfolio_repository_for_transactions.get_portfolio_with_assets_and_prices(
                portfolio_to_save.wallet_address
            )
        )

        assert not_saved is None

        await add_asset_and_crypto_price_for_portfolio()
        await async_session.commit()

        saved = await portfolio_repository_for_transactions.get_portfolio_with_assets_and_prices(
            portfolio_to_save.wallet_address
        )

        assert saved is not None

    @pytest.mark.asyncio
    async def test_portfolio_updates_correctly(
        self,
        async_session,
        portfolio_repository_for_transactions,
        integration_portfolio_entity,
        fill_integration_base_fields,
    ):

        saved = await portfolio_repository_for_transactions.save_portfolio(
            integration_portfolio_entity
        )
        await async_session.commit()

        data_to_update = integration_portfolio_entity.set_total_value(Decimal("100_000_000"))

        assert saved.total_value != Decimal("100_000_000")

        await portfolio_repository_for_transactions.update_portfolio(data_to_update)

        await async_session.commit()

        updated_portfolio = (
            await portfolio_repository_for_transactions.get_portfolio_with_assets_and_prices(
                wallet_address=integration_portfolio_entity.wallet_address
            )
        )

        assert updated_portfolio is not None
        assert updated_portfolio.total_value == Decimal("100_000_000")
