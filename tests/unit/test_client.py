"""Unit tests for PinergyClient (mocked HTTP)."""

import pytest
from requests_mock import Mocker

from pinergy_client.client import PinergyClient
from pinergy_client.exceptions import PinergyAPIError, PinergyAuthError
from pinergy_client.models import TopUpRequest


@pytest.fixture
def base_url() -> str:
    return "https://api.pinergy.ie/api"


@pytest.fixture
def client(base_url: str) -> PinergyClient:
    return PinergyClient(base_url=base_url, auth_token="test-token")


class TestPinergyClientAuth:
    def test_requires_auth_for_balance(self, base_url: str) -> None:
        c = PinergyClient(base_url=base_url)
        with pytest.raises(PinergyAuthError):
            c.balance()

    def test_sets_auth_header_after_login(self, base_url: str) -> None:
        c = PinergyClient(base_url=base_url)
        with Mocker() as m:
            m.post(
                f"{base_url}/login",
                json={
                    "success": True,
                    "auth_token": "new-token",
                    "user": {},
                    "house": None,
                    "credit_cards": [],
                    "premises_number": "",
                    "is_legacy_meter": False,
                    "is_no_wan_meter": False,
                },
            )
            c.login("a@b.ie", "pass")
            assert c.auth_token == "new-token"


class TestPinergyClientEndpoints:
    def test_login_success(self, client: PinergyClient, base_url: str) -> None:
        with Mocker() as m:
            m.post(
                f"{base_url}/login",
                json={
                    "success": True,
                    "auth_token": "t123",
                    "user": {"name": "Test"},
                    "house": None,
                    "credit_cards": [],
                    "premises_number": "P1",
                    "is_legacy_meter": False,
                    "is_no_wan_meter": False,
                },
            )
            resp = client.login("a@b.ie", "pass")
            assert resp.success is True
            assert resp.auth_token == "t123"
            assert resp.user is not None
            assert resp.user.name == "Test"

    def test_balance_success(self, client: PinergyClient, base_url: str) -> None:
        with Mocker() as m:
            m.get(
                f"{base_url}/balance",
                json={
                    "success": True,
                    "balance": 30.0,
                    "credit_low": False,
                    "emergency_credit": False,
                    "last_reading": 0,
                    "last_top_up_time": 0,
                    "last_top_up_amount": 20.0,
                    "pending_top_up": False,
                    "pending_top_up_by": "",
                    "power_off": False,
                    "top_up_in_days": 5,
                },
            )
            resp = client.balance()
            assert resp.success is True
            assert resp.balance == 30.0

    def test_balance_http_error_raises(self, client: PinergyClient, base_url: str) -> None:
        with Mocker() as m:
            m.get(f"{base_url}/balance", status_code=500, json={"message": "Server error"})
            with pytest.raises(PinergyAPIError) as exc_info:
                client.balance()
            assert exc_info.value.status_code == 500
            assert "Server error" in str(exc_info.value)

    def test_get_defaults_no_auth(self, client: PinergyClient, base_url: str) -> None:
        c = PinergyClient(base_url=base_url)
        with Mocker() as m:
            m.get(
                f"{base_url}/defaultsinfo",
                json={
                    "success": True,
                    "default_adults": 2,
                    "default_bedrooms": 3,
                    "default_children": 0,
                    "max_adults": 10,
                    "max_bedrooms": 10,
                    "max_children": 10,
                    "heating_types": [{"id": 1, "name": "Gas"}],
                    "house_types": [{"id": 1, "name": "House"}],
                },
            )
            resp = c.get_defaults_info()
            assert resp.success is True
            assert resp.default_adults == 2
            assert len(resp.heating_types) == 1
            assert resp.heating_types[0].name == "Gas"

    def test_landlord_check(self, base_url: str) -> None:
        c = PinergyClient(base_url=base_url)
        with Mocker() as m:
            m.get(
                f"{base_url}/landlordcheck",
                json={"success": True, "is_landlord_account": True},
            )
            resp = c.landlord_check(premises_number="P123")
            assert resp.is_landlord_account is True
            assert "premises_number" in (m.last_request.query or "")
