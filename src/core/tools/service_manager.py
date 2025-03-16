from PyQt6.QtCore import QObject, pyqtSignal
import subprocess
import logging
from typing import List, Tuple, Optional, Dict, Any


class ServiceManager(QObject):
    """Service Manager Tool that uses main terminal for output"""

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    request_input = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the service manager.

        Args:
            parent: Parent object
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.services = []
        self.show_all_services = False  # Default to showing only active services

    def set_show_all_services(self, show_all: bool) -> None:
        """Set whether to show all services or only active ones.

        Args:
            show_all: True to show all services, False to show only active services
        """
        self.show_all_services = show_all
        self.logger.debug(f"Show all services set to: {show_all}")

    def list_services(self) -> None:
        """List all system services"""
        try:
            self.log_output.emit("\nFetching system services...")
            self.update_progress.emit(0)

            # Construct the command based on settings
            base_command = ["systemctl", "list-units", "--type=service"]

            if self.show_all_services:
                base_command.append("--all")
                self.log_output.emit("Including all services (including inactive)")
            else:
                self.log_output.emit("Showing active services only")

            # Get all services
            output = subprocess.check_output(base_command, text=True)

            # Parse service information
            self.services = []
            for line in output.split('\n')[1:]:  # Skip header
                if "loaded" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        service_name = parts[0]
                        status = parts[3]
                        self.services.append((service_name, status))

            # Display services
            self.log_output.emit(f"\nAvailable Services ({len(self.services)}):")
            for i, (name, status) in enumerate(self.services, 1):
                status_color = "green" if status == "active" else "yellow"
                self.log_output.emit(f"{i}. {name:<40} [{status}]")

            self.update_progress.emit(100)
            self.log_output.emit("\nEnter the number of the service to manage:")
            self.request_input.emit(
                "\nService number (or 'q' to quit): ",
                "handle_service_selection"
            )

        except Exception as e:
            self.logger.exception(f"Service listing error: {str(e)}")
            self.error_occurred.emit(f"Service listing error: {str(e)}")
            self.update_progress.emit(0)

    def handle_service_selection(self, selection: str) -> None:
        """Handle user's service selection"""
        try:
            if selection.lower() == 'q':
                self.log_output.emit("\nExiting Service Manager")
                return

            # Validate selection
            service_num = int(selection)
            if service_num < 1 or service_num > len(self.services):
                self.error_occurred.emit("Invalid service number")
                return

            selected_service = self.services[service_num - 1][0]
            self.show_service_options(selected_service)

        except ValueError:
            self.error_occurred.emit("Please enter a valid number or 'q' to quit")
        except Exception as e:
            self.logger.exception(f"Error handling selection: {str(e)}")
            self.error_occurred.emit(f"Error handling selection: {str(e)}")

    def show_service_options(self, service: str) -> None:
        """Show available actions for selected service"""
        self.log_output.emit(f"\nManaging service: {service}")
        self.log_output.emit("\nAvailable actions:")
        self.log_output.emit("1. Start service")
        self.log_output.emit("2. Stop service")
        self.log_output.emit("3. Restart service")
        self.log_output.emit("4. Enable service")
        self.log_output.emit("5. Disable service")
        self.log_output.emit("6. Show service status")
        self.log_output.emit("7. Back to service list")

        self.current_service = service
        self.request_input.emit(
            "\nEnter action number: ",
            "handle_action_selection"
        )

    def handle_action_selection(self, selection: str) -> None:
        """Handle user's action selection"""
        try:
            action_num = int(selection)

            if action_num == 7:
                self.list_services()
                return

            if action_num < 1 or action_num > 7:
                self.error_occurred.emit("Invalid action number")
                return

            # Map actions to commands
            actions = {
                1: ("start", "Starting"),
                2: ("stop", "Stopping"),
                3: ("restart", "Restarting"),
                4: ("enable", "Enabling"),
                5: ("disable", "Disabling"),
                6: ("status", "Checking status of")
            }

            action, action_text = actions[action_num]
            self.log_output.emit(f"\n{action_text} {self.current_service}...")
            self.update_progress.emit(50)

            # Execute service command
            self.run_command(["sudo", "systemctl", action, self.current_service])

            self.update_progress.emit(100)

            # Show updated status after action
            if action != "status":
                self.run_command(["systemctl", "status", self.current_service])

            # Return to service options
            self.show_service_options(self.current_service)

        except ValueError:
            self.error_occurred.emit("Please enter a valid number")
        except Exception as e:
            self.logger.exception(f"Error performing action: {str(e)}")
            self.error_occurred.emit(f"Error performing action: {str(e)}")
            self.update_progress.emit(0)

    def run_command(self, command: List[str]) -> None:
        """Execute a system command and handle its output"""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=isinstance(command, str)
            )
            stdout, stderr = process.communicate()

            if stdout:
                self.log_output.emit(stdout)
            if stderr:
                self.log_output.emit(f"Warning: {stderr}")

        except Exception as e:
            self.logger.exception(f"Error executing command: {str(e)}")
            self.error_occurred.emit(f"Error executing command: {str(e)}")