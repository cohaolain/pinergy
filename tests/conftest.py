"""Pytest fixtures and env for integration tests."""

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration (uses real API; needs .env)",
    )


@pytest.fixture(scope="session")
def env_auth() -> tuple[str, str] | None:
    """Email and password from env for integration tests. None if not set."""
    email = os.environ.get("PINERGY_EMAIL", "").strip()
    password = os.environ.get("PINERGY_PASSWORD", "").strip()
    if email and password:
        return (email, password)
    token = os.environ.get("PINERGY_AUTH_TOKEN", "").strip()
    if token:
        return ("token", token)  # placeholder; client will use token
    return None
