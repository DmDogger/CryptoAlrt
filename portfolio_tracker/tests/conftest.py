"""Pytest configuration for portfolio tracker tests."""

import pytest

pytest_plugins = [
    "tests.helpers.mocks.redis",
    "tests.helpers.mocks.repositories",
    "tests.helpers.mocks.use_cases",
    "tests.fixtures.domain_fixtures",
    "tests.fixtures.application_fixtures",
    "tests.fixtures.infra_fixtures",
]
