"""CLI for the Neware battery cycling API."""

import typer

app = typer.Typer()


@app.command()
def start() -> None:
    """Start the cycling process."""
    typer.echo("Starting the cycling process for battery is NOT IMPLEMENTED YET.")


@app.command()
def status() -> None:
    """Get the status of the cycling process."""
    typer.echo("Getting the status of the cycling process is NOT IMPLEMENTED YET.")


if __name__ == "__main__":
    app()
