import pytest

from src.domain.exceptions import TokenValidationError
from src.domain.value_objects.token_vo import TokenPairVO
from src.infrastructures.exceptions import InfrastructureError


class TestTokensIssuerUC:
    @pytest.mark.asyncio
    async def test_correct(
        self, mock_tokens_issuer, fake_wallet_repository, sample_wallet_entity
    ):
        await fake_wallet_repository.create_wallet(
            wallet_entity=sample_wallet_entity,
        )

        tokens = await mock_tokens_issuer.execute(
            wallet_address=sample_wallet_entity.wallet_address.value
        )

        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert isinstance(tokens, TokenPairVO)

    @pytest.mark.parametrize(
        "exception_, expected_exception",
        [
            (TokenValidationError, TokenValidationError),
            (Exception, InfrastructureError),
        ],
    )
    @pytest.mark.asyncio
    async def test_raises(
        self,
        exception_: type[Exception],
        expected_exception: type[Exception],
        mock_tokens_issuer_with_mocks,
        fake_wallet_repository,
        sample_wallet_entity,
        mock_refresh_token_use_case_mock,
    ) -> None:
        """Test that TokensIssuerUseCase properly handles exceptions.

        Args:
            exception_: Exception type to raise.
            expected_exception: Expected exception type to be raised.
            mock_tokens_issuer_with_mocks: Fixture with mocked use cases.
            fake_wallet_repository: Fake wallet repository fixture.
            sample_wallet_entity: Sample wallet entity fixture.
            mock_refresh_token_use_case_mock: Mocked refresh token use case.
        """
        await fake_wallet_repository.create_wallet(
            wallet_entity=sample_wallet_entity,
        )

        mock_refresh_token_use_case_mock.execute.side_effect = exception_

        with pytest.raises(expected_exception):
            await mock_tokens_issuer_with_mocks.execute(
                wallet_address=sample_wallet_entity.wallet_address.value
            )
