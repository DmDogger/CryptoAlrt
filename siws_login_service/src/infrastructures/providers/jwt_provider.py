"""JWT providers for Dishka dependency injection."""

from dishka import Provider, Scope, provide

from src.application.interfaces.token_issuer import (
    AccessTokenIssuerProtocol,
    RefreshTokenIssuerProtocol,
)
from src.config.jwt import JWTSettings
from src.infrastructures.jwt.token_issuer import (
    JWTAccessIssuer,
    JWTRefreshIssuer,
)


class JWTProvider(Provider):
    """Provider for JWT-related dependencies."""

    @provide(scope=Scope.APP)
    def provide_jwt_settings(self) -> JWTSettings:
        """Provide JWTSettings instance."""
        return JWTSettings()

    @provide(scope=Scope.APP)
    def provide_access_token_issuer(
        self,
        jwt_settings: JWTSettings,
    ) -> AccessTokenIssuerProtocol:
        """Provide JWTAccessIssuer instance."""
        return JWTAccessIssuer(_jwt_settings=jwt_settings)

    @provide(scope=Scope.APP)
    def provide_refresh_token_issuer(
        self,
        jwt_settings: JWTSettings,
    ) -> RefreshTokenIssuerProtocol:
        """Provide JWTRefreshIssuer instance."""
        return JWTRefreshIssuer(_jwt_settings=jwt_settings)
