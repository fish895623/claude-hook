"""Command-line interface for Claude Hook system."""

import click


@click.group()
@click.version_option(version="0.1.0", prog_name="claude-hook")
def main() -> None:
    """Extensible hook system for Claude Code."""


@main.command()
def init() -> None:
    """Initialize hook configuration."""
    click.echo("Initializing Claude Hook configuration...")
    # TODO: Implement initialization logic


@main.command()
def config() -> None:
    """Configure hooks."""
    click.echo("Opening hook configuration...")
    # TODO: Implement configuration logic


@main.command()
def test() -> None:
    """Test hook system."""
    click.echo("Testing hook system...")
    # TODO: Implement test logic


if __name__ == "__main__":
    main()
