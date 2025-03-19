#!/usr/bin/env python3
"""
System Update Tool for managing package updates across multiple package managers.

Like Sisyphus endlessly pushing his boulder uphill, this module perpetually
chases the asymptotic goal of an up-to-date system - a Sisyphean task made
all the more poignant by the eternal march of software releases that ensures
our work is never truly complete.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import subprocess
import logging
import shutil
import os
import json
from typing import Optional, List, Dict, Union, Tuple, Any, Set, cast
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime, timedelta

from utils.system_utils import execute_command


class PackageManagerType(Enum):
    """
    Enumeration of supported package manager types.

    An arbitrary taxonomy of digital distribution mechanisms, each with their
    own philosophical approach to the fundamental question: "How should
    software be packaged and distributed in our ephemeral digital realm?"
    """
    APT = auto()
    FLATPAK = auto()
    SNAP = auto()


@dataclass
class UpdateSummary:
    """
    Data container for update operation results.

    A structured monument to our system's transient state - capturing
    a moment in time that, like all moments, has already passed by the
    time we acknowledge it.
    """
    timestamp: datetime
    total_updates: int
    succeeded: int
    failed: int
    skipped: int
    duration: timedelta
    error_messages: List[str]

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of the updates."""
        return self.succeeded / self.total_updates if self.total_updates > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the summary to a serializable dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_updates': self.total_updates,
            'succeeded': self.succeeded,
            'failed': self.failed,
            'skipped': self.skipped,
            'duration_seconds': self.duration.total_seconds(),
            'error_messages': self.error_messages,
            'success_rate': self.success_rate
        }


class SystemUpdater(QObject):
    """
    System Update Tool for managing package updates across multiple package managers.

    Like a digital janitor sweeping up the accumulated entropy of yesterday's code,
    this class diligently updates system packages across multiple package management
    ecosystems - a polyglot custodian of our software dependencies, ever vigilant
    against bit rot and security vulnerabilities.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    update_complete = pyqtSignal(dict)  # Emits update summary as dict

    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize the system updater with proper logging and signal setup.

        Args:
            parent: Parent QObject for this updater
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Track update status
        self._total_packages: int = 0
        self._updated_packages: int = 0
        self._failed_packages: int = 0
        self._skipped_packages: int = 0
        self._error_messages: List[str] = []
        self._start_time: Optional[datetime] = None

        # Package manager availability cache
        self._available_package_managers: Dict[PackageManagerType, bool] = {}

        self.logger.debug("System Updater initialized - preparing for entropic battle")

    def is_package_manager_available(self, manager_type: PackageManagerType) -> bool:
        """
        Check if a specific package manager is available on the system.

        Args:
            manager_type: The package manager type to check

        Returns:
            Boolean indicating availability

        Like a digital cartographer mapping the contours of the system, this method
        probes for the existence of various package management tools, determining
        what territories our update expedition can traverse.
        """
        # Check cache first
        if manager_type in self._available_package_managers:
            return self._available_package_managers[manager_type]

        # Command lookup
        commands = {
            PackageManagerType.APT: "apt",
            PackageManagerType.FLATPAK: "flatpak",
            PackageManagerType.SNAP: "snap"
        }

        command = commands[manager_type]

        # Check if command exists
        try:
            is_available = shutil.which(command) is not None

            # Cache the result
            self._available_package_managers[manager_type] = is_available

            if not is_available:
                self.logger.info(f"Package manager '{command}' not available on this system")

            return is_available
        except Exception as e:
            self.logger.error(f"Error checking for package manager '{command}': {str(e)}")
            self._available_package_managers[manager_type] = False
            return False

    def start_update(self, clean_after: bool = True) -> None:
        """
        Execute the system update process, updating all available package managers.

        Args:
            clean_after: Whether to perform cleanup operations after updating

        Like a conductor coordinating an orchestra of disparate package managers,
        each with their own tempo and notation system, this method orchestrates
        a harmonious update sequence - even if the underlying components would
        rather play in discord.
        """
        try:
            # Reset tracking variables
            self._total_packages = 0
            self._updated_packages = 0
            self._failed_packages = 0
            self._skipped_packages = 0
            self._error_messages = []
            self._start_time = datetime.now()

            self.log_output.emit("\n—— Starting System Update ——")
            self.update_progress.emit(0)
            self.logger.info("Initiating system update process")

            # Update apt package lists first (if available)
            if self.is_package_manager_available(PackageManagerType.APT):
                self.log_output.emit("Checking for available updates...")
                self._update_apt_lists()

            # Check for updates across all package managers
            apt_updates = self._check_apt_updates() if self.is_package_manager_available(PackageManagerType.APT) else 0
            flatpak_updates = self._check_flatpak_updates() if self.is_package_manager_available(
                PackageManagerType.FLATPAK) else 0
            snap_updates = self._check_snap_updates() if self.is_package_manager_available(
                PackageManagerType.SNAP) else 0

            # Calculate total updates
            self._total_packages = apt_updates + flatpak_updates + snap_updates

            # If no updates, exit early
            if self._total_packages <= 0:
                self.log_output.emit("\n✓ Your system is already up to date!")
                self.update_progress.emit(100)
                self._finalize_update(clean_after=False)  # No need to clean if nothing updated
                self.logger.info("System is already up to date - no packages to update")
                return

            # Report found updates in user-friendly format
            self.log_output.emit(
                f"\nFound {self._total_packages} update{'' if self._total_packages == 1 else 's'} available:")

            # Use more friendly terms for different types of updates
            if apt_updates > 0:
                self.log_output.emit(f"  • {apt_updates} system package{'' if apt_updates == 1 else 's'}")
            if flatpak_updates > 0:
                self.log_output.emit(f"  • {flatpak_updates} desktop application{'' if flatpak_updates == 1 else 's'}")
            if snap_updates > 0:
                self.log_output.emit(f"  • {snap_updates} snap application{'' if snap_updates == 1 else 's'}")

            self.update_progress.emit(10)

            # Define operation steps and weights
            operations = []
            progress_offset = 10  # Starting from 10% after checks

            # Update APT
            if apt_updates > 0:
                weight = int(apt_updates / self._total_packages * 50)  # 50% of progress bar for APT
                operations.append((self._update_apt_packages, weight))

            # Update Flatpak
            if flatpak_updates > 0:
                weight = int(flatpak_updates / self._total_packages * 20)  # 20% of progress bar for Flatpak
                operations.append((self._update_flatpak_packages, weight))

            # Update Snap
            if snap_updates > 0:
                weight = int(snap_updates / self._total_packages * 20)  # 20% of progress bar for Snap
                operations.append((self._update_snap_packages, weight))

            # Execute each update operation with weighted progress tracking
            for operation, weight in operations:
                try:
                    operation()
                    progress_offset += weight
                    self.update_progress.emit(progress_offset)
                except Exception as e:
                    error_msg = f"Error during update operation: {str(e)}"
                    self.error_occurred.emit(error_msg)
                    self.logger.error(error_msg)
                    # Continue with next operation despite errors

            # Clean up if requested
            if clean_after:
                progress_offset += 5  # Allow 5% for cleanup
                self._cleanup_packages()

            # Finalize and report results
            self._finalize_update(clean_after)

        except Exception as e:
            error_msg = f"Update process failed: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.update_progress.emit(0)
            self.logger.error(f"Update failed: {str(e)}", exc_info=True)

            # Still try to emit summary
            self._finalize_update(clean_after=False)

    def _update_apt_lists(self) -> None:
        """
        Update APT package lists to get latest package information.

        Like refreshing stale memory with new truths from the remote repositories,
        this method updates our local cache of package knowledge - preparing us
        for the more substantial work of actually updating the packages themselves.
        """
        try:
            self.log_output.emit("\nUpdating package lists...")
            self.logger.info("Updating APT package lists")

            result = self.run_command(["sudo", "apt-get", "update", "-q"], "Failed to update package lists")

            if result != 0:
                raise Exception("Failed to update package lists")

        except Exception as e:
            error_msg = f"Failed to update APT package lists: {str(e)}"
            self._error_messages.append(error_msg)
            self.error_occurred.emit(error_msg)
            self.logger.error(error_msg)

    def _check_apt_updates(self) -> int:
        """
        Check for available APT package updates.

        Returns:
            Number of APT updates available

        Like a digital accountant tallying potential expenditures of time and bandwidth,
        this method quantifies the APT updates awaiting our attention - a numerical
        representation of our system's growing divergence from modernity.
        """
        try:
            self.log_output.emit("\nChecking for APT updates...")

            # Use apt list --upgradable for more reliable output
            output = execute_command(["apt", "list", "--upgradable"], return_output=True)
            if not isinstance(output, str):
                return 0

            # Parse the output - each line after the first represents an upgradable package
            lines = output.strip().split('\n')

            # Handling the header line and counting packages
            # First line is always header ("Listing... Done" or similar)
            count = max(0, len(lines) - 1)

            if count > 0:
                self.logger.info(f"Found {count} APT package updates available")
            else:
                self.logger.info("No APT package updates available")

            return count

        except Exception as e:
            self.logger.warning(f"Error checking APT updates: {str(e)}")
            return 0

    def _check_flatpak_updates(self) -> int:
        """
        Check for available Flatpak application updates.

        Returns:
            Number of Flatpak updates available

        Like an inspector examining the Flatpak application containers for signs
        of obsolescence, this method identifies which sandboxed applications
        require renovation - tallying the work that awaits us in this domain.
        """
        try:
            self.log_output.emit("\nChecking for Flatpak updates...")

            # Use remote-ls --updates for more reliable count
            output = execute_command(["flatpak", "remote-ls", "--updates"], return_output=True)
            if not isinstance(output, str):
                return 0

            # Count non-empty lines
            count = len([line for line in output.split('\n') if line.strip()])

            if count > 0:
                self.logger.info(f"Found {count} Flatpak updates available")
            else:
                self.logger.info("No Flatpak updates available")

            return count

        except Exception as e:
            self.logger.warning(f"Error checking Flatpak updates: {str(e)}")
            return 0

    def _check_snap_updates(self) -> int:
        """
        Check for available Snap package updates.

        Returns:
            Number of Snap updates available

        Like a census taker counting the Snap packages yearning for renewal,
        this method quantifies the updates available through Ubuntu's
        self-contained package format - each number a container soon to be refreshed.
        """
        try:
            self.log_output.emit("\nChecking for Snap updates...")

            # Use more reliable refresh --list command
            output = execute_command(["snap", "refresh", "--list"], return_output=True)
            if not isinstance(output, str):
                return 0

            # If "All snaps up to date" or similar is in output, no updates available
            if "All snaps up to date" in output or "No updates available" in output:
                self.logger.info("No Snap updates available")
                return 0

            # Count non-empty lines that don't contain headers or info messages
            # Usually snap refresh --list has a header line we need to ignore
            count = len([line for line in output.split('\n')
                         if line.strip() and "Name" not in line and "Version" not in line])

            if count > 0:
                self.logger.info(f"Found {count} Snap updates available")

            return count

        except Exception as e:
            self.logger.warning(f"Error checking Snap updates: {str(e)}")
            return 0

    def _update_apt_packages(self) -> None:
        """
        Update APT packages with proper error handling and status reporting.

        Like a surgeon carefully applying patches to wounded software,
        this method administers updated code to heal vulnerabilities and resolve
        bugs - an exercise in digital healthcare for our aging packages.
        """
        try:
            self.log_output.emit("\nUpdating system packages...")
            self.logger.info("Updating APT packages")

            # Use apt-get upgrade with flags for more reliable updates
            # -y: Automatic yes to prompts
            # -q: Produce output suitable for logging, omitting progress indicators
            # --with-new-pkgs: Allow installing new packages if required
            result = self.run_command(
                ["sudo", "apt-get", "upgrade", "-y", "-q", "--with-new-pkgs"],
                "Failed to upgrade system packages"
            )

            if result != 0:
                error_msg = "System package update failed"
                self._error_messages.append(error_msg)
                self.error_occurred.emit(error_msg)
                self._failed_packages += 1
                return

            # Note: We don't need to emit success here, as the run_command method
            # will already provide user-friendly output based on the actual packages updated
            self.logger.info("APT packages updated successfully")
            self._updated_packages += 1

        except Exception as e:
            error_msg = f"Error updating system packages: {str(e)}"
            self._error_messages.append(error_msg)
            self.error_occurred.emit("System package update failed")  # Simplified for users
            self.logger.error(error_msg)
            self._failed_packages += 1

    def _update_flatpak_packages(self) -> None:
        """
        Update all Flatpak applications with proper error handling.

        Like a lighthouse keeper maintaining isolated signals along a digital coast,
        this method updates the self-contained Flatpak applications - each one a
        beacon of functionality, isolated from the mainland system.
        """
        try:
            self.log_output.emit("\nUpdating desktop applications...")
            self.logger.info("Updating Flatpak applications")

            # Update all flatpak applications
            # -y: Automatic yes to prompts
            # --noninteractive: Don't ask questions
            result = self.run_command(
                ["flatpak", "update", "-y", "--noninteractive"],
                "Failed to update desktop applications"
            )

            if result != 0:
                error_msg = "Desktop application update failed"
                self._error_messages.append(error_msg)
                self.error_occurred.emit(error_msg)
                self._failed_packages += 1
                return

            # Success message handled by run_command's user-friendly output
            self.logger.info("Flatpak applications updated successfully")
            self._updated_packages += 1

        except Exception as e:
            error_msg = f"Error updating Flatpak applications: {str(e)}"
            self._error_messages.append(error_msg)
            self.error_occurred.emit("Desktop application update failed")  # Simplified for users
            self.logger.error(error_msg)
            self._failed_packages += 1

    def _update_snap_packages(self) -> None:
        """
        Update all Snap packages with proper error handling.

        Like a keeper of sealed time capsules, this method updates the
        containerized Snap packages - hermetically sealed units of functionality
        that require periodic refreshment despite their isolation.
        """
        try:
            self.log_output.emit("\nUpdating snap applications...")
            self.logger.info("Updating Snap packages")

            # Update all snap packages
            result = self.run_command(
                ["sudo", "snap", "refresh"],
                "Failed to update snap applications"
            )

            # Special handling: Snap returns 0 even when nothing is updated
            if result != 0:
                error_msg = "Snap application update failed"
                self._error_messages.append(error_msg)
                self.error_occurred.emit(error_msg)
                self._failed_packages += 1
                return

            # Success message handled by run_command's user-friendly output
            self.logger.info("Snap packages updated successfully")
            self._updated_packages += 1

        except Exception as e:
            error_msg = f"Error updating Snap packages: {str(e)}"
            self._error_messages.append(error_msg)
            self.error_occurred.emit("Snap application update failed")  # Simplified for users
            self.logger.error(error_msg)
            self._failed_packages += 1

    def _cleanup_packages(self) -> None:
        """
        Perform cleanup operations after updates to free up disk space.

        Like a meticulous janitor sweeping away the debris left behind by renovation,
        this method cleans up the digital detritus accumulated during our update
        operations - reclaiming space for the future.
        """
        try:
            self.log_output.emit("\nCleaning up temporary files...")
            self.logger.info("Performing post-update cleanup")

            # Clean up with apt
            if self.is_package_manager_available(PackageManagerType.APT):
                # Remove unused dependencies (no need to tell user details)
                self.run_command(
                    ["sudo", "apt-get", "autoremove", "-y"],
                    "Warning: Failed to remove unused dependencies"
                )

                # Clean package cache (no need to tell user details)
                self.run_command(
                    ["sudo", "apt-get", "clean"],
                    "Warning: Failed to clean package cache"
                )

            # Cleanup flatpak unused applications and runtimes (no need to tell user details)
            if self.is_package_manager_available(PackageManagerType.FLATPAK):
                self.run_command(
                    ["flatpak", "uninstall", "--unused", "-y"],
                    "Warning: Failed to clean up unused Flatpak components"
                )

            # The success message and space freed will be emitted by run_command's
            # user-friendly summary if relevant
            self.logger.info("Post-update cleanup completed")

        except Exception as e:
            warning_msg = f"Warning: Cleanup operations partially failed: {str(e)}"
            self.log_output.emit("Cleanup completed with minor issues.")  # Simplified for users
            self.logger.warning(warning_msg)
            # Don't add to error_messages as cleanup is non-critical

    def _finalize_update(self, clean_after: bool) -> None:
        """
        Finalize the update process and emit completion signal with statistics.

        Args:
            clean_after: Whether cleanup was performed

        Like an accountant finalizing the ledger after a day of transactions,
        this method tallies our successes and failures, producing a final
        report on our update operations - a numerical epitaph for our efforts.
        """
        try:
            # Calculate elapsed time
            end_time = datetime.now()
            start_time = self._start_time if self._start_time else end_time
            duration = end_time - start_time

            # Create summary
            summary = UpdateSummary(
                timestamp=end_time,
                total_updates=self._total_packages,
                succeeded=self._updated_packages,
                failed=self._failed_packages,
                skipped=self._skipped_packages,
                duration=duration,
                error_messages=self._error_messages
            )

            # Log summary to terminal in user-friendly format
            minutes, seconds = divmod(int(duration.total_seconds()), 60)
            dur_str = f"{minutes} minute{'' if minutes == 1 else 's'} {seconds} second{'' if seconds == 1 else 's'}" if minutes > 0 else f"{seconds} second{'' if seconds == 1 else 's'}"

            # For users, simple summary is better than detailed statistics
            self.log_output.emit("\n—— Update Complete ——")

            # Different message based on whether there were updates
            if summary.total_updates == 0:
                self.log_output.emit("No updates were needed. Your system is up to date.")
            else:
                # Different messages based on success/failure
                if summary.failed > 0:
                    self.log_output.emit(f"Updated {summary.succeeded} of {summary.total_updates} items.")
                    if summary.failed == 1:
                        self.log_output.emit("1 item could not be updated.")
                    else:
                        self.log_output.emit(f"{summary.failed} items could not be updated.")
                else:
                    if summary.total_updates == 1:
                        self.log_output.emit("1 item was successfully updated.")
                    else:
                        self.log_output.emit(f"All {summary.total_updates} items were successfully updated.")

            # Simple duration display
            self.log_output.emit(f"Time taken: {dur_str}")

            # For the technical logs, keep the detailed summary
            self.logger.info(f"Update summary: {summary.total_updates} total, {summary.succeeded} succeeded, " +
                             f"{summary.failed} failed, {summary.skipped} skipped, duration: {dur_str}")

            # Add overall success/failure message
            if summary.failed > 0:
                self.log_output.emit("\n⚠️ Update completed with some items not updated.")
                self.logger.warning(f"Update completed with {summary.failed} failures")
            elif summary.total_updates > 0:
                self.log_output.emit("\n✓ Update completed successfully!")
                self.logger.info("System update completed successfully")
            else:
                # No updates needed case
                self.logger.info("System update complete - no updates needed")

            # Set final progress
            self.update_progress.emit(100)

            # Emit update_complete signal with summary as dict
            self.update_complete.emit(summary.to_dict())

        except Exception as e:
            error_msg = f"Error generating update summary: {str(e)}"
            self.error_occurred.emit("Could not generate update summary.")  # Simplified for users
            self.logger.error(error_msg)
            # Ensure progress bar is set to completed state regardless
            self.update_progress.emit(100)

    def run_command(self, command: List[str], error_message: str = "") -> int:
        """
        Execute a system command and handle its output with user-friendly filtering.

        Args:
            command: Command list to execute
            error_message: Custom error message on failure

        Returns:
            Command return code (0 for success)

        Like a diplomatic translator simplifying complex technical jargon
        into understandable human language, this method not only executes
        commands but filters their verbose output into a digestible narrative
        suitable for users who, quite reasonably, don't care about the arcane
        implementation details of package management.
        """
        try:
            self.logger.debug(f"Running command: {' '.join(command)}")

            # Determine the type of operation for context-aware filtering
            operation_type = self._determine_operation_type(command)

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=isinstance(command, str)
            )

            # Collect output for intelligently filtered reporting
            output_lines: List[str] = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    if line:
                        output_lines.append(line)
                        # Log all lines for debugging, even if we don't show them to the user
                        self.logger.debug(f"Command output: {line}")

            # Wait for process to complete
            process.wait()

            # Get any stderr content
            stderr = process.stderr.read()
            if stderr:
                self.logger.warning(f"Command stderr: {stderr}")
                # We'll handle this in our user-friendly summary

            # Generate user-friendly summary instead of raw output dump
            self._emit_user_friendly_summary(
                command=command,
                operation_type=operation_type,
                output_lines=output_lines,
                stderr=stderr,
                return_code=process.returncode
            )

            # Handle error cases
            if process.returncode != 0 and error_message:
                # Emit a simplified error message without technical codes
                cleaned_error = error_message.replace(" (code: {process.returncode})", "")
                self.error_occurred.emit(cleaned_error)

            return process.returncode

        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            self.logger.error(error_msg)
            # Simplify the error message for users
            user_error = "Operation failed. The system encountered an unexpected problem."
            self.error_occurred.emit(user_error)
            return 1

    def _determine_operation_type(self, command: List[str]) -> str:
        """
        Determine the type of operation being performed for context-aware filtering.

        Args:
            command: The command being executed

        Returns:
            String identifying the operation type
        """
        cmd_str = " ".join(command)

        if "update" in cmd_str and ("apt-get" in cmd_str or "apt" in cmd_str):
            return "apt-update"
        elif "upgrade" in cmd_str and ("apt-get" in cmd_str or "apt" in cmd_str):
            return "apt-upgrade"
        elif "autoremove" in cmd_str or "clean" in cmd_str:
            return "apt-cleanup"
        elif "flatpak" in cmd_str and "update" in cmd_str:
            return "flatpak-update"
        elif "flatpak" in cmd_str and "uninstall --unused" in cmd_str:
            return "flatpak-cleanup"
        elif "snap" in cmd_str and "refresh" in cmd_str:
            return "snap-update"
        elif "list" in cmd_str or "remote-ls" in cmd_str:
            return "list-packages"
        else:
            return "generic"

    def _emit_user_friendly_summary(
            self,
            command: List[str],
            operation_type: str,
            output_lines: List[str],
            stderr: str,
            return_code: int
    ) -> None:
        """
        Generate and emit a user-friendly summary of command results.

        Args:
            command: The command that was executed
            operation_type: Type of operation for context-aware filtering
            output_lines: Raw output lines from command
            stderr: Standard error output if any
            return_code: Command return code

        Like a poet distilling complex emotions into a concise verse,
        this method transforms the verbose technical output into simple,
        meaningful messages that focus on what the user actually cares about.
        """
        # Default case - if we can't create a special summary, at least limit the output
        if not output_lines and not stderr:
            if return_code == 0:
                # Command succeeded but had no output
                return
            else:
                # Command failed but had no output
                self.log_output.emit("The operation couldn't be completed.")
                return

        # Handle different operation types with custom user-friendly messages
        if operation_type == "apt-update":
            # Don't show anything for package list updates - it's just preparation
            pass

        elif operation_type == "apt-upgrade":
            # Summarize package upgrades
            package_count = self._count_packages_from_apt_output(output_lines)
            if package_count > 0:
                self.log_output.emit(f"Updating {package_count} system packages...")

                # Optionally show a few package names if there aren't too many
                if 1 <= package_count <= 5:
                    packages = self._extract_package_names_from_apt(output_lines)
                    if packages:
                        self.log_output.emit(f"Packages: {', '.join(packages)}")
            else:
                self.log_output.emit("No system packages need updating.")

        elif operation_type == "flatpak-update":
            # Parse and summarize Flatpak updates
            app_count = self._count_packages_from_flatpak(output_lines)
            if app_count > 0:
                self.log_output.emit(f"Updating {app_count} Flatpak applications...")

                # Show app names for a small number of updates
                if 1 <= app_count <= 5:
                    apps = self._extract_app_names_from_flatpak(output_lines)
                    if apps:
                        self.log_output.emit(f"Applications: {', '.join(apps)}")
            else:
                self.log_output.emit("No Flatpak applications need updating.")

        elif operation_type == "snap-update":
            # Parse and summarize Snap updates
            if any("All snaps up to date" in line for line in output_lines):
                self.log_output.emit("No Snap packages need updating.")
            else:
                app_count = self._count_packages_from_snap(output_lines)
                if app_count > 0:
                    self.log_output.emit(f"Updating {app_count} Snap packages...")

                    # Show app names for a small number of updates
                    if 1 <= app_count <= 5:
                        apps = self._extract_app_names_from_snap(output_lines)
                        if apps:
                            self.log_output.emit(f"Packages: {', '.join(apps)}")

        elif operation_type == "apt-cleanup":
            # For cleanup operations, just summarize the amount of space freed
            space_freed = self._extract_space_freed(output_lines)
            if space_freed:
                self.log_output.emit(f"Freed up {space_freed} of disk space.")
            else:
                self.log_output.emit("Cleaned up system packages.")

        elif operation_type == "flatpak-cleanup" or operation_type == "list-packages":
            # These operations don't need user-visible output
            pass

        elif operation_type == "generic":
            # For unknown operations, just show if it succeeded or failed
            if return_code == 0:
                self.log_output.emit("Operation completed successfully.")
            else:
                self.log_output.emit("The operation encountered a problem.")

        # If there was an error, show a simplified version
        if stderr and return_code != 0:
            # Extract just the essential error message, not technical details
            clean_error = self._simplify_error_message(stderr)
            if clean_error:
                self.log_output.emit(f"Error: {clean_error}")

    def _simplify_error_message(self, error_text: str) -> str:
        """Extract a user-friendly error message from technical error text."""
        # Split into lines and take just the most meaningful ones
        lines = error_text.split('\n')

        # Filter out common noise in error messages
        filtered_lines = [
            line for line in lines
            if line.strip() and
               not line.startswith('E:') and
               not line.startswith('W:') and
               not line.startswith('N:') and
               not line.startswith('Traceback') and
               not 'WARNING' in line and
               not 'DEBUG' in line
        ]

        if filtered_lines:
            # Take just the first meaningful line
            return filtered_lines[0].strip()
        else:
            # Fallback general message
            return "The operation couldn't be completed."

    def _count_packages_from_apt_output(self, output_lines: List[str]) -> int:
        """Extract the number of packages being upgraded from apt output."""
        # Look for lines like "X packages upgraded, Y newly installed, Z to remove"
        for line in output_lines:
            if "packages upgraded" in line or "package upgraded" in line:
                parts = line.split(',')
                for part in parts:
                    if "upgraded" in part:
                        try:
                            return int(part.split()[0])
                        except (ValueError, IndexError):
                            pass
        return 0

    def _extract_package_names_from_apt(self, output_lines: List[str]) -> List[str]:
        """Extract package names from apt upgrade output."""
        packages = []
        # Look for lines with package names
        for line in output_lines:
            if '->' in line and '/' in line:  # Typical package upgrade line
                try:
                    # Extract just the package name from lines like "package/repo arch [version]"
                    package_name = line.split()[0].split('/')[0]
                    if package_name and package_name not in packages:
                        packages.append(package_name)
                except (ValueError, IndexError):
                    pass
        return packages

    def _count_packages_from_flatpak(self, output_lines: List[str]) -> int:
        """Count the number of Flatpak applications being updated."""
        # This is approximate as Flatpak output format can vary
        update_count = 0
        for line in output_lines:
            # Look for lines indicating an update operation
            if '=>' in line and ('Installing' in line or 'Updating' in line):
                update_count += 1
        return update_count

    def _extract_app_names_from_flatpak(self, output_lines: List[str]) -> List[str]:
        """Extract application names from Flatpak update output."""
        apps = []
        for line in output_lines:
            if '=>' in line and ('Installing' in line or 'Updating' in line):
                try:
                    # Try to extract the app name from the line
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part in ('Installing', 'Updating') and i + 1 < len(parts):
                            app_name = parts[i + 1].split('/')[-1]  # Get last part after slash
                            if app_name and app_name not in apps:
                                apps.append(app_name)
                except (ValueError, IndexError):
                    pass
        return apps

    def _count_packages_from_snap(self, output_lines: List[str]) -> int:
        """Count the number of Snap packages being updated."""
        # Count non-header lines that look like package updates
        update_count = 0
        for line in output_lines:
            # Skip header and information lines
            if not line or "Name" in line or "Publisher" in line or "All snaps up to date" in line:
                continue
            # Count lines that likely represent package updates
            if line.strip() and len(line.split()) >= 2:
                update_count += 1
        return update_count

    def _extract_app_names_from_snap(self, output_lines: List[str]) -> List[str]:
        """Extract application names from Snap update output."""
        apps = []
        for line in output_lines:
            # Skip header and information lines
            if not line or "Name" in line or "Publisher" in line or "All snaps up to date" in line:
                continue
            # Extract first word as app name
            if line.strip():
                parts = line.split()
                if parts:
                    app_name = parts[0]
                    if app_name and app_name not in apps:
                        apps.append(app_name)
        return apps

    def _extract_space_freed(self, output_lines: List[str]) -> Optional[str]:
        """Extract the amount of disk space freed from cleanup operations."""
        for line in output_lines:
            # Look for lines indicating freed space
            if "freed" in line.lower() and "disk" in line.lower():
                # Extract the amount with its unit
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in ("freed", "free"):
                        if i > 0 and i + 2 < len(words):
                            try:
                                amount = words[i - 1]
                                unit = words[i + 2]
                                return f"{amount} {unit}"
                            except (ValueError, IndexError):
                                pass
        return None