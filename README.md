# Pinergy Python Client

Python client for the **Pinergy API**, reverse-engineered from the official Android app.

> **Disclaimer:** This is an **unofficial** client and is not affiliated with or endorsed by Pinergy. It is based on independent research and reverse-engineering of the public API. Use at your own risk; the API may change without notice and the authors assume no liability for any use of this software.

- **Auth:** Session-based; login with email/password to obtain an `auth_token` sent on subsequent requests.
- **Endpoints:** Balance, usage, top-up, compare, profile, notifications, config, landlord check, etc.

## Requirements

- Python **3.13+**
- `requests`, `rich`, `rich-click`, `python-dotenv`

## Install

From PyPI (Python 3.13+):

```bash
pip install pinergy
```

Optional: use a virtual environment and/or uv:

```bash
python3 -m venv .venv
source .venv/bin/activate   # or on Windows: .venv\Scripts\activate
pip install pinergy
```

**Install from source (development):** from the project root (directory containing `pyproject.toml`):

```bash
pip install -e ".[dev]"
# or: uv pip install -e ".[dev]"
```

## Usage

Both the **library** and **CLI** can use the same environment variables (or a `.env` file with `python-dotenv`). Set any of:

- `PINERGY_EMAIL` / `PINERGY_PASSWORD` — for login
- `PINERGY_AUTH_TOKEN` — use an existing token (skip login)
- `PINERGY_BASE_URL` — optional; default `https://api.pinergy.ie/api`

### As a library

The client reads `PINERGY_BASE_URL`, `PINERGY_AUTH_TOKEN`, and (for login) `PINERGY_EMAIL` / `PINERGY_PASSWORD` from the environment when you don’t pass them. Use a `.env` file and `python-dotenv` if you like.

```python
import json
from pinergy_client import PinergyClient

# Uses PINERGY_* env vars automatically (or .env with load_dotenv())
client = PinergyClient()

# Log in if no PINERGY_AUTH_TOKEN set (email/password from env)
if not client.auth_token:
    resp = client.login()
    if not resp.success:
        print(resp.message)
        exit(1)

print(f"Balance: €{client.balance().balance:.2f}")

# Level Pay / rebrand usage
level_pay = client.get_level_pay_usage()
print("Level Pay usage:", json.dumps(level_pay.usage_data, indent=2, default=str))

client.close()
```

You can pass credentials explicitly instead of using env:

```python
client = PinergyClient()
resp = client.login(email="you@example.ie", password="your_password")
# or: client = PinergyClient(auth_token="existing_token")
```

### CLI

Uses **rich** and **rich-click**. All options can be provided via env vars, so you can omit `--email`, `--password`, `--token` when they are set.

```bash
# With PINERGY_EMAIL and PINERGY_PASSWORD set, login needs no args
pinergy login

# With PINERGY_AUTH_TOKEN set, authenticated commands need no args
pinergy balance
pinergy usage

# Level Pay / rebrand usage (summary tables; use --raw for full JSON)
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

**Level Pay output** — The API returns usage with **half-hourly** resolution (48 slots per day: 00:00, 00:30, …). The CLI prints compact **summary** tables: daily, **peak half-hours (average)** — top 5 consumption and top 5 cost slots — then last 7 days, weekly, and monthly. Each table shows Total kWh, Total €, then for **each plan** in the data (e.g. Standard, Drive, or other tariff names) both **kWh and €** columns. Plan names are read from the API, so different plans are supported. Example extract:

```
Level Pay — Daily (recent days)
┃ Date  ┃ Total kWh ┃ Total € ┃ Drive kWh ┃ Standard kWh ┃ Drive € ┃ Standard € ┃
│ 21/02 │     12.61 │   €0.73 │     12.48 │         0.12 │   €0.69 │      €0.05 │
...
Level Pay — Peak half-hours (average)
┃ Top consumption ┃ Avg kWh ┃ Top cost ┃  Avg € ┃
│ 02:00           │   5.541 │ 02:00    │ €0.304 │
...
Level Pay — Weekly
┃ Week  ┃ Total kWh ┃ Total € ┃ Standard kWh ┃ Drive kWh ┃ Standard € ┃ Drive € ┃
│ 09/02 │    198.66 │  €13.66 │         8.38 │    190.28 │      €3.21 │  €10.45 │
```

Use `--raw` to print the full JSON (including half-hourly series per day).

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

- **Releasing:** See [RELEASING.md](RELEASING.md) for CI/CD and PyPI publish steps.
- **API details:** [Pinergy API reverse-engineering notes](PINERGY_API_FINDINGS.md) document how the API was derived from the Android app.

## License

MIT.
