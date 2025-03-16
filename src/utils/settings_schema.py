#!/usr/bin/env python3
"""Module for defining and validating settings schema."""

import os
from typing import Dict, Any, List, Optional, Callable, Union


class SettingsValidator:
    """Provides validation for settings values."""

    @staticmethod
    def validate_int_range(value: int, min_val: int, max_val: int) -> bool:
        """Validate that an integer is within a specific range.

        Args:
            value: The value to validate
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value

        Returns:
            Boolean indicating if value is valid
        """
        return isinstance(value, int) and min_val <= value <= max_val

    @staticmethod
    def validate_string_options(value: str, options: List[str]) -> bool:
        """Validate that a string is one of a set of options.

        Args:
            value: The value to validate
            options: List of valid options

        Returns:
            Boolean indicating if value is valid
        """
        return value in options

    @staticmethod
    def validate_file_path(value: str, must_exist: bool = False) -> bool:
        """Validate that a string is a valid file path.

        Args:
            value: The value to validate
            must_exist: Whether the file must already exist

        Returns:
            Boolean indicating if value is valid
        """
        if not isinstance(value, str):
            return False

        if must_exist:
            return os.path.isfile(value)

        try:
            # Check if the directory exists
            dir_path = os.path.dirname(value)
            return os.path.isdir(dir_path)
        except:
            return False

    @staticmethod
    def validate_dir_path(value: str, must_exist: bool = False) -> bool:
        """Validate that a string is a valid directory path.

        Args:
            value: The value to validate
            must_exist: Whether the directory must already exist

        Returns:
            Boolean indicating if value is valid
        """
        if not isinstance(value, str):
            return False

        if must_exist:
            return os.path.isdir(value)

        return True


class SettingsSchema:
    """Defines the schema for application settings."""

    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get the complete settings schema.

        Returns:
            Dictionary defining the schema for all settings
        """
        return {
            "general": {
                "theme": {
                    "type": "string",
                    "options": ["dark", "light", "system"],
                    "description": "Application color theme",
                    "default": "dark",
                    "validator": lambda x: SettingsValidator.validate_string_options(x, ["dark", "light", "system"])
                },
                "terminal_font_size": {
                    "type": "integer",
                    "min": 8,
                    "max": 24,
                    "description": "Font size for terminal output",
                    "default": 13,
                    "validator": lambda x: SettingsValidator.validate_int_range(x, 8, 24)
                },
                "terminal_buffer_size": {
                    "type": "integer",
                    "min": 100,
                    "max": 10000,
                    "description": "Number of lines to keep in terminal buffer",
                    "default": 1000,
                    "validator": lambda x: SettingsValidator.validate_int_range(x, 100, 10000)
                },
                "window_size": {
                    "type": "object",
                    "properties": {
                        "width": {
                            "type": "integer",
                            "min": 600,
                            "max": 2000,
                            "default": 1200
                        },
                        "height": {
                            "type": "integer",
                            "min": 400,
                            "max": 2000,
                            "default": 950
                        }
                    },
                    "description": "Default window size",
                    "default": {"width": 1200, "height": 950}
                },
                "sidebar_width": {
                    "type": "integer",
                    "min": 200,
                    "max": 400,
                    "description": "Width of the sidebar",
                    "default": 275,
                    "validator": lambda x: SettingsValidator.validate_int_range(x, 200, 400)
                }
            },
            "system": {
                "sudo_remember_credentials": {
                    "type": "boolean",
                    "description": "Remember sudo credentials for session",
                    "default": True
                },
                "package_manager_priority": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["apt", "flatpak", "snap"]
                    },
                    "description": "Priority order for package managers",
                    "default": ["apt", "flatpak", "snap"]
                },
                "log_level": {
                    "type": "string",
                    "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    "description": "Logging level",
                    "default": "INFO",
                    "validator": lambda x: SettingsValidator.validate_string_options(
                        x, ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
                },
                "log_file": {
                    "type": "string",
                    "description": "Path to log file",
                    "default": "",
                    "validator": lambda x: SettingsValidator.validate_file_path(x) if x else True
                }
            },
            "tools": {
                "update_check_on_startup": {
                    "type": "boolean",
                    "description": "Check for updates when application starts",
                    "default": True
                },
                "hardware_monitor_refresh_rate": {
                    "type": "integer",
                    "min": 500,
                    "max": 5000,
                    "description": "Refresh rate for hardware monitor (ms)",
                    "default": 1000,
                    "validator": lambda x: SettingsValidator.validate_int_range(x, 500, 5000)
                },
                "service_manager_show_all": {
                    "type": "boolean",
                    "description": "Show all services in service manager",
                    "default": False
                }
            }
        }

    @staticmethod
    def validate_setting(section: str, key: str, value: Any) -> bool:
        """Validate a setting against the schema.

        Args:
            section: Settings section
            key: Setting key
            value: Setting value to validate

        Returns:
            Boolean indicating if value is valid
        """
        schema = SettingsSchema.get_schema()

        if section not in schema:
            return False

        if key not in schema[section]:
            return False

        setting_schema = schema[section][key]

        if "validator" in setting_schema:
            return setting_schema["validator"](value)

        # Simple type check if no validator provided
        expected_type = setting_schema.get("type")

        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)

        return True  # No validation rules, assume valid