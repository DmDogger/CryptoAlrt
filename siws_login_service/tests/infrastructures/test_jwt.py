import jwt
from freezegun import freeze_time

from src.config.jwt import jwt_settings
from src.infrastructures.jwt.token_issuer import JWTAccessIssuer, JWTRefreshIssuer


class TestJWTAccessIssuer:
    """Test suite for JWTAccessIssuer."""

    @freeze_time("2030-01-01 08:00:00")
    def test_issue_creates_valid_jwt_token_with_correct_payload(
        self, mock_access_issuer: JWTAccessIssuer
    ) -> None:
        """Test that JWTAccessIssuer correctly issues JWT tokens with valid signature.

        Verifies that issued token can be decoded, contains correct payload fields,
        and has valid signature that can be verified with public key.

        Args:
            mock_access_issuer: Fixture providing JWTAccessIssuer with test settings.
        """
        result = mock_access_issuer.issue(sub="test_sub", ttl=3)

        assert result is not None
        assert isinstance(result, str)

        decoded = jwt.decode(
            result,
            mock_access_issuer._jwt_settings.public_key,
            verify=True,
            algorithms=["EdDSA"],
        )

        assert decoded["sub"] == "test_sub"
        assert decoded["iss"] == "cryptoalrt.io"
        assert decoded["exp"] == 1893484980


class TestJWTRefreshIssuer:
    """Test suite for JWTRefreshIssuer."""

    @freeze_time("2030-01-01 08:00:00")
    def test_issue_created_valid_refresh_jwt_token_with_correct_payload(
        self,
        mock_refresh_issuer: JWTRefreshIssuer,
    ) -> None:
        """Test that JWTRefreshIssuer correctly issues refresh JWT tokens.

        Args:
            mock_refresh_issuer: Fixture providing JWTRefreshIssuer with test settings.
        """
        result_jwt = mock_refresh_issuer.issue(sub="test_sub_refresh", device_id="str", ttl=3)

        assert result_jwt is not None
        assert isinstance(result_jwt, str)

        decoded = jwt.decode(
            result_jwt,
            jwt_settings.public_key,
            verify=True,
            algorithms=["EdDSA"],
        )

        assert decoded["sub"] == "test_sub_refresh"
        assert decoded["iss"] == "cryptoalrt.io"
        assert decoded["exp"] == 1893484980
        assert decoded["jti"] is not None
        assert isinstance(decoded["jti"], str)
