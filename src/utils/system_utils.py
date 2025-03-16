# src/utils/system_utils.py
"""System utility functions used across the application."""

import subprocess
import os
import logging
from typing import List, Union, Dict, Optional

# Setup logger
logger = logging.getLogger(__name__)


def execute_command(command: List[str], return_output: bool = False,
                    timeout: Optional[int] = None) -> Union[int, str]:
    """Execute a system command and return result.

    Args:
        command: Command list to execute
        return_output: Whether to return output as string
        timeout: Maximum execution time in seconds

    Returns:
        Return code or command output

    Raises:
        Exception: If command execution fails
    """
    try:
        logger.debug(f"Executing command: {' '.join(command)}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=timeout)

        if stderr:
            logger.warning(f"Command warning: {stderr}")

        if return_output:
            return stdout.strip()
        return process.returncode
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error(f"Command timed out after {timeout} seconds")
        raise Exception(f"Command timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}")
        raise Exception(f"Command execution failed: {str(e)}")


def check_package_installed(package_name: str) -> bool:
    """Check if a package is installed via apt.

    Args:
        package_name: Name of the package to check

    Returns:
        bool: True if installed, False otherwise
    """
    try:
        result = execute_command(['dpkg', '-s', package_name], return_output=True)
        return "Status: install ok installed" in result
    except Exception:
        return False


def get_system_info() -> Dict[str, str]:
    """Get basic system information.

    Returns:
        Dict containing basic system information
    """
    info = {}

    try:
        # Get OS information
        with open('/etc/os-release', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('NAME='):
                    info['os_name'] = line.split('=')[1].strip().strip('"')
                elif line.startswith('VERSION='):
                    info['os_version'] = line.split('=')[1].strip().strip('"')
    except Exception as e:
        logger.error(f"Failed to get OS info: {str(e)}")
        info['os_name'] = "Unknown"
        info['os_version'] = "Unknown"

    try:
        # Get kernel version
        kernel = execute_command(['uname', '-r'], return_output=True)
        info['kernel'] = kernel
    except Exception as e:
        logger.error(f"Failed to get kernel info: {str(e)}")
        info['kernel'] = "Unknown"

    return info