"""Pinergy API client using requests.Session with auth_token header."""

from __future__ import annotations

import hashlib
import json
import secrets
import string
import sys
from typing import Any, IO

import requests

from pinergy_client.exceptions import PinergyAPIError, PinergyAuthError
from pinergy_client.models import (
    ActiveTopUpsResponse,
    BalanceResponse,
    BaseResponse,
    CompareResponse,
    ConfigInfoResponse,
    CredoraxHPPLinkReturn,
    DefaultInfoResponse,
    EditHouseDetailsRequest,
    EditProfileRequest,
    GetPrefsResponse,
    LandLordCheckResponse,
    LandlordRequest,
    LevelPayUsage,
    LoginRequest,
    LoginResponse,
    NotificationSettingsRequest,
    NotificationSettingsResponse,
    TopUpHistoryResponse,
    TopUpRequest,
    TopUpResponse,
    UpdateDeviceTokenRequest,
    UsagesResponse,
)

DEFAULT_BASE_URL = "https://api.pinergy.ie/api"
AUTH_HEADER = "auth_token"
DEFAULT_TIMEOUT = (90, 90)  # connect, read in seconds


class PinergyClient:
    """HTTP client for the Pinergy API with session-based auth."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        auth_token: str | None = None,
        timeout: tuple[int, int] = DEFAULT_TIMEOUT,
        debug: bool = False,
        log_stream: IO[str] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._debug = debug
        self._log_stream: IO[str] = log_stream or sys.stdout
        self._session = requests.Session()
        self._session.headers["Content-Type"] = "application/json"
        self._session.headers["Accept"] = "application/json"
        # API may reject default python-requests User-Agent; mimic app
        self._session.headers["User-Agent"] = "Pinergy/1.0 (Android 14)"
        if auth_token:
            self._session.headers[AUTH_HEADER] = auth_token

    @property
    def auth_token(self) -> str | None:
        return self._session.headers.get(AUTH_HEADER)

    def set_auth_token(self, token: str) -> None:
        print(f"Setting auth_token: {token}")
        self._session.headers[AUTH_HEADER] = token

    # Internal helpers
    @staticmethod
    def _generate_fake_fcm_token(length: int = 152) -> str:
        """Generate a fake, FCM-like device token string."""
        alphabet = string.ascii_letters + string.digits + "-_"
        body = "".join(secrets.choice(alphabet) for _ in range(length - 5))
        return "APA91" + body

    def _debug_log_request(
        self,
        method: str,
        url: str,
        *,
        json_body: dict[str, Any] | None,
        params: dict[str, str] | None,
        redact_password: bool = False,
    ) -> None:
        if not self._debug:
            return

        # Build safe headers snapshot
        headers = dict(self._session.headers)
        for h in list(headers):
            if h.lower() in {"auth_token", "authorization"}:
                headers[h] = "***REDACTED***"

        safe_body: Any = json_body
        if isinstance(json_body, dict) and redact_password and "password" in json_body:
            safe_body = {**json_body, "password": "***REDACTED***"}

        print("=== PinergyClient request ===", file=self._log_stream)
        print(f"{method} {url}", file=self._log_stream)
        if params:
            print(f"params={params}", file=self._log_stream)
        print("headers=", json.dumps(headers, indent=2, sort_keys=True), file=self._log_stream)
        if safe_body is not None:
            print("json_body=", json.dumps(safe_body, indent=2, sort_keys=True), file=self._log_stream)
        else:
            print("json_body=None", file=self._log_stream)

    def _debug_log_response(self, status_code: int, body: Any) -> None:
        if not self._debug:
            return
        print(f"=== PinergyClient response ({status_code}) ===", file=self._log_stream)
        try:
            print(json.dumps(body, indent=2, sort_keys=True), file=self._log_stream)
        except Exception:
            print(repr(body), file=self._log_stream)

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        auth_required: bool = True,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if auth_required and not self._session.headers.get(AUTH_HEADER):
            raise PinergyAuthError("Not authenticated; call login() or set auth_token first.")
        self._debug_log_request(
            method,
            url,
            json_body=json,
            params=params,
            redact_password=False,
        )
        resp = self._session.request(
            method,
            url,
            json=json,
            params=params,
            timeout=self._timeout,
        )
        try:
            data = resp.json() if resp.content else {}
        except Exception:
            data = {}
        self._debug_log_response(resp.status_code, data)
        if not resp.ok:
            raise PinergyAPIError(
                data.get("message", resp.reason or f"HTTP {resp.status_code}"),
                status_code=resp.status_code,
                body=data,
            )
        if isinstance(data, dict) and data.get("success") is False and method != "GET":
            raise PinergyAPIError(
                data.get("message", "Request failed"),
                status_code=resp.status_code,
                body=data,
            )
        return data

    def login(
        self,
        email: str,
        password: str,
        device_token: str = "",
    ) -> LoginResponse:
        """Authenticate and set auth_token on this session.

        Sends only email, SHA-1(UTF-8) hex of password, and device_token (matches LoginApiRequest).
        """
        email = (email or "").strip()
        raw_password = (password or "").strip()
        password = hashlib.sha1(raw_password.encode("utf-8")).hexdigest()
        if not device_token:
            device_token = self._generate_fake_fcm_token()
        req = LoginRequest(
            email=email,
            password=password,
            device_token=(device_token or "").strip(),
        )
        data = self._request("POST", "/login", json=req.to_dict(), auth_required=False)
        out = LoginResponse.from_dict(data)
        if out.auth_token:
            self.set_auth_token(out.auth_token)
        return out

    def logout(self) -> BaseResponse:
        data = self._request("POST", "/logout", json={})
        return BaseResponse.from_dict(data)

    def forgot_password(self, email: str) -> BaseResponse:
        data = self._request(
            "POST", "/forgot", params={"email": email}, json={}, auth_required=False
        )
        return BaseResponse.from_dict(data)

    def change_password(self, new_password: str) -> BaseResponse:
        from pinergy_client.models import ChangePasswordRequest

        req = ChangePasswordRequest(new_password=new_password)
        data = self._request("POST", "/changepass", json=req.to_dict())
        return BaseResponse.from_dict(data)

    def balance(self) -> BalanceResponse:
        data = self._request("GET", "/balance")
        return BalanceResponse.from_dict(data)

    def top_up(self, request: TopUpRequest) -> TopUpResponse:
        data = self._request("POST", "/topup", json=request.to_dict())
        return TopUpResponse.from_dict(data)

    def schedule_top_up(self, request: TopUpRequest) -> BaseResponse:
        data = self._request("POST", "/scheduletopup", json=request.to_dict())
        return BaseResponse.from_dict(data)

    def auto_top_up(self, request: TopUpRequest) -> BaseResponse:
        data = self._request("POST", "/autotopup", json=request.to_dict())
        return BaseResponse.from_dict(data)

    def get_active_top_ups(self) -> ActiveTopUpsResponse:
        data = self._request("GET", "/activetopups")
        return ActiveTopUpsResponse.from_dict(data)

    def get_top_up_history(self) -> TopUpHistoryResponse:
        data = self._request("GET", "/topuphistory")
        return TopUpHistoryResponse.from_dict(data)

    def get_usage(self) -> UsagesResponse:
        data = self._request("GET", "/usage")
        return UsagesResponse.from_dict(data)

    def get_level_pay_usage(self) -> LevelPayUsage:
        data = self._request("GET", "/levelPayUsage")
        return LevelPayUsage.from_dict(data)

    def compare(self) -> CompareResponse:
        data = self._request("GET", "/compare")
        return CompareResponse.from_dict(data)

    def edit_profile(self, request: EditProfileRequest) -> BaseResponse:
        data = self._request("POST", "/editprofile", json=request.to_dict())
        return BaseResponse.from_dict(data)

    def update_house(self, request: EditHouseDetailsRequest) -> BaseResponse:
        data = self._request("POST", "/updatehouse", json=request.to_dict())
        return BaseResponse.from_dict(data)

    def get_notification_settings(self) -> GetPrefsResponse:
        data = self._request("GET", "/getnotif")
        return GetPrefsResponse.from_dict(data)

    def update_notification_settings(
        self, request: NotificationSettingsRequest
    ) -> NotificationSettingsResponse:
        data = self._request("POST", "/updatenotif", json=request.to_dict())
        return NotificationSettingsResponse.from_dict(data)

    def update_device_token(self, request: UpdateDeviceTokenRequest) -> BaseResponse:
        data = self._request("POST", "/updatedevicetoken", json=request.to_dict())
        return BaseResponse.from_dict(data)

    def delete_credit_card(self, cc_token: str) -> BaseResponse:
        from pinergy_client.models import DeleteCreditCardRequest

        req = DeleteCreditCardRequest(cc_token=cc_token)
        data = self._request("POST", "/deletecc", json=req.to_dict())
        return BaseResponse.from_dict(data)

    def get_config_info(self) -> ConfigInfoResponse:
        data = self._request("GET", "/configinfo")
        return ConfigInfoResponse.from_dict(data)

    def get_defaults_info(self) -> DefaultInfoResponse:
        data = self._request("GET", "/defaultsinfo", auth_required=False)
        return DefaultInfoResponse.from_dict(data)

    def landlord_check(self, premises_number: str) -> LandLordCheckResponse:
        data = self._request(
            "GET",
            "/landlordcheck",
            params={"premises_number": premises_number},
            auth_required=False,
        )
        return LandLordCheckResponse.from_dict(data)

    def landlord_verify(self, request: LandlordRequest) -> BaseResponse:
        data = self._request("POST", "/landlordverify", json=request.to_dict(), auth_required=False)
        return BaseResponse.from_dict(data)

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> PinergyClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
