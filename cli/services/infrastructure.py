import click
import requests

from cli.utils import api_request, format_output


@click.group()
def infra():
    """Infrastructure management commands."""
    pass


@infra.command()
@click.option(
    "--format",
    default="raw",
    type=click.Choice(["csv", "column", "json", "raw"], case_sensitive=False),
    help="Output format",
)
@format_output()
def list(format) -> None:
    """List all infrastructure resources."""

    res = api_request(
        method="get",
        endpoint="/api/gsm/gsm/common/getNodeList?type=BMC",
    )

    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        click.secho(f"Error fetching data: {http_err}", fg="red")
        return

    return res.json()
