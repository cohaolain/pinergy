# Pinergy API – Reverse-Engineering Findings

This document describes the API used by the Pinergy Android app, derived from the decompiled smali and resources (resource IDs → `public.xml` → `strings.xml` and related values).

---

## 1. Resource ID → Configuration

| Resource ID   | Resource name (public.xml)              | Value / meaning |
|---------------|-----------------------------------------|------------------|
| **0x7f140087** | `conf_server_url` (string)             | **API root** (see below) |
| 0x7f0b0006    | `conf_server_connect_timeout_millisec` (integer) | 90000 ms |
| 0x7f0b0007    | `conf_server_read_timeout_millisec` (integer)   | 90000 ms |
| 0x7f050003    | `conf_server_full_logs` (bool)         | true (Retrofit log level FULL when true, NONE otherwise) |

**API root (from `strings.xml`):**

- **`conf_server_url`** = `https://api.pinergy.ie/api/`

All Pinergy app API calls (except payment/key endpoints below) use this base URL.

---

## 2. ServerConnector and API Clients

- **Retrofit 1.x** with OkHttp, Gson converter, custom `PinergyErrorHandler` and `PinergyConverter`.
- **Single interface:** `PinergyApi` — same interface is used against different base URLs depending on context:

| Method            | Base URL source | Use |
|-------------------|-----------------|-----|
| `build()`, `apiCredRedirect()` | `getString(0x7f140087)` → **https://api.pinergy.ie/api/** | Main app API + Credorax redirect (Pinergy backend) |
| `apiPKey()`        | Hardcoded `"https://ppskey-int.credorax.com/"` | Credorax key/payment key service |
| `apiPayment()`     | Hardcoded `"https://pps-int.credorax.com/"`   | Credorax payment processing |

So:

- **Pinergy backend:** `https://api.pinergy.ie/api/`
- **Credorax (key):** `https://ppskey-int.credorax.com/`
- **Credorax (payments):** `https://pps-int.credorax.com/`

---

## 3. Authentication

- **Header name:** `auth_token` (constant in `PinergyApi`: `AUTHORIZATION_HEADER_NAME = "auth_token"`).
- Authenticated requests send `auth_token: <token>`.
- Token is obtained from **POST /login** (see below).
- **Login** does **not** send `auth_token`; only the body is sent (`@Body` only on `PinergyApi.login`).

### 3.1 Login request (app behaviour)

- The **live app** uses **AuthViewModel** → **RetroInstance/ApiService** with **LoginApiRequest**: only **email**, **password**, **device_token** (no `device_type` or `os_version`).
- **Password:** sent as **SHA-1(UTF-8) hex** (40 chars). `CommonUtils.getHash(String)` = SHA-1 → `convertToHex` → lowercase hex. The Python client hashes the password the same way before sending.
- **AuthHelper** (legacy ServerConnector path) used a different request shape; the current API is the new one (LoginApiRequest, three fields only).

---

## 4. Pinergy API Endpoints (base: `https://api.pinergy.ie/api/`)

All paths are relative to the base URL. Same interface is re-used for Credorax bases where noted.

### 4.0 Version & checkmail (no auth)

**Version (app update info)** — root host, not under `/api`:

- **URL:** `https://api.pinergy.ie/version.json`
- **HTTP:** GET, no auth.
- **Response (example):**

```json
{
  "ios": {
    "minimum_version": "2.3.8",
    "latest_version": {
      "version": "2.3.8",
      "notification_type": "ALWAYS"
    }
  },
  "android": {
    "minimum_version": "2.5.2",
    "minimum_version_min_sdk": 16,
    "latest_version": {
      "version": "2.5.2",
      "notification_type": "ALWAYS",
      "min_sdk": 16
    },
    "required_version": 256,
    "last_version_available": 256,
    "notify_last_version_frequency": "ALWAYS"
  },
  "meta": {
    "below_minimum": "A new version of the app is available. Please update to continue using the app. If the update page doesn't open, search for Pinergy Smart in the Store manually.",
    "not_latest": "There is a new version of the app available. Please update to continue to get the most from your Pinergy system."
  }
}
```

**Check email (before password on login):**

- **Path:** `https://api.pinergy.ie/api/checkmail`
- **HTTP:** POST (or GET with param); request sends **email_address** (e.g. `email_address: yourmail@example.ie`).
- **Use:** The app calls this during login **before** the user enters password, to validate the email.
- **Response (example):** `{"success": true, "message": "", "error_code": 0}`.

### 4.1 Auth & account

| Method | Path          | HTTP | Auth   | Description |
|--------|---------------|------|--------|-------------|
| checkmail | `/checkmail` | POST | No     | Body/param: `email_address`. Called before password entry on login. Returns `{success, message, error_code}`. |
| login  | `/login`      | POST | No     | Body: `LoginRequest`. Returns `LoginResponse` (includes token). |
| logout | `/logout`     | POST | Yes    | Body: `EmptyRequest`. Returns `BaseResponse`. |
| register | `/register` | POST | No     | Body: `RegisterRequest`. Returns `BaseResponse`. |
| forgotPassword | `/forgot` | POST | No | Body: `EmptyRequest`, query `email`. Returns `BaseResponse`. |
| changePassword | `/changepass` | POST | Yes | Body: `ChangePasswordRequest`. Returns `BaseResponse`. |

### 4.2 Balance & top-up

| Method          | Path             | HTTP | Auth | Description |
|-----------------|------------------|------|------|-------------|
| balance         | `/balance`       | GET  | Yes  | Returns `BalanceResponse`. |
| topUp           | `/topup`         | POST | Yes  | Body: `TopUpRequest`. Returns `TopUpResponse`. |
| scheduleTopUp   | `/scheduletopup` | POST | Yes  | Body: `TopUpRequest`. Returns `BaseResponse`. |
| autoTopUp      | `/autotopup`     | POST | Yes  | Body: `TopUpRequest`. Returns `BaseResponse`. |
| getActiveTopUps | `/activetopups`  | GET  | Yes  | Returns `ActiveTopUpsResponse`. |
| getTopUpHistory | `/topuphistory`  | GET  | Yes  | Returns `TopUpHistoryResponse`. |

### 4.3 Usage & compare

| Method           | Path           | HTTP | Auth | Description |
|------------------|----------------|------|------|-------------|
| getUsages        | `/usage`       | GET  | Yes  | Returns `UsagesResponse`. |
| getUsagesRebrand | `/levelPayUsage` | GET | Yes  | Returns `LevelPayUsage` (rebrand model). |
| compare          | `/compare`     | GET  | Yes  | Returns `CompareResponse`. |

### 4.4 Profile & settings

| Method                | Path              | HTTP | Auth | Description |
|-----------------------|-------------------|------|------|-------------|
| editProfile           | `/editprofile`    | POST | Yes  | Body: `EditProfileRequest`. Returns `BaseResponse`. |
| updateHouse           | `/updatehouse`    | POST | Yes  | Body: `EditHouseDetailsRequest`. Returns `BaseResponse`. |
| getNotificationSettings | `/getnotif`     | GET  | Yes  | Returns `GetPrefsResponse`. |
| notificationSettings  | `/updatenotif`    | POST | Yes  | Body: `NotificationSettingsRequest`. Returns `NotificationSettingsResponse`. |
| updateDeviceToken     | `/updatedevicetoken` | POST | Yes | Body: `UpdateDeviceTokenRequest`. Returns `BaseResponse`. |

### 4.5 Cards (Credorax flow via Pinergy backend)

| Method          | Path       | HTTP | Auth | Description |
|-----------------|------------|------|------|-------------|
| addCreditCard   | `/addcc/`  | POST | Yes  | Body: `TypedInput`. Returns `AddCreditCardResponse`. |
| editCreditCard  | `/editcc/` | POST | Yes  | Body: `TypedInput`. Returns `EditCreditCardResponse`. |
| deleteCreditCard| `/deletecc`| POST | Yes  | Body: `DeleteCreditCardRequest`. Returns `BaseResponse`. |

### 4.6 Config & landlord

| Method        | Path          | HTTP | Auth | Description |
|---------------|---------------|------|------|-------------|
| getConfigInfo | `/configinfo` | GET  | Yes  | Returns `ConfigInfoResponse`. |
| getDefaultsInfo | `/defaultsinfo` | GET | No   | Returns `DefaultInfoResponse`. |
| landLordCheck | `/landlordcheck` | GET | No   | Query: `premises_number`. Returns `LandLordCheckResponse`. |
| landlordVerify| `/landlordverify` | POST | No | Body: `LandlordRequest`. Returns `BaseResponse`. |

**What landLordCheck / landlordVerify are for:** Some Pinergy accounts are **landlord-managed** (e.g. rental properties). The flow is:

1. **landLordCheck** — `GET /landlordcheck?premises_number=<card_number>`. Returns `is_landlord_account` (boolean). The app calls this when the user enters their Pinergy card number (e.g. at login/registration).
2. If `is_landlord_account` is true, the app shows **LandlordVerifyDialogFragment**: a dialog with a message, password field, Cancel and Submit. The user must enter a **Landlord Password** (shared by the landlord with the tenant) to proceed.
3. **landlordVerify** — `POST /landlordverify` with body `{ "password", "premises_number" }`. Verifies that password and returns `BaseResponse`; on success the app continues (e.g. login/registration).

**App strings (from `strings.xml`):**
- `landlord_password_label` (0x7f1400fa): **"Landlord Password"**
- `your_pinergy_card_number_label`: **"Your Pinergy Card Number is associated with a Landlord account."**
- `message_enter_password` (0x7f140136, used in landlord dialog when empty): **"Please enter a password"**
- Dialog uses `account_password_label` for the password field label and `submit_label` for the submit button.

### 4.7 Payment redirect (Pinergy backend → Credorax)

| Method        | Path              | HTTP | Auth | Description |
|---------------|-------------------|------|------|-------------|
| getCredRedirect | `/CredoraxHPPLink` | POST | Yes  | Body: `RedirectRequest`. Used with `apiCredRedirect()` (base URL = `conf_server_url`). Returns/callback: `BaseResponse` / `JsonObject`. |
| getRedirect    | `/CredoraxHPPLink` | POST | Yes  | Body: `RedirectRequest`. Returns `CredoraxHPPLinkReturn`. |

---

## 5. Credorax-specific endpoints (same PinergyApi interface, different base URL)

Used with **apiPKey()** base `https://ppskey-int.credorax.com/`:

| Method   | Path                        | HTTP | Body/params |
|----------|-----------------------------|------|-------------|
| getPKey  | `/keypayment/rest/v2/store` | POST | FormUrlEncoded: M, RequestID, Statickey, b1, b3, b4, b5, c1. Callback: `JsonObject`. |

Used with **apiPayment()** base `https://pps-int.credorax.com/`:

| Method    | Path                              | HTTP | Body/params |
|-----------|-----------------------------------|------|-------------|
| getRedirect (form) | `/keypayment/rest/v2/paymentRequest` | POST | FormUrlEncoded: K, M, O, a1, a4, a5, SuccessURL, FailURL, BackURL. Callback: `JsonObject`. |
| getToken  | `/keypayment/rest/v2/payment`     | POST | Query: K, M, O, PKey, Statickey, a1, a4, a5, a6, a7. Body: `JsonObject`. Callback: `JsonObject`. |
| getTokenA9| `/keypayment/rest/v2/payment`     | POST | Same path; extra query param `a9`. Body: `JsonObject`. Callback: `JsonObject`. |

---

## 6. Summary table – Full URLs (Pinergy backend)

Base: **`https://api.pinergy.ie/api/`**

| Endpoint            | Full URL |
|---------------------|----------|
| Version             | `https://api.pinergy.ie/version.json` |
| Check email         | `https://api.pinergy.ie/api/checkemail` |
| Login               | `https://api.pinergy.ie/api/login` |
| Logout               | `https://api.pinergy.ie/api/logout` |
| Register            | `https://api.pinergy.ie/api/register` |
| Forgot password     | `https://api.pinergy.ie/api/forgot` |
| Change password     | `https://api.pinergy.ie/api/changepass` |
| Balance             | `https://api.pinergy.ie/api/balance` |
| Top-up              | `https://api.pinergy.ie/api/topup` |
| Schedule top-up     | `https://api.pinergy.ie/api/scheduletopup` |
| Auto top-up         | `https://api.pinergy.ie/api/autotopup` |
| Active top-ups      | `https://api.pinergy.ie/api/activetopups` |
| Top-up history      | `https://api.pinergy.ie/api/topuphistory` |
| Usage               | `https://api.pinergy.ie/api/usage` |
| Level Pay usage     | `https://api.pinergy.ie/api/levelPayUsage` |
| Compare             | `https://api.pinergy.ie/api/compare` |
| Edit profile        | `https://api.pinergy.ie/api/editprofile` |
| Update house        | `https://api.pinergy.ie/api/updatehouse` |
| Get notification    | `https://api.pinergy.ie/api/getnotif` |
| Update notification | `https://api.pinergy.ie/api/updatenotif` |
| Update device token | `https://api.pinergy.ie/api/updatedevicetoken` |
| Add card            | `https://api.pinergy.ie/api/addcc/` |
| Edit card           | `https://api.pinergy.ie/api/editcc/` |
| Delete card         | `https://api.pinergy.ie/api/deletecc` |
| Config info         | `https://api.pinergy.ie/api/configinfo` |
| Defaults info       | `https://api.pinergy.ie/api/defaultsinfo` |
| Landlord check      | `https://api.pinergy.ie/api/landlordcheck` |
| Landlord verify     | `https://api.pinergy.ie/api/landlordverify` |
| Credorax HPP link   | `https://api.pinergy.ie/api/CredoraxHPPLink` |


---

## 7. Tracing resource IDs (how this was derived)

1. **conf_server_url:** Code uses `0x7f140087` → `public.xml`: `type="string" name="conf_server_url" id="0x7f140087"` → `strings.xml`: `<string name="conf_server_url">https://api.pinergy.ie/api/</string>`.
2. **Timeouts and logging:** `ServerConnector.smali` uses `0x7f0b0006`, `0x7f0b0007` (integers) and `0x7f050003` (boolean); resolved via `public.xml` to `integers.xml` and `bools.xml`.
3. **Endpoints:** All paths come from `PinergyApi.smali` (`@retrofit/http/GET`, `@retrofit/http/POST`, `value = "/..."`).
4. **Credorax bases:** Hardcoded in `ServerConnector.smali` in `apiPKey()` and `apiPayment()`.

This document reflects the API as implemented in the decompiled app; actual server behaviour may differ (e.g. extra validations or versioning).

---

## Appendix: Request, response and data object definitions

All JSON keys below are from Gson `@SerializedName` in the smali. Types are abbreviated: string, int, bool, double, long; lists/objects described inline.

### Base and common

- **BaseResponse** — `success` (bool), `message` (string), `error_code` (int). Base for most API responses.
- **EmptyRequest** — No body fields (used for logout, forgot with email as query param).

### Requests (body/query)

- **LoginRequest** — `email`, `password`, `device_token`, `device_type` (e.g. "android"), `os_version`.
- **RegisterRequest** — `email`, `password`, `first_name`, `last_name`, `title`, `mobile`, `premises_number`, `house` (HouseServer), `credit_card` (CreditCardServer), `device_token`.
- **ChangePasswordRequest** — `new_password`.
- **EditProfileRequest** — `title`, `first_name`, `last_name`, `mobile`.
- **EditHouseDetailsRequest** — `house` (HouseServer).
- **TopUpRequest** — `pinergy_id`, `cc_token`, `amount` (double), optional `threshold` (Double), optional `day_of_month` (Integer).
- **NotificationSettingsRequest** — `sms`, `email`, `phone` (all bool).
- **UpdateDeviceTokenRequest** — `device_token`, `device_type`, `os_version`.
- **RedirectRequest** — `BackUrl`, `SuccessUrl`, `FailUrl`, `premises_number`, `email`.
- **LandlordRequest** — `password`, `premises_number`.
- **DeleteCreditCardRequest** — `cc_token`.

### Responses

- **LoginResponse** (extends BaseResponse) — `auth_token`, `user` (UserServer), `house` (HouseServer), `credit_cards` (List&lt;CreditCardServer&gt;), `premises_number`, `is_legacy_meter`, `is_no_wan_meter`.
- **BalanceResponse** — BaseResponse + `balance`, `credit_low`, `emergency_credit`, `last_reading`, `last_top_up_time`, `last_top_up_amount`, `pending_top_up`, `pending_top_up_by`, `power_off`, `top_up_in_days`.
- **TopUpResponse** — BaseResponse + `last_top_up_time`, `latest_balance`, `pending_top_up`, `top_up_code`, `top_up_in_days`, `top_up_message`.
- **UsagesResponse** — BaseResponse + `day`, `month`, `week` (each List&lt;UsageDataServer&gt;).
- **RebrandUsagesResponse** — BaseResponse + `daily`, `monthly`, `sevenDays`, `weekly` (each List&lt;UsageDataServer&gt;).
- **CompareResponse** — BaseResponse + `month`, `week` (each CompareTimeDataServer).
- **ConfigInfoResponse** — BaseResponse + `auto_up_amounts`, `scheduled_top_up_amounts`, `thresholds`, `top_up_amounts` (integer arrays).
- **DefaultInfoResponse** — BaseResponse + `default_adults`, `default_bedrooms`, `default_children`, `max_adults`, `max_bedrooms`, `max_children`, `heating_types`, `house_types` (lists of FieldServer).
- **GetPrefsResponse** — `email`, `phone`, `sms`, `should_show`, `should_show_message` (notification prefs).
- **NotificationSettingsResponse** — `email`, `sms` (bool).
- **ActiveTopUpsResponse** — BaseResponse + `auto_top_ups`, `scheduled` (each List&lt;TopUpUser&gt;).
- **TopUpHistoryResponse** — BaseResponse + `top_ups` (List&lt;TopUpServer&gt;).
- **AddCreditCardResponse** — BaseResponse + `cc_token`.
- **EditCreditCardResponse** — BaseResponse + `credit_card` (CreditCardServer).
- **LandLordCheckResponse** — BaseResponse + `is_landlord_account` (bool).
- **CredoraxHPPLinkReturn** — `success`, `message`, `hpplink` (Hosted Payment Page URL).

### LevelPayUsage (GET /levelPayUsage)

- **LevelPayUsage** — `success`, `message`, `error_code`, `usageData` (UsageData). Rebrand usage model; uses `LOWER_CASE_WITH_UNDERSCORES` when parsing from JSON. Nested structure includes `UsageData` → `daily` (Daily), `weekly` (Weekly), `monthly` (Monthly), `sevenDays` (SevenDays); Daily has `labels`, `values` (List&lt;Value&gt;), `flags`; Value has `label`, `day_euro`, `half_hourly_*` lists (euro/kWh, cohort/typical), etc.

### Server data (nested in responses)

- **HouseServer** — `type`, `adult_count`, `bedroom_count`, `children_count`, `heating_type` (all int).
- **UserServer** — `name`, `title`, `pinergy_id`, `mobile_number`, `email_notifications`, `sms_notifications`.
- **CreditCardServer** — `name`, `cc_token`, `payment_token`, `last_4_digits`, `z50`, `email`.
- **UsageDataServer** — `date` (long), `amount`, `kwh`, `co2` (double).
- **TopUpServer** — `top_up_id`, `top_up_amount`, `top_up_date`, `top_up_action`, `top_up_code`.
- **TopUpUser** — `customer`, `current_user` (bool), `top_up_amount`, `top_up_day`, `top_up_threshold`.
- **FieldServer** — `id`, `name` (e.g. heating/house type options).
- **CompareTimeDataServer** — `available` (bool), `kwh` (CompareDataServer), `co2` (CompareDataServer).
- **CompareDataServer** — `average_home`, `users_home` (double).
- **Monthly** (compare/usage) — `avgMonthCohortEuro`, `avgMonthCohortKwh`, `avgMonthEuro`, `avgMonthkWh`, `labels` (List&lt;String&gt;), `monthlykWh`.

### String / config notes from the app

- **Auth header:** `auth_token` (sent as HTTP header; value from login).
- **Forgot password:** POST `/forgot` with body EmptyRequest; `email` is sent as **query** parameter.
- **Landlord:** See section 4.6; `premises_number` is the Pinergy card number in this flow; landlord password is a separate secret for tenant access.
- **Config integers (from `integers.xml`):** `conf_server_connect_timeout_millisec` = 90000, `conf_server_read_timeout_millisec` = 90000.
- **Config bool:** `conf_server_full_logs` = true → Retrofit log level FULL (debug builds).
