import base64
import inspect
import json
from pathlib import Path

import click
import requests
from packaging.version import Version
from pydantic import BaseModel, Field
from rich.console import Console
from datetime import datetime

CONFIG_FILE = Path("~/.podmanagercli/.config")


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
    expire_at: str = Field(None, description="Token expiration time in ISO format")

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
    def save(cls, target_server: str, access_token: str, expire_at: str) -> None:
        """
        Save the configuration to the config file.

        Args:
            target_server (str): The target server URL.
            access_token (str): The access token to save.
        """
        config = cls(target_server=target_server, access_token=access_token, expire_at=expire_at)
        encoded_data = base64.b64encode(config.model_dump_json().encode()).decode()

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
    # Get caller information
    stack = inspect.stack()
    caller_frame = stack[1]  # The frame of the function that called api_request
    caller_file = caller_frame.filename
    caller_function = caller_frame.function

    config = Config.load()
    if not config or not config.access_token:
        raise AuthError("No valid token found. Please login first.")

    if config.expire_at and int(config.expire_at) < datetime.now().timestamp():
        raise AuthError("Token has expired. Please login again.")

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {config.access_token}"

    url = f"{config.target_server}{endpoint}"

    with console.status(f"Processing {Path(caller_file).stem}.{caller_function}..."):
        return requests.request(method, url, headers=headers, **kwargs)


def parse_filter_condition(condition):
    """Parse a filter condition into key, operator, and value."""
    for operator in [">=", "<=", "!=", ">", "<", "="]:
        if operator in condition:
            key, value = condition.split(operator, 1)
            return key.strip(), operator, value.strip()
    raise ValueError("Invalid filter condition")


def compare_values(item, value, operator):
    """Compare two values with the given operator, supporting float, version, and string comparisons."""
    try:
        # Attempt to interpret the values as float or version
        if operator in [">=", "<=", ">", "<"]:
            try:
                # Try comparing as float
                item = float(item)
                value = float(value)

            except ValueError:
                try:
                    # If not float, compare as version
                    item = Version(str(item))
                    value = Version(str(value))
                except ValueError:
                    # If not version, compare as string (dictionary order)
                    item = str(item)
                    value = str(value)
            except TypeError:
                return False

        # Perform comparison
        if operator == ">=":
            return item >= value
        elif operator == "<=":
            return item <= value
        elif operator == "!=":
            return str(item) != str(value)
        elif operator == ">":
            return item > value
        elif operator == "<":
            return item < value
        elif operator == "=":
            return str(item) == str(value)
    except (ValueError, TypeError) as e:
        import traceback

        print(traceback.format_exc())
        click.secho(f"Error comparing values: {e}")
        return False
    return False


def evaluate_condition(item, key, operator, value):
    """Evaluate a filter condition, supporting nested keys."""
    try:
        # Resolve nested keys (e.g., "power.status")
        keys = key.split(".")
        for k in keys:
            if isinstance(item, dict):
                item = item.get(k)
            else:
                return False
        # Use the compare_values function for comparison
        return compare_values(item, value, operator)
    except (ValueError, TypeError) as e:
        click.secho(f"Error evaluating condition: {e}", fg="red")
        return False


def apply_filters(data, filter_conditions):
    """Apply filter conditions to a list of data items."""
    if not filter_conditions:
        return data

    filtered_data = []
    for item in data:
        include_item = True
        for condition in filter_conditions:
            try:
                key, operator, value = parse_filter_condition(condition)

                if not evaluate_condition(item, key, operator, value):
                    include_item = False
                    break
            except ValueError:
                click.secho(f"Invalid filter condition: {condition}", fg="red")
                return []

        if include_item:
            filtered_data.append(item)

    return filtered_data


def apply_sorting(data, sort_key, reverse=False):
    """Sort data based on a specified key."""
    if not sort_key:
        return data

    try:
        return sorted(data, key=lambda x: x.get(sort_key, ""), reverse=reverse)
    except Exception as e:
        click.secho(f"Error sorting data: {e}", fg="red")
        return data
