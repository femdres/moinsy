# src/config.py
"""Application configuration handling."""

import os
import json
import logging
from typing import Dict, Any, Optional

# Setup basic logging
logger = logging.getLogger(__name__)

# Base paths
MOINSY_ROOT = "/opt/moinsy"
SRC_DIR = os.path.join(MOINSY_ROOT, "src")

# Resource paths
RESOURCES_DIR = os.path.join(SRC_DIR, "resources")
CONFIG_DIR = os.path.join(RESOURCES_DIR, "configs")
DATA_DIR = os.path.join(RESOURCES_DIR, "data")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")
DESKTOPS_DIR = os.path.join(RESOURCES_DIR, "desktops")
POLICIES_DIR = os.path.join(RESOURCES_DIR, "policies")
TEXTS_DIR = os.path.join(RESOURCES_DIR, "texts")


def get_resource_path(*parts: str) -> str:
    """Get absolute path to a resource file.

    Args:
        *parts: Path parts to join with the resources directory

    Returns:
        Absolute path to the resource
    """
    try:
        path = os.path.join(RESOURCES_DIR, *parts)
        logger.debug(f"Resource path requested: {path}")
        # Check if path exists and log warning if not
        if not os.path.exists(path):
            logger.warning(f"Resource path does not exist: {path}")
        return path
    except Exception as e:
        logger.error(f"Error getting resource path: {str(e)}")
        # Return the best path we can
        return os.path.join(RESOURCES_DIR, *parts)


def get_username() -> Optional[str]:
    """Get the current username from file.

    Returns:
        Username string or None if file not found
    """
    try:
        username_file = os.path.join(TEXTS_DIR, "username.txt")
        if os.path.exists(username_file):
            with open(username_file, "r") as f:
                return f.read().strip()
        else:
            logger.warning(f"Username file not found: {username_file}")
            # Try fallback to environment
            import getpass
            username = getpass.getuser()
            logger.info(f"Using username from environment: {username}")
            return username
    except Exception as e:
        logger.error(f"Failed to read username: {str(e)}")
        return None


def load_json_config(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON configuration file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the parsed JSON data
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Config file not found: {file_path}")
            return {}

        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file {file_path}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error reading config file {file_path}: {str(e)}")
        return {}


def ensure_directories() -> None:
    """Ensure all required directories exist."""
    dirs = [
        CONFIG_DIR,
        DATA_DIR,
        ICONS_DIR,
        DESKTOPS_DIR,
        POLICIES_DIR,
        TEXTS_DIR
    ]

    for directory in dirs:
        try:
            logger.debug(f"Ensuring directory exists: {directory}")
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {str(e)}")
            # Continue trying other directories