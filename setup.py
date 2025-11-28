from setuptools import setup, find_packages
import sys

# Choose readline package depending on OS
if sys.platform == "win32":
    readline_pkg = "pyreadline3"
else:
    readline_pkg = "readline"

setup(
    name="openagentcli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastmcp",
        "cohere",
        "python-dotenv",
        "pyyaml",
        readline_pkg,
    ],
    entry_points={
        "console_scripts": [
            "openagentcli=openagentcli.main:main",
        ],
    },
    python_requires=">=3.8",
)
