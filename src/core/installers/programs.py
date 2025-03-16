# src/core/installers/programs.py
"""Installer class for managing program installations from online sources."""

from PyQt6.QtCore import QObject, pyqtSignal
import os
import json
import logging
from typing import List, Dict, Any, Optional, Union, Callable

from config import get_resource_path, DATA_DIR
from utils.system_utils import execute_command

# Setup module logger
logger = logging.getLogger(__name__)


class ProgramInstaller(QObject):
    """Installer class for managing program installations from online sources.

    This class handles the installation of programs from multiple package
    managers including apt, snap, and flatpak.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    request_input = pyqtSignal(str, str)
    pass_command = pyqtSignal(list, bool)

    def __init__(self):
        """Initialize the program installer."""
        super().__init__()
        self.program_dir = None
        self.programs_path = None
        self.programs_data = None
        self.options = []
        logger.debug("Program installer initialized")

    @property
    def programs_path_prop(self) -> str:
        """Get path to programs.json configuration file.

        Returns:
            Absolute path to programs.json
        """
        if self.programs_path is None:
            self.programs_path = os.path.join(DATA_DIR, "programs.json")

            # Fall back to old location if needed
            if not os.path.exists(self.programs_path):
                self.programs_path = get_resource_path("installers", "resources", "programs.json")

        return self.programs_path

    @property
    def programs_data_prop(self) -> Dict[str, Any]:
        """Get program definitions from JSON file.

        Returns:
            Dictionary containing parsed program data
        """
        if self.programs_data is None:
            self.programs_data = self.load_programs()
        return self.programs_data

    def load_programs(self) -> Dict[str, Any]:
        """Load program definitions from JSON file.

        Returns:
            Dictionary containing parsed programs data

        Raises:
            Exception: If programs data cannot be loaded
        """
        try:
            logger.info(f"Loading programs data from {self.programs_path_prop}")
            with open(self.programs_path_prop, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            error_msg = f"Programs definition file not found: {self.programs_path_prop}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except json.JSONDecodeError:
            error_msg = f"Invalid JSON in programs file: {self.programs_path_prop}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to load programs: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_options(self) -> None:
        """Display available programs by category."""
        try:
            data = self.programs_data_prop
            if not data or "categories" not in data:
                self.error_occurred.emit("No program categories found.")
                logger.error("No program categories found in programs.json")
                return

            self.options = []
            self.log_output.emit("\nAvailable programs to install:")

            # Display all categories and programs
            for cat_id, category in data["categories"].items():
                self.log_output.emit(f"\n{category['name']}:")
                for prog_id, program in category["programs"].items():
                    self.options.append({
                        "id": prog_id,
                        "name": program["name"],
                        "type": program["type"],
                        "package": program["package"]
                    })
                    self.log_output.emit(f"{len(self.options)}. {program['name']}")

            if not self.options:
                self.log_output.emit("\nNo programs available for installation.")
                logger.warning("No programs available for installation")
                return

            self.request_input.emit(
                "\nEnter the numbers of the programs you want to install (separated by spaces):",
                "install_options"
            )
            logger.info(f"Displayed {len(self.options)} available programs")

        except Exception as e:
            error_msg = f"Error getting program options: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)

    def install_options(self, user_input: str) -> None:
        """Install selected programs.

        Args:
            user_input: Space-separated list of program numbers to install
        """
        try:
            # Validate input
            try:
                selected_programs = [int(x) for x in user_input.split()]
                if any(i <= 0 or i > len(self.options) for i in selected_programs):
                    raise ValueError("Invalid program number selected")
                logger.info(f"Selected programs: {selected_programs}")
            except ValueError as e:
                self.error_occurred.emit(f"Invalid input: {str(e)}")
                logger.error(f"Invalid user input: {user_input} - {str(e)}")
                return

            # Install dependencies
            self.install_package_managers()

            # Calculate progress steps
            progress_step = 100 // (len(selected_programs) + 1)
            current_progress = 0

            # Install each selected program
            for i, number in enumerate(selected_programs, 1):
                program = self.options[number - 1]
                self.log_output.emit(f"\nInstalling {program['name']}")
                logger.info(f"Installing program: {program['name']}")

                if not self.install_program(program):
                    self.error_occurred.emit(f"Failed to install {program['name']}")
                    logger.error(f"Failed to install {program['name']}")
                    return

                current_progress += progress_step
                self.update_progress.emit(current_progress)

            self.update_progress.emit(100)
            self.log_output.emit("\nProgram installation completed successfully.")
            logger.info("Program installation completed successfully")

        except Exception as e:
            error_msg = f"Installation error: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)

    def install_package_managers(self) -> None:
        """Install and configure required package managers.

        Raises:
            Exception: If package managers cannot be configured
        """
        self.log_output.emit("\nConfiguring package managers...")
        logger.info("Configuring package managers")

        try:
            # Update apt
            self.log_output.emit("Updating apt repositories...")
            self.pass_command.emit(["sudo", "apt-get", "update"], False)

            # Install snap if not present
            self.log_output.emit("Ensuring snap is installed...")
            self.pass_command.emit(["sudo", "apt-get", "install", "snapd", "-y"], False)

            # Install flatpak and required components
            self.log_output.emit("Ensuring flatpak is installed...")
            self.pass_command.emit(["sudo", "apt-get", "install", "flatpak", "gnome-software-plugin-flatpak", "-y"],
                                   False)

            # Configure Flatpak repositories
            self.log_output.emit("\nConfiguring Flatpak...")
            self.pass_command.emit([
                "sudo", "flatpak", "remote-add", "--if-not-exists",
                "--system", "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo"
            ], False)

            # Update Flatpak
            self.log_output.emit("Updating Flatpak...")
            self.pass_command.emit(["sudo", "flatpak", "update", "--system", "--noninteractive"], False)
            logger.info("Package managers configured successfully")

        except Exception as e:
            error_msg = f"Failed to configure package managers: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def install_program(self, program: Dict[str, str]) -> bool:
        """Install a single program using appropriate package manager.

        Args:
            program: Dictionary containing program details

        Returns:
            True if installation successful, False otherwise
        """
        try:
            program_type = program["type"]
            package = program["package"]
            name = program["name"]

            self.log_output.emit(f"Installing {name} using {program_type}...")
            logger.info(f"Installing {name} ({package}) using {program_type}")

            if program_type == "apt":
                command = ["sudo", "apt-get", "install", package, "-y"]
            elif program_type == "snap":
                command = ["sudo", "snap", "install", package]
            elif program_type == "flatpak":
                command = ["sudo", "flatpak", "install", "--system", "--noninteractive", "flathub", package]
            else:
                raise ValueError(f"Unknown installation type: {program_type}")

            result = self.pass_command.emit(command, True)
            success = isinstance(result, int) and result == 0

            if success:
                self.log_output.emit(f"Successfully installed {name}")
                logger.info(f"Successfully installed {name}")
            else:
                self.log_output.emit(f"Failed to install {name}")
                logger.error(f"Failed to install {name}")

            return success

        except Exception as e:
            self.log_output.emit(f"Warning: Failed to install {program['name']}: {str(e)}")
            logger.error(f"Failed to install {program['name']}: {str(e)}")
            return False