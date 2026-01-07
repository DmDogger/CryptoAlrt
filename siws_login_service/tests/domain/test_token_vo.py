import pytest

from src.domain.exceptions import TokenValidationError
from src.domain.value_objects.token_vo import TokenPairVO


class TestTokenPairVO:
    """Test suite for TokenPairVO value object."""

    def test_correct_pair(
        self,
        sample_token_vo: TokenPairVO,
    ) -> None:
        """Test that TokenPairVO is created correctly with valid JWT tokens.

        Args:
            sample_token_vo: Fixture providing a valid TokenPairVO instance.
        """
        assert isinstance(sample_token_vo, TokenPairVO)
        assert sample_token_vo.access_token == "access.token.test"
        assert sample_token_vo.refresh_token == "refresh.token.test"

    @pytest.mark.parametrize(
        "access, refresh",
        [
            ("not_3_parts", "not_3_parts"),
            (33, True),
            (None, -1),
            ("", ""),
        ],
    )
    def test_token_not_3_parts(
        self,
        access: str | int | None,
        refresh: str | bool | int | None,
    ) -> None:
        """Test that TokenValidationError is raised for invalid tokens.

        Tests various invalid token formats: non-JWT strings, non-string types,
        and empty strings.

        Args:
            access: Invalid access token value.
            refresh: Invalid refresh token value.
        """
        with pytest.raises(TokenValidationError):
            TokenPairVO.from_string(
                access_token=access,
                refresh_token=refresh,
            )
