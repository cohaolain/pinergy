"""CLI for Pinergy API client (rich-click)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import rich_click as click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from pinergy_client.client import PinergyClient
from pinergy_client.models import TopUpRequest

load_dotenv()

console = Console()

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True


def get_client() -> PinergyClient:
    base = os.environ.get("PINERGY_BASE_URL", "https://api.pinergy.ie/api")
    token = os.environ.get("PINERGY_AUTH_TOKEN")
    return PinergyClient(base_url=base, auth_token=token or None)


@click.group()
@click.option(
    "--base-url",
    envvar="PINERGY_BASE_URL",
    default="https://api.pinergy.ie/api",
    help="API base URL",
)
@click.pass_context
def main(ctx: click.Context, base_url: str) -> None:
    """Pinergy API client — balance, usage, top-up, and more."""
    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base_url.rstrip("/")


@main.command()
@click.option("--email", envvar="PINERGY_EMAIL", required=True, help="Account email")
@click.option("--password", envvar="PINERGY_PASSWORD", required=True, help="Account password")
@click.pass_context
def login(ctx: click.Context, email: str, password: str) -> None:
    """Log in and print auth token (set PINERGY_AUTH_TOKEN for other commands)."""
    client = PinergyClient(base_url=ctx.obj["base_url"])
    try:
        resp = client.login(email=email, password=password)
        if resp.success and resp.auth_token:
            console.print("[green]Login successful.[/green]")
            console.print(f"Auth token: [dim]{resp.auth_token[:20]}...[/dim]")
        else:
            console.print(f"[red]Login failed: {resp.message}[/red]")
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def balance(ctx: click.Context, token: str) -> None:
    """Fetch current balance and status."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.balance()
        if not resp.success:
            console.print(f"[red]{resp.message}[/red]")
            raise SystemExit(1)
        table = Table(title="Balance")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Balance", f"€{resp.balance:.2f}")
        table.add_row("Credit low", str(resp.credit_low))
        table.add_row("Emergency credit", str(resp.emergency_credit))
        table.add_row("Power off", str(resp.power_off))
        table.add_row("Top up in days", str(resp.top_up_in_days))
        table.add_row("Last top up amount", f"€{resp.last_top_up_amount:.2f}")
        console.print(table)
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def usage(ctx: click.Context, token: str) -> None:
    """Fetch usage (day / week / month)."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.get_usage()
        if not resp.success:
            console.print(f"[red]{resp.message}[/red]")
            raise SystemExit(1)
        def fmt_date(ts: int) -> str:
            if ts <= 0:
                return ""
            # API returns Unix timestamp in seconds
            try:
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                return dt.strftime("%Y-%m-%d")
            except (OSError, ValueError):
                return str(ts)

        for period_name, items in [("Day", resp.day), ("Week", resp.week), ("Month", resp.month)]:
            if not items:
                continue
            table = Table(title=f"Usage — {period_name}")
            table.add_column("Date", style="cyan")
            table.add_column("kWh", style="green")
            table.add_column("Amount", style="green")
            table.add_column("CO2", style="green")
            for u in items[:15]:
                table.add_row(fmt_date(u.date), f"{u.kwh:.2f}", f"€{u.amount:.2f}", f"{u.co2:.2f}")
            if len(items) > 15:
                table.add_row("…", "…", "…", "…")
            console.print(table)
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def config(ctx: click.Context, token: str) -> None:
    """Fetch config (top-up amounts, thresholds)."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.get_config_info()
        if not resp.success:
            console.print(f"[red]{resp.message}[/red]")
            raise SystemExit(1)
        table = Table(title="Config")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("top_up_amounts", str(resp.top_up_amounts))
        table.add_row("auto_up_amounts", str(resp.auto_up_amounts))
        table.add_row("scheduled_top_up_amounts", str(resp.scheduled_top_up_amounts))
        table.add_row("thresholds", str(resp.thresholds))
        console.print(table)
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def level_pay_usage(ctx: click.Context, token: str) -> None:
    """Fetch Level Pay / rebrand usage (usageData)."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.get_level_pay_usage()
        if not resp.success and resp.error_code != 0:
            console.print(f"[red]{resp.message or 'Request failed'}[/red]")
            raise SystemExit(1)
        if resp.usage_data:
            console.print("[bold]Level Pay usage data:[/bold]")
            console.print(json.dumps(resp.usage_data, indent=2, default=str))
        else:
            console.print("[dim]No usage data.[/dim]")
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def account(ctx: click.Context, token: str) -> None:
    """Fetch account notification preferences (email, SMS)."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.get_notification_settings()
        table = Table(title="Account (notification prefs)")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("email notifications", str(resp.email))
        table.add_row("phone notifications", str(resp.phone))
        table.add_row("sms notifications", str(resp.sms))
        table.add_row("should_show", str(resp.should_show))
        if resp.should_show_message:
            table.add_row("should_show_message", resp.should_show_message)
        console.print(table)
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def compare(ctx: click.Context, token: str) -> None:
    """Fetch compare (your usage vs average home)."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.compare()
        if not resp.success:
            console.print(f"[red]{resp.message}[/red]")
            raise SystemExit(1)
        table = Table(title="Compare")
        table.add_column("Period", style="cyan")
        table.add_column("Type", style="cyan")
        table.add_column("Your home", style="green")
        table.add_column("Average home", style="green")
        for period_name, period in [("Month", resp.month), ("Week", resp.week)]:
            if period is None:
                continue
            if period.kwh:
                table.add_row(period_name, "kWh", f"{period.kwh.users_home:.2f}", f"{period.kwh.average_home:.2f}")
            if period.co2:
                table.add_row(period_name, "CO2", f"{period.co2.users_home:.2f}", f"{period.co2.average_home:.2f}")
        console.print(table)
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def active_topups(ctx: click.Context, token: str) -> None:
    """Fetch active top-ups (auto and scheduled)."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.get_active_top_ups()
        if not resp.success:
            console.print(f"[red]{resp.message}[/red]")
            raise SystemExit(1)
        table = Table(title="Active top-ups")
        table.add_column("Type", style="cyan")
        table.add_column("Customer", style="green")
        table.add_column("Amount", style="green")
        table.add_column("Day", style="green")
        table.add_column("Threshold", style="green")
        for u in resp.auto_top_ups:
            table.add_row("auto", u.customer, f"€{u.top_up_amount:.2f}", str(u.top_up_day), str(u.top_up_threshold))
        for u in resp.scheduled:
            table.add_row("scheduled", u.customer, f"€{u.top_up_amount:.2f}", str(u.top_up_day), str(u.top_up_threshold))
        if not resp.auto_top_ups and not resp.scheduled:
            console.print("[dim]No active top-ups.[/dim]")
        else:
            console.print(table)
    finally:
        client.close()


@main.command()
@click.option("--token", envvar="PINERGY_AUTH_TOKEN", required=True, help="Auth token")
@click.pass_context
def topup_history(ctx: click.Context, token: str) -> None:
    """Fetch top-up history."""
    client = PinergyClient(base_url=ctx.obj["base_url"], auth_token=token)
    try:
        resp = client.get_top_up_history()
        if not resp.success:
            console.print(f"[red]{resp.message}[/red]")
            raise SystemExit(1)
        table = Table(title="Top-up history")
        table.add_column("ID", style="cyan")
        table.add_column("Amount", style="green")
        table.add_column("Date", style="green")
        table.add_column("Action", style="green")
        table.add_column("Code", style="green")
        for u in resp.top_ups[:30]:
            ts = datetime.fromtimestamp(u.top_up_date, tz=timezone.utc).strftime("%Y-%m-%d") if u.top_up_date else ""
            table.add_row(u.top_up_id, f"€{u.top_up_amount:.2f}", ts, u.top_up_action, u.top_up_code)
        if len(resp.top_ups) > 30:
            table.add_row("…", "…", "…", "…", "…")
        if not resp.top_ups:
            console.print("[dim]No top-up history.[/dim]")
        else:
            console.print(table)
    finally:
        client.close()


@main.command()
@click.pass_context
def defaults(ctx: click.Context) -> None:
    """Fetch defaults (house types, heating types, limits). No auth required."""
    client = PinergyClient(base_url=ctx.obj["base_url"])
    try:
        resp = client.get_defaults_info()
        if not resp.success:
            console.print(f"[red]{resp.message}[/red]")
            raise SystemExit(1)
        table = Table(title="Defaults")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("default_adults", str(resp.default_adults))
        table.add_row("default_bedrooms", str(resp.default_bedrooms))
        table.add_row("max_adults", str(resp.max_adults))
        table.add_row("max_bedrooms", str(resp.max_bedrooms))
        table.add_row("heating_types", str([(f.id, f.name) for f in resp.heating_types]))
        table.add_row("house_types", str([(f.id, f.name) for f in resp.house_types]))
        console.print(table)
    finally:
        client.close()


@main.command()
@click.option("--premises", required=True, help="Premises (card) number")
@click.pass_context
def landlord_check(ctx: click.Context, premises: str) -> None:
    """Check if premises is a landlord account. No auth required."""
    client = PinergyClient(base_url=ctx.obj["base_url"])
    try:
        resp = client.landlord_check(premises_number=premises)
        if resp.is_landlord_account:
            console.print("[yellow]This is a landlord account.[/yellow]")
        else:
            console.print("[green]Not a landlord account.[/green]")
    finally:
        client.close()


if __name__ == "__main__":
    main()
