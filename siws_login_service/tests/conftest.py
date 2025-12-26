from uuid import uuid4

import pytest

pytest_plugins = ["tests.fixtures.domain_fixtures"]

@pytest.fixture
def sample_uuid():
    return uuid4()