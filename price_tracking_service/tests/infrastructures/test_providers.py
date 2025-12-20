import pytest
from unittest.mock import MagicMock

from application.use_cases.check_threshold import CheckThresholdUseCase


class TestCheckThresholdUseCaseProvider:
    """Tests for CheckThresholdUseCase provider factory function."""

    @pytest.fixture
    def mock_alert_repository(self):
        """Create mock AlertRepositoryProtocol."""
        return MagicMock()

    @pytest.fixture
    def mock_event_publisher(self):
        """Create mock EventPublisherProtocol."""
        return MagicMock()

    def test_check_threshold_use_case_creation_returns_correct_type(
        self,
        mock_alert_repository,
        mock_event_publisher
    ):
        """Test that CheckThresholdUseCase can be created with proper dependencies."""
        # Act
        result = CheckThresholdUseCase(
            alert_repository=mock_alert_repository,
            event_publisher=mock_event_publisher
        )

        # Assert
        assert isinstance(result, CheckThresholdUseCase)

    def test_check_threshold_use_case_with_dependencies(
        self,
        mock_alert_repository,
        mock_event_publisher
    ):
        """Test that CheckThresholdUseCase stores correct dependencies."""
        # Act
        result = CheckThresholdUseCase(
            alert_repository=mock_alert_repository,
            event_publisher=mock_event_publisher
        )

        # Assert
        assert result._alert_repository == mock_alert_repository
        assert result._event_publisher == mock_event_publisher

    def test_check_threshold_use_case_creates_new_instance_each_time(
        self,
        mock_alert_repository,
        mock_event_publisher
    ):
        """Test that CheckThresholdUseCase creates new instance on each call."""
        # Act
        result1 = CheckThresholdUseCase(
            alert_repository=mock_alert_repository,
            event_publisher=mock_event_publisher
        )
        result2 = CheckThresholdUseCase(
            alert_repository=mock_alert_repository,
            event_publisher=mock_event_publisher
        )

        # Assert
        assert result1 is not result2
        assert isinstance(result1, CheckThresholdUseCase)
        assert isinstance(result2, CheckThresholdUseCase)

    def test_check_threshold_use_case_accepts_none_dependencies(
        self
    ):
        """Test that CheckThresholdUseCase accepts None dependencies (though not recommended)."""
        # Act
        result = CheckThresholdUseCase(
            alert_repository=None,
            event_publisher=None
        )

        # Assert
        assert result._alert_repository is None
        assert result._event_publisher is None
        assert isinstance(result, CheckThresholdUseCase)

    def test_check_threshold_use_case_has_required_attributes(
        self,
        mock_alert_repository,
        mock_event_publisher
    ):
        """Test that CheckThresholdUseCase has correct attributes and methods."""
        # Act
        result = CheckThresholdUseCase(
            alert_repository=mock_alert_repository,
            event_publisher=mock_event_publisher
        )

        # Assert
        # Check that the result has the expected attributes from CheckThresholdUseCase
        assert hasattr(result, '_alert_repository')
        assert hasattr(result, '_event_publisher')
        assert hasattr(result, 'execute')
        assert callable(result.execute)

    @pytest.mark.parametrize("alert_repo_mock,event_pub_mock", [
        (MagicMock(), MagicMock()),
        (MagicMock(spec=['find_by_cryptocurrency']), MagicMock(spec=['publish'])),
    ])
    def test_check_threshold_use_case_with_different_mock_types(
        self,
        alert_repo_mock,
        event_pub_mock
    ):
        """Test CheckThresholdUseCase with different types of mocks."""
        # Act
        result = CheckThresholdUseCase(
            alert_repository=alert_repo_mock,
            event_publisher=event_pub_mock
        )

        # Assert
        assert result._alert_repository == alert_repo_mock
        assert result._event_publisher == event_pub_mock
        assert isinstance(result, CheckThresholdUseCase)