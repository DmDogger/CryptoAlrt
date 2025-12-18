import aiosmtplib
from email.message import EmailMessage

import structlog

from config.smtp import smtp_settings
from application.interfaces.email_client import EmailClientProtocol
from domain.exceptions import EmailSendingError

logger = structlog.getLogger(__name__)


class SMTPEmailClient(EmailClientProtocol):
    """SMTP email client implementation.
    
    Uses aiosmtplib for async SMTP operations with context manager support.
    """
    
    def __init__(self, smtp: aiosmtplib.SMTP):
        """Initialize SMTP email client.
        
        Args:
            smtp: Connected and authenticated SMTP client instance.
        """
        self._smtp = smtp

    async def send(
            self,
            to: str,
            from_: str | None,
            subject: str,
            body: str,
    ) -> None:
        """Send an email message via SMTP.
        
        Args:
            to: Recipient email address.
            from_: Sender email address. If None, uses default noreply address.
            subject: Email subject line.
            body: Email body content.
            
        Raises:
            EmailSendingError: If sending email fails.
        """
        from_address = from_ or smtp_settings.noreply_email
        
        logger.info(
            "Preparing to send email",
            to=to,
            from_address=from_address,
            subject=subject,
        )
        
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = from_address
            msg['To'] = to
            msg.set_content(body)

            logger.debug(
                "Sending email message via SMTP",
                to=to,
                from_address=from_address,
                subject=subject,
                body_length=len(body),
            )
            
            await self._smtp.send_message(msg)
            
            logger.info(
                "Email sent successfully",
                to=to,
                from_address=from_address,
                subject=subject,
            )
            
        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(
                "SMTP authentication error occurred",
                to=to,
                from_address=from_address,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise EmailSendingError(
                f"SMTP authentication failed when sending email to {to} with subject '{subject}'"
            ) from e
            
        except aiosmtplib.SMTPConnectError as e:
            logger.error(
                "SMTP connection error occurred",
                to=to,
                from_address=from_address,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise EmailSendingError(
                f"SMTP connection error when sending email to {to} with subject '{subject}'"
            ) from e
            
        except aiosmtplib.SMTPRecipientsRefused as e:
            logger.error(
                "SMTP recipients refused",
                to=to,
                from_address=from_address,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise EmailSendingError(
                f"Recipient {to} refused when sending email with subject '{subject}'"
            ) from e
            
        except aiosmtplib.SMTPDataError as e:
            logger.error(
                "SMTP data error occurred",
                to=to,
                from_address=from_address,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise EmailSendingError(
                f"SMTP data error when sending email to {to} with subject '{subject}'"
            ) from e
            
        except aiosmtplib.SMTPException as e:
            logger.error(
                "SMTP error occurred",
                to=to,
                from_address=from_address,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise EmailSendingError(
                f"SMTP error occurred when sending email to {to} with subject '{subject}': {e}"
            ) from e
            
        except Exception as e:
            logger.error(
                "Unexpected error occurred during email sending",
                to=to,
                from_address=from_address,
                subject=subject,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise EmailSendingError(
                f"Unexpected error occurred when sending email to {to} with subject '{subject}': {e}"
            ) from e
