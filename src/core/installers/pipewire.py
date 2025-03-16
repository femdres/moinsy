# src/core/installers/pipewire.py
"""Installer class for PipeWire audio system and configuration."""

from PyQt6.QtCore import QObject, pyqtSignal
import os
import subprocess
import time
import logging
from typing import List, Optional, Dict, Any, Union

from config import get_resource_path, CONFIG_DIR
from utils.system_utils import execute_command

# Setup module logger
logger = logging.getLogger(__name__)


class PipeWireInstaller(QObject):
    """Installer class for PipeWire audio system and configuration.

    This class handles the installation and configuration of the PipeWire
    audio system, including repository setup, package installation, and
    service configuration.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    request_input = pyqtSignal(str, str)
    pass_command = pyqtSignal(list, bool)

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the PipeWire installer.

        Args:
            parent: Parent QObject for this installer
        """
        super().__init__(parent)
        self.device_nicknames: List[str] = []
        self.device_names: List[str] = []
        self.username: Optional[str] = None
        self.program_dir: Optional[str] = None
        self.config_dir: Optional[str] = None
        logger.debug("PipeWire installer initialized")

    @property
    def program_dir_prop(self) -> str:
        """Get the program directory path.

        Returns:
            Absolute path to program directory
        """
        if self.program_dir is None:
            self.program_dir = os.path.dirname(os.path.abspath(__file__))
        return self.program_dir

    @property
    def config_dir(self) -> str:
        """Get the PipeWire configuration directory path.

        Returns:
            Absolute path to PipeWire configuration directory
        """
        if self._config_dir is None:
            self._config_dir = os.path.join(CONFIG_DIR, "pipewire")

            # Fall back to old location if needed
            if not os.path.exists(self._config_dir):
                self._config_dir = get_resource_path("configs")

        return self._config_dir

    @config_dir.setter
    def config_dir(self, value: Optional[str]) -> None:
        """Set the configuration directory path.

        Args:
            value: Path to configuration directory
        """
        self._config_dir = value

    @property
    def username_prop(self) -> Optional[str]:
        """Get the current username.

        Returns:
            Current system username or None if not available
        """
        if self.username is None:
            try:
                username_file = get_resource_path("texts", "username.txt")
                with open(username_file, "r") as file:
                    self.username = file.read().strip()
            except Exception as e:
                logger.error(f"Error loading username: {str(e)}")
                self.username = None
        return self.username

    def install_base_system(self) -> None:
        """Start PipeWire installation and base system configuration."""
        self.log_output.emit("\nStarting PipeWire installation...")
        logger.info("Starting PipeWire installation")

        try:
            # Installation steps
            self.add_repositories()
            self.install_pipewire()
            self.install_wireplumber()
            self.configure_services()

            # Wait a bit for services to start
            time.sleep(5)

            # Now that PipeWire is installed, get audio devices
            if self.get_audio_devices():
                self.show_device_options()
            else:
                error_msg = "Failed to detect audio devices after PipeWire installation."
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)

        except Exception as e:
            error_msg = f"Installation error: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)

    def add_repositories(self) -> None:
        """Add required PipeWire repositories."""
        self.log_output.emit("\nSetting up package management...")
        logger.info("Adding PipeWire repositories")

        # Add repositories one by one with status updates
        repos = [
            "ppa:pipewire-debian/pipewire-upstream",
            "ppa:pipewire-debian/wireplumber-upstream"
        ]

        for repo in repos:
            self.log_output.emit(f"\nAdding repository: {repo}")
            logger.info(f"Adding repository: {repo}")
            result = self.pass_command.emit(["sudo", "add-apt-repository", "--yes", repo], True)

            if isinstance(result, int) and result != 0:
                error_msg = f"Failed to add repository: {repo}"
                logger.error(error_msg)
                raise Exception(error_msg)

        # Update package lists with status
        self.log_output.emit("\nUpdating package lists...")
        logger.info("Updating package lists")
        result = self.pass_command.emit(["sudo", "apt-get", "update"], True)

        if isinstance(result, int) and result != 0:
            error_msg = "Failed to update package lists"
            logger.error(error_msg)
            raise Exception(error_msg)

        self.update_progress.emit(15)

    def install_pipewire(self) -> None:
        """Install PipeWire and its dependencies."""
        self.log_output.emit("\nInstalling PipeWire dependencies...")
        logger.info("Installing PipeWire packages")

        packages = [
            "gstreamer1.0-pipewire",
            "libpipewire-0.3-0",
            "libpipewire-0.3-dev",
            "libpipewire-0.3-modules",
            "pipewire",
            "pipewire-audio-client-libraries",
            "pipewire-pulse",
            "pipewire-bin",
            "pipewire-jack",
            "pipewire-alsa",
            "pipewire-v4l2",
            "pipewire-libcamera",
            "pipewire-locales",
            "pipewire-tests",
            "libspa-0.2-bluetooth",
            "libspa-0.2-dev",
            "libspa-0.2-jack",
            "libspa-0.2-modules",
            "pipewire-doc"
        ]

        result = self.pass_command.emit(["sudo", "apt-get", "install", "-y"] + packages, True)

        if isinstance(result, int) and result != 0:
            error_msg = "Failed to install PipeWire packages"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.info("PipeWire packages installed successfully")
        self.update_progress.emit(45)

    def install_wireplumber(self) -> None:
        """Install WirePlumber session manager."""
        self.log_output.emit("\nInstalling WirePlumber dependencies...")
        logger.info("Installing WirePlumber packages")

        packages = [
            "wireplumber",
            "libwireplumber-0.4-0",
            "libwireplumber-0.4-dev",
            "gir1.2-wp-0.4",
            "wireplumber-doc"
        ]

        result = self.pass_command.emit(["sudo", "apt-get", "install", "-y"] + packages, True)

        if isinstance(result, int) and result != 0:
            error_msg = "Failed to install WirePlumber packages"
            logger.error(error_msg)
            raise Exception(error_msg)

        logger.info("WirePlumber packages installed successfully")
        self.update_progress.emit(75)

    def configure_services(self) -> None:
        """Configure system services for PipeWire."""
        self.log_output.emit("\nConfiguring audio services...")
        logger.info("Configuring PipeWire services")

        try:
            # Create default PipeWire configuration directory
            self.pass_command.emit(["sudo", "mkdir", "-p", "/etc/pipewire"], True)

            # Reload systemd to recognize new services
            self.log_output.emit("Reloading systemd configuration...")
            logger.info("Reloading systemd configuration")
            self.pass_command.emit(["sudo", "systemctl", "daemon-reload"], True)

            # Configure services
            self.log_output.emit("Starting audio services...")
            logger.info("Configuring and starting audio services")

            services_config = [
                # Stop and mask PulseAudio
                ["systemctl", "--system", "disable", "pulseaudio.socket"],
                ["systemctl", "--system", "disable", "pulseaudio.service"],
                ["systemctl", "--system", "mask", "pulseaudio"],

                # Enable and start PipeWire services
                ["systemctl", "--system", "--now", "enable", "pipewire"],
                ["systemctl", "--system", "--now", "enable", "pipewire-pulse"],
                ["systemctl", "--system", "--now", "enable", "pipewire.socket"],
                ["systemctl", "--system", "--now", "enable", "pipewire.service"],
                ["systemctl", "--system", "--now", "enable", "filter-chain.service"],

                # Enable and start WirePlumber Service
                ["systemctl", "--system", "--now", "enable", "wireplumber.service"]
            ]

            for cmd in services_config:
                result = self.pass_command.emit(["sudo"] + cmd, True)
                if isinstance(result, int) and result != 0:
                    logger.warning(f"Command returned non-zero: {' '.join(cmd)}")
                time.sleep(1)

            # Verify PipeWire is running
            self.log_output.emit("Verifying PipeWire service status...")
            logger.info("Verifying PipeWire service status")

            result = subprocess.run(
                ["sudo", "systemctl", "is-active", "pipewire.service"],
                capture_output=True,
                text=True
            )

            if result.stdout.strip() != "active":
                error_msg = "PipeWire service failed to start properly"
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info("PipeWire services configured successfully")
            self.update_progress.emit(92)

        except Exception as e:
            error_msg = f"Service configuration failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_audio_devices(self) -> bool:
        """Query system for available audio devices.

        Returns:
            True if audio devices were found, False otherwise
        """
        try:
            if not self.username_prop:
                error_msg = "Username not found, cannot get audio devices"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

            # Get user UID
            uid_result = execute_command(['id', '-u', self.username_prop], return_output=True)
            if not isinstance(uid_result, str):
                error_msg = f"Failed to get UID for user {self.username_prop}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

            uid = int(uid_result)

            # Set up environment
            env = {
                'XDG_RUNTIME_DIR': f'/run/user/{uid}',
                'DBUS_SESSION_BUS_ADDRESS': f'unix:path=/run/user/{uid}/bus',
                'USER': self.username_prop,
                'HOME': f'/home/{self.username_prop}'
            }

            # Get device names first
            self.log_output.emit("Detecting audio devices...")
            logger.info("Detecting PipeWire audio devices")

            result = subprocess.run(
                ["sudo", "-u", self.username_prop, "pw-cli", "list-objects", "Node"],
                capture_output=True,
                text=True,
                env=env
            )

            if result.returncode != 0:
                error_msg = "Failed to get audio devices. Is PipeWire running?"
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)
                return False

            # Parse the output
            output_lines = result.stdout.split('\n')
            self.device_names = []
            self.device_nicknames = []

            for line in output_lines:
                if 'node.name' in line:
                    name = line.split('=')[1].strip().strip('"')
                    self.device_names.append(name)
                if 'node.nick' in line:
                    nick = line.split('=')[1].strip().strip('"')
                    self.device_nicknames.append(nick)

            # If we don't have nicknames for all devices, use names as nicknames
            while len(self.device_nicknames) < len(self.device_names):
                self.device_nicknames.append(self.device_names[len(self.device_nicknames)])

            if len(self.device_names) > 0:
                logger.info(f"Found {len(self.device_names)} audio devices")
                return True
            else:
                logger.warning("No audio devices found")
                return False

        except subprocess.SubprocessError as e:
            error_msg = f"Error retrieving audio devices: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error getting audio devices: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return False

    def show_device_options(self) -> None:
        """Display available audio devices for configuration."""
        if not self.device_names:
            error_msg = "No audio devices available."
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return

        self.log_output.emit("\nAvailable audio devices:")
        for i, (name, nickname) in enumerate(zip(self.device_names, self.device_nicknames), 1):
            self.log_output.emit(f"{i}. {nickname} ({name})")

        self.request_input.emit(
            "\nEnter the number of the device you want to configure:",
            "configure_device"
        )
        logger.info("Displayed audio device options")

    def configure_device(self, chosen_index: str) -> None:
        """Configure the selected audio device.

        Args:
            chosen_index: String containing the numerical index of the chosen device
        """
        try:
            # Validate input
            index = int(chosen_index)
            if index < 1 or index > len(self.device_names):
                error_msg = "Invalid device selection."
                self.error_occurred.emit(error_msg)
                logger.error(error_msg)
                return

            chosen_device = self.device_names[index - 1]
            logger.info(f"Configuring device: {chosen_device}")

            self.configure_settings(chosen_device)
            self.log_output.emit("\nPipeWire installation and configuration completed successfully.")
            logger.info("PipeWire installation and configuration completed successfully")

        except ValueError:
            error_msg = f"Invalid device selection: {chosen_index}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"Configuration error: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)

    def configure_settings(self, chosen_device: str) -> None:
        """Configure PipeWire settings for the chosen device.

        Args:
            chosen_device: Name of the audio device to configure
        """
        if not self.username_prop:
            error_msg = "Username not found, cannot configure settings"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        self.log_output.emit("\nConfiguring audio settings...")
        logger.info(f"Configuring PipeWire settings for device: {chosen_device}")

        try:
            # Create configuration directories
            config_paths = [
                f"/home/{self.username_prop}/.config/wireplumber/main.lua.d",
                f"/home/{self.username_prop}/.config/pipewire"
            ]

            for path in config_paths:
                os.makedirs(path, exist_ok=True)
                logger.debug(f"Created directory: {path}")

            # Copy configuration files
            alsa_config_path = os.path.join(self.config_dir, "50-alsa-config.lua")
            result = self.pass_command.emit([
                "cp",
                alsa_config_path,
                f"/home/{self.username_prop}/.config/wireplumber/main.lua.d/"
            ], True)

            if isinstance(result, int) and result != 0:
                error_msg = "Failed to copy alsa configuration"
                logger.error(error_msg)
                raise Exception(error_msg)

            pipewire_config_path = os.path.join(self.config_dir, "pipewire.conf")
            result = self.pass_command.emit([
                "cp",
                pipewire_config_path,
                f"/home/{self.username_prop}/.config/pipewire/"
            ], True)

            if isinstance(result, int) and result != 0:
                error_msg = "Failed to copy pipewire configuration"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Update device configuration
            config_file = f"/home/{self.username_prop}/.config/wireplumber/main.lua.d/50-alsa-config.lua"

            sed_commands = [
                f"sed -i '42s/{{ \\'device\\.name\\', \\'equals\\',  }}/{{ \\'device.name\\', \\'equals\\',  \\\"{chosen_device}\\\" }}/' {config_file}",
                f"sed -i '89s/{{ \\'node\\.name\\', \\'equals\\',  }}/{{ \\'node.name\\', \\'equals\\',  \\\"{chosen_device}\\\" }}/' {config_file}"
            ]

            for cmd in sed_commands:
                self.pass_command.emit(cmd, True)

            logger.info("PipeWire configuration completed successfully")
            self.update_progress.emit(100)

        except Exception as e:
            error_msg = f"Failed to configure PipeWire settings: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)