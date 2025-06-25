import os

from setuptools import find_packages, setup

__version__ = "0.1.0-dev"


root_dir = os.path.dirname(__file__)
requirements = []
with open(os.path.join(root_dir, "requirements.txt"), "r") as infile:
    for line in infile:
        line = line.strip()
        if line and not line[0] == "#":  # ignore commentsF
            requirements.append(line)
setup(
    name="podmanager-cli",
    version=__version__,
    description="A CLI tool for managing podmanager with APIs",
    author="Jeromie Hsin",
    author_email="jeromie.hsin@gigacomputing.com",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "podmanager-cli=cli.commands:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
