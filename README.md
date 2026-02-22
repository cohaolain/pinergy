# pinergy-client

Python client for the **Pinergy API**, reverse-engineered from the official Android app.

- **Auth:** Session-based; login with email/password to obtain an `auth_token` sent on subsequent requests.
- **Endpoints:** Balance, usage, top-up, compare, profile, notifications, config, landlord check, etc.

## Requirements

- Python **3.13+**
- `requests`, `rich`, `rich-click`, `python-dotenv`

## Install

From the project root (directory containing `pyproject.toml`):

```bash
# Optional: create a new venv
python3 -m venv .venv
source .venv/bin/activate   # or on Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

Or with uv:

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Usage

### As a library

```python
from pinergy_client import PinergyClient

client = PinergyClient()
resp = client.login(email="you@example.ie", password="your_password")
if not resp.success:
    print(resp.message)
    exit(1)

balance = client.balance()
print(f"Balance: €{balance.balance:.2f}")

usage = client.get_usage()
# usage.day, usage.week, usage.month

client.close()
```

Or with a context manager:

```python
with PinergyClient() as client:
    client.login("you@example.ie", "your_password")
    print(client.balance().balance)
```

Using an existing token:

```python
client = PinergyClient(auth_token="your_token_from_login")
balance = client.balance()
```

### CLI

Uses **rich** and **rich-click**. Commands read credentials from environment (or options).

```bash
# Login (prints token)
pinergy login --email you@example.ie --password your_password

# Balance (requires PINERGY_AUTH_TOKEN or login first)
export PINERGY_AUTH_TOKEN=your_token
pinergy balance

# Usage
pinergy usage

# Level Pay / rebrand usage
pinergy level-pay-usage

# Account (notification prefs: email, SMS)
pinergy account

# Compare (your usage vs average home)
pinergy compare

# Active top-ups (auto & scheduled)
pinergy active-topups

# Top-up history
pinergy topup-history

# Config (top-up amounts, thresholds)
pinergy config

# Defaults (house/heating types; no auth)
pinergy defaults

# Landlord check (no auth)
pinergy landlord-check --premises P123456
```

Environment variables (or `.env`):

- `PINERGY_EMAIL` / `PINERGY_PASSWORD` — for login
- `PINERGY_AUTH_TOKEN` — skip login and use this token
- `PINERGY_BASE_URL` — optional; default `https://api.pinergy.ie/api`

## Tests

**Unit tests** (no network, mocked):

```bash
pytest tests/unit -v
```

**Integration tests** (real API; require credentials in env):

1. Copy `.env.example` to `.env` and set `PINERGY_EMAIL` and `PINERGY_PASSWORD` (or `PINERGY_AUTH_TOKEN`).
2. Run:

```bash
pytest tests/integration -v -m integration
```

Or run all tests (integration tests are skipped if env is not set):

```bash
pytest tests -v
```

## API coverage

- Auth: login, logout, forgot password, change password  
- Balance & top-up: balance, topUp, scheduleTopUp, autoTopUp, active top-ups, top-up history  
- Usage: usage (day/week/month), levelPayUsage  
- Compare: compare  
- Profile: edit profile, update house, notification settings, update device token  
- Cards: delete credit card (add/edit go through Credorax HPP flow)  
- Config: configinfo, defaultsinfo  
- Landlord: landlordcheck, landlordverify  

Request/response types are implemented as dataclasses; see `pinergy_client.models`.

## License

MIT.
