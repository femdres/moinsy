"""Installer class for PipeWire audio system and configuration.

Like a persistent monk performing a sacred audio ritual,
this method initiates the complex ceremony of transforming
the system's sound architecture, promising enlightenment
in the form of lower latency and better Bluetooth connectivity.
"""

from PyQt6.QtCore import QObject, pyqtSignal
import os
import subprocess
import time
import logging
import shutil
from typing import List, Optional, Dict, Any, Union, Tuple, cast

from config import get_resource_path, CONFIG_DIR
from utils.system_utils import execute_command

# Try to import the audio config module, but don't fail if it's not available
try:
    from gui.components.audio_config import launch_audio_config
    HAS_AUDIO_CONFIG = True
except ImportError:
    HAS_AUDIO_CONFIG = False
    import traceback
    logging.warning(f"Could not import audio_config module: {traceback.format_exc()}")


class PipeWireInstaller(QObject):
    """Installer class for PipeWire audio system and configuration.

    Like a digital audiophile endlessly tweaking frequency response curves
    in pursuit of the perfect sound, this class tirelessly manages the
    installation and configuration of the PipeWire audio system, offering
    the elusive promise of better Bluetooth connectivity and lower latency
    in an otherwise indifferent universe.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    request_input = pyqtSignal(str, str)
    pass_command = pyqtSignal(list, bool)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize the PipeWire installer.

        Args:
            parent: Parent QObject for this installer
        """
        super().__init__(parent)
        self.device_nicknames: List[str] = []
        self.device_names: List[str] = []
        self.username: Optional[str] = None
        self._program_dir: Optional[str] = None
        self._config_dir: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        self.logger.debug("PipeWire installer initialized - digital audiophile awakened")
        self._config_window = None  # Store reference to config window
        self._installation_complete = False  # Track if installation is complete

    @property
    def program_dir(self) -> str:
        """Get the program directory path.

        Returns:
            Absolute path to program directory
        """
        if self._program_dir is None:
            self._program_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return self._program_dir

    @program_dir.setter
    def program_dir(self, value: Optional[str]) -> None:
        """Set the program directory path.

        Args:
            value: Path to program directory
        """
        self._program_dir = value

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
                    self.logger.debug(f"Retrieved username: {self.username}")
            except Exception as e:
                self.logger.error(f"Error loading username: {str(e)}")
                self.username = None

        return self.username

    def install_base_system(self) -> None:
        """Start PipeWire installation and base system configuration.

        Like a persistent monk performing a sacred audio ritual,
        this method initiates the complex ceremony of transforming
        the system's sound architecture, promising enlightenment
        in the form of lower latency and better Bluetooth connectivity.
        """
        self.log_output.emit("\nStarting PipeWire installation...")
        self.logger.info("Starting PipeWire installation - audio transformation ritual begins")

        try:
            # Installation steps
            self.add_repositories()
            self.install_pipewire()
            self.install_wireplumber()
            self.configure_services()

            # Wait a bit for services to start, though we know we won't be able to access them as root
            time.sleep(2)

            # Set installation complete flag
            self._installation_complete = True

            # Launch the GUI configuration if available, otherwise use text-based
            if HAS_AUDIO_CONFIG:
                self.configure_devices_gui()
            else:
                self.prepare_user_configuration()
                # Use text-based configuration as fallback
                if self.get_audio_devices():
                    self.show_device_options()
                else:
                    self.log_output.emit("\n⚠️ Could not detect audio devices. You'll need to configure devices after restarting.")
                    self.log_output.emit("\n✅ PipeWire installation complete. Please restart your system to enable the new audio system.")
                    self.update_progress.emit(100)

        except Exception as e:
            error_msg = f"Installation error: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(f"The audio transformation ritual was interrupted: {error_msg}")

    def configure_devices_gui(self) -> None:
        """Launch GUI for configuring PipeWire audio devices.

        Like an enlightened shaman presenting an interface between worlds,
        this method summons forth a graphical portal through which the user
        may shape their sonic landscape - a more elegant approach than the
        text-based rituals of a bygone digital era.
        """
        try:
            self.log_output.emit("\nLaunching PipeWire configuration interface...")
            self.logger.info("Opening graphical PipeWire device configuration interface")

            # Show a success message about installation completion
            if self._installation_complete:
                self.log_output.emit("\n✅ PipeWire installation complete.")
                self.log_output.emit("\n🔧 Now launching the configuration interface for your audio devices.")

                # Update progress to indicate we're in configuration phase
                self.update_progress.emit(95)

            # Launch the audio configuration window
            # We use the parent of this QObject to ensure proper modal behavior
            if self.parent() and hasattr(self.parent(), 'parent'):
                parent_window = self.parent().parent()
            else:
                parent_window = None

            # Launch the configuration window and store reference
            self._config_window = launch_audio_config(parent_window)

            # Connect to the configuration saved signal
            self._config_window.config_saved.connect(self.on_audio_config_saved)

        except Exception as e:
            error_msg = f"Error launching audio configuration interface: {str(e)}"
            self.logger.exception(error_msg)
            self.error_occurred.emit(error_msg)

            # Fall back to text-based configuration
            self.log_output.emit("\nFalling back to text-based configuration...")
            if self.get_audio_devices():
                self.show_device_options()
            else:
                self.log_output.emit("\n⚠️ Could not detect audio devices. You'll need to configure devices after restarting.")
                self.log_output.emit("\n✅ PipeWire installation complete. Please restart your system to enable the new audio system.")
                self.update_progress.emit(100)

    def on_audio_config_saved(self, config_data: dict) -> None:
        """Handle saved configurations from the audio configuration window.

        Args:
            config_data: Dictionary containing configuration results

        Like a witness bearing testament to the user's audio preferences,
        this method acknowledges their configuration choices and completes
        the installation ritual - the digital equivalent of saying "amen"
        at the end of a prayer to the gods of audio fidelity.
        """
        try:
            # Log the configuration results
            config_path = config_data.get('path', 'unknown location')
            device_count = config_data.get('devices', 0)

            self.log_output.emit(f"\n✅ Audio configuration complete. Saved {device_count} device configurations.")
            self.log_output.emit(f"\n📁 Configuration saved to: {config_path}")
            self.log_output.emit("\n🔄 To apply changes, log out and back in, or restart PipeWire with:")
            self.log_output.emit("\n   systemctl --user restart pipewire.service")
            self.log_output.emit("\n   systemctl --user restart wireplumber.service")

            # Add a note about the end result
            self.log_output.emit("\n🎧 Your PipeWire audio system is now installed and configured!")

            # Update progress to 100%
            self.update_progress.emit(100)

            self.logger.info(f"PipeWire configuration completed. Saved {device_count} device configurations to {config_path}")

        except Exception as e:
            self.logger.error(f"Error handling saved configuration: {str(e)}")
            # Still consider this a success since configs were likely saved
            self.update_progress.emit(100)
            self.log_output.emit("\n✅ PipeWire installation and configuration completed.")

    def prepare_user_configuration(self) -> None:
        """Prepare user-level PipeWire configuration to be applied after login.

        Unlike our futile attempts to transcend privilege boundaries, this method
        accepts the limitations of existence and prepares a configuration that will
        manifest when the user returns in their next incarnation (login session).
        """
        if not self.username_prop:
            error_msg = "Username not found, cannot prepare user configuration"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        self.log_output.emit("\nPreparing user configuration for next login session...")
        self.logger.info(f"Preparing PipeWire user configuration for {self.username_prop}")

        try:
            # Create user's config directories
            user_config_dirs = [
                f"/home/{self.username_prop}/.config/pipewire",
                f"/home/{self.username_prop}/.config/wireplumber/main.lua.d"
            ]

            for directory in user_config_dirs:
                os.makedirs(directory, exist_ok=True)
                # Make sure the user owns their config directories
                os.system(f"chown -R {self.username_prop}:{self.username_prop} {directory}")

            # Copy configuration files from resources
            pipewire_conf_src = os.path.join(self.config_dir, "pipewire.conf")
            pipewire_conf_dest = f"/home/{self.username_prop}/.config/pipewire/pipewire.conf"

            alsa_config_src = os.path.join(self.config_dir, "50-alsa-config.lua")
            alsa_config_dest = f"/home/{self.username_prop}/.config/wireplumber/main.lua.d/50-alsa-config.lua"

            # Copy files
            shutil.copy2(pipewire_conf_src, pipewire_conf_dest)
            shutil.copy2(alsa_config_src, alsa_config_dest)

            # Set ownership
            os.system(f"chown {self.username_prop}:{self.username_prop} {pipewire_conf_dest}")
            os.system(f"chown {self.username_prop}:{self.username_prop} {alsa_config_dest}")

            # Create a dynamic configuration script that will run after the user logs in
            # This script will detect and set the default audio device, effectively doing
            # what we were unsuccessfully trying to do from the root context
            autoconfig_script = f"""#!/bin/bash
# PipeWire auto-configuration script
# Created by Moinsy

# Wait for PipeWire to start
sleep 5

# Find default sink
DEFAULT_SINK=$(pactl info | grep 'Default Sink' | cut -d: -f2 | xargs)

if [ -n "$DEFAULT_SINK" ]; then
    # User-friendly message
    echo "Setting $DEFAULT_SINK as default audio device"
    
    # Create device configuration file
    cat > ~/.config/wireplumber/main.lua.d/51-device-default.lua << EOF
-- Automatically generated by Moinsy
-- Default device configuration

local rule = {{
  matches = {{
    {{
      {{ "node.name", "equals", "$DEFAULT_SINK" }},
    }},
  }},
  apply_properties = {{
    ["node.description"] = "Default Output Device",
    ["priority.session"] = 2000,
    ["priority.driver"] = 2000,
  }},
}}

table.insert(alsa_monitor.rules, rule)
EOF

    # Restart wireplumber to apply changes
    systemctl --user restart wireplumber.service
fi
"""

            # Create autostart directory if it doesn't exist
            autostart_dir = f"/home/{self.username_prop}/.config/autostart"
            os.makedirs(autostart_dir, exist_ok=True)

            # Write the script to a file
            script_path = f"/home/{self.username_prop}/.config/pipewire/pipewire-autoconfig.sh"
            with open(script_path, 'w') as f:
                f.write(autoconfig_script)

            # Make the script executable
            os.chmod(script_path, 0o755)

            # Set ownership
            os.system(f"chown {self.username_prop}:{self.username_prop} {script_path}")

            # Create a desktop entry to run this script at login
            desktop_entry = f"""[Desktop Entry]
Type=Application
Name=PipeWire Auto Configuration
Comment=Automatically configures PipeWire audio settings
Exec=/home/{self.username_prop}/.config/pipewire/pipewire-autoconfig.sh
Terminal=false
X-GNOME-Autostart-enabled=true
Hidden=false
"""

            # Write the desktop entry
            desktop_path = f"{autostart_dir}/pipewire-autoconfig.desktop"
            with open(desktop_path, 'w') as f:
                f.write(desktop_entry)

            # Set ownership
            os.system(f"chown {self.username_prop}:{self.username_prop} {desktop_path}")
            os.system(f"chown -R {self.username_prop}:{self.username_prop} {autostart_dir}")

            self.log_output.emit("User configuration prepared successfully")
            self.logger.info("PipeWire user configuration prepared for next login")

        except Exception as e:
            error_msg = f"Failed to prepare user configuration: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def add_repositories(self) -> None:
        """Add required PipeWire repositories.

        Like a cartographer mapping unexplored territories of package
        repositories, this method extends the system's knowledge of
        where to find the arcane audio components.
        """
        self.log_output.emit("\nSetting up package repositories...")
        self.logger.info("Adding PipeWire repositories")

        # Add repositories one by one with status updates
        repos = [
            "ppa:pipewire-debian/pipewire-upstream",
            "ppa:pipewire-debian/wireplumber-upstream"
        ]

        for repo in repos:
            self.log_output.emit(f"\nAdding repository: {repo}")
            self.logger.info(f"Adding repository: {repo}")
            result = self.pass_command.emit(["sudo", "add-apt-repository", "--yes", repo], True)

            if isinstance(result, int) and result != 0:
                error_msg = f"Failed to add repository: {repo}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

        # Update package lists with status
        self.log_output.emit("\nUpdating package lists...")
        self.logger.info("Updating package lists")
        result = self.pass_command.emit(["sudo", "apt-get", "update"], True)

        if isinstance(result, int) and result != 0:
            error_msg = "Failed to update package lists"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        self.update_progress.emit(20)
        self.logger.info("Package repositories successfully configured")

    def install_pipewire(self) -> None:
        """Install PipeWire and its dependencies.

        Like a meticulous sculptor assembling a complex audio edifice,
        this method installs the foundational components of the PipeWire
        audio system, each package a precisely cut stone in our sonic cathedral.
        """
        self.log_output.emit("\nInstalling PipeWire core components...")
        self.logger.info("Installing PipeWire packages")

        try:
            # Expanded package list based on current best practices
            packages = [
                "gstreamer1.0-pipewire",
                "libpipewire-0.3-0",
                "libpipewire-0.3-dev",
                "libpipewire-0.3-modules",
                "libspa-0.2-bluetooth",
                "libspa-0.2-dev",
                "libspa-0.2-jack",
                "libspa-0.2-modules",
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
                "pipewire-doc",  # Documentation package included
                "pavucontrol"    # Include PulseAudio Volume Control for easy device management
            ]

            install_cmd = ["apt-get", "install", "-y"] + packages
            self.log_output.emit(f"Running: apt-get install -y {' '.join(packages)}")

            # Execute the command directly rather than through pass_command
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = f"Failed to install PipeWire packages: {result.stderr}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            self.logger.info("PipeWire packages installed successfully")
            self.update_progress.emit(50)

        except Exception as e:
            error_msg = f"Error installing PipeWire packages: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def install_wireplumber(self) -> None:
        """Install WirePlumber session manager.

        Like installing the conductor for our digital audio orchestra,
        this method sets up WirePlumber, the crucial session manager that
        directs the chaotic symphony of audio streams into coherent outputs.
        """
        self.log_output.emit("\nInstalling WirePlumber session manager...")
        self.logger.info("Installing WirePlumber packages")

        try:
            # Updated package list for WirePlumber
            packages = [
                "wireplumber",
                "wireplumber-doc",
                "gir1.2-wp-0.4",
                "libwireplumber-0.4-0",
                "libwireplumber-0.4-dev"
            ]

            install_cmd = ["apt-get", "install", "-y"] + packages
            self.log_output.emit(f"Running: apt-get install -y {' '.join(packages)}")

            # Execute directly
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = f"Failed to install WirePlumber packages: {result.stderr}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            self.logger.info("WirePlumber packages installed successfully")
            self.update_progress.emit(70)

        except Exception as e:
            error_msg = f"Error installing WirePlumber packages: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def configure_services(self) -> None:
        """Configure system services for PipeWire.

        Like a stern system administrator reorganizing the hierarchy
        of audio daemons, this method disables the old sound regime
        and establishes the new order of PipeWire services, hoping that
        this digital coup d'état will result in better audio governance.

        Unlike our previous misguided attempts to straddle root/user contexts,
        this method acknowledges that we dwell in the elevated realm of root
        privilege, and can only affect system-wide policies while leaving
        the user session configuration for a post-reboot reality.
        """
        self.log_output.emit("\nConfiguring audio services...")
        self.logger.info("Configuring PipeWire services")

        try:
            # Create default PipeWire configuration directory if needed
            os.makedirs("/etc/pipewire", exist_ok=True)

            # Get the current username for systemctl user commands
            if not self.username_prop:
                error_msg = "Username not found, cannot configure services"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            # Reload systemd to recognize new services
            self.log_output.emit("Reloading systemd configuration...")
            subprocess.run(["systemctl", "daemon-reload"], check=True)

            # Create a configuration file that will run when the user logs in
            # This will disable PulseAudio and enable PipeWire for the user
            service_config = """
# Created by Moinsy PipeWire installer

# First login after PipeWire installation
# Disable PulseAudio and enable PipeWire

systemctl --user --now disable pulseaudio.socket 2>/dev/null || true
systemctl --user --now disable pulseaudio.service 2>/dev/null || true
systemctl --user mask pulseaudio 2>/dev/null || true

# Enable PipeWire services
systemctl --user --now enable pipewire.socket
systemctl --user --now enable pipewire.service
systemctl --user --now enable pipewire-pulse.socket
systemctl --user --now enable pipewire-pulse.service  
systemctl --user --now enable filter-chain.service

# Enable WirePlumber
systemctl --user --now enable wireplumber.service

# Log results for debugging
echo "PipeWire service setup complete" > ~/.config/pipewire/setup-complete.log
echo "Date: $(date)" >> ~/.config/pipewire/setup-complete.log
echo "PipeWire status:" >> ~/.config/pipewire/setup-complete.log
systemctl --user status pipewire.service >> ~/.config/pipewire/setup-complete.log 2>&1
"""

            # Create user's config directory if it doesn't exist
            user_config_dir = f"/home/{self.username_prop}/.config/pipewire"
            os.makedirs(user_config_dir, exist_ok=True)

            # Write the service setup script
            service_script_path = f"{user_config_dir}/setup-services.sh"
            with open(service_script_path, 'w') as f:
                f.write(service_config)

            # Make it executable
            os.chmod(service_script_path, 0o755)

            # Ensure proper ownership
            os.system(f"chown -R {self.username_prop}:{self.username_prop} {user_config_dir}")

            # Create autostart desktop entry to run this once on next login
            autostart_dir = f"/home/{self.username_prop}/.config/autostart"
            os.makedirs(autostart_dir, exist_ok=True)

            desktop_entry = f"""[Desktop Entry]
Type=Application
Name=PipeWire Service Setup
Comment=One-time setup for PipeWire audio services
Exec=/home/{self.username_prop}/.config/pipewire/setup-services.sh
Terminal=false
X-GNOME-Autostart-enabled=true
Hidden=false
"""

            desktop_path = f"{autostart_dir}/pipewire-service-setup.desktop"
            with open(desktop_path, 'w') as f:
                f.write(desktop_entry)

            # Ensure proper ownership
            os.system(f"chown -R {self.username_prop}:{self.username_prop} {autostart_dir}")

            # Log success
            self.log_output.emit("PipeWire services configured to start on next login")
            self.logger.info("PipeWire service configuration prepared for next login")
            self.update_progress.emit(90)

        except Exception as e:
            error_msg = f"Service configuration error: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def verify_pipewire_running(self) -> bool:
        """Verify that PipeWire is actually running and ready.

        Returns:
            True if PipeWire services are ready, False otherwise

        Like a doctor checking vital signs before a procedure, this method
        ensures the PipeWire daemon has actually come to life before we
        attempt to interrogate it about audio devices - a ritual of confirmation
        in the uncertain void of service initialization.
        """
        if not self.username_prop:
            self.logger.error("Username not found, cannot verify PipeWire status")
            return False

        self.log_output.emit("\nVerifying PipeWire availability...")

        # We'll try a few times with increasing delays
        max_attempts = 3
        attempt = 0
        base_delay = 2  # seconds

        while attempt < max_attempts:
            attempt += 1
            delay = base_delay * attempt  # Progressive delay

            try:
                # Use machinectl instead of su - more reliable for accessing user session
                self.log_output.emit(f"Checking PipeWire status (attempt {attempt}/{max_attempts})...")
                result = subprocess.run(
                    ["machinectl", "shell", f"{self.username_prop}@.host", "/usr/bin/pw-cli", "info", "0"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    self.log_output.emit("PipeWire service is responsive.")
                    self.logger.info("PipeWire service is responsive")
                    return True

                # Check for specific error messages
                if "Host is down" in result.stderr:
                    self.log_output.emit("PipeWire socket exists but daemon isn't responsive yet.")
                    self.logger.warning("PipeWire socket exists but daemon isn't responsive - 'Host is down'")
                elif "No such file or directory" in result.stderr:
                    self.log_output.emit("PipeWire socket doesn't exist yet.")
                    self.logger.warning("PipeWire socket doesn't exist yet")
                elif "Failed to set interface attribute: Protocol error" in result.stderr:
                    self.log_output.emit("Could not communicate with user session (systemd protocol error)")
                    self.logger.warning("Failed to communicate with user session via machinectl")
                else:
                    stderr = result.stderr.strip() if result.stderr else "No error output"
                    stdout = result.stdout.strip() if result.stdout else "No stdout"
                    self.log_output.emit(f"PipeWire check returned: {stderr or stdout}")
                    self.logger.warning(f"Unexpected output checking PipeWire: {stderr or stdout}")

                self.log_output.emit(f"PipeWire not fully available yet. Waiting {delay} seconds...")
                self.logger.info(f"PipeWire not responsive on attempt {attempt}/{max_attempts}, waiting {delay}s")
                time.sleep(delay)

            except subprocess.TimeoutExpired:
                self.logger.warning(f"Command timed out on attempt {attempt}/{max_attempts}")
                self.log_output.emit(f"Command timed out. Waiting {delay} seconds...")
                time.sleep(delay)
            except Exception as e:
                self.logger.warning(f"Error checking PipeWire status: {str(e)}")
                self.log_output.emit(f"Error checking PipeWire: {str(e)}")
                time.sleep(delay)

        self.logger.warning(f"PipeWire service didn't become available after {max_attempts} attempts")
        self.log_output.emit("PipeWire service not available. Continuing with configuration preparation.")
        return False

    def get_audio_devices(self) -> bool:
        """Query system for available audio devices with retry logic.

        Returns:
            True if audio devices were found, False otherwise

        Like a curious explorer mapping the sonic landscape, this method
        surveys the newly transformed audio environment to catalog its
        inhabitants - the devices that will give voice to our digital realm.
        But unlike naive explorers, it knows the terrain may still be forming,
        so it patiently attempts multiple surveys with increasing wait times.
        """
        try:
            if not self.username_prop:
                error_msg = "Username not found, cannot get audio devices"
                self.logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

            # Before attempting to get devices, verify PipeWire is running
            if not self.verify_pipewire_running():
                self.log_output.emit("PipeWire not running, cannot detect audio devices at this time.")
                self.log_output.emit("You'll need to configure audio devices after restarting your system.")
                return False

            # Use retry logic for device detection
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                # Get device names using pw-cli with machinectl
                self.log_output.emit(f"\nDetecting audio devices (attempt {attempt}/{max_attempts})...")
                self.logger.info(f"Detecting PipeWire audio devices - attempt {attempt}/{max_attempts}")

                try:
                    # Use machinectl to run pw-cli in the user session
                    result = subprocess.run(
                        ["machinectl", "shell", f"{self.username_prop}@.host", "/usr/bin/pw-cli", "list-objects", "Node"],
                        capture_output=True,
                        text=True,
                        timeout=15  # Longer timeout since this command produces more output
                    )

                    if "Failed to set interface attribute: Protocol error" in result.stderr:
                        self.log_output.emit("Could not communicate with user session (systemd protocol error)")
                        self.logger.warning(f"machinectl protocol error on attempt {attempt}/{max_attempts}")

                        if attempt < max_attempts:
                            wait_time = attempt * 3
                            self.log_output.emit(f"Waiting {wait_time} seconds before retrying...")
                            time.sleep(wait_time)
                            continue
                        else:
                            self.log_output.emit("Could not access user's PipeWire session. This is an expected limitation.")
                            self.log_output.emit("PipeWire installation is still successful - you'll need to configure audio")
                            self.log_output.emit("devices after restarting your system.")
                            return False

                    if result.returncode != 0:
                        error_msg = f"pw-cli command failed with code {result.returncode}"
                        if result.stderr:
                            error_msg += f": {result.stderr.strip()}"

                        self.logger.warning(f"{error_msg} (attempt {attempt}/{max_attempts})")

                        if attempt < max_attempts:
                            wait_time = attempt * 3
                            self.log_output.emit(f"Waiting {wait_time} seconds before retrying...")
                            time.sleep(wait_time)
                            continue
                        else:
                            self.error_occurred.emit(f"Failed to list audio devices after {max_attempts} attempts")
                            return False

                    # Parse the output
                    output_lines = result.stdout.split('\n')
                    self.device_names = []
                    self.device_nicknames = []

                    current_device: Optional[str] = None
                    current_nick: Optional[str] = None

                    # More robust parsing - handle multi-line output for each object
                    for line in output_lines:
                        line = line.strip()

                        # New object section starts with id
                        if line.startswith("id"):
                            # Save previous device if we have one
                            if current_device:
                                self.device_names.append(current_device)
                                self.device_nicknames.append(current_nick or current_device)

                            # Reset for new device
                            current_device = None
                            current_nick = None

                        # Extract properties
                        elif ':' in line:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip().strip('"')

                                if "node.name" in key:
                                    current_device = value
                                elif "node.nick" in key:
                                    current_nick = value

                    # Add the last device if exists
                    if current_device:
                        self.device_names.append(current_device)
                        self.device_nicknames.append(current_nick or current_device)

                    # If we don't have nicknames for all devices, use names as nicknames
                    while len(self.device_nicknames) < len(self.device_names):
                        self.device_nicknames.append(self.device_names[len(self.device_nicknames)])

                    # Filter out non-output devices and common non-main devices
                    output_devices = []
                    output_nicknames = []

                    for i, name in enumerate(self.device_names):
                        name_lower = name.lower()
                        # Skip certain devices we don't want to show
                        if ('monitor' in name_lower or
                            'sink_input' in name_lower or
                            'source_output' in name_lower):
                            continue

                        # Look for likely audio output devices
                        if ('output' in name_lower or
                            'sink' in name_lower or
                            'speaker' in name_lower or
                            'headphone' in name_lower or
                            'alsa' in name_lower):
                            output_devices.append(name)
                            if i < len(self.device_nicknames):
                                output_nicknames.append(self.device_nicknames[i])

                    # If we found likely output devices, use those instead
                    if output_devices:
                        self.device_names = output_devices
                        self.device_nicknames = output_nicknames[:len(output_devices)]

                    # Make sure we still have nicknames after filtering
                    while len(self.device_nicknames) < len(self.device_names):
                        self.device_nicknames.append(self.device_names[len(self.device_nicknames)])

                    if len(self.device_names) > 0:
                        self.logger.info(f"Found {len(self.device_names)} audio devices")
                        self.log_output.emit(f"Successfully detected {len(self.device_names)} audio devices.")
                        return True
                    else:
                        if attempt < max_attempts:
                            self.log_output.emit("No audio devices found yet. PipeWire may still be initializing...")
                            self.logger.warning("No audio devices found, retrying...")
                            time.sleep(attempt * 3)  # Progressive wait
                            continue
                        else:
                            self.log_output.emit("No audio devices found after multiple attempts.")
                            self.logger.warning("No audio devices found after maximum attempts")
                            return False

                except subprocess.TimeoutExpired:
                    self.logger.warning(f"pw-cli command timed out on attempt {attempt}/{max_attempts}")
                    if attempt < max_attempts:
                        wait_time = attempt * 3
                        self.log_output.emit(f"Command timed out. Waiting {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                    else:
                        self.error_occurred.emit("Device detection timed out repeatedly")
                        return False

            # If we get here, all attempts failed
            return False

        except subprocess.SubprocessError as e:
            error_msg = f"Error retrieving audio devices: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error getting audio devices: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return False

    def show_device_options(self) -> None:
        """Display available audio devices for configuration.

        Like a waiter presenting a menu of sonic delicacies, this method
        displays the available audio devices for the user to choose from,
        each one promising a unique auditory experience in our digital feast.
        """
        if not self.device_names:
            error_msg = "No audio devices available."
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
            return

        self.log_output.emit("\nAvailable audio devices:")
        for i, (name, nickname) in enumerate(zip(self.device_names, self.device_nicknames), 1):
            self.log_output.emit(f"{i}. {nickname} ({name})")

        self.request_input.emit(
            "\nEnter the number of the device you want to configure as your default output:",
            "configure_device"
        )
        self.logger.info("Displayed audio device options")

    def configure_device(self, chosen_index: str) -> None:
        """Configure the selected audio device.

        Args:
            chosen_index: String containing the numerical index of the chosen device

        Like a sound engineer routing cables on a mixing console,
        this method establishes the default pathways for audio signals,
        ensuring the chosen device receives the digital symphony.
        """
        try:
            # Validate input
            index = int(chosen_index)
            if index < 1 or index > len(self.device_names):
                error_msg = f"Invalid device selection: {chosen_index}"
                self.error_occurred.emit(error_msg)
                self.logger.error(error_msg)
                return

            chosen_device = self.device_names[index - 1]
            chosen_nickname = self.device_nicknames[index - 1]
            self.logger.info(f"Configuring device: {chosen_device}")
            self.log_output.emit(f"\nConfiguring '{chosen_nickname}' as default audio output...")

            self.configure_settings(chosen_device)
            self.update_progress.emit(100)

            self.log_output.emit("\nPipeWire installation and configuration completed successfully.")
            self.log_output.emit("\nYou may need to restart your system to ensure all changes take effect.")
            self.logger.info("PipeWire installation and configuration completed successfully")

        except ValueError:
            error_msg = f"Invalid device selection: {chosen_index}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)
        except Exception as e:
            error_msg = f"Configuration error: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)

    def configure_settings(self, chosen_device: str) -> None:
        """Configure PipeWire settings for the chosen device.

        Args:
            chosen_device: Name of the audio device to configure

        Like a meticulous librarian organizing audio configuration files,
        this method writes the necessary settings to establish the selected
        device as the primary output, bringing order to the sonic chaos.
        """
        if not self.username_prop:
            error_msg = "Username not found, cannot configure settings"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        self.log_output.emit("\nConfiguring audio settings...")
        self.logger.info(f"Configuring PipeWire settings for device: {chosen_device}")

        try:
            # Create configuration directories
            config_paths = [
                f"/home/{self.username_prop}/.config/wireplumber/main.lua.d",
                f"/home/{self.username_prop}/.config/pipewire"
            ]

            for directory in config_paths:
                os.makedirs(directory, exist_ok=True)
                # Make sure the user owns their config directories
                os.system(f"chown -R {self.username_prop}:{self.username_prop} {directory}")
                self.logger.debug(f"Created directory: {directory}")

            # Copy configuration files from resources
            alsa_config_path = os.path.join(self.config_dir, "50-alsa-config.lua")
            user_alsa_config = f"/home/{self.username_prop}/.config/wireplumber/main.lua.d/50-alsa-config.lua"

            pipewire_config_path = os.path.join(self.config_dir, "pipewire.conf")
            user_pipewire_config = f"/home/{self.username_prop}/.config/pipewire/pipewire.conf"

            # Copy the files directly
            shutil.copy2(alsa_config_path, user_alsa_config)
            shutil.copy2(pipewire_config_path, user_pipewire_config)

            # Set ownership
            os.system(f"chown {self.username_prop}:{self.username_prop} {user_alsa_config}")
            os.system(f"chown {self.username_prop}:{self.username_prop} {user_pipewire_config}")

            # Create a custom device configuration file
            device_conf_path = f"/home/{self.username_prop}/.config/wireplumber/main.lua.d/51-device-default.lua"

            # Create a Lua configuration that sets the default device
            device_conf_content = f"""-- Automatically generated by Moinsy
-- Default device configuration

local rule = {{
  matches = {{
    {{
      {{ "node.name", "equals", "{chosen_device}" }},
    }},
  }},
  apply_properties = {{
    ["node.description"] = "Default Output Device",
    ["priority.session"] = 2000,
    ["priority.driver"] = 2000,
  }},
}}

table.insert(alsa_monitor.rules, rule)
"""
            # Write the configuration file
            with open(device_conf_path, "w") as f:
                f.write(device_conf_content)

            # Set ownership
            os.system(f"chown {self.username_prop}:{self.username_prop} {device_conf_path}")

            self.log_output.emit(f"Set '{chosen_device}' as default audio output device")
            self.log_output.emit("Configuration will be applied when PipeWire starts in your next session")
            self.logger.info("PipeWire configuration completed successfully")

        except Exception as e:
            error_msg = f"Failed to configure PipeWire settings: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)