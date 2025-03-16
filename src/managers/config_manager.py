#!/usr/bin/env python3
"""Module for managing application configuration settings."""

import os
import json
import logging
import shutil
from typing import Dict, Any, Optional, Union


class ConfigManager:
    """Manages application configuration settings and persistence."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the configuration manager.

        Args:
            config_dir: Optional custom config directory. If not provided, uses ~/.config/moinsy/
        """
        self.logger = logging.getLogger(__name__)

        # Set default config directory if not specified
        if config_dir is None:
            self.config_dir = os.path.expanduser("~/.config/moinsy")
        else:
            self.config_dir = config_dir

        # Ensure config directory exists
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

        self.config_file = os.path.join(self.config_dir, "settings.json")
        self.config = self._load_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get the default configuration.

        Returns:
            Dictionary containing default settings
        """
        return {
            "general": {
                "theme": "dark",
                "terminal_font_size": 13,
                "terminal_buffer_size": 1000,
                "window_size": {
                    "width": 1200,
                    "height": 950
                },
                "sidebar_width": 275
            },
            "system": {
                "sudo_remember_credentials": True,
                "package_manager_priority": ["apt", "flatpak", "snap"],
                "log_level": "INFO",
                "log_file": os.path.join(self.config_dir, "moinsy.log")
            },
            "tools": {
                "update_check_on_startup": True,
                "hardware_monitor_refresh_rate": 1000,  # ms
                "service_manager_show_all": False
            }
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if it doesn't exist.

        Returns:
            Dictionary containing configuration settings
        """
        if not os.path.exists(self.config_file):
            # Create default config
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Ensure all default keys exist (for backward compatibility)
            default_config = self._get_default_config()
            self._ensure_default_keys(config, default_config)

            return config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            self.logger.info("Using default configuration")

            # Backup corrupted config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                shutil.copy2(self.config_file, backup_file)
                self.logger.info(f"Backed up corrupted config to {backup_file}")

            # Create default config
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config

    def _ensure_default_keys(self, config: Dict[str, Any], default_config: Dict[str, Any]) -> None:
        """Recursively ensure all default keys exist in the config.

        Args:
            config: Current configuration dictionary
            default_config: Default configuration dictionary
        """
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                self._ensure_default_keys(config[key], value)

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file.

        Args:
            config: Configuration dictionary to save

        Returns:
            Boolean indicating success
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
            return False

    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value.

        Args:
            section: Settings section (general, system, tools)
            key: Setting key
            default: Default value if setting doesn't exist

        Returns:
            Setting value or default
        """
        try:
            return self.config[section][key]
        except KeyError:
            return default

    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """Set a specific setting value.

        Args:
            section: Settings section (general, system, tools)
            key: Setting key
            value: Setting value

        Returns:
            Boolean indicating success
        """
        try:
            if section not in self.config:
                self.config[section] = {}

            self.config[section][key] = value
            return self._save_config(self.config)
        except Exception as e:
            self.logger.error(f"Error setting config value: {str(e)}")
            return False

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire settings section.

        Args:
            section: Settings section name

        Returns:
            Dictionary containing section settings
        """
        return self.config.get(section, {})

    def save(self) -> bool:
        """Save current configuration to file.

        Returns:
            Boolean indicating success
        """
        return self._save_config(self.config)

    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values.

        Returns:
            Boolean indicating success
        """
        self.config = self._get_default_config()
        return self._save_config(self.config)