"""Module for parsing and validating Linux commands."""

import logging
from typing import Dict, List, Optional, Tuple, Set, Union
import re
import shlex


class CommandParser:
    """Provides methods for parsing and validating command syntax."""

    # List of potentially dangerous commands that should be prevented
    _DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+[/]',  # Recursive force delete on root
        r'rm\s+-rf\s+--no-preserve-root',  # Force delete with no root preservation
        r':(){ :|:& };',  # Fork bomb
        r'\|\s*sh',  # Pipe to shell
        r'dd\s+if=/dev/random',  # Random data to device
        r'dd\s+if=/dev/zero',  # Zero out device
        r'mkfs',  # Format filesystem
        r'mv\s+.*\s+/dev/',  # Move to device files
        r'>.*\.conf',  # Overwrite config files
        r'chmod\s+-R\s+777',  # Recursive loose permissions
        r'chown\s+-R\s+root',  # Change ownership to root
    ]

    # Compiled regex patterns for dangerous commands
    _DANGEROUS_REGEX = [re.compile(pattern) for pattern in _DANGEROUS_PATTERNS]

    # Safe command whitelist (basic system commands)
    _SAFE_COMMANDS = {
        'ls', 'cd', 'pwd', 'echo', 'cat', 'grep', 'find', 'cp',
        'systemctl', 'apt', 'apt-get', 'flatpak', 'snap',
        'mkdir', 'rmdir', 'touch', 'less', 'more', 'head', 'tail',
        'df', 'du', 'free', 'top', 'ps', 'kill', 'whoami', 'id',
        'uname', 'date', 'time', 'uptime', 'which', 'sudo'
    }

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the command parser.

        Args:
            logger: Optional custom logger
        """
        self.logger = logger or logging.getLogger(__name__)

    def validate_command(self, command: str) -> bool:
        """Check if a command follows basic safety and syntax rules.

        Args:
            command: Command string to validate

        Returns:
            Boolean indicating command validity
        """
        if not command or not isinstance(command, str):
            return False

        # Log the command being validated
        self.logger.debug(f"Validating command: {command}")

        # Check against dangerous patterns
        for pattern in self._DANGEROUS_REGEX:
            if pattern.search(command):
                self.logger.warning(f"Command matches dangerous pattern: {command}")
                return False

        # Basic syntax validation to catch unmatched quotes etc.
        try:
            # Use shlex to validate shell syntax
            shlex.split(command)
        except ValueError as e:
            self.logger.warning(f"Command has invalid syntax: {command} - {str(e)}")
            return False

        # Extract base command
        try:
            base_command = shlex.split(command)[0]
        except IndexError:
            return False

        # Check if base command is in whitelist
        if base_command not in self._SAFE_COMMANDS:
            self.logger.warning(f"Command not in whitelist: {base_command}")
            return False

        return True

    def parse_command(self, command: str) -> Tuple[str, List[str]]:
        """Parse a command string into command and arguments.

        Args:
            command: Command string to parse

        Returns:
            Tuple of (base_command, arguments)
        """
        if not command:
            return "", []

        try:
            parts = shlex.split(command)
            if not parts:
                return "", []

            return parts[0], parts[1:]
        except Exception as e:
            self.logger.error(f"Error parsing command: {str(e)}")
            return "", []