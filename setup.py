from setuptools import setup, find_packages
from custom_secrets_manager import __version__

# Package metadata
NAME = "custom_secrets_manager"
DESCRIPTION = "A utility for managing secrets and API keys"
AUTHOR = "Vashishtha Vidyarthi"
LICENSE = "MIT"
URL = "https://github.com/vvid643/custom_secrets_manager"

# Package dependencies
REQUIRES = ["anyconfig==0.13.0", "cryptography==41.0.1"]

# Readme file content
with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

# Setup configuration
setup(
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    license=LICENSE,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRES,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "custom_secrets_manager = custom_secrets_manager.starter_process:main"
        ]
    },
)
