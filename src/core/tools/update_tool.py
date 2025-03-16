# src/core/tools/update_tool.py
"""System Update Tool that handles package updates across different package managers."""

from PyQt6.QtCore import QObject, pyqtSignal
import subprocess
import logging
from typing import Optional, List, Union

from utils.system_utils import execute_command

# Setup module logger
logger = logging.getLogger(__name__)


class SystemUpdater(QObject):
    """System Update Tool that handles system package updates.

    This class provides functionality to update system packages across
    multiple package managers (apt, flatpak, snap).
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the system updater.

        Args:
            parent: Parent QObject for this updater
        """
        super().__init__(parent)
        logger.debug("System Updater initialized")

    def start_update(self) -> None:
        """Execute the system update process."""
        try:
            # Update apt package lists
            self.log_output.emit("\nUpdating package lists...")
            self.update_progress.emit(0)
            logger.info("Starting system update")

            result = self.run_command(["sudo", "apt-get", "update"])
            if result != 0:
                self.error_occurred.emit("Failed to update package lists")
                logger.error("Failed to update package lists")
                return

            # Get list of upgradeable packages
            self.log_output.emit("\nChecking for available updates...")
            logger.info("Checking for available updates")

            # Check apt updates
            apt_updates = self._check_apt_updates()
            logger.info(f"Found {apt_updates} apt updates")

            # Check Flatpak updates
            flatpak_updates = self._check_flatpak_updates()
            logger.info(f"Found {flatpak_updates} flatpak updates")

            # Check Snap updates
            snap_updates = self._check_snap_updates()
            logger.info(f"Found {snap_updates} snap updates")

            total_updates = apt_updates + flatpak_updates + snap_updates
            if total_updates <= 0:
                self.log_output.emit("\nSystem is already up to date!")
                self.update_progress.emit(100)
                logger.info("System is already up to date")
                return

            self.log_output.emit(f"\nFound {total_updates} updates available")
            self.update_progress.emit(20)

            # Update apt packages
            if apt_updates > 0:
                self.log_output.emit("\nUpdating system packages...")
                logger.info("Updating apt packages")
                result = self.run_command(["sudo", "apt-get", "upgrade", "-y"])
                if result != 0:
                    self.error_occurred.emit("Failed to upgrade system packages")
                    logger.error("Failed to upgrade system packages")
                    return

                self.update_progress.emit(50)
                self.log_output.emit("System packages updated")

            # Update Flatpak packages
            if flatpak_updates > 0:
                self.log_output.emit("\nUpdating Flatpak applications...")
                logger.info("Updating Flatpak applications")
                result = self.run_command(["flatpak", "update", "-y"])
                if result != 0:
                    self.error_occurred.emit("Failed to update Flatpak applications")
                    logger.warning("Failed to update Flatpak applications")
                    # Continue with other updates

                self.update_progress.emit(75)
                self.log_output.emit("Flatpak applications updated")

            # Update Snap packages
            if snap_updates > 0:
                self.log_output.emit("\nUpdating Snap applications...")
                logger.info("Updating Snap applications")
                result = self.run_command(["sudo", "snap", "refresh"])
                if result != 0:
                    self.error_occurred.emit("Failed to update Snap applications")
                    logger.warning("Failed to update Snap applications")
                    # Continue with cleanup

                self.update_progress.emit(90)
                self.log_output.emit("Snap applications updated")

            # Clean up
            self.log_output.emit("\nCleaning up...")
            logger.info("Cleaning up after update")
            self.run_command(["sudo", "apt-get", "autoremove", "-y"])
            self.run_command(["sudo", "apt-get", "clean"])

            self.update_progress.emit(100)
            self.log_output.emit("\nSystem update completed successfully!")
            logger.info("System update completed successfully")

        except Exception as e:
            error_msg = f"Update error: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.update_progress.emit(0)
            logger.error(f"Update failed: {str(e)}")

    def _check_apt_updates(self) -> int:
        """Check for available apt updates.

        Returns:
            Number of apt updates available
        """
        try:
            output = execute_command(["apt", "list", "--upgradeable"], return_output=True)
            if not isinstance(output, str):
                return 0

            # Count lines excluding header
            return len([line for line in output.split('\n') if line.strip()]) - 1
        except Exception as e:
            logger.warning(f"Error checking apt updates: {str(e)}")
            return 0

    def _check_flatpak_updates(self) -> int:
        """Check for available Flatpak updates.

        Returns:
            Number of Flatpak updates available
        """
        try:
            output = execute_command(["flatpak", "remote-ls", "--updates"], return_output=True)
            if not isinstance(output, str):
                return 0

            # Count lines with content
            return len([line for line in output.split('\n') if line.strip()])
        except Exception as e:
            logger.warning(f"Error checking Flatpak updates: {str(e)}")
            return 0

    def _check_snap_updates(self) -> int:
        """Check for available Snap updates.

        Returns:
            Number of Snap updates available
        """
        try:
            output = execute_command(["snap", "refresh", "--list"], return_output=True)
            if not isinstance(output, str):
                return 0

            # Count lines with content
            return len([line for line in output.split('\n') if line.strip()])
        except Exception as e:
            logger.warning(f"Error checking Snap updates: {str(e)}")
            return 0

    def run_command(self, command: List[str]) -> int:
        """Execute a system command and handle its output.

        Args:
            command: Command list to execute

        Returns:
            Command return code (0 for success)
        """
        try:
            logger.debug(f"Running command: {' '.join(command)}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=isinstance(command, str)
            )
            stdout, stderr = process.communicate()

            if stdout and len(stdout.strip()) > 0:
                logger.debug(f"Command output: {stdout[:500]}...")

            if stderr and len(stderr.strip()) > 0:
                self.log_output.emit(f"Warning: {stderr}")
                logger.warning(f"Command warning: {stderr}")

            return process.returncode
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return 1