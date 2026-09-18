from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from kernellab.cli.output import print_error, print_success

image_app = typer.Typer(help="Manage VM images")
console = Console()


def _get_service():
    from kernellab.images.repository import ImageRepository
    from kernellab.images.service import ImageService
    from kernellab.persistence.database import DatabaseManager

    db = DatabaseManager()
    db.create_tables()
    repo = ImageRepository(db)
    return ImageService(repo)


@image_app.command("add")
def add_image(
    name: str = typer.Argument(..., help="Image name"),
    path: str = typer.Argument(..., help="Path to image file"),
    provider: str = typer.Option("virtualbox", help="Target provider"),
    format: str | None = typer.Option(None, help="Image format (auto-detected from extension)"),
    architecture: str = typer.Option("x86_64", help="Target architecture"),
) -> None:
    """Register a VM image."""
    svc = _get_service()
    try:
        image = svc.add_image(
            name=name,
            path=path,
            provider=provider,
            format=format,
            architecture=architecture,
        )
        print_success(f"Image '{image.name}' registered (id={image.id}, format={image.format})")
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc


@image_app.command("list")
def list_images() -> None:
    """List registered images."""
    svc = _get_service()
    images = svc.list_images()

    if not images:
        print_error("No images registered.")
        raise typer.Exit(1)

    table = Table(title="Images", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="bold")
    table.add_column("Provider")
    table.add_column("Format")
    table.add_column("Architecture")
    table.add_column("Path")

    for img in images:
        table.add_row(img.name, img.provider, img.format, img.architecture, img.path)

    console.print(table)


@image_app.command("show")
def show_image(name: str = typer.Argument(..., help="Image name")) -> None:
    """Show image details."""
    svc = _get_service()
    try:
        image = svc.get_image(name)
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc

    from rich.panel import Panel

    lines = [
        f"[bold]Name:[/bold]         {image.name}",
        f"[bold]ID:[/bold]           {image.id}",
        f"[bold]Provider:[/bold]     {image.provider}",
        f"[bold]Format:[/bold]       {image.format}",
        f"[bold]Architecture:[/bold] {image.architecture}",
        f"[bold]Path:[/bold]         {image.path}",
        f"[bold]Created:[/bold]      {image.created_at.isoformat()}",
    ]
    console.print(Panel("\n".join(lines), title="Image Details", border_style="cyan"))


@image_app.command("remove")
def remove_image(name: str = typer.Argument(..., help="Image name")) -> None:
    """Remove an image registration."""
    svc = _get_service()
    try:
        svc.remove_image(name)
        print_success(f"Image '{name}' removed.")
    except Exception as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
