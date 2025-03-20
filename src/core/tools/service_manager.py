#!/usr/bin/env python3
"""
Service Manager Tool for interfacing with system services.

Like an orchestra conductor with a temperamental ensemble of performers,
this module attempts to bring harmony to the chaotic world of system services,
waving its digital baton in hopes that the unpredictable musicians of systemd
will follow its guidance - all while knowing that true control is ultimately
an illusion in the complex symphony of a modern operating system.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import subprocess
import logging
import shlex
import time
from typing import List, Tuple, Optional, Dict, Any, Union, cast
from enum import Enum, auto
from dataclasses import dataclass


class ServiceStatus(Enum):
    """
    Enumeration of possible service states.

    Like the emotional spectrum of digital entities, these states
    represent the lifecycle of services as they flicker between
    existence and dormancy in the shadowy realm of process tables.
    """
    ACTIVE = auto()
    INACTIVE = auto()
    FAILED = auto()
    UNKNOWN = auto()


@dataclass
class ServiceInfo:
    """
    Data container for service information.

    A structured monument to the ephemeral state of a service - a snapshot
    of its fleeting configuration in the perpetual river of system processes.
    """
    name: str
    status: ServiceStatus
    enabled: bool
    description: str = ""

    @property
    def is_running(self) -> bool:
        """Determine if the service is currently running."""
        return self.status == ServiceStatus.ACTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Convert the service info to a serializable dictionary."""
        return {
            'name': self.name,
            'status': self.status.name,
            'enabled': self.enabled,
            'description': self.description,
            'is_running': self.is_running
        }


class ServiceManager(QObject):
    """
    Service Manager Tool that interfaces with systemd to control system services.

    Like a digital puppeteer manipulating the strings of systemd marionettes,
    this class provides the illusion of control over system services - an exercise
    in technological agency that masks the underlying complexity and chaos of
    processes that will eventually decide their own fate regardless of our input.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    request_input = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """
        Initialize the service manager with proper logging.

        Args:
            parent: Parent QObject for this manager
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Service state tracking
        self.services: List[Tuple[str, str]] = []  # List of (service_name, status) tuples
        self.show_all_services: bool = False  # Default to showing only active services
        self.current_service: Optional[str] = None  # Currently selected service

        self.logger.debug("Service Manager initialized - digital puppeteer awaits the strings")

    def set_show_all_services(self, show_all: bool) -> None:
        """
        Set whether to show all services or only active ones.

        Args:
            show_all: True to show all services, False to show only active services

        Like a curator deciding which artifacts deserve exhibition, this method
        determines the visibility criteria for our service collection - a boundary
        between the seen and unseen entities in our digital museum.
        """
        try:
            self.show_all_services = show_all
            self.logger.debug(f"Show all services set to: {show_all} - adjusting our curatorial filter")
        except Exception as e:
            error_msg = f"Failed to update show all services setting: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def list_services(self) -> None:
        """
        List all system services with filtering based on settings.

        Like a census taker counting the ephemeral citizens of processland,
        this method enumerates the services that populate our system's hidden
        society - each one a digital entity with its own lifecycle and purpose,
        now momentarily visible in our terminal's narrow viewport.
        """
        try:
            self.log_output.emit("\nFetching system services...")
            self.update_progress.emit(0)
            self.logger.info("Retrieving service list from systemd")

            # Construct the command based on settings
            base_command = ["systemctl", "list-units", "--type=service"]

            if self.show_all_services:
                base_command.append("--all")
                self.log_output.emit("Including all services (including inactive)")
                self.logger.debug("Including all services in listing")
            else:
                self.log_output.emit("Showing active services only")
                self.logger.debug("Filtering to show only active services")

            # Get all services with proper error handling
            try:
                self.update_progress.emit(10)
                output = subprocess.check_output(base_command, text=True)
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to retrieve service list: {str(e)}"
                self.error_occurred.emit(error_msg)
                self.logger.error(error_msg)
                self.update_progress.emit(0)
                return

            # Parse service information
            self.services = []
            active_count = 0
            inactive_count = 0

            self.update_progress.emit(30)

            # Process the output in a more robust way
            lines = output.splitlines()
            header_passed = False

            for line in lines:
                # Skip until we pass the header line
                if not header_passed:
                    if line.strip() and "UNIT" in line and "LOAD" in line and "ACTIVE" in line:
                        header_passed = True
                    continue

                # Skip separator and empty lines
                if not line.strip() or line.startswith("LOAD") or "loaded units listed" in line:
                    continue

                # Parse service information
                try:
                    parts = line.split(maxsplit=4)
                    if len(parts) >= 4:
                        service_name = parts[0]
                        status = parts[3]

                        # Only include actual service units
                        if service_name.endswith('.service'):
                            self.services.append((service_name, status))

                            # Count by status for reporting
                            if status.lower() == "active":
                                active_count += 1
                            else:
                                inactive_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to parse service line: {line}. Error: {str(e)}")
                    continue

            self.update_progress.emit(60)

            # Sort services alphabetically for easier viewing
            self.services.sort(key=lambda x: x[0])

            # Display services with better formatting
            self.log_output.emit(
                f"\nAvailable Services ({len(self.services)} total, {active_count} active, {inactive_count} inactive):")

            # Display services in a formatted table-like structure
            # Header
            self.log_output.emit("\n{:<4} {:<40} {:<10}".format("No.", "Service Name", "Status"))
            self.log_output.emit("-" * 60)

            # Content
            for i, (name, status) in enumerate(self.services, 1):
                # Remove the '.service' suffix for cleaner display
                display_name = name.replace('.service', '')

                # Color-code status
                if status.lower() == "active":
                    status_color = "green"
                elif status.lower() == "failed":
                    status_color = "red"
                else:
                    status_color = "yellow"

                # Determine highlight for alternate rows
                row_color = "#2a2a2a" if i % 2 == 0 else "transparent"

                # Emit as an HTML-styled row
                self.log_output.emit(
                    f"<span style='background-color: {row_color}'>"
                    f"{i:<4} {display_name:<40} "
                    f"<span style='color: {status_color}'>{status}</span>"
                    f"</span>"
                )

            self.update_progress.emit(100)
            self.log_output.emit("\nEnter the number of the service to manage:")
            self.request_input.emit(
                "\nService number (or 'q' to quit): ",
                "handle_service_selection"
            )

            self.logger.info(f"Successfully listed {len(self.services)} services")

        except Exception as e:
            error_msg = f"Service listing error: {str(e)}"
            self.logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
            self.update_progress.emit(0)

    def handle_service_selection(self, selection: str) -> None:
        """
        Handle user's service selection input.

        Args:
            selection: User input string containing service selection

        Like an interpreter translating the cryptic utterances of users
        into meaningful actions, this method processes selection input
        and routes it to the appropriate service management pathway -
        a bridge between human intent and system manipulation.
        """
        try:
            if selection.lower() == 'q':
                self.log_output.emit("\nExiting Service Manager")
                self.logger.info("User exited Service Manager")
                return

            # Validate selection as integer
            try:
                service_num = int(selection)
            except ValueError:
                error_msg = "Please enter a valid number or 'q' to quit"
                self.error_occurred.emit(error_msg)
                self.logger.warning(f"Invalid service selection: {selection}")
                self.request_input.emit("\nService number (or 'q' to quit): ", "handle_service_selection")
                return

            # Validate range
            if service_num < 1 or service_num > len(self.services):
                error_msg = f"Invalid service number. Please enter a number between 1 and {len(self.services)}"
                self.error_occurred.emit(error_msg)
                self.logger.warning(f"Service selection out of range: {service_num}")
                self.request_input.emit("\nService number (or 'q' to quit): ", "handle_service_selection")
                return

            # Get selected service
            selected_service = self.services[service_num - 1][0]
            self.current_service = selected_service
            self.logger.info(f"Selected service: {selected_service}")

            # Show service options
            self.show_service_options(selected_service)

        except Exception as e:
            error_msg = f"Error handling selection: {str(e)}"
            self.logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
            # Prompt again
            self.request_input.emit("\nService number (or 'q' to quit): ", "handle_service_selection")

    def show_service_options(self, service: str) -> None:
        """
        Show available actions for the selected service.

        Args:
            service: Name of the selected service

        Like a sommelier presenting a menu of options to an indecisive patron,
        this method offers the user a curated list of possible actions for their
        chosen service - each one a potential pathway toward digital harmony
        or system chaos, depending on the cosmic dice roll of runtime execution.
        """
        try:
            # Get current service status for better context
            status = self.get_service_status(service)

            # Create a more informative header with service details
            display_name = service.replace('.service', '')
            self.log_output.emit(f"\n📊 Managing service: {display_name}")

            # Show current status information
            self.log_output.emit(f"\nCurrent Status: {status['status']}")
            self.log_output.emit(f"Enabled at Boot: {'Yes' if status['enabled'] else 'No'}")
            if 'description' in status and status['description']:
                self.log_output.emit(f"Description: {status['description']}")

            # Show available actions with context-aware options
            self.log_output.emit("\nAvailable actions:")

            # Context-aware action list
            if status['status'] == 'active':
                self.log_output.emit("1. ⏹️ Stop service")
                self.log_output.emit("2. 🔄 Restart service")
            else:
                self.log_output.emit("1. ▶️ Start service")
                self.log_output.emit("2. 🔄 Restart service (will attempt to start if not running)")

            if status['enabled']:
                self.log_output.emit("3. 🚫 Disable service at boot")
            else:
                self.log_output.emit("3. ✅ Enable service at boot")

            self.log_output.emit("4. 📋 Show detailed service status")
            self.log_output.emit("5. 📜 View service logs")
            self.log_output.emit("6. 🔙 Back to service list")

            self.request_input.emit(
                "\nEnter action number: ",
                "handle_action_selection"
            )

            self.logger.debug(f"Displayed service options for {service}")

        except Exception as e:
            error_msg = f"Error showing service options: {str(e)}"
            self.logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
            # Try to get back to service list
            self.list_services()

    def get_service_status(self, service: str) -> Dict[str, Any]:
        """
        Get detailed status information for a service.

        Args:
            service: Name of the service to check

        Returns:
            Dictionary containing status information

        Like a physician examining a patient, this method attempts to diagnose
        the current condition of a service - taking its pulse, checking its
        reflexes, and assessing its vital signs to determine whether it is
        healthy, struggling, or has already crossed the digital river Styx.
        """
        status_info = {
            'name': service,
            'status': 'unknown',
            'enabled': False,
            'description': '',
            'error': ''
        }

        try:
            # Check if service is active
            is_active_cmd = ["systemctl", "is-active", service]
            try:
                active_result = subprocess.run(is_active_cmd, capture_output=True, text=True)
                status_info['status'] = active_result.stdout.strip()
            except Exception as e:
                self.logger.warning(f"Failed to check if service is active: {str(e)}")
                status_info['error'] = f"Failed to check active status: {str(e)}"

            # Check if service is enabled
            is_enabled_cmd = ["systemctl", "is-enabled", service]
            try:
                enabled_result = subprocess.run(is_enabled_cmd, capture_output=True, text=True)
                status_info['enabled'] = enabled_result.stdout.strip() == 'enabled'
            except Exception as e:
                self.logger.warning(f"Failed to check if service is enabled: {str(e)}")

            # Get service description
            try:
                desc_cmd = ["systemctl", "show", service, "--property=Description"]
                desc_result = subprocess.run(desc_cmd, capture_output=True, text=True)
                desc_line = desc_result.stdout.strip()
                if desc_line.startswith("Description="):
                    status_info['description'] = desc_line[len("Description="):].strip()
            except Exception as e:
                self.logger.warning(f"Failed to get service description: {str(e)}")

            self.logger.debug(
                f"Retrieved status for {service}: {status_info['status']}, enabled: {status_info['enabled']}")
            return status_info

        except Exception as e:
            error_msg = f"Error checking service status: {str(e)}"
            self.logger.exception(error_msg)
            status_info['error'] = str(e)
            return status_info

    def handle_action_selection(self, selection: str) -> None:
        """
        Handle the user's action selection for a service.

        Args:
            selection: User input string containing action selection

        Like a translator of intent converting abstract desires into concrete
        system commands, this method interprets the user's wishes and transforms
        them into the appropriate incantations to manipulate service state -
        a bridge between human aspiration and machine implementation.
        """
        try:
            if not self.current_service:
                self.error_occurred.emit("No service selected")
                self.list_services()
                return

            # Validate input
            try:
                action_num = int(selection)
            except ValueError:
                self.error_occurred.emit("Please enter a valid number")
                self.show_service_options(self.current_service)
                return

            # Get current status for context-aware actions
            status = self.get_service_status(self.current_service)
            is_active = status['status'] == 'active'
            is_enabled = status['enabled']

            # Process selection based on current service state
            if action_num == 1:  # Start/Stop based on current state
                if is_active:
                    self.perform_service_action("stop", "Stopping")
                else:
                    self.perform_service_action("start", "Starting")

            elif action_num == 2:  # Restart
                self.perform_service_action("restart", "Restarting")

            elif action_num == 3:  # Enable/Disable based on current state
                if is_enabled:
                    self.perform_service_action("disable", "Disabling")
                else:
                    self.perform_service_action("enable", "Enabling")

            elif action_num == 4:  # Status
                self.perform_service_action("status", "Checking status of")

            elif action_num == 5:  # View logs
                self.view_service_logs()

            elif action_num == 6:  # Back to list
                self.list_services()
                return

            else:
                self.error_occurred.emit(f"Invalid action number. Please enter a number between 1 and 6")
                self.show_service_options(self.current_service)
                return

            # Return to service options after action (except for "back" action)
            if action_num != 6:
                # Add a small delay to allow the action to complete
                QTimer.singleShot(500, lambda: self.show_service_options(self.current_service))

        except Exception as e:
            error_msg = f"Error performing action: {str(e)}"
            self.logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
            # Try to get back to service options
            if self.current_service:
                self.show_service_options(self.current_service)
            else:
                self.list_services()

    def perform_service_action(self, action: str, action_text: str) -> None:
        """
        Execute a systemctl action on the current service.

        Args:
            action: The systemctl action to perform
            action_text: User-friendly description of the action

        Like a surgeon performing a delicate operation on the living organism
        of our system, this method executes precise commands that can heal
        a malfunctioning service or, if performed incorrectly, potentially
        create new problems - a reminder of the inherent risk in all system
        modifications.
        """
        if not self.current_service:
            self.error_occurred.emit("No service selected")
            return

        try:
            service_name = self.current_service
            display_name = service_name.replace('.service', '')

            self.log_output.emit(f"\n{action_text} {display_name}...")
            self.update_progress.emit(50)
            self.logger.info(f"Executing {action} on service {service_name}")

            # Don't use sudo for status command or if already root
            if action == "status":
                command = ["systemctl", action, service_name]
            else:
                command = ["sudo", "systemctl", action, service_name]

            # Execute the command with robust error handling
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Process and display output in real-time for better user experience
                while True:
                    output_line = process.stdout.readline()
                    if output_line == '' and process.poll() is not None:
                        break
                    if output_line:
                        self.log_output.emit(output_line.strip())

                # Get final return code and any remaining output
                return_code = process.wait()
                stdout, stderr = process.communicate()

                # Process any remaining output
                if stdout:
                    for line in stdout.strip().split('\n'):
                        if line:
                            self.log_output.emit(line)

                # Handle errors
                if return_code != 0:
                    if stderr:
                        self.log_output.emit(f"Warning: {stderr.strip()}")
                    self.error_occurred.emit(f"Failed to {action} {display_name}")
                    self.logger.error(f"Command {action} failed with code {return_code}")
                else:
                    if action != "status":  # Don't show success for status as it shows its own output
                        self.log_output.emit(f"Successfully completed {action} operation on {display_name}")

            except subprocess.SubprocessError as e:
                error_msg = f"Error executing {action} command: {str(e)}"
                self.error_occurred.emit(error_msg)
                self.logger.error(error_msg)

            self.update_progress.emit(100)

        except Exception as e:
            error_msg = f"Error performing {action} action: {str(e)}"
            self.logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
            self.update_progress.emit(0)

    def view_service_logs(self) -> None:
        """
        Show recent logs for the selected service.

        Like an archaeologist examining ancient scrolls for clues about
        a lost civilization, this method retrieves the historical record
        of a service's activity - its triumphs, struggles, and failures
        laid bare in the cryptic hieroglyphics of log messages.
        """
        if not self.current_service:
            self.error_occurred.emit("No service selected")
            return

        try:
            service_name = self.current_service
            display_name = service_name.replace('.service', '')

            self.log_output.emit(f"\nFetching recent logs for {display_name}...")
            self.update_progress.emit(25)
            self.logger.info(f"Retrieving logs for service {service_name}")

            # Use journalctl to get recent logs, limit to last 50 entries
            command = ["journalctl", "-u", service_name, "-n", "50", "--no-pager"]

            # Execute command
            try:
                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True
                )

                self.update_progress.emit(75)

                # Process output for better readability
                log_lines = process.stdout.strip().split('\n')

                if not log_lines or (len(log_lines) == 1 and not log_lines[0].strip()):
                    self.log_output.emit(f"\nNo logs found for {display_name}")
                else:
                    self.log_output.emit(f"\n📜 Recent Logs for {display_name} (last 50 entries):")
                    self.log_output.emit("─" * 60)

                    # Show the logs with syntax highlighting
                    for line in log_lines:
                        # Color code based on log level
                        if "ERROR" in line or "CRIT" in line or "ALERT" in line or "EMERG" in line:
                            self.log_output.emit(f"<span style='color: #ff5252'>{line}</span>")
                        elif "WARNING" in line or "WARN" in line:
                            self.log_output.emit(f"<span style='color: #ffd740'>{line}</span>")
                        elif "INFO" in line or "NOTICE" in line:
                            self.log_output.emit(f"<span style='color: #4caf50'>{line}</span>")
                        else:
                            self.log_output.emit(line)

                    self.log_output.emit("\n(End of logs)")

            except subprocess.CalledProcessError as e:
                error_msg = f"Error retrieving logs: {str(e)}"
                self.error_occurred.emit(error_msg)
                self.logger.error(error_msg)
                if e.stderr:
                    self.log_output.emit(f"Error: {e.stderr}")

            self.update_progress.emit(100)
            self.log_output.emit("\nPress any key to return to service options...")

        except Exception as e:
            error_msg = f"Error viewing service logs: {str(e)}"
            self.logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
            self.update_progress.emit(0)

        # Return to service options after viewing logs
        if self.current_service:
            self.show_service_options(self.current_service)