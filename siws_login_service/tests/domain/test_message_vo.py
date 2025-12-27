"""Tests for MessageVO value object."""

from domain.entities.nonce_entity import NonceEntity
from domain.value_objects.message_vo import MessageVO
from domain.value_objects.wallet_vo import WalletAddressVO


class TestMessageVO:
    """Test suite for MessageVO value object."""

    def test_correct_message_vo_from_record(
        self,
        sample_message_vo: MessageVO,
        sample_nonce_entity: NonceEntity,
        sample_wallet_vo: WalletAddressVO,
    ) -> None:
        """Test that from_record() creates MessageVO with correct values from NonceEntity.

        Args:
            sample_message_vo: Fixture providing a valid MessageVO instance.
            sample_nonce_entity: Fixture providing a valid NonceEntity instance.
            sample_wallet_vo: Fixture providing a valid WalletAddressVO instance.
        """
        assert sample_message_vo is not None
        assert sample_message_vo.wallet_address == sample_wallet_vo
        assert sample_message_vo.domain == sample_nonce_entity.domain
        assert sample_message_vo.statement == sample_nonce_entity.statement
        assert sample_message_vo.version == sample_nonce_entity.version
        assert sample_message_vo.chain_id == sample_nonce_entity.chain_id
        assert sample_message_vo.nonce == sample_nonce_entity.nonce.value
        assert sample_message_vo.expiration_time == sample_nonce_entity.expiration_time

    def test_correct_message_vo_to_string(
        self,
        sample_message_vo: MessageVO,
    ) -> None:
        """Test that to_string() method returns formatted string representation.

        Args:
            sample_message_vo: Fixture providing a valid MessageVO instance.
        """
        string_message = sample_message_vo.to_string()

        assert isinstance(string_message, str)
        assert (
            f"{sample_message_vo.domain} wants you to sign in with your Solana account"
            in string_message
        )

