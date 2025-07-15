# Podmanager CLI

A CLI tool for managing podmanager with APIs. This tool provides a convenient way to interact with podmanager services.

## Testing Environment

This CLI tool has been tested on the following environment:

- **Operating System**: Ubuntu 24.04
- **Python Version**: 3.12.3

## Installation

To install the Podmanager CLI, run the following commands:

```shell
python setup.py bdist_wheel
pip install dist/podmanager_cli-0.1.0-py3-none-any.whl
```

## Usage

### Example Command: `login`

The `login` command authenticates the user and sets up the environment for subsequent CLI operations. You need to provide the target URL, account, and password.

#### Command Options:

- `Url`: Specify the target server URL (e.g., `https://gigapod.myelintek.com`).
- `Account`: Provide the username for authentication (e.g., `admin`).
- `Password`: Enter the password for the account.

#### Example:

```shell
(podmanager) root@LAPTOP-8KSBN9VT:~/# podmanager-cli login
Url [https://gigapod.myelintek.com]:
Account [admin]:
Password:
Login successful.
```

### Example Command: `infra list`

The `infra list` command retrieves a list of resources from the infrastructure service. You can apply filters, sort the data, and format the output using various options.

#### Command Options:

- `--filter`: Apply filters to the data (e.g., `--filter "status=Warning"`).
- `--sort-key`: Specify the key to sort by (e.g., `--sort-key "name").
- `--sort-order`: Specify the sort order (`asc` or `desc`).
- `--columns`: Specify the columns to display (e.g., `--columns "name,status").
- `--format`: Specify the output format (`raw`, `json`, `csv`, or `table`).

#### Example:

```shell
(podmanager) root@LAPTOP-8KSBN9VT:~/# podmanager-cli infra list --format table --sort-key "BMC IPv4" --sort-order desc
                                                     cli.services.infrastructure.list Output
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Host Name       ┃ BMC MAC           ┃ Fru.0.Product.ProductName ┃ Power.Status ┃ Status  ┃ BMC IPv4     ┃ Firmware.BMCImage1 ┃ Firmware.BIOS1 ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ AMI10FFE074D535 │ 10:FF:E0:74:D5:35 │ R163-Z35-AAH1-000         │ Off          │ Warning │ 100.74.5.203 │ 13.06.15           │ R17_F34        │
│ AMI10FFE074D4AE │ 10:FF:E0:74:D4:AE │ R163-Z35-AAH1-000         │ Off          │ Warning │ 100.74.5.202 │ 13.06.15           │ R17_F34        │
│ AMI10FFE074D45D │ 10:FF:E0:74:D4:5D │ R163-Z35-AAH1-000         │ Off          │ Health  │ 100.74.5.201 │ 13.06.14           │ R17_F34        │
└─────────────────┴───────────────────┴───────────────────────────┴──────────────┴─────────┴──────────────┴────────────────────┴────────────────┘
```

### Example Command: `provision osimg-list`

The `provision osimg-list` command retrieves a list of os image from the provision service. You can apply filters, sort the data, and format the output using various options.

#### Command Options:

- `--filter`: Apply filters to the data (e.g., `--filter "size>200"`).
- `--sort-key`: Specify the key to sort by (e.g., `--sort-key "name").
- `--sort-order`: Specify the sort order (`asc` or `desc`).
- `--columns`: Specify the columns to display (e.g., `--columns "os,name").
- `--format`: Specify the output format (`raw`, `json`, `csv`, or `table`).

#### Example:

```shell
(podmanager) root@LAPTOP-8KSBN9VT:~/# podmanager-cli provision osimg-list --format table
                          cli.services.provision.osimg_list Output
┏━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ id ┃ os     ┃ release ┃ name         ┃ architecture ┃ size      ┃ last_deployed           ┃
┡━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 32 │ ubuntu │ jammy   │ ubuntu/jammy │ amd64        │ 651220699 │ 2025-06-27T10:30:47.883 │
│ 38 │ ubuntu │ noble   │ ubuntu/noble │ amd64        │ 365732414 │ None                    │
└────┴────────┴─────────┴──────────────┴──────────────┴───────────┴─────────────────────────┘
```
