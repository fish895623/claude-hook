"""Test CLI functionality."""

from click.testing import CliRunner

from claude_hooks.cli import main


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Extensible hook system for Claude Code" in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_init_command():
    """Test init command."""
    runner = CliRunner()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert "Initializing Claude Hook configuration" in result.output


def test_config_command():
    """Test config command."""
    runner = CliRunner()
    result = runner.invoke(main, ["config"])
    assert result.exit_code == 0
    assert "Opening hook configuration" in result.output


def test_test_command():
    """Test test command."""
    runner = CliRunner()
    result = runner.invoke(main, ["test"])
    assert result.exit_code == 0
    assert "Testing hook system" in result.output
