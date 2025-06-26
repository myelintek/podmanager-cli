import csv
import functools
import io

import click
from rich.console import Console
from rich.table import Table

from cli.utils import AuthError, apply_filters, apply_sorting

console = Console()


def add_common_options(command):
    """Add common options to a Click command."""

    command = click.option(
        "--sort-order",
        default="asc",
        type=click.Choice(["asc", "desc"], case_sensitive=False),
        help="Set the sort order for the output. Options are 'asc' for ascending and 'desc' for descending. Default is 'asc'.",
    )(command)
    command = click.option(
        "--sort-key",
        default=None,
        help="Sort the output by a specific column. Specify the column name to sort by.",
    )(command)
    command = click.option(
        "--filter",
        multiple=True,
        help="Apply filters to the data using conditions like 'key>=value', 'key!=value', etc. Multiple filters can be specified.",
    )(command)
    command = click.option(
        "--format",
        default="raw",
        type=click.Choice(["csv", "column", "json", "raw", "table"], case_sensitive=False),
        help="Specify the output format for the command. Options include 'csv', 'column', 'json', 'raw', and 'table'. Default is 'raw'.",
    )(command)

    return command


def filters_decorator(func):
    """Decorator to apply filters to the data returned by a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        filter_conditions = kwargs.get("filter", None)
        data = func(*args, **kwargs)

        if filter_conditions:
            data = apply_filters(data, filter_conditions)

        return data

    return wrapper


def format_decorator(format_type: str = None, columns: str = None):
    """Decorator to format and display data for click commands."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            format_type = kwargs.get("format", "raw")
            display_column = kwargs.get("columns", None)

            # Convert display_column from comma-separated string to list
            display_column = display_column.split(",") if display_column else None

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
            elif format_type == "json":
                console.print(data)
            elif format_type == "csv":
                output = io.StringIO()
                if display_column:
                    columns = display_column
                else:
                    columns = list(data[0].keys()) if data else []

                writer = csv.DictWriter(output, fieldnames=columns)
                writer.writeheader()
                for item in data:
                    row = {}
                    for column in columns:
                        keys = column.split(".")
                        value = item
                        for key in keys:
                            value = value.get(key, "") if isinstance(value, dict) else ""
                        row[column] = str(value)
                    writer.writerow(row)
                console.print(output.getvalue())
            elif format_type == "column":
                for item in data:
                    console.print("-------------")
                    console.print("\n".join(f"{key}: {value}" for key, value in item.items()))
                console.print("-------------")
                console.print("Total items:", len(data))
            elif format_type == "table":
                if display_column:
                    # Use user-specified columns
                    columns = display_column
                else:
                    # Default to all keys in the first item
                    columns = list(data[0].keys()) if data else []

                table = Table(title=f"{func.__module__}.{func.__name__} Output")
                for column in columns:
                    table.add_column(column)
                for item in data:
                    row = []
                    for column in columns:
                        # Support nested keys like "Power.Status"
                        keys = column.split(".")
                        value = item
                        for key in keys:
                            value = value.get(key, "") if isinstance(value, dict) else ""
                        row.append(str(value))
                    table.add_row(*row)
                console.print(table)

        return wrapper

    return decorator


def sort_decorator():
    """Decorator to sort data based on a specified key."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sort_key = kwargs.get("sort_key", None)
            reverse = kwargs.get("sort_order", "asc") == "desc"

            data = func(*args, **kwargs)
            if sort_key:
                return apply_sorting(data, sort_key, reverse)
            return data

        return wrapper

    return decorator


def chain_decorator(*decorators):
    """Combine multiple decorators into a single decorator using chain pattern."""

    def combined_decorator(func):
        for decorator in reversed(decorators):
            func = decorator(func)
        return func

    return combined_decorator


general_decorator = chain_decorator(format_decorator(), sort_decorator(), filters_decorator)
