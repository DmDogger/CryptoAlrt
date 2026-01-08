from infrastructures.database.mappers import NotificationDBMapper


class TestNotificationDBMapper:
    """Tests for NotificationDBMapper."""

    def test_to_database_model_maps_all_fields(
        self,
        sample_notification_entity,
        sample_notification_db_model,
    ):
        """Test that to_database_model() correctly maps all fields from Entity to DB Model."""
        result = NotificationDBMapper.to_database_model(sample_notification_entity)

        assert result.id == sample_notification_db_model.id
        assert result.channel == sample_notification_db_model.channel
        assert result.message == sample_notification_db_model.message
        assert result.recipient == sample_notification_db_model.recipient
        assert result.status == sample_notification_db_model.status
        assert result.sent_at == sample_notification_db_model.sent_at
        assert result.idempotency_key == sample_notification_db_model.idempotency_key
        assert result.created_at == sample_notification_db_model.created_at

    def test_from_database_model_maps_all_fields(
        self, sample_notification_entity, sample_notification_db_model
    ):
        """Test that from_database_model() correctly maps all fields from DB Model to Entity."""
        result = NotificationDBMapper.from_database_model(sample_notification_db_model)

        assert result.id == sample_notification_db_model.id
        assert result.channel == sample_notification_entity.channel
        assert result.message.text == sample_notification_entity.message.text
        assert result.recipient == sample_notification_entity.recipient
        assert result.status == sample_notification_entity.status
        assert result.idempotency_key.key == sample_notification_entity.idempotency_key.key

    def test_round_trip_mapping(
        self,
        sample_notification_entity,
    ):
        """Test Entity → DB Model → Entity round-trip mapping without data loss."""
        db_model = NotificationDBMapper.to_database_model(sample_notification_entity)
        result_entity = NotificationDBMapper.from_database_model(db_model)

        assert result_entity.id == sample_notification_entity.id
        assert result_entity.channel == sample_notification_entity.channel
        assert result_entity.message.text == sample_notification_entity.message.text
        assert result_entity.recipient == sample_notification_entity.recipient
        assert result_entity.status == sample_notification_entity.status
        assert result_entity.idempotency_key.key == sample_notification_entity.idempotency_key.key
