from __future__ import annotations

import typer
from rich.console import Console

from kernellab.cli.output import print_error, print_info

config_app = typer.Typer(help="Manage configuration")
console = Console()


@config_app.command("validate")
def validate() -> None:
    """Load and validate kernellab.yaml."""
    from kernellab.config.loader import load_config, validate_config

    try:
        config = load_config()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    errors = validate_config(config)
    if errors:
        print_error("Configuration validation failed:")
        for err in errors:
            console.print(f"  - {err}")
        raise typer.Exit(1)

    print_info(f"Configuration '{config.name}' is valid.")
