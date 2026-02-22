"""Integration tests against the real Pinergy API using credentials from .env."""

import os

import pytest
from dotenv import load_dotenv

from pinergy_client.client import PinergyClient
from pinergy_client.exceptions import PinergyAPIError

load_dotenv()

pytestmark = pytest.mark.integration

BASE_URL = os.environ.get("PINERGY_BASE_URL", "https://api.pinergy.ie/api")


def _has_auth() -> bool:
    token = os.environ.get("PINERGY_AUTH_TOKEN", "").strip()
    if token:
        return True
    email = os.environ.get("PINERGY_EMAIL", "").strip()
    password = os.environ.get("PINERGY_PASSWORD", "").strip()
    return bool(email and password)


@pytest.fixture(scope="module")
def client() -> PinergyClient:
    token = os.environ.get("PINERGY_AUTH_TOKEN", "").strip()
    c = PinergyClient(base_url=BASE_URL, auth_token=token or None, debug=True)
    if not token:
        email = os.environ.get("PINERGY_EMAIL", "").strip()
        password = os.environ.get("PINERGY_PASSWORD", "").strip()
        print(f"Email: {email}, Password: {password}")
        if not email or not password:
            pytest.skip("Set PINERGY_EMAIL and PINERGY_PASSWORD (or PINERGY_AUTH_TOKEN) for integration tests")
        resp = c.login(email=email, password=password)
        if not resp.success:
            pytest.skip(f"Login failed: {resp.message}")
    yield c
    c.close()


@pytest.mark.skipif(not _has_auth(), reason="No PINERGY_EMAIL/PINERGY_PASSWORD or PINERGY_AUTH_TOKEN in env")
def test_login_and_balance(client: PinergyClient) -> None:
    """Login (if using password) and fetch balance."""
    resp = client.balance()
    assert resp.success, resp.message
    assert hasattr(resp, "balance")
    assert isinstance(resp.balance, (int, float))


@pytest.mark.skipif(not _has_auth(), reason="No PINERGY_EMAIL/PINERGY_PASSWORD or PINERGY_AUTH_TOKEN in env")
def test_get_defaults_info() -> None:
    """Defaults endpoint does not require auth."""
    c = PinergyClient(base_url=BASE_URL)
    try:
        resp = c.get_defaults_info()
        assert resp.success, resp.message
        assert hasattr(resp, "house_types")
        assert hasattr(resp, "heating_types")
    finally:
        c.close()


@pytest.mark.skipif(not _has_auth(), reason="No PINERGY_EMAIL/PINERGY_PASSWORD or PINERGY_AUTH_TOKEN in env")
def test_get_usage(client: PinergyClient) -> None:
    """Fetch usage (day/week/month)."""
    resp = client.get_usage()
    assert resp.success, resp.message
    assert hasattr(resp, "day")
    assert hasattr(resp, "week")
    assert hasattr(resp, "month")


@pytest.mark.skipif(not _has_auth(), reason="No PINERGY_EMAIL/PINERGY_PASSWORD or PINERGY_AUTH_TOKEN in env")
def test_get_config_info(client: PinergyClient) -> None:
    """Fetch config (top-up amounts, thresholds)."""
    resp = client.get_config_info()
    assert resp.success, resp.message
    assert hasattr(resp, "top_up_amounts")
    assert hasattr(resp, "thresholds")


@pytest.mark.skipif(not _has_auth(), reason="No PINERGY_EMAIL/PINERGY_PASSWORD or PINERGY_AUTH_TOKEN in env")
def test_get_notification_settings(client: PinergyClient) -> None:
    """Fetch notification prefs."""
    resp = client.get_notification_settings()
    assert hasattr(resp, "email")
    assert hasattr(resp, "sms")
