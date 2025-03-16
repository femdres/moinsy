"""Module for executing system commands with robust error handling and logging."""

import subprocess
import logging
import shlex
from typing import Tuple, Optional, List, Union, Dict, Any


class CommandExecutor:
    """Manages the execution of system commands with enhanced safety and logging."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the command executor.

        Args:
            logger: Optional custom logger. If not provided, creates a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, command: Union[str, List[str]],
                use_sudo: bool = False,
                timeout: int = 30,
                capture_output: bool = True,
                shell: bool = False) -> Tuple[int, str, str]:
        """Execute a system command with optional sudo privileges.

        Args:
            command: The command to execute (string or list of arguments)
            use_sudo: Whether to run the command with sudo
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture stdout and stderr
            shell: Whether to execute the command through the shell

        Returns:
            A tuple of (return_code, stdout, stderr)
        """
        try:
            # Process command based on input type
            if isinstance(command, str) and not shell:
                cmd_list = shlex.split(command)
            elif isinstance(command, list):
                cmd_list = command
            else:
                # For shell execution or other cases, keep as is
                cmd_list = command

            # Add sudo if needed
            if use_sudo and isinstance(cmd_list, list):
                cmd_list = ["sudo"] + (cmd_list if isinstance(cmd_list, list) else [cmd_list])
            elif use_sudo and isinstance(cmd_list, str):
                cmd_list = f"sudo {cmd_list}"

            self.logger.info(f"Executing command: {cmd_list}")

            # Execute command with safety precautions
            result = subprocess.run(
                cmd_list,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )

            self.logger.debug(f"Command completed with code {result.returncode}")

            # Process output
            stdout = result.stdout.strip() if capture_output else ""
            stderr = result.stderr.strip() if capture_output else ""

            if stdout and self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Command stdout: {stdout[:200]}{'...' if len(stdout) > 200 else ''}")

            if stderr:
                self.logger.warning(f"Command stderr: {stderr[:200]}{'...' if len(stderr) > 200 else ''}")

            return (
                result.returncode,
                stdout,
                stderr
            )

        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout}s: {command}")
            return (-1, "", f"Command timed out after {timeout} seconds")

        except FileNotFoundError:
            self.logger.error(f"Command not found: {command}")
            return (-1, "", "Command not found")

        except PermissionError:
            self.logger.error(f"Permission denied for command: {command}")
            return (-1, "", "Permission denied")

        except Exception as e:
            self.logger.exception(f"Command execution failed: {e}")
            return (-1, "", str(e))

    def check_command_availability(self, command: str) -> bool:
        """Check if a command is available in the system.

        Args:
            command: The command to check

        Returns:
            Boolean indicating if command is available
        """
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error checking command availability: {str(e)}")
            return False