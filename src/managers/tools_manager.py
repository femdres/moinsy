from PyQt6.QtCore import QObject, pyqtSignal
import subprocess
import logging
from typing import Optional, Dict, Any, List

from managers.config_manager import ConfigManager
from gui.components.settings.settings_window import SettingsWindow


class ToolsManager(QObject):
    """Manages system tools and their functionality"""

    # Signal definitions for GUI communication
    log_output = pyqtSignal(str, str)  # message, color
    update_progress = pyqtSignal(int, str)  # percentage, status
    error_occurred = pyqtSignal(str)
    settings_changed = pyqtSignal()  # Emitted when settings are changed

    def __init__(self, config_manager: ConfigManager, parent: Optional[QObject] = None):
        """Initialize the tools manager.

        Args:
            config_manager: The application configuration manager
            parent: Parent object
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.current_tool = None
        self.current_input_callback = None

    def show_system_tools(self, parent):
        """Show the system tools window"""
        from gui.components.system_tools import SystemToolsWindow

        tools_window = SystemToolsWindow(parent)
        tools_window.setStyleSheet("""
            QDialog {
                background-color: #1a1b1e;
            }
        """)
        tools_window.exec()

    def show_settings(self, parent):
        """Show settings dialog

        Args:
            parent: Parent widget for the settings window
        """
        self.logger.debug("Opening settings window")
        settings_window = SettingsWindow(self.config_manager, parent)

        # Connect settings_saved signal
        settings_window.settings_saved.connect(self.on_settings_saved)

        settings_window.setStyleSheet("""
            QDialog {
                background-color: #1a1b1e;
            }
        """)

        settings_window.exec()

    def on_settings_saved(self):
        """Handle when settings are saved in the settings window"""
        self.logger.info("Settings have been updated")
        self.log_output.emit("Settings have been updated successfully.", "#4CAF50")

        # Notify the application that settings have changed
        self.settings_changed.emit()

    def start_system_update(self):
        """Initialize and start the system update process"""
        from core.tools.update_tool import SystemUpdater

        self.update_progress.emit(0, "Initializing")

        # Get settings for updater
        check_on_startup = self.config_manager.get_setting("tools", "update_check_on_startup", True)

        # Initialize updater
        self.system_updater = SystemUpdater()

        # Connect signals
        self.system_updater.log_output.connect(lambda msg: self.log_output.emit(msg, "white"))
        self.system_updater.update_progress.connect(lambda val: self.update_progress.emit(val, None))
        self.system_updater.error_occurred.connect(self.error_occurred.emit)

        # Start update process
        self.current_tool = self.system_updater
        self.log_output.emit("Starting system update...", "white")
        self.system_updater.start_update()

    def start_service_manager(self):
        """Initialize and start the service manager"""
        from core.tools.service_manager import ServiceManager

        self.update_progress.emit(0, "Initializing")

        # Get settings
        show_all_services = self.config_manager.get_setting("tools", "service_manager_show_all", False)

        # Initialize service manager
        self.service_manager = ServiceManager()

        # Apply settings
        self.service_manager.set_show_all_services(show_all_services)

        # Connect signals
        self.service_manager.log_output.connect(lambda msg: self.log_output.emit(msg, "white"))
        self.service_manager.update_progress.connect(lambda val: self.update_progress.emit(val, None))
        self.service_manager.error_occurred.connect(self.error_occurred.emit)
        self.service_manager.request_input.connect(self.handle_user_input)

        # Start service listing
        self.current_tool = self.service_manager
        self.log_output.emit("Starting Service Manager...", "white")
        self.service_manager.list_services()

    def handle_user_input(self, prompt, callback):
        """Handle user input requests"""
        self.log_output.emit(prompt, "white")

        if hasattr(self.current_tool, callback):
            self.current_input_callback = getattr(self.current_tool, callback)
        else:
            self.error_occurred.emit(f"Error: Callback '{callback}' not found")
            self.current_input_callback = None

    def process_user_input(self, text):
        """Process user input and pass to the appropriate tool callback"""
        if self.current_input_callback:
            try:
                self.current_input_callback(text)
                return True
            except Exception as e:
                self.logger.exception(f"Error processing input: {str(e)}")
                self.error_occurred.emit(f"Error processing input: {str(e)}")
                return False
        return False