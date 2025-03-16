from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import subprocess
import os
from core.installers import ProgramInstaller, PipeWireInstaller


class InstallationManager(QObject):
    """Manages installation processes and communication with installer modules"""

    # Signal definitions for GUI communication
    log_output = pyqtSignal(str, str)  # message, color
    update_progress = pyqtSignal(int, str)  # percentage, status
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_installer = None
        self.current_input_callback = None
        self.program_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.setup_installers()

    def setup_installers(self):
        """Initialize installers"""
        # Setup Program Installer
        self.program_installer = ProgramInstaller()
        self.connect_installer_signals(self.program_installer)

        # Setup PipeWire Installer
        self.pipewire_installer = PipeWireInstaller()
        self.connect_installer_signals(self.pipewire_installer)

    def connect_installer_signals(self, installer):
        """Helper method to connect all signals for an installer"""
        installer.log_output.connect(lambda msg: self.log_output.emit(msg, "white"))
        installer.update_progress.connect(lambda val: self.update_progress.emit(val, None))
        installer.error_occurred.connect(self.error_occurred.emit)
        installer.pass_command.connect(self.execute_command)
        installer.request_input.connect(self.handle_user_input)

    def show_installation_options(self, parent):
        """Show installation options window"""
        from gui.components.installation_window import InstallationWindow

        installation_window = InstallationWindow(parent)
        installation_window.installation_selected.connect(self.start_installation)
        installation_window.setStyleSheet("""
            QDialog {
                background-color: #1a1b1e;
            }
        """)
        installation_window.exec()

    def start_installation(self, program):
        """Start the installation process for selected program"""
        self.update_progress.emit(0, "Initializing")
        self.log_output.emit(f"Initializing {program} installation...", "white")

        if program == "PipeWire":
            self.current_installer = self.pipewire_installer
            self.update_progress.emit(5, "Initializing...")
            # Add a small delay to allow UI to update
            QTimer.singleShot(100, self.pipewire_installer.install_base_system)
        elif program == "Programs":
            self.current_installer = self.program_installer
            self.program_installer.get_options()
        elif program == "OneDrive":
            # Placeholder for OneDrive installation
            self.log_output.emit("OneDrive installation will be implemented in a future update.", "#FFC107")

    def execute_command(self, command, return_output=False):
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

            if stderr:
                self.log_output.emit(f"Warning: {stderr}", "yellow")

            return stdout.strip() if return_output else process.returncode
        except Exception as e:
            self.error_occurred.emit(f"Error executing command: {str(e)}")
            return None if return_output else 1

    def handle_user_input(self, prompt, callback):
        """Handle user input requests from installers"""
        self.log_output.emit(prompt, "white")
        self.current_input_callback = getattr(self.current_installer, callback)

    def process_user_input(self, text):
        """Process user input and pass to the appropriate installer callback"""
        if self.current_input_callback:
            try:
                self.current_input_callback(text)
                return True
            except Exception as e:
                self.error_occurred.emit(f"Error processing input: {str(e)}")
                return False
        return False

    # These methods are now handled by the InstallationWindow class