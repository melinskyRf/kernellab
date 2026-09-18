from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.table import Table

from kernellab.cli.output import print_error

if TYPE_CHECKING:
    from kernellab.providers.registry import ProviderRegistry

provider_app = typer.Typer(help="Manage providers")
console = Console()


def _get_registry() -> ProviderRegistry:
    from kernellab.providers.registry import get_provider_registry
    return get_provider_registry()


@provider_app.command("list")
def list_providers() -> None:
    """List all providers with availability."""
    registry = _get_registry()
    names = registry.list_providers()

    if not names:
        print_error("No providers registered.")
        raise typer.Exit(1)

    table = Table(title="Providers", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Version")
    table.add_column("Executable")

    for name in sorted(names):
        try:
            info = registry.get_provider_info(name)
            if info.available:
                table.add_row(
                    name,
                    "[green]available[/green]",
                    info.version or "-",
                    info.executable or "-",
                )
            else:
                table.add_row(
                    name,
                    "[red]unavailable[/red]",
                    "-",
                    "-",
                )
        except Exception:
            table.add_row(
                name,
                "[yellow]error[/yellow]",
                "-",
                "-",
            )

    console.print(table)


@provider_app.command("show")
def show_provider(name: str = typer.Argument(..., help="Provider name")) -> None:
    """Show provider capabilities."""
    registry = _get_registry()

    try:
        provider = registry.get(name)
    except KeyError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    info = provider.probe() if hasattr(provider, "probe") else None
    caps = provider.capabilities() if hasattr(provider, "capabilities") else None

    table = Table(title=f"Provider: {name}", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold")
    table.add_column("Value")

    if info:
        table.add_row("Available", "[green]Yes[/green]" if info.available else "[red]No[/red]")
        table.add_row("Version", info.version or "-")
        table.add_row("Executable", info.executable or "-")
        if info.host_info:
            table.add_row("Host Info", info.host_info)
    else:
        table.add_row("Info", "Not available")

    if caps:
        table.add_section()
        table.add_row("Create", "[green]Yes[/green]" if caps.create else "[red]No[/red]")
        table.add_row("Start", "[green]Yes[/green]" if caps.start else "[red]No[/red]")
        table.add_row("Stop", "[green]Yes[/green]" if caps.stop else "[red]No[/red]")
        table.add_row("Destroy", "[green]Yes[/green]" if caps.destroy else "[red]No[/red]")
        table.add_row("Serial", "[green]Yes[/green]" if caps.serial else "[red]No[/red]")
        table.add_row("Snapshots", "[green]Yes[/green]" if caps.snapshots else "[red]No[/red]")
        table.add_row("Guest Exec", "[green]Yes[/green]" if caps.guest_exec else "[red]No[/red]")

    console.print(table)
