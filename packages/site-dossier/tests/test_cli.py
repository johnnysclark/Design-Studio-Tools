"""CLI smoke tests — --help and --version don't need network."""

from site_dossier.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # typer renders the help with the command name; assert on flags we know are present.
    assert "address" in result.stdout.lower()
    assert "--lat" in result.stdout
    assert "--sections" in result.stdout


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "site-dossier" in result.stdout


def test_missing_input_exits_2():
    result = runner.invoke(app, [])
    assert result.exit_code == 2
