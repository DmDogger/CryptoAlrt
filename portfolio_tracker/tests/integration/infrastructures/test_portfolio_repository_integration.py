from decimal import Decimal
from collections.abc import Callable, Coroutine

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructures.database.models.asset import Asset
from infrastructures.database.models.cryptoprice import CryptoPrice
from infrastructures.database.mappers.asset_db_mapper import AssetDBMapper
from domain.entities.portfolio_entity import PortfolioEntity
from infrastructures.database.repositories.portfolio import SQLAlchemyPortfolioRepository

from domain.value_objects.analytics_vo import AnalyticsValueObject

from domain.entities.asset_entity import AssetEntity
from fixtures.domain_fixtures import integration_portfolio_entity, sample_uuid, sample_asset_entity
from fixtures.infra_fixtures import portfolio_repository_for_transactions, async_session


class TestPortfolioRepository:
    @pytest.mark.asyncio
    async def test_get_portfolio_with_assets_and_prices(
        self,
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        fill_integration_base_fields: None,
        async_session: AsyncSession,
    ) -> None:
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
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        fill_integration_base_fields: None,
        async_session: AsyncSession,
    ) -> None:
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
    async def test_get_portfolio_with_assets_count_and_update(
        self,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        integration_empty_portfolio_entity: PortfolioEntity,
        fill_integration_base_fields: None,
        async_session: AsyncSession,
    ) -> None:
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
    async def test_save_portfolio_without_assets_then_add_assets(
        self,
        async_session: AsyncSession,
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        add_asset_and_crypto_price_for_portfolio: Callable[[], Coroutine[None, None, None]],
    ) -> None:
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
    async def test_update_portfolio_total_value(
        self,
        async_session: AsyncSession,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        integration_portfolio_entity: PortfolioEntity,
        fill_integration_base_fields: None,
    ) -> None:

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

    @pytest.mark.asyncio
    async def test_get_position_value(
        self,
        async_session: AsyncSession,
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        fill_integration_base_fields: None,
    ):

        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        analytics_vo = await portfolio_repository_for_transactions.get_position_value(
            ticker="BTC",
            wallet_address=integration_portfolio_entity.wallet_address,
        )

        assert isinstance(analytics_vo, AnalyticsValueObject)
        assert analytics_vo.position_value is not None
        assert analytics_vo.ticker is not None

    @pytest.mark.asyncio
    async def test_get_position_values(
        self,
        async_session: AsyncSession,
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        fill_integration_base_fields: None,
    ):

        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        analytics_vo_list = await portfolio_repository_for_transactions.get_position_values(
            wallet_address=integration_portfolio_entity.wallet_address,
        )

        assert len(analytics_vo_list) > 0
        assert all(isinstance(a, AnalyticsValueObject) for a in analytics_vo_list)

    @pytest.mark.asyncio
    async def test_get_portfolio_total_value_only(
        self,
        integration_portfolio_entity: PortfolioEntity,
        async_session: AsyncSession,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        fill_integration_base_fields: None,
    ):

        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        dec_res = await portfolio_repository_for_transactions.get_portfolio_total_value_only(
            wallet_address=integration_portfolio_entity.wallet_address
        )

        assert isinstance(dec_res, Decimal)

    @pytest.mark.asyncio
    async def test_get_portfolio_total_value_only_returns_none_when_no_assets(
        self,
        integration_portfolio_entity: PortfolioEntity,
        async_session: AsyncSession,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
    ):

        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        none_res = await portfolio_repository_for_transactions.get_portfolio_total_value_only(
            wallet_address=integration_portfolio_entity.wallet_address
        )

        assert none_res is None

    @pytest.mark.asyncio
    async def test_get_current_and_last_prices(
        self,
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        fill_integration_base_fields: None,
        async_session: AsyncSession,
    ):
        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        curr_price, last_price = (
            await portfolio_repository_for_transactions.get_current_and_last_prices(
                ticker="BTC",
                hours=48,  # by default is 24h.
            )
        )

        assert last_price is not None and curr_price is not None
        assert isinstance(last_price, Decimal) and isinstance(curr_price, Decimal)
        assert last_price < curr_price

    @pytest.mark.asyncio
    async def test_get_counted_assets(
        self,
        integration_portfolio_entity: PortfolioEntity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        fill_integration_base_fields: None,
        async_session: AsyncSession,
    ):
        await portfolio_repository_for_transactions.save_portfolio(integration_portfolio_entity)

        await async_session.commit()

        counted_assets = await portfolio_repository_for_transactions.get_assets_counted(
            wallet_address=integration_portfolio_entity.wallet_address
        )

        assert isinstance(counted_assets, int)
        assert counted_assets == 1

    @pytest.mark.asyncio
    async def test_get_asset_by_id_returns_none_when_not_found(
        self,
        sample_uuid,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
    ):
        none_asset = await portfolio_repository_for_transactions.get_asset_by_id(
            asset_id=sample_uuid
        )

        assert none_asset is None

    @pytest.mark.asyncio
    async def test_add_asset_saves_to_database(
        self,
        sample_asset_entity: AssetEntity,
        integration_portfolio_entity,
        portfolio_repository_for_transactions: SQLAlchemyPortfolioRepository,
        async_session: AsyncSession,
    ):
        portfolio = PortfolioEntity.create(wallet_address=sample_asset_entity.wallet_address)

        await portfolio_repository_for_transactions.save_portfolio(portfolio)
        await async_session.commit()

        asset = await portfolio_repository_for_transactions.add_asset(sample_asset_entity)
        await async_session.commit()

        retrieved_asset = await portfolio_repository_for_transactions.get_asset_by_id(
            sample_asset_entity.asset_id
        )

        assert asset == retrieved_asset

    @pytest.mark.asyncio
    async def test_update_asset_works_correctly(
        self,
        portfolio_repository_for_transactions,
        integration_portfolio_entity,
        fill_eth_price: None,
        async_session: AsyncSession,
    ):
        portfolio = PortfolioEntity.create(
            wallet_address=integration_portfolio_entity.wallet_address
        )
        await portfolio_repository_for_transactions.save_portfolio(portfolio)
        await async_session.commit()

        asset_entity = integration_portfolio_entity.assets[0]
        await portfolio_repository_for_transactions.add_asset(asset_entity)
        await async_session.commit()

        with_new_ticker = asset_entity.change_ticker(ticker="ETH")
        await portfolio_repository_for_transactions.update_asset(with_new_ticker)
        await async_session.commit()

        with_new_ticker_from_db = await portfolio_repository_for_transactions.get_asset_by_id(
            asset_entity.asset_id
        )

        assert with_new_ticker_from_db is not None
        assert with_new_ticker_from_db.ticker == "ETH"
