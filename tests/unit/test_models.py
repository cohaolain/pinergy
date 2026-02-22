"""Unit tests for request/response dataclasses."""

import pytest

from pinergy_client.models import (
    BaseResponse,
    LoginResponse,
    BalanceResponse,
    TopUpResponse,
    UsagesResponse,
    CompareResponse,
    ConfigInfoResponse,
    DefaultInfoResponse,
    GetPrefsResponse,
    LandLordCheckResponse,
    CredoraxHPPLinkReturn,
    LevelPayUsage,
    HouseServer,
    UserServer,
    CreditCardServer,
    UsageDataServer,
    TopUpServer,
    TopUpUser,
    FieldServer,
    CompareDataServer,
    CompareTimeDataServer,
    LoginRequest,
    ChangePasswordRequest,
    EditProfileRequest,
    TopUpRequest,
    NotificationSettingsRequest,
    LandlordRequest,
    DeleteCreditCardRequest,
)


class TestBaseResponse:
    def test_from_dict_empty(self) -> None:
        r = BaseResponse.from_dict(None)
        assert r.success is False
        assert r.message == ""
        assert r.error_code == 0

    def test_from_dict_full(self) -> None:
        r = BaseResponse.from_dict(
            {"success": True, "message": "OK", "error_code": 0}
        )
        assert r.success is True
        assert r.message == "OK"
        assert r.error_code == 0


class TestLoginResponse:
    def test_from_dict_with_token(self) -> None:
        r = LoginResponse.from_dict(
            {
                "success": True,
                "auth_token": "abc123",
                "premises_number": "P123",
                "user": {"name": "Joe", "pinergy_id": "u1"},
                "house": {"type": 1, "adult_count": 2},
                "credit_cards": [],
            }
        )
        assert r.success is True
        assert r.auth_token == "abc123"
        assert r.premises_number == "P123"
        assert r.user is not None
        assert r.user.name == "Joe"
        assert r.house is not None
        assert r.house.adult_count == 2
        assert r.credit_cards == []


class TestBalanceResponse:
    def test_from_dict(self) -> None:
        r = BalanceResponse.from_dict(
            {
                "success": True,
                "balance": 25.50,
                "credit_low": False,
                "top_up_in_days": 7,
            }
        )
        assert r.success is True
        assert r.balance == 25.50
        assert r.credit_low is False
        assert r.top_up_in_days == 7


class TestUsagesResponse:
    def test_from_dict_with_lists(self) -> None:
        r = UsagesResponse.from_dict(
            {
                "success": True,
                "day": [{"date": 123, "kwh": 5.0, "amount": 1.2, "co2": 0.5}],
                "week": [],
                "month": [],
            }
        )
        assert r.success is True
        assert len(r.day) == 1
        assert r.day[0].kwh == 5.0
        assert r.day[0].amount == 1.2
        assert len(r.week) == 0


class TestLoginRequest:
    def test_to_dict(self) -> None:
        req = LoginRequest(email="a@b.ie", password="secret", device_token="dt")
        d = req.to_dict()
        assert d == {"email": "a@b.ie", "password": "secret", "device_token": "dt"}
        assert list(d.keys()) == ["email", "password", "device_token"]


class TestTopUpRequest:
    def test_to_dict_minimal(self) -> None:
        req = TopUpRequest(pinergy_id="p1", cc_token="cc1", amount=20.0)
        d = req.to_dict()
        assert d["pinergy_id"] == "p1"
        assert d["cc_token"] == "cc1"
        assert d["amount"] == 20.0
        assert "threshold" not in d
        assert "day_of_month" not in d

    def test_to_dict_with_optionals(self) -> None:
        req = TopUpRequest(
            pinergy_id="p1",
            cc_token="cc1",
            amount=20.0,
            threshold=10.0,
            day_of_month=15,
        )
        d = req.to_dict()
        assert d["threshold"] == 10.0
        assert d["day_of_month"] == 15


class TestNestedModels:
    def test_house_server_from_dict(self) -> None:
        h = HouseServer.from_dict(
            {"type": 1, "adult_count": 2, "bedroom_count": 3}
        )
        assert h is not None
        assert h.type == 1
        assert h.adult_count == 2
        assert h.bedroom_count == 3

    def test_compare_response_from_dict(self) -> None:
        r = CompareResponse.from_dict(
            {
                "success": True,
                "week": {
                    "available": True,
                    "kwh": {"average_home": 100, "users_home": 80},
                    "co2": {"average_home": 50, "users_home": 40},
                },
            }
        )
        assert r.week is not None
        assert r.week.available is True
        assert r.week.kwh is not None
        assert r.week.kwh.average_home == 100

    def test_config_info_response_from_dict(self) -> None:
        r = ConfigInfoResponse.from_dict(
            {
                "success": True,
                "top_up_amounts": [10, 20, 50],
                "thresholds": [5, 10],
            }
        )
        assert r.top_up_amounts == [10, 20, 50]
        assert r.thresholds == [5, 10]

    def test_landlord_check_response(self) -> None:
        r = LandLordCheckResponse.from_dict(
            {"success": True, "is_landlord_account": True}
        )
        assert r.is_landlord_account is True

    def test_level_pay_usage_from_dict(self) -> None:
        r = LevelPayUsage.from_dict(
            {
                "success": True,
                "message": "OK",
                "error_code": 0,
                "usageData": {"daily": {}, "weekly": {}},
            }
        )
        assert r.success is True
        assert "daily" in r.usage_data
