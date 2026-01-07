from uuid import uuid4

import pytest

pytest_plugins = [
    "tests.helpers.mocks",
    "tests.helpers.fakes",
    "tests.fixtures.domain_fixtures",
    "tests.fixtures.infra_fixtures",
    "tests.fixtures.application_fixtures",
]


@pytest.fixture
def sample_uuid():
    return uuid4()
