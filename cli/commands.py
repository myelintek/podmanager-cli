from importlib.metadata import version

import click
import requests
from jose import jwt

from .services import infrastructure as infra_commands
from .utils import Config


@click.group()
@click.version_option(version=version("podmanager-cli"), message="Gigapod CLI Version %(version)s")
def cli():
    """Main entry point for the CLI."""
    pass


@cli.command()
@click.option("--url", prompt=True, help="API URL", default="https://gigapod.myelintek.com")
@click.option("--account", prompt=True, help="Your account", default="admin")
@click.option("--password", prompt=True, hide_input=True, help="Your password")
def login(url, account, password):
    """Login to the application and save token."""

    try:
        response = requests.post(f"{url}/api/v1/auth/login", params={"account": account, "password": password})
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            click.secho(f"Login failed: {http_err} -> {response.text}", fg="red")
            return

        data = response.json()
        token = data.get("access_token")
        if not token:
            click.secho("Login failed: No access token received.", fg="red")
            return

        # Decode the JWT to get the expiration time
        decoded_token = jwt.decode(token, key=None, options={"verify_signature": False})
        expire_at = str(decoded_token.get("exp"))
        Config.save(target_server=url, access_token=token, expire_at=expire_at)

        click.secho("Login successful.", fg="green")
    except requests.exceptions.RequestException as e:
        click.secho(f"Login failed: {e}", fg="red")


@cli.command()
def logout():
    """Logout from the application and clear token."""
    try:
        Config.clear()
        click.secho("Logout successful.", fg="green")
    except Exception as e:
        click.secho(f"Logout failed: {e}", fg="red")


cli.add_command(infra_commands.infra)

if __name__ == "__main__":
    cli()
