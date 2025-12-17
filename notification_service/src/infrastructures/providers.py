from typing import AsyncIterable

import aiosmtplib
from dishka import Provider, Scope, provide

from config.smtp import smtp_settings


class InfrastructureProvider(Provider):
    """Провайдер для инфраструктурного слоя."""
    
    @provide(scope=Scope.REQUEST)
    async def get_smtp_client(self) -> AsyncIterable[aiosmtplib.SMTP]:
        """SMTP client для каждого запроса с контекстным менеджером."""
        smtp = aiosmtplib.SMTP(
            hostname=smtp_settings.host,
            port=smtp_settings.port,
            use_tls=smtp_settings.use_tls,
        )
        await smtp.connect()
        await smtp.login(smtp_settings.username, smtp_settings.password)
        try:
            yield smtp
        finally:
            await smtp.quit()
