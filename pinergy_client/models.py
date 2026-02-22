"""Request and response dataclasses matching the Pinergy API JSON."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _strip_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


# --- Nested / server data (used in requests and responses) ---


@dataclass
class HouseServer:
    type: int = 0
    adult_count: int = 0
    bedroom_count: int = 0
    children_count: int = 0
    heating_type: int = 0

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> HouseServer | None:
        if d is None:
            return None
        return cls(
            type=d.get("type", 0),
            adult_count=d.get("adult_count", 0),
            bedroom_count=d.get("bedroom_count", 0),
            children_count=d.get("children_count", 0),
            heating_type=d.get("heating_type", 0),
        )


@dataclass
class UserServer:
    name: str = ""
    title: str = ""
    pinergy_id: str = ""
    mobile_number: str = ""
    email_notifications: bool = False
    sms_notifications: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> UserServer | None:
        if d is None:
            return None
        return cls(
            name=d.get("name", ""),
            title=d.get("title", ""),
            pinergy_id=d.get("pinergy_id", ""),
            mobile_number=d.get("mobile_number", ""),
            email_notifications=d.get("email_notifications", False),
            sms_notifications=d.get("sms_notifications", False),
        )


@dataclass
class CreditCardServer:
    name: str = ""
    cc_token: str = ""
    payment_token: str = ""
    last_4_digits: str = ""
    z50: str = ""
    email: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> CreditCardServer | None:
        if d is None:
            return None
        return cls(
            name=d.get("name", ""),
            cc_token=d.get("cc_token", ""),
            payment_token=d.get("payment_token", ""),
            last_4_digits=d.get("last_4_digits", ""),
            z50=d.get("z50", ""),
            email=d.get("email", ""),
        )


@dataclass
class UsageDataServer:
    date: int = 0
    amount: float = 0.0
    kwh: float = 0.0
    co2: float = 0.0

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> UsageDataServer | None:
        if d is None:
            return None
        return cls(
            date=int(d.get("date", 0)),
            amount=float(d.get("amount", 0)),
            kwh=float(d.get("kwh", 0)),
            co2=float(d.get("co2", 0)),
        )


@dataclass
class TopUpServer:
    top_up_id: str = ""
    top_up_amount: float = 0.0
    top_up_date: int = 0
    top_up_action: str = ""
    top_up_code: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> TopUpServer | None:
        if d is None:
            return None
        return cls(
            top_up_id=d.get("top_up_id", ""),
            top_up_amount=float(d.get("top_up_amount", 0)),
            top_up_date=int(d.get("top_up_date", 0)),
            top_up_action=d.get("top_up_action", ""),
            top_up_code=d.get("top_up_code", ""),
        )


@dataclass
class TopUpUser:
    customer: str = ""
    current_user: bool = False
    top_up_amount: float = 0.0
    top_up_day: int = 0
    top_up_threshold: int = 0

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> TopUpUser | None:
        if d is None:
            return None
        return cls(
            customer=d.get("customer", ""),
            current_user=d.get("current_user", False),
            top_up_amount=float(d.get("top_up_amount", 0)),
            top_up_day=int(d.get("top_up_day", 0)),
            top_up_threshold=int(d.get("top_up_threshold", 0)),
        )


@dataclass
class FieldServer:
    id: int = 0
    name: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> FieldServer | None:
        if d is None:
            return None
        return cls(id=int(d.get("id", 0)), name=d.get("name", ""))


@dataclass
class CompareDataServer:
    average_home: float = 0.0
    users_home: float = 0.0

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> CompareDataServer | None:
        if d is None:
            return None
        return cls(
            average_home=float(d.get("average_home", 0)),
            users_home=float(d.get("users_home", 0)),
        )


@dataclass
class CompareTimeDataServer:
    available: bool = False
    kwh: CompareDataServer | None = None
    co2: CompareDataServer | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> CompareTimeDataServer | None:
        if d is None:
            return None
        return cls(
            available=d.get("available", False),
            kwh=CompareDataServer.from_dict(d.get("kwh")),
            co2=CompareDataServer.from_dict(d.get("co2")),
        )


# --- Base response ---


@dataclass
class BaseResponse:
    success: bool = False
    message: str = ""
    error_code: int = 0

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> BaseResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
        )


# --- Requests (payloads we send) ---


@dataclass
class LoginRequest:
    """Login body: only email, password (SHA-1 hex), device_token.

    Matches the app's LoginApiRequest (AuthViewModel path): no device_type or os_version.
    """

    email: str
    password: str
    device_token: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "email": self.email,
            "password": self.password,
            "device_token": self.device_token,
        }


@dataclass
class ChangePasswordRequest:
    new_password: str

    def to_dict(self) -> dict[str, Any]:
        return {"new_password": self.new_password}


@dataclass
class EditProfileRequest:
    title: str
    first_name: str
    last_name: str
    mobile: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mobile": self.mobile,
        }


@dataclass
class EditHouseDetailsRequest:
    house: HouseServer

    def to_dict(self) -> dict[str, Any]:
        return {
            "house": {
                "type": self.house.type,
                "adult_count": self.house.adult_count,
                "bedroom_count": self.house.bedroom_count,
                "children_count": self.house.children_count,
                "heating_type": self.house.heating_type,
            }
        }


@dataclass
class TopUpRequest:
    pinergy_id: str
    cc_token: str
    amount: float
    threshold: float | None = None
    day_of_month: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "pinergy_id": self.pinergy_id,
            "cc_token": self.cc_token,
            "amount": self.amount,
        }
        if self.threshold is not None:
            d["threshold"] = self.threshold
        if self.day_of_month is not None:
            d["day_of_month"] = self.day_of_month
        return d


@dataclass
class NotificationSettingsRequest:
    sms: bool
    email: bool
    phone: bool

    def to_dict(self) -> dict[str, Any]:
        return {"sms": self.sms, "email": self.email, "phone": self.phone}


@dataclass
class UpdateDeviceTokenRequest:
    device_token: str
    device_type: str = "python"
    os_version: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_token": self.device_token,
            "device_type": self.device_type,
            "os_version": self.os_version or "1",
        }


@dataclass
class LandlordRequest:
    password: str
    premises_number: str

    def to_dict(self) -> dict[str, Any]:
        return {"password": self.password, "premises_number": self.premises_number}


@dataclass
class DeleteCreditCardRequest:
    cc_token: str

    def to_dict(self) -> dict[str, Any]:
        return {"cc_token": self.cc_token}


# --- Responses ---


@dataclass
class LoginResponse(BaseResponse):
    auth_token: str = ""
    user: UserServer | None = None
    house: HouseServer | None = None
    credit_cards: list[CreditCardServer] = field(default_factory=list)
    premises_number: str = ""
    is_legacy_meter: bool = False
    is_no_wan_meter: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> LoginResponse:
        if d is None:
            return cls()
        cards = d.get("credit_cards") or []
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            auth_token=d.get("auth_token", ""),
            user=UserServer.from_dict(d.get("user")),
            house=HouseServer.from_dict(d.get("house")),
            credit_cards=[CreditCardServer.from_dict(c) for c in cards if c],
            premises_number=d.get("premises_number", ""),
            is_legacy_meter=d.get("is_legacy_meter", False),
            is_no_wan_meter=d.get("is_no_wan_meter", False),
        )


@dataclass
class BalanceResponse(BaseResponse):
    balance: float = 0.0
    credit_low: bool = False
    emergency_credit: bool = False
    last_reading: int = 0
    last_top_up_time: int = 0
    last_top_up_amount: float = 0.0
    pending_top_up: bool = False
    pending_top_up_by: str = ""
    power_off: bool = False
    top_up_in_days: int = 0

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> BalanceResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            balance=float(d.get("balance", 0)),
            credit_low=d.get("credit_low", False),
            emergency_credit=d.get("emergency_credit", False),
            last_reading=int(d.get("last_reading", 0)),
            last_top_up_time=int(d.get("last_top_up_time", 0)),
            last_top_up_amount=float(d.get("last_top_up_amount", 0)),
            pending_top_up=d.get("pending_top_up", False),
            pending_top_up_by=d.get("pending_top_up_by", ""),
            power_off=d.get("power_off", False),
            top_up_in_days=int(d.get("top_up_in_days", 0)),
        )


@dataclass
class TopUpResponse(BaseResponse):
    last_top_up_time: int = 0
    latest_balance: float = 0.0
    pending_top_up: bool = False
    top_up_code: str = ""
    top_up_in_days: int = 0
    top_up_message: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> TopUpResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            last_top_up_time=int(d.get("last_top_up_time", 0)),
            latest_balance=float(d.get("latest_balance", 0)),
            pending_top_up=d.get("pending_top_up", False),
            top_up_code=d.get("top_up_code", ""),
            top_up_in_days=int(d.get("top_up_in_days", 0)),
            top_up_message=d.get("top_up_message", ""),
        )


@dataclass
class UsagesResponse(BaseResponse):
    day: list[UsageDataServer] = field(default_factory=list)
    month: list[UsageDataServer] = field(default_factory=list)
    week: list[UsageDataServer] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> UsagesResponse:
        if d is None:
            return cls()
        def load_list(key: str) -> list[UsageDataServer]:
            items = d.get(key) or []
            return [x for i in items if i and (x := UsageDataServer.from_dict(i))]
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            day=load_list("day"),
            month=load_list("month"),
            week=load_list("week"),
        )


@dataclass
class CompareResponse(BaseResponse):
    month: CompareTimeDataServer | None = None
    week: CompareTimeDataServer | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> CompareResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            month=CompareTimeDataServer.from_dict(d.get("month")),
            week=CompareTimeDataServer.from_dict(d.get("week")),
        )


@dataclass
class ConfigInfoResponse(BaseResponse):
    auto_up_amounts: list[int] = field(default_factory=list)
    scheduled_top_up_amounts: list[int] = field(default_factory=list)
    thresholds: list[int] = field(default_factory=list)
    top_up_amounts: list[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> ConfigInfoResponse:
        if d is None:
            return cls()
        def int_list(key: str) -> list[int]:
            raw = d.get(key)
            if raw is None:
                return []
            return [int(x) for x in raw] if isinstance(raw, list) else []
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            auto_up_amounts=int_list("auto_up_amounts"),
            scheduled_top_up_amounts=int_list("scheduled_top_up_amounts"),
            thresholds=int_list("thresholds"),
            top_up_amounts=int_list("top_up_amounts"),
        )


@dataclass
class DefaultInfoResponse(BaseResponse):
    default_adults: int = 0
    default_bedrooms: int = 0
    default_children: int = 0
    max_adults: int = 0
    max_bedrooms: int = 0
    max_children: int = 0
    heating_types: list[FieldServer] = field(default_factory=list)
    house_types: list[FieldServer] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> DefaultInfoResponse:
        if d is None:
            return cls()
        def field_list(key: str) -> list[FieldServer]:
            raw = d.get(key) or []
            return [FieldServer.from_dict(x) for x in raw if x] or []
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            default_adults=int(d.get("default_adults", 0)),
            default_bedrooms=int(d.get("default_bedrooms", 0)),
            default_children=int(d.get("default_children", 0)),
            max_adults=int(d.get("max_adults", 0)),
            max_bedrooms=int(d.get("max_bedrooms", 0)),
            max_children=int(d.get("max_children", 0)),
            heating_types=field_list("heating_types"),
            house_types=field_list("house_types"),
        )


@dataclass
class GetPrefsResponse:
    email: bool = False
    phone: bool = False
    sms: bool = False
    should_show: bool = False
    should_show_message: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> GetPrefsResponse:
        if d is None:
            return cls()
        return cls(
            email=d.get("email", False),
            phone=d.get("phone", False),
            sms=d.get("sms", False),
            should_show=d.get("should_show", False),
            should_show_message=d.get("should_show_message", ""),
        )


@dataclass
class NotificationSettingsResponse(BaseResponse):
    email: bool = False
    sms: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> NotificationSettingsResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            email=d.get("email", False),
            sms=d.get("sms", False),
        )


@dataclass
class ActiveTopUpsResponse(BaseResponse):
    auto_top_ups: list[TopUpUser] = field(default_factory=list)
    scheduled: list[TopUpUser] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> ActiveTopUpsResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            auto_top_ups=[TopUpUser.from_dict(x) for x in (d.get("auto_top_ups") or []) if x],
            scheduled=[TopUpUser.from_dict(x) for x in (d.get("scheduled") or []) if x],
        )


@dataclass
class TopUpHistoryResponse(BaseResponse):
    top_ups: list[TopUpServer] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> TopUpHistoryResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            top_ups=[TopUpServer.from_dict(x) for x in (d.get("top_ups") or []) if x],
        )


@dataclass
class LandLordCheckResponse(BaseResponse):
    is_landlord_account: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> LandLordCheckResponse:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            is_landlord_account=d.get("is_landlord_account", False),
        )


@dataclass
class CredoraxHPPLinkReturn:
    success: bool | None = None
    message: str = ""
    hpplink: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> CredoraxHPPLinkReturn:
        if d is None:
            return cls()
        return cls(
            success=d.get("success"),
            message=d.get("message", ""),
            hpplink=d.get("hpplink", ""),
        )


# --- LevelPayUsage (rebrand usage; nested usageData) ---


@dataclass
class LevelPayUsage:
    success: bool = False
    message: str = ""
    error_code: int = 0
    usage_data: dict[str, Any] = field(default_factory=dict)  # keep raw for flexibility

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> LevelPayUsage:
        if d is None:
            return cls()
        return cls(
            success=d.get("success", False),
            message=d.get("message", ""),
            error_code=int(d.get("error_code", 0)),
            usage_data=d.get("usageData") or d.get("usage_data") or {},
        )
