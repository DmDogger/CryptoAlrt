from typing import Protocol


class EmailClientProtocol(Protocol):
    """Protocol for email client.

    Defines methods for sending emails.
    This interface allows the Application layer to send emails without
    depending on Infrastructure implementations.
    """

    async def send(
        self, to: str, subject: str, body: str, from_: str | None = None
    ) -> None:
        """Send an email message.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Email body content.
            from_: Sender email address (optional).

        Raises:
            EmailSendError: If sending email fails.
        """
        ...
