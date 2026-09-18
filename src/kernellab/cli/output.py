from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

MARKERS = {
    "success": "[green]\u2713[/green]",
    "error": "[red]\u2717[/red]",
    "info": "[blue]\u24d8[/blue]",
    "warning": "[yellow]\u26a0[/yellow]",
}


def print_success(message: str) -> None:
    console.print(f"{MARKERS['success']} {message}")


def print_error(message: str) -> None:
    console.print(f"{MARKERS['error']} {message}")


def print_info(message: str) -> None:
    console.print(f"{MARKERS['info']} {message}")


def print_warning(message: str) -> None:
    console.print(f"{MARKERS['warning']} {message}")


def print_table(title: str, columns: list[str], rows: list[list[str]]) -> None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_lab_detail(lab: dict[str, Any]) -> None:
    lines = [
        f"[bold]Name:[/bold]       {lab['name']}",
        f"[bold]ID:[/bold]         {lab['id']}",
        f"[bold]Status:[/bold]     {lab['status']}",
        f"[bold]Provider:[/bold]   {lab['provider']}",
        f"[bold]Created:[/bold]    {lab['created_at']}",
        f"[bold]Updated:[/bold]    {lab['updated_at']}",
    ]
    if lab.get("description"):
        lines.insert(2, f"[bold]Description:[/bold] {lab['description']}")
    console.print(Panel("\n".join(lines), title="Lab Details", border_style="cyan"))


def print_job_detail(job: dict[str, Any]) -> None:
    lines = [
        f"[bold]ID:[/bold]         {job['id']}",
        f"[bold]Lab:[/bold]        {job['lab_id']}",
        f"[bold]Type:[/bold]       {job['type']}",
        f"[bold]Status:[/bold]     {job['status']}",
        f"[bold]Created:[/bold]    {job['created_at']}",
    ]
    if job.get("started_at"):
        lines.append(f"[bold]Started:[/bold]    {job['started_at']}")
    if job.get("finished_at"):
        lines.append(f"[bold]Finished:[/bold]   {job['finished_at']}")
    if job.get("exit_code") is not None:
        lines.append(f"[bold]Exit Code:[/bold]  {job['exit_code']}")
    if job.get("error"):
        lines.append(f"[bold]Error:[/bold]      [red]{job['error']}[/red]")
    console.print(Panel("\n".join(lines), title="Job Details", border_style="cyan"))


def print_job_logs(logs: str) -> None:
    console.print(Panel(logs, title="Job Logs", border_style="dim"))
