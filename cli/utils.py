import base64
import csv
import functools
import io
import json
from pathlib import Path

import click
import requests
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

CONFIG_FILE = Path("/etc/podmanager/cli/config")


console = Console()


class AuthError(Exception):
    """Custom exception for authentication errors."""

    pass


class Config(BaseModel):
    """
    Configuration model for the CLI.
    This model is used to store the token in a base64 encoded format.
    """

    target_server: str = Field(..., description="The target server URL")
    access_token: str = Field(..., description="Base64 encoded token for authentication")

    @classmethod
    def load(cls) -> "Config":
        """
        Load the configuration from the config file.

        Returns:
            Config: An instance of Config with the loaded token.
        """
        if not CONFIG_FILE.exists():
            return None

        # if not CONFIG_FILE.exists():
        #     raise FileNotFoundError(f"Configuration file {CONFIG_FILE} does not exist.")

        with open(CONFIG_FILE, "r") as file:
            data = file.read()

        decoded_data = json.loads(base64.b64decode(data).decode())
        if not isinstance(decoded_data, dict):
            raise ValueError("Invalid configuration format.")

        return cls(**decoded_data)

    @classmethod
    def save(cls, target_server: str, access_token: str) -> None:
        """
        Save the configuration to the config file.

        Args:
            target_server (str): The target server URL.
            access_token (str): The access token to save.
        """
        config = cls(target_server=target_server, access_token=access_token)
        encoded_data = base64.b64encode(config.json().encode()).decode()

        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as file:
            file.write(encoded_data)

    @classmethod
    def clear(cls) -> None:
        """
        Clear the configuration by deleting the config file.
        """
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()


def format_output(format_type: str = None):
    """Decorator to format and display data for click commands."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            format_type = kwargs.get("format", "raw")
            try:
                data = func(*args, **kwargs)
            except AuthError as e:
                console.print(f"[red]Authentication error: {e}[/red]")
                return

            if not data:
                console.print("[yellow]No data found.[/yellow]")
                return

            if format_type == "raw":
                click.echo(data)
            if format_type == "json":
                console.print(data)
            elif format_type == "csv":
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                console.print(output.getvalue())
            elif format_type == "column":
                for item in data:
                    console.print("-------------")
                    console.print("\n".join(f"{key}: {value}" for key, value in item.items()))
                console.print("-------------")
                console.print("Total items:", len(data))
            elif format_type == "table":
                table = Table(title="Data Output")
                for key in data[0].keys():
                    table.add_column(key)
                for item in data:
                    table.add_row(*[str(value) for value in item.values()])
                console.print(table)

        return wrapper

    return decorator


def api_request(method: str, endpoint: str, **kwargs):
    """
    Make an API request to the configured server.

    Args:
        method (str): HTTP method (GET, POST, etc.).
        endpoint (str): API endpoint to call.
        **kwargs: Additional parameters for the request.

    Returns:
        Response: The response object from the requests library.
    """
    config = Config.load()
    if not config or not config.access_token:
        raise AuthError("No valid token found. Please login first.")

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {config.access_token}"

    url = f"{config.target_server}{endpoint}"
    return requests.request(method, url, headers=headers, **kwargs)
