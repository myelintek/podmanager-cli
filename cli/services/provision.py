import click
import requests
from rich.console import Console

from cli.decorator import general_decorator, add_common_options, format_decorator
from cli.utils import api_request

console = Console()


@click.group()
def provision():
    """Provision management commands."""
    pass


@provision.command()
@add_common_options
@click.option(
    "--columns",
)
@general_decorator
def osimg_list(format, filter, columns, sort_key, sort_order) -> None:
    """List all image resources with optional filtering."""
    # Fetch image list

    images_res = api_request(
        method="get",
        endpoint="/api/v1/provision/osimg",
    )

    try:
        images_res.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        click.secho(f"Error fetching os image: {http_err}", fg="red")
        click.secho(f"Response: {image_res.text}", fg="yellow")
        return

    images_json = images_res.json()

    return images_json


@provision.command()
@click.option(
    "--id",
    help="OS image ID",
)
def osimg_delete(id: str) -> None:
    # Delete image

    image_res = api_request(
        method="delete",
        endpoint=f"/api/v1/provision/osimg/{id}"
    )

    try:
        image_res.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        click.secho(f"Error delete os image: {http_err}", fg="red")
        click.secho(f"Response: {image_res.text}", fg="yellow")
        return

    image_json = image_res.json()
    print(f"Delete OS image {id} success")


@provision.command()
@click.option(
    "--format",
    default="raw",
    type=click.Choice(["csv", "column", "json", "raw", "table"], case_sensitive=False),
    help="Specify the output format for the command. Options include 'csv', 'column', 'json', 'raw', and 'table'. Default is 'raw'.",
)
@click.option(
    "--osimage",
    required=True,
    help="OS image file",
)
@click.option(
    "--title",
    required=True,
    help="Title for the os image.",
)
@click.option(
    "--name",
    required=True,
    help="Name of the os image.",
)
@click.option(
    "--architecture",
    required=True,
    help="Architecture the os image supports.",
)
@general_decorator
def osimg_upload(format, architecture: str, name: str, title: str, osimage: str) -> None:
    """Upload os image."""
    queries = f"architecture={architecture}&name={name}&title={title}"

    try:
        with open(osimage, 'rb') as f:
            myfiles = {'content': f}
            upload_res = api_request(
                method="post",
                endpoint=f"/api/v1/provision/osimg?{queries}",
                files=myfiles,
            )
    except Exception as e:
        click.secho(f"Error upload os image: {str(e)}", fg="red")
        exit()

    try:
        upload_res.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        click.secho(f"Error upload os image: {http_err}", fg="red")
        click.secho(f"Response: {upload_res.text}", fg="yellow")
        return

    upload_json = upload_res.json()

    return [upload_json]
