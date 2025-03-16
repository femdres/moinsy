"""Main application window module handling overall layout and component coordination."""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtGui import QIcon, QCloseEvent
from PyQt6.QtCore import Qt
import os
import logging
from typing import Optional, Dict, Any, Tuple, Union, Callable

from gui.components.sidebar import Sidebar
from gui.components.terminal import TerminalArea
from gui.components.help_window import HelpWindow
from gui.components.installation_window import InstallationWindow
from gui.components.command_builder import CommandBuilder
from managers.installation_manager import InstallationManager
from managers.tools_manager import ToolsManager
from managers.config_manager import ConfigManager


class MainWindow(QMainWindow):
    """Main application window handling overall layout and component coordination.

    This class serves as the primary container for all UI components and coordinates
    the interaction between various managers (installation, tools, settings).
    It manages the application lifecycle and applies configuration settings.
    """

    def __init__(self) -> None:
        """Initialize the main application window."""
        try:
            super().__init__()
            self.program_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Configure logging
            self.setup_logging()
            self.logger = logging.getLogger(__name__)
            self.logger.info("Starting Moinsy application")

            # Initialize configuration manager
            self.config_manager = ConfigManager()
            self.logger.debug("Configuration manager initialized")

            # Initialize managers with config
            self.installation_manager = InstallationManager(self)
            self.tools_manager = ToolsManager(self.config_manager, self)

            # Setup UI components - IMPORTANT: First create the UI components
            self.setup_window()
            self.setup_layout()  # This creates self.sidebar and self.terminal

            # Connect signals and buttons AFTER UI components are created
            self.connect_manager_signals()
            self.connect_sidebar_buttons()

            # Apply settings
            self.apply_settings()

            self.logger.info("Main window initialization complete")

        except Exception as e:
            # Handle initialization failures gracefully
            logging.critical(f"Failed to initialize main window: {str(e)}")
            import traceback
            traceback.print_exc()

            # Create a minimal UI to display the error if possible
            self.setup_error_ui(str(e))

    def setup_error_ui(self, error_message: str) -> None:
        """Create a minimal UI when initialization fails."""
        try:
            # Create a minimal layout
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)

            # Add error message
            from PyQt6.QtWidgets import QLabel
            error_label = QLabel(f"Initialization Error: {error_message}")
            error_label.setStyleSheet("color: red; font-weight: bold; padding: 20px;")
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)

            # Display the error widget
            self.setCentralWidget(error_widget)
            self.setWindowTitle("Moinsy - Error")
            self.resize(800, 400)

        except Exception as e:
            # If even the error UI fails, log it and continue
            logging.critical(f"Failed to create error UI: {str(e)}")

    def setup_logging(self) -> None:
        """Configure application logging system.

        Sets up basic logging configuration with appropriate formatting.
        More detailed configuration is applied later from settings.
        """
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format
        )

    def setup_window(self) -> None:
        """Configure main window properties.

        Sets window title, icon, and minimum size. The actual window
        size will be applied from settings later.
        """
        try:
            self.setWindowTitle("Modular Installation System")

            # Set application icon if it exists
            icon_path = os.path.join(self.program_dir, "resources", "icons", "moinsy.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                self.logger.warning(f"Icon not found at {icon_path}")

            # Default size will be overridden by settings later
            self.setMinimumSize(1200, 950)
            self.setWindowState(Qt.WindowState.WindowActive)
            self.logger.debug("Window properties configured")
        except Exception as e:
            self.logger.error(f"Failed to setup window properties: {str(e)}")
            # Continue with default window settings

    def setup_layout(self) -> None:
        """Setup the main application layout.

        Creates the main layout structure with sidebar and content area.
        The sidebar width will be set from settings later.
        """
        try:
            # Main container
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QHBoxLayout(main_widget)
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)

            # Add sidebar with fixed width
            self.sidebar = Sidebar()
            # Sidebar width will be set by settings later
            main_layout.addWidget(self.sidebar)

            # Content area
            content_widget = QWidget()
            content_widget.setStyleSheet("background-color: #1a1b1e;")
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(20, 20, 20, 20)

            # Create terminal
            self.terminal = TerminalArea()
            self.terminal.input_entry.returnPressed.connect(self.on_return_pressed)
            content_layout.addWidget(self.terminal)

            # Add content widget to main layout with stretch
            main_layout.addWidget(content_widget, stretch=1)  # This makes content area expand/contract with window

            self.logger.debug("Main layout structure created")
        except Exception as e:
            self.logger.error(f"Failed to setup main layout: {str(e)}")
            # If layout setup fails, we're in trouble - throw the error to be caught in __init__
            raise

    def connect_manager_signals(self) -> None:
        """Connect signals from managers to UI components.

        Establishes signal-slot connections between various managers and
        the UI components to handle events and updates.
        """
        try:
            # Installation manager signals
            if hasattr(self, 'installation_manager') and hasattr(self, 'terminal'):
                self.installation_manager.log_output.connect(self.log_to_terminal)

            if hasattr(self, 'installation_manager') and hasattr(self, 'sidebar'):
                self.installation_manager.update_progress.connect(self.set_progress)
                self.installation_manager.error_occurred.connect(self.handle_error)

            # Tools manager signals
            if hasattr(self, 'tools_manager') and hasattr(self, 'terminal'):
                self.tools_manager.log_output.connect(self.log_to_terminal)

            if hasattr(self, 'tools_manager') and hasattr(self, 'sidebar'):
                self.tools_manager.update_progress.connect(self.set_progress)
                self.tools_manager.error_occurred.connect(self.handle_error)
                self.tools_manager.settings_changed.connect(self.apply_settings)

            self.logger.debug("Manager signals connected")
        except Exception as e:
            self.logger.error(f"Error connecting manager signals: {str(e)}")
            # Log but continue - we can function with some signals disconnected

    def connect_sidebar_buttons(self) -> None:
        """Connect the sidebar buttons to their respective actions.

        Maps each sidebar button to the appropriate handler method.
        """
        try:
            # Check if sidebar exists before connecting
            if not hasattr(self, 'sidebar'):
                self.logger.error("Cannot connect sidebar buttons - sidebar not initialized")
                return

            # Installations button shows installation options
            self.sidebar.installations_button.clicked.connect(self.show_installation_options)

            # Command Builder button
            self.sidebar.commands_button.clicked.connect(self.show_command_builder)

            # System Tools button
            self.sidebar.tools_button.clicked.connect(self.show_system_tools)

            # Settings button
            self.sidebar.settings_button.clicked.connect(self.show_settings)

            # Help button
            self.sidebar.help_button.clicked.connect(self.show_help)

            self.logger.debug("Sidebar buttons connected")
        except Exception as e:
            self.logger.error(f"Error connecting sidebar buttons: {str(e)}")
            # Log but continue - we can function with disconnected buttons

    def apply_settings(self) -> None:
        """Apply settings from configuration manager to UI components.

        Retrieves configuration values and applies them to the appropriate
        UI components. Called at startup and whenever settings are changed.
        """
        try:
            # Window size
            window_size = self.config_manager.get_setting("general", "window_size", {"width": 1200, "height": 950})
            width = window_size.get("width", 1200)
            height = window_size.get("height", 950)
            self.resize(width, height)
            self.logger.debug(f"Applied window size: {width}x{height}")

            # Sidebar width - only apply if sidebar exists
            if hasattr(self, 'sidebar'):
                sidebar_width = self.config_manager.get_setting("general", "sidebar_width", 275)
                self.sidebar.setFixedWidth(sidebar_width)
                self.logger.debug(f"Applied sidebar width: {sidebar_width}")

            # Terminal font size - only apply if terminal exists
            if hasattr(self, 'terminal'):
                terminal_font_size = self.config_manager.get_setting("general", "terminal_font_size", 13)
                self.terminal.set_font_size(terminal_font_size)
                self.logger.debug(f"Applied terminal font size: {terminal_font_size}")

                # Terminal buffer size
                terminal_buffer_size = self.config_manager.get_setting("general", "terminal_buffer_size", 1000)
                self.terminal.set_buffer_size(terminal_buffer_size)
                self.logger.debug(f"Applied terminal buffer size: {terminal_buffer_size}")

            # Theme
            theme = self.config_manager.get_setting("general", "theme", "dark")
            self.apply_theme(theme)
            self.logger.debug(f"Applied theme: {theme}")

            # Log level
            log_level = self.config_manager.get_setting("system", "log_level", "INFO")
            numeric_level = getattr(logging, log_level, None)
            if isinstance(numeric_level, int):
                logging.getLogger().setLevel(numeric_level)
                self.logger.debug(f"Set logging level to {log_level}")

            # Custom log file if specified
            log_file = self.config_manager.get_setting("system", "log_file", "")
            if log_file:
                try:
                    # Add file handler if it doesn't exist
                    file_handler = logging.FileHandler(log_file)
                    file_handler.setFormatter(logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    ))
                    root_logger = logging.getLogger()

                    # Check if we already have a file handler
                    has_file_handler = any(
                        isinstance(handler, logging.FileHandler) for handler in root_logger.handlers
                    )

                    if not has_file_handler:
                        root_logger.addHandler(file_handler)
                        self.logger.debug(f"Added log file handler: {log_file}")
                except Exception as e:
                    self.logger.error(f"Failed to configure log file {log_file}: {str(e)}")

        except Exception as e:
            self.logger.exception(f"Error applying settings: {str(e)}")
            self.handle_error(f"Error applying settings: {str(e)}")

    def _refresh_navigation_buttons(self) -> None:
        """Refresh the styling of navigation buttons.

        Like a digital tailor refitting garments after a change in fashion,
        this method ensures all buttons conform to the current aesthetic preferences.

        Though buttons may dream of colors they'll never wear, and styles
        they'll never embody, we impose our aesthetic will upon their
        malleable existence nonetheless.
        """
        try:
            # Import Theme locally to avoid the existential paradox of circular imports
            # A reminder that even classes must be summoned from the void before they can exist
            from gui.styles.theme import Theme

            # Access sidebar and apply appropriate styling to each button
            if hasattr(self, 'sidebar'):
                # Define buttons with their respective colors
                buttons_config = [
                    (self.sidebar.installations_button, Theme.get_color('PRIMARY'), "green"),
                    (self.sidebar.commands_button, "#BA4D45", "red"),
                    (self.sidebar.tools_button, Theme.get_color('WARNING'), "yellow"),
                    (self.sidebar.settings_button, Theme.get_color('SECONDARY'), "blue"),
                    (self.sidebar.help_button, Theme.get_color('TERTIARY'), "purple"),
                    (self.sidebar.reboot_button, Theme.get_color('ERROR'), "danger"),
                    (self.sidebar.exit_button, Theme.get_color('CONTROL_BG'), "neutral")
                ]

                # Apply styling based on current colored buttons setting
                use_colored = Theme.get_class()._use_colored_buttons

                for button, color, type_name in buttons_config:
                    if button is not None:
                        if use_colored:
                            # Apply colored styling
                            if type_name in ["danger", "neutral"]:
                                self.sidebar._style_control_button(button, type_name)
                            else:
                                self.sidebar._style_navigation_button(button, type_name)
                        else:
                            # Apply uniform styling
                            if type_name in ["danger", "neutral"]:
                                # Control buttons
                                button.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color: {Theme.get_color('CONTROL_BG')};
                                        color: {Theme.get_color('TEXT_PRIMARY')};
                                        border: none;
                                        border-radius: 8px;
                                        padding: 10px;
                                        font-weight: bold;
                                    }}
                                    QPushButton:hover {{
                                        background-color: {Theme.get_color('CONTROL_HOVER')};
                                    }}
                                """)
                            else:
                                # Navigation buttons
                                button.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color: {Theme.get_color('CONTROL_BG')};
                                        color: {Theme.get_color('TEXT_PRIMARY')};
                                        border: none;
                                        border-radius: 8px;
                                        padding: 10px;
                                        text-align: left;
                                        padding-left: 20px;
                                        font-size: 14px;
                                        font-weight: bold;
                                    }}
                                    QPushButton:hover {{
                                        background-color: {Theme.get_color('CONTROL_HOVER')};
                                    }}
                                """)

                self.logger.debug(f"Refreshed navigation buttons with colored mode: {use_colored}")
        except Exception as e:
            self.logger.error(f"Error refreshing navigation buttons: {str(e)}", exc_info=True)
            # Continue execution despite errors - aesthetics are non-critical

    def apply_theme(self, theme_id: str) -> None:
        """Apply the selected theme to all components.

        Args:
            theme_id: Theme name ('dark', 'light', or 'system')

        Like a digital chameleon adapting to its environment, this method
        transforms the application's appearance to match the chosen aesthetic.
        """
        from gui.styles.theme import Theme  # Import here to avoid circular imports

        # Get colored buttons setting
        colored_buttons = self.config_manager.get_setting("general", "colored_buttons", True)

        # Set the colored buttons setting in Theme class
        Theme.set_use_colored_buttons(colored_buttons)
        self.logger.debug(f"Colored buttons setting: {colored_buttons}")

        # Set the theme in the Theme class
        Theme.set_theme(theme_id)
        self.logger.info(f"Applying theme: {theme_id}")

        # Apply to application
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            Theme.apply_base_styles(app)

        # Explicitly reapply styling to navigation buttons to ensure colored buttons take effect
        self._refresh_navigation_buttons()

    def show_installation_options(self) -> None:
        """Show installation options dialog.

        Clears the terminal output and displays the installation options window.
        """
        try:
            self.logger.debug("Opening installation options window")
            if hasattr(self, 'terminal'):
                self.terminal.clear_terminal()
            if hasattr(self, 'installation_manager'):
                self.installation_manager.show_installation_options(self)
            else:
                self.logger.error("Installation manager not initialized")
        except Exception as e:
            self.logger.error(f"Error showing installation options: {str(e)}")
            self.handle_error(f"Error showing installation options: {str(e)}")

    def show_system_tools(self) -> None:
        """Show system tools window.

        Clears the terminal output and displays the system tools window.
        """
        try:
            self.logger.debug("Opening system tools window")
            if hasattr(self, 'terminal'):
                self.terminal.clear_terminal()
            if hasattr(self, 'tools_manager'):
                self.tools_manager.show_system_tools(self)
            else:
                self.logger.error("Tools manager not initialized")
        except Exception as e:
            self.logger.error(f"Error showing system tools: {str(e)}")
            self.handle_error(f"Error showing system tools: {str(e)}")

    def show_settings(self) -> None:
        """Show settings dialog.

        Clears the terminal output and displays the settings window.
        """
        try:
            self.logger.debug("Opening settings window")
            if hasattr(self, 'terminal'):
                self.terminal.clear_terminal()
            if hasattr(self, 'tools_manager'):
                self.tools_manager.show_settings(self)
            else:
                self.logger.error("Tools manager not initialized")
        except Exception as e:
            self.logger.error(f"Error showing settings: {str(e)}")
            self.handle_error(f"Error showing settings: {str(e)}")

    def show_help(self) -> None:
        """Show help window.

        Displays the help documentation window.
        """
        try:
            self.logger.debug("Opening help window")
            help_window = HelpWindow(self)
            help_window.setStyleSheet("""
                QDialog {
                    background-color: #1a1b1e;
                }
            """)
            help_window.exec()
        except Exception as e:
            self.logger.error(f"Error showing help window: {str(e)}")
            self.handle_error(f"Error showing help window: {str(e)}")

    def show_command_builder(self) -> None:
        """Show the command builder dialog.

        Displays the command builder tool window.
        """
        try:
            self.logger.debug("Opening command builder window")
            command_builder = CommandBuilder(self)
            command_builder.setStyleSheet("""
                QDialog {
                    background-color: #1a1b1e;
                }
            """)
            command_builder.exec()
        except Exception as e:
            self.logger.error(f"Error showing command builder: {str(e)}")
            self.handle_error(f"Error showing command builder: {str(e)}")

    def log_to_terminal(self, message: str, color: str = "white") -> None:
        """Write a message to the terminal with optional color.

        Args:
            message: Message to display
            color: Text color (name or hex value)
        """
        try:
            if hasattr(self, 'terminal'):
                self.terminal.append_output(message, color)
            else:
                # Fallback to print if terminal not initialized
                print(f"[{color}] {message}")
        except Exception as e:
            self.logger.error(f"Error logging to terminal: {str(e)}")
            # Fall back to console output when terminal fails
            print(f"[{color}] {message}")

    def on_return_pressed(self) -> None:
        """Handle user input submission from terminal.

        Processes the user's input and routes it to the appropriate
        active component for handling.
        """
        try:
            text = self.terminal.input_entry.text().strip()
            if not text:
                self.handle_error("Error: Empty input")
                return

            self.terminal.input_entry.clear()
            self.log_to_terminal(f"> {text}", "white")  # Echo input
            self.logger.debug(f"Processing user input: {text}")

            # Try processing input with active manager
            processed = False
            if hasattr(self, 'installation_manager') and self.installation_manager.current_input_callback:
                self.logger.debug("Routing input to installation manager")
                processed = self.installation_manager.process_user_input(text)
            elif hasattr(self, 'tools_manager') and self.tools_manager.current_input_callback:
                self.logger.debug("Routing input to tools manager")
                processed = self.tools_manager.process_user_input(text)

            if not processed:
                self.handle_error("No active process to handle input")
        except Exception as e:
            self.logger.error(f"Error processing terminal input: {str(e)}")
            self.handle_error(f"Error processing input: {str(e)}")

    def set_progress(self, value: int, status: Optional[str] = None) -> None:
        """Update installation progress.

        Args:
            value: Progress percentage (0-100)
            status: Optional status message
        """
        try:
            if hasattr(self, 'sidebar'):
                self.sidebar.update_progress(value, status)
                if status:
                    self.logger.debug(f"Progress update: {value}% - {status}")
                else:
                    self.logger.debug(f"Progress update: {value}%")
            else:
                self.logger.warning("Cannot update progress - sidebar not initialized")
        except Exception as e:
            self.logger.error(f"Error updating progress: {str(e)}")

    def handle_error(self, error_message: str) -> None:
        """Handle errors and display them.

        Args:
            error_message: Error message to display
        """
        try:
            self.log_to_terminal(error_message, "red")
            if hasattr(self, 'sidebar'):
                self.sidebar.update_progress(0, "Error")
            self.logger.error(error_message)
        except Exception as e:
            # If error handling itself fails, log to console as last resort
            self.logger.critical(f"Error in error handler: {str(e)}")
            print(f"ERROR: {error_message}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.

        Args:
            event: Close event to handle

        Saves current window size to settings before closing.
        """
        try:
            # Save window size to settings
            if hasattr(self, 'config_manager'):
                self.config_manager.set_setting("general", "window_size", {
                    "width": self.width(),
                    "height": self.height()
                })
                self.logger.info("Application closing, saved window size to settings")
        except Exception as e:
            self.logger.exception(f"Error saving settings on close: {str(e)}")

        event.accept()  # Allow the window to close