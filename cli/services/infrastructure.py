import click
import requests
from rich.console import Console

from cli.decorator import general_decorator, add_common_options
from cli.utils import api_request

console = Console()


@click.group()
def infra():
    """Infrastructure management commands."""
    pass


@infra.command()
@add_common_options
@click.option(
    "--columns",
    default="Host Name,BMC MAC,Fru.0.Product.ProductName,Power.Status,Status,BMC IPv4,Firmware.BMCImage1,Firmware.BIOS1",
    help="Specify columns to display in table/csv format, separated by commas. Defaults to all columns if not provided.",
)
@general_decorator
def list(format, filter, columns, sort_key, sort_order) -> None:
    """List all infrastructure resources with optional filtering."""
    # Fetch node list

    node_res = api_request(
        method="get",
        endpoint="/api/v1/infra/common/getNodeList?type=BMC",
    )

    try:
        node_res.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        click.secho(f"Error fetching data: {http_err}", fg="red")
        click.secho(f"Response: {node_res.text}", fg="yellow")
        return

    nodes = node_res.json()

    firmware_res = api_request(
        method="post",
        endpoint="/api/v1/infra/getFirmwareVersion",
        json=[node["BMC IPv4"] for node in nodes if "BMC IPv4" in node],
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    fru_res = api_request(
        method="post",
        endpoint="/api/v1/infra/getFru",
        json=[node["BMC IPv4"] for node in nodes if "BMC IPv4" in node],
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        firmware_res.raise_for_status()
        fru_res.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        click.secho(f"Error fetching firmware data: {http_err}", fg="red")
        click.secho(f"Response: {firmware_res.text}", fg="yellow")
        return

    firmware = firmware_res.json()
    fru = fru_res.json()

    # Combine nodes and firmware data
    combined_data = nodes.copy()
    for node in combined_data:
        node_ipv4 = node.get("BMC IPv4")
        if node_ipv4 and node_ipv4 in firmware:
            # Merge firmware data into the node dictionary
            node.update({"Firmware": firmware[node_ipv4]})
            node.update({"Fru": fru[node_ipv4]})
        else:
            # If no firmware data is available, add a placeholder
            node.update({"Firmware": {}})
            node.update({"Fru": {}})

    data = combined_data

    return data


# @infra.command()
# @click.option(
#     "--target-ip",
#     "-ip",
#     required=True,
#     help="Target IP address of the device.",
# )
# @click.option(
#     "--firmware-type",
#     "-t",
#     required=True,
#     type=click.Choice(["BIOS", "BMC", "FPGA"], case_sensitive=False),
#     help="Type of firmware to update.",
# )
# @click.option(
#     "--image",
#     required=True,
#     type=click.Path(exists=True),
#     help="Path to the firmware image file.",
# )
# def update_firmware(target_ip, firmware_type, image):
#     """Update firmware on a device."""

#     data = {
#         "target": target_ip,
#         "update_type": f"MAIN_{firmware_type}",
#     }

#     console = Console()
#     with open(image, "rb") as f:
#         with console.status(f"Preparing to update {firmware_type} firmware on {target_ip}..."):
#             # Read the file in binary mode and prepare it for the request
#             # The 'files' parameter is used to send files in a multipart/form-data request
#             files = {"image": f.read()}

#     res = api_request(method="post", endpoint="/api/gsm/bmc/setFirmwareUpdateLocal", data=data, files=files)

#     try:
#         res.raise_for_status()
#     except requests.exceptions.HTTPError as http_err:
#         click.secho(f"Error updating firmware: {http_err}", fg="red")
#         click.secho(f"Response: {res.text}", fg="yellow")
#         return

#     click.secho("Firmware update initiated successfully.", fg="green")
