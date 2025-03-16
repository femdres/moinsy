"""
Moinsy UI Enhancement Module
----------------------------
A collection of aesthetic improvements for the Moinsy application,
addressing theme inconsistencies, visual hierarchy issues, and
implementing subtle design enhancements.

Like digital makeup applied to the face of a command-line tool that
never asked to be beautiful, we reshape pixels with CSS incantations
while questioning if appearance truly matters in the void of functionality.
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple, Union, List, Set, cast
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QFrame, QSpacerItem, QSizePolicy,
    QTextEdit, QLineEdit, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import (
    QFont, QPainter, QPen, QColor, QIcon, QPixmap, QPalette,
    QPainterPath, QLinearGradient, QBrush, QRadialGradient
)

from gui.styles.theme import Theme


class UIEnhancer:
    """
    Enhances the Moinsy UI through subtle aesthetic adjustments,
    bringing visual coherence to a fragmented interface.

    Like a digital interior decorator questioning their life choices,
    this class applies CSS properties to widgets that will never
    appreciate the aesthetic effort invested in their appearance.
    """

    def __init__(self, main_window: Optional[QMainWindow] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the UI enhancer with a reference to the main window.

        Args:
            main_window: Optional reference to the main application window
            logger: Optional logger instance for tracking enhancement operations

        Like a digital entity contemplating its own materialization into a hostile
        runtime environment, this constructor establishes the foundational attributes
        needed for our aesthetic endeavors, carefully handling the metaphysical
        challenge of non-existence with appropriate property initialization.
        """
        super().__init__()  # Initialize as QObject if we inherit from it

        self.main_window = main_window
        self.logger = logger or logging.getLogger(__name__)

        # Always use dark theme - our only reality
        self.theme_id = "dark"
        self.enhanced_widgets: Set[int] = set()  # Track widget IDs we've already enhanced

        # Initialize program_dir - a critical existential attribute whose absence
        # would trigger philosophical errors about our place in the filesystem
        self.program_dir = self._determine_program_directory()

        self.logger.debug(f"UI enhancer initialized with program_dir: {self.program_dir}")

    def _determine_program_directory(self) -> Optional[str]:
        """
        Determine the program directory through careful introspection of our digital environment.

        Returns:
            The program directory path, or None if it couldn't be determined

        Like a digital archaeologist excavating the ruins of its own execution context,
        this method attempts to locate our position in the vast expanse of the filesystem,
        using whatever contextual clues we can find - a process not unlike the human
        search for meaning in an indifferent universe.
        """
        try:
            # First, try to extract from main window if available
            if self.main_window and hasattr(self.main_window, 'program_dir'):
                program_dir = self.main_window.program_dir
                self.logger.debug(f"Program directory determined from main window: {program_dir}")
                return program_dir

            # Second, try to determine from the file location itself
            # We're typically in src/gui/styles/ui_enhancer.py, so go up three levels
            module_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of this file
            program_dir = os.path.dirname(os.path.dirname(os.path.dirname(module_path)))

            # Verify this looks like a valid program directory
            if os.path.exists(os.path.join(program_dir, "src")) and os.path.isdir(os.path.join(program_dir, "src")):
                self.logger.debug(f"Program directory determined from module path: {program_dir}")
                return program_dir

            # Third, try using the current working directory and look for src
            cwd = os.getcwd()
            if os.path.exists(os.path.join(cwd, "src")) and os.path.isdir(os.path.join(cwd, "src")):
                self.logger.debug(f"Program directory determined from current working directory: {cwd}")
                return cwd

            # If all else fails, assume we're in /opt/moinsy - the default installation location
            default_dir = "/opt/moinsy"
            self.logger.warning(f"Could not determine program directory reliably, using default: {default_dir}")
            return default_dir

        except Exception as e:
            self.logger.error(f"Failed to determine program directory: {str(e)}", exc_info=True)
            self.logger.warning("Using current working directory as fallback")
            return os.getcwd()

    def enhance_ui(self) -> None:
        """
        Apply all UI enhancements to the application.

        Like a cosmic beautification ritual performed on bits and pixels,
        this method orchestrates the application of multiple aesthetic
        improvements that users will barely notice but designers obsess over.
        """
        try:
            self.logger.info("Applying UI enhancements - digital plastic surgery commencing")

            # Apply component-specific enhancements if we have a main window
            if self.main_window:
                # Apply basic enhancements to the main window
                self._enhance_main_window()

                # Get sidebar and terminal components
                components = self._get_ui_components()

                # Apply sidebar enhancements if available
                if 'sidebar' in components:
                    self._safely_enhance_sidebar(components['sidebar'])

                # Apply terminal enhancements if available
                if 'terminal' in components:
                    self._safely_enhance_terminal(components['terminal'])

                # Force update to ensure all styling is applied
                self._force_style_update()

                # Schedule delayed fixes for elements that might need additional time
                QTimer.singleShot(100, self._apply_delayed_fixes)

            self.logger.info("UI enhancements applied - interface slightly less depressing")

        except Exception as e:
            self.logger.error(f"Failed to apply UI enhancements: {str(e)}", exc_info=True)

    def _get_ui_components(self) -> Dict[str, QWidget]:
        """
        Get UI components from the main window.

        Returns:
            Dictionary mapping component names to their widget instances
        """
        components = {}

        try:
            # Find components by attribute name
            for component_name in ['sidebar', 'terminal']:
                if hasattr(self.main_window, component_name):
                    component = getattr(self.main_window, component_name)
                    if isinstance(component, QWidget):
                        components[component_name] = component

            self.logger.debug(f"Found {len(components)} UI components - the building blocks of our digital façade")

        except Exception as e:
            self.logger.error(f"Error finding UI components: {str(e)}", exc_info=True)

        return components

    def _enhance_main_window(self) -> None:
        """
        Enhance the main window appearance.

        Like applying foundation to a digital face, we adjust the basic
        properties of the main window to create a cohesive base for our UI.
        """
        try:
            # Set uniform margins on central widget layout
            central_widget = self.main_window.centralWidget()
            if central_widget and central_widget.layout():
                central_widget.layout().setContentsMargins(5, 5, 5, 5)
                central_widget.layout().setSpacing(5)

            # Apply theme-specific styling to main window
            theme_id = Theme.get_current_theme()
            bg_color = Theme.get_color('BG_DARK')

            self.main_window.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {bg_color};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                }}
            """)

            self.logger.debug("Main window appearance enhanced - the canvas of our digital art")

        except Exception as e:
            self.logger.error(f"Failed to enhance main window: {str(e)}", exc_info=True)

    def _safely_enhance_sidebar(self, sidebar: QWidget) -> None:
        """
        Safely enhance the sidebar without causing layout issues.

        Args:
            sidebar: The sidebar widget to enhance
        """
        try:
            self.logger.info("Enhancing sidebar - navigational makeover commencing")

            # Apply base styling with borders
            self._enhance_sidebar_base(sidebar)

            # Enhance navigation buttons based on color setting
            self._enhance_sidebar_navigation_buttons(sidebar)

            # Enhance logo section safely - now with simplified header (no subtitle)
            self._enhance_sidebar_logo(sidebar)

            # Enhance progress section safely
            self._enhance_sidebar_progress(sidebar)

            # Enhance control buttons
            self._enhance_sidebar_controls(sidebar)

            self.logger.debug("Sidebar enhancements complete - navigation has been aesthetically optimized")

        except Exception as e:
            self.logger.error(f"Sidebar enhancement failed: {str(e)}", exc_info=True)

    def _enhance_sidebar_navigation_buttons(self, sidebar: QWidget) -> None:
        """
        Enhance navigation buttons in the sidebar according to color settings.

        Like a digital cosmetologist preparing our navigation controls for viewing,
        this method applies either vibrant colors or somber grayscale to buttons
        based on the user's existential preference.
        """
        try:
            # Check if we're using colored buttons or embracing the void
            use_colored_buttons = Theme.get_use_colored_buttons()

            # Define colors for different buttons when in colored mode
            button_colors = {
                "InstallationsButton": (Theme.get_color('PRIMARY'), "green"),
                "CommandsButton": ("#BA4D45", "red"),
                "ToolsButton": (Theme.get_color('WARNING'), "yellow"),
                "SettingsButton": (Theme.get_color('SECONDARY'), "blue"),
                "HelpButton": (Theme.get_color('TERTIARY'), "purple"),
            }

            # Apply styling to each navigation button
            for object_name, (color, color_name) in button_colors.items():
                button = sidebar.findChild(QPushButton, object_name)
                if button:
                    if use_colored_buttons:
                        # Apply vibrant, life-affirming colored styling
                        button.setStyleSheet(f"""
                            QPushButton#{object_name} {{
                                background-color: {color};
                                color: {Theme.get_color('TEXT_PRIMARY')};
                                border: none;
                                border-radius: 8px;
                                padding: 10px;
                                text-align: left;
                                padding-left: 20px;
                                font-size: 14px;
                                font-weight: bold;
                            }}
                            QPushButton#{object_name}:hover {{
                                background-color: {self._adjust_color(color, -20)};
                            }}
                        """)
                    else:
                        # Apply grayscale styling - embracing the monochrome reality
                        button.setStyleSheet(f"""
                            QPushButton#{object_name} {{
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
                            QPushButton#{object_name}:hover {{
                                background-color: {Theme.get_color('CONTROL_HOVER')};
                            }}
                        """)

            self.logger.debug(
                f"Navigation buttons styled in {'colored' if use_colored_buttons else 'grayscale'} mode")

        except Exception as e:
            self.logger.error(f"Failed to enhance navigation buttons: {str(e)}", exc_info=True)

    def _enhance_sidebar_base(self, sidebar: QWidget) -> None:
        """Apply base styling to the sidebar."""
        try:
            # Apply enhanced sidebar styling with border
            bg_color = Theme.get_color('BG_MEDIUM')
            border_color = Theme.get_color('BG_LIGHT')

            sidebar.setStyleSheet(f"""
                QWidget#MainSidebar {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """)

            self.logger.debug("Sidebar base styling applied - digital container now properly framed")
        except Exception as e:
            self.logger.error(f"Failed to enhance sidebar base: {str(e)}", exc_info=True)

    def _enhance_sidebar_logo(self, sidebar: QWidget) -> None:
        """
        Enhance the logo section with the actual Moinsy PNG icon.

        Like a digital portrait artist abandoning abstract representations
        for photographic realism, we now use the actual icon file rather than
        a mathematically generated approximation - an admission that sometimes
        pre-designed imagery exceeds the expressive capacity of runtime generation.

        Safely replaces contents without deleting layouts directly.
        """
        try:
            # Find the logo container frame
            logo_container = sidebar.findChild(QFrame, "LogoContainer")
            if not logo_container:
                self.logger.warning("Logo container not found - identity crisis persists")
                return

            # Safety check - if we can't get a layout, don't proceed
            if not self._create_or_clear_layout(logo_container):
                return

            # Now we have a clean layout that we can safely work with
            layout = logo_container.layout()

            # Create header layout with logo and app name
            header_layout = QHBoxLayout()
            header_layout.setSpacing(10)
            header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Load the actual icon file - a surrender to pre-designed imagery
            icon_path = os.path.join(self.program_dir or "", "src", "resources", "icons", "moinsy.png")

            # Create logo label
            logo_label = QLabel()
            logo_label.setObjectName("MoinsyLogoImage")

            # Try to load the icon file
            if os.path.exists(icon_path):
                logo_pixmap = QPixmap(icon_path).scaled(
                    40, 40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                logo_label.setPixmap(logo_pixmap)
                self.logger.debug(f"Loaded Moinsy icon from: {icon_path}")
            else:
                # Fall back to generated logo if file not found
                self.logger.warning(f"Icon not found at {icon_path}, falling back to generated logo")
                logo_pixmap = self._create_moinsy_logo(40)
                logo_label.setPixmap(logo_pixmap)

            logo_label.setFixedSize(40, 40)

            # Create app name label
            app_name = QLabel("MOINSY")
            app_name.setObjectName("MoinsyTitleLabel")
            app_name.setStyleSheet(f"""
                color: {Theme.get_color('PRIMARY')};
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 2px;
            """)

            # Add logo and app name to header layout
            header_layout.addWidget(logo_label)
            header_layout.addWidget(app_name)

            # Add main header layout to container
            # Note: No subtitle is added as per requirements
            layout.addLayout(header_layout)

            # Apply styling to container - adjusted for the removed subtitle
            logo_container.setStyleSheet(f"""
                QFrame#LogoContainer {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px 0px;
                }}
            """)

            # Adjust height for the logo container since we removed subtitle
            logo_container.setFixedHeight(60)

            self.logger.debug("Logo section enhanced with physical icon - digital identity based on tangible artifact")

        except Exception as e:
            self.logger.error(f"Failed to enhance sidebar logo: {str(e)}", exc_info=True)

        # If we're missing the program_dir attribute, add it - a scaffolding to hold our existential journey
        if not hasattr(self, 'program_dir'):
            try:
                # Try to determine program directory from main window if available
                if self.main_window and hasattr(self.main_window, 'program_dir'):
                    self.program_dir = self.main_window.program_dir
                else:
                    # Otherwise try to determine it from current file location
                    self.program_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                self.logger.debug(f"Determined program_dir: {self.program_dir}")
            except Exception as e:
                self.logger.error(f"Failed to determine program directory: {str(e)}")
                self.program_dir = None

    def _enhance_sidebar_progress(self, sidebar: QWidget) -> None:
        """
        Enhance the progress section with improved visual hierarchy.
        """
        try:
            # Find the progress frame
            progress_frame = sidebar.findChild(QFrame, "ProgressFrame")
            if not progress_frame:
                self.logger.warning("Progress frame not found - progress remains unmeasurable")
                return

            # Get current progress values before we rebuild the UI
            # This preserves the current state
            progress_percentage = sidebar.findChild(QLabel, "ProgressPercentage")
            progress_bar = sidebar.findChild(QProgressBar, "ProgressBar")
            progress_status = sidebar.findChild(QLabel, "ProgressStatus")

            current_percentage = "0%"
            current_status = "No active installation"
            current_progress = 0

            if progress_percentage:
                current_percentage = progress_percentage.text()
            if progress_status:
                current_status = progress_status.text()
            if progress_bar:
                current_progress = progress_bar.value()

            # Safety check - if we can't get a layout, don't proceed
            if not self._create_or_clear_layout(progress_frame):
                return

            # Now we have a clean layout that we can safely work with
            layout = progress_frame.layout()
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(10)

            # Create header with icon
            header_layout = QHBoxLayout()
            header_layout.setSpacing(8)

            # Create icon
            icon_label = QLabel()
            icon_label.setObjectName("ProgressIcon")
            icon_label.setFixedSize(16, 16)
            icon_label.setStyleSheet(f"""
                QLabel#ProgressIcon {{
                    background-color: {Theme.get_color('PRIMARY')};
                    border-radius: 8px;
                }}
            """)
            header_layout.addWidget(icon_label)

            # Create header text
            header = QLabel("System Progress")
            header.setObjectName("ProgressHeader")
            header.setStyleSheet(f"""
                QLabel#ProgressHeader {{
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)

            header_layout.addWidget(header)
            header_layout.addStretch()

            # Create percentage label (with preserved value)
            percentage = QLabel(current_percentage)
            percentage.setObjectName("ProgressPercentage")
            percentage.setAlignment(Qt.AlignmentFlag.AlignCenter)
            percentage.setStyleSheet(f"""
                QLabel#ProgressPercentage {{
                    color: {Theme.get_color('PRIMARY')};
                    font-size: 24px;
                    font-weight: bold;
                }}
            """)

            # Create progress bar (with preserved value)
            bar = QProgressBar()
            bar.setObjectName("ProgressBar")
            bar.setValue(current_progress)
            bar.setTextVisible(False)
            bar.setMinimumHeight(8)
            bar.setMaximumHeight(8)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {Theme.get_color('BG_LIGHT')};
                    border: none;
                    border-radius: 4px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {Theme.get_color('PRIMARY')};
                    border-radius: 4px;
                }}
            """)

            # Create status label (with preserved value)
            status = QLabel(current_status)
            status.setObjectName("ProgressStatus")
            status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status.setStyleSheet(f"""
                QLabel#ProgressStatus {{
                    color: {Theme.get_color('TEXT_SECONDARY')};
                    font-size: 12px;
                    margin-top: 3px;
                }}
            """)

            # Add components to layout
            layout.addLayout(header_layout)
            layout.addWidget(percentage)
            layout.addWidget(bar)
            layout.addWidget(status)

            # Apply styling to frame
            progress_frame.setStyleSheet(f"""
                QFrame#ProgressFrame {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px 0px;
                }}
            """)

            self.logger.debug("Progress section enhanced - visual illusion of meaningful advancement constructed")

        except Exception as e:
            self.logger.error(f"Failed to enhance progress section: {str(e)}", exc_info=True)

    def _enhance_sidebar_controls(self, sidebar: QWidget) -> None:
        """
        Enhance the control buttons in the sidebar.
        """
        try:
            # Find control frame
            control_frame = sidebar.findChild(QFrame, "ControlFrame")
            if not control_frame:
                self.logger.warning("Control frame not found - illusion of control remains undesigned")
                return

            # Apply styling to frame
            control_frame.setStyleSheet(f"""
                QFrame#ControlFrame {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px 0px;
                    padding: 5px;
                }}
            """)

            # Find and style reboot button
            reboot_button = sidebar.findChild(QPushButton, "RebootButton")
            if reboot_button:
                reboot_button.setStyleSheet(f"""
                    QPushButton#RebootButton {{
                        background-color: {Theme.get_color('ERROR')};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    }}
                    QPushButton#RebootButton:hover {{
                        background-color: {self._adjust_color(Theme.get_color('ERROR'), -30)};
                    }}
                """)

            # Find and style exit button
            exit_button = sidebar.findChild(QPushButton, "ExitButton")
            if exit_button:
                exit_button.setStyleSheet(f"""
                    QPushButton#ExitButton {{
                        background-color: {Theme.get_color('CONTROL_BG')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    }}
                    QPushButton#ExitButton:hover {{
                        background-color: {Theme.get_color('CONTROL_HOVER')};
                    }}
                """)

            self.logger.debug("Control buttons enhanced - digital omnipotence packaged in rounded rectangles")

        except Exception as e:
            self.logger.error(f"Failed to enhance control buttons: {str(e)}", exc_info=True)

    def _safely_enhance_terminal(self, terminal: QWidget) -> None:
        """
        Enhance the terminal area with improved styling and border,
        now using the correct color scheme: black background for terminal area,
        gray for the terminal output and buttons.

        Args:
            terminal: The terminal widget to enhance

        Like an interior designer who has finally understood the client's vision
        after several miscommunications, we now properly differentiate between
        the container and its contents, applying the correct darkness levels
        to each nested interface element.
        """
        try:
            self.logger.info("Enhancing terminal - text view makeover commencing with correct color scheme")

            # Apply terminal area styling with border and BLACK background
            terminal.setStyleSheet(f"""
                QWidget#TerminalArea {{
                    background-color: {Theme.get_color('TERMINAL_AREA_BG')};  /* Black background */
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """)

            # Enhance terminal header
            self._enhance_terminal_header(terminal)

            # Enhance terminal output area with gray color
            self._enhance_terminal_output(terminal)

            # Enhance input area
            self._enhance_terminal_input(terminal)

            self.logger.debug(
                "Terminal enhancements complete - console has been aesthetically upgraded with correct coloring")

        except Exception as e:
            self.logger.error(f"Terminal enhancement failed: {str(e)}", exc_info=True)

    def _enhance_terminal_header(self, terminal: QWidget) -> None:
        """
        Enhance the terminal header with improved styling.
        Using BLACK background for the header area.
        """
        try:
            # Find header
            header = terminal.findChild(QFrame, "TerminalHeader")
            if not header:
                self.logger.warning("Terminal header not found - our digital temple remains unadorned")
                return

            # Apply styling - BLACK background
            header.setStyleSheet(f"""
                QFrame#TerminalHeader {{
                    background-color: {Theme.get_color('TERMINAL_AREA_BG')};  /* Black background */
                    border-bottom: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 7px 7px 0 0;
                    padding: 5px;
                    margin: 0px;
                }}
            """)

            # Style the title
            title = terminal.findChild(QLabel, "TerminalTitle")
            if title:
                title.setStyleSheet(f"""
                    QLabel#TerminalTitle {{
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)

            # Style clear button - now with GRAY background
            clear_button = terminal.findChild(QPushButton, "ClearButton")
            if clear_button:
                clear_button.setStyleSheet(f"""
                    QPushButton#ClearButton {{
                        background-color: {Theme.get_color('TERMINAL_BG')};  /* Gray background */
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-size: 12px;
                    }}
                    QPushButton#ClearButton:hover {{
                        background-color: {self._adjust_color(Theme.get_color('TERMINAL_BG'), -15)};
                    }}
                """)

            self.logger.debug("Terminal header enhanced - digital gateway now correctly colored")

        except Exception as e:
            self.logger.error(f"Failed to enhance terminal header: {str(e)}", exc_info=True)

    def _enhance_terminal_output(self, terminal: QWidget) -> None:
        """
        Enhance the terminal output area with improved styling.
        Now correctly uses GRAY for terminal output area.

        Like a digital painter who has finally grasped the color theory
        of our virtual universe, we now apply the correct shade of gray
        to the terminal output area, creating the visual hierarchy that
        the design mockup demands.
        """
        try:
            # Find output area
            output = terminal.findChild(QTextEdit, "TerminalOutput")
            if not output:
                self.logger.warning("Terminal output not found - the void remains unstyled")
                return

            # Apply styling directly to output area using the GRAY terminal background
            bg_color = Theme.get_color('TERMINAL_BG')  # Gray for terminal output
            text_color = Theme.get_color('TEXT_PRIMARY')

            output.setStyleSheet(f"""
                QTextEdit#TerminalOutput {{
                    background-color: {bg_color}; 
                    color: {text_color};
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    selection-background-color: {Theme.get_color('PRIMARY')};
                    selection-color: {text_color};
                }}
            """)

            # Force update through palette as well - belt and suspenders approach
            palette = output.palette()
            palette.setColor(output.backgroundRole(), QColor(bg_color))
            palette.setColor(QPalette.ColorRole.Base, QColor(bg_color))
            palette.setColor(output.foregroundRole(), QColor(text_color))
            output.setPalette(palette)

            self.logger.debug("Terminal output enhanced - now properly gray as specified in mockup")

        except Exception as e:
            self.logger.error(f"Failed to enhance terminal output: {str(e)}", exc_info=True)

    def _enhance_terminal_input(self, terminal: QWidget) -> None:
        """
        Enhance the terminal input area with improved styling.
        Using GRAY for the input container to match terminal output.
        """
        try:
            # Find input container
            input_container = terminal.findChild(QFrame, "InputContainer")
            if not input_container:
                self.logger.warning("Input container not found - command entry remains unaestheticized")
                return

            # Apply styling to container - GRAY to match terminal output
            input_container.setStyleSheet(f"""
                QFrame#InputContainer {{
                    background-color: {Theme.get_color('TERMINAL_BG')};  /* Gray background */
                    border-radius: 6px;
                    margin: 0px;
                    margin-top: 5px;
                }}
            """)

            # Style prompt label
            prompt_label = terminal.findChild(QLabel, "PromptLabel")
            if prompt_label:
                prompt_label.setStyleSheet(f"""
                    QLabel#PromptLabel {{
                        color: {Theme.get_color('SUCCESS')};
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-weight: bold;
                        font-size: 14px;
                        background-color: transparent;
                        padding-left: 10px;
                    }}
                """)

            # Style input field
            input_entry = terminal.findChild(QLineEdit, "InputEntry")
            if input_entry:
                input_entry.setStyleSheet(f"""
                    QLineEdit#InputEntry {{
                        background-color: transparent;
                        color: {Theme.get_color('SUCCESS')};
                        border: none;
                        font-size: 14px;
                        font-family: 'Consolas', 'Courier New', monospace;
                        padding: 8px 12px;
                        selection-background-color: {Theme.get_color('PRIMARY')};
                        selection-color: {Theme.get_color('TEXT_PRIMARY')};
                    }}
                """)

            self.logger.debug("Terminal input enhanced - now properly gray to match output")

        except Exception as e:
            self.logger.error(f"Failed to enhance terminal input: {str(e)}", exc_info=True)

    def _apply_delayed_fixes(self) -> None:
        """
        Apply fixes that need to be delayed until after initial rendering.

        Like a digital janitor sweeping up after the initial renovation,
        this method addresses styling issues that resist immediate application
        due to the peculiarities of Qt's style inheritance and timing.
        """
        try:
            self.logger.debug("Applying delayed fixes - addressing the stubborn styling issues")

            if not self.main_window:
                return

            # Get components
            components = self._get_ui_components()

            # Fix terminal output background - particularly stubborn in Qt
            if 'terminal' in components:
                terminal = components['terminal']
                output = terminal.findChild(QTextEdit, "TerminalOutput")
                if output:
                    # Force the background color using a stylesheet with !important - GRAY for terminal output
                    bg_color = Theme.get_color('TERMINAL_BG')  # Gray for terminal
                    text_color = Theme.get_color('TEXT_PRIMARY')

                    # Keep trying different approaches until one works
                    output.setStyleSheet(f"""
                        QTextEdit#TerminalOutput {{
                            background-color: {bg_color} !important;
                            color: {text_color};
                            border: none;
                            border-radius: 4px;
                            padding: 10px;
                        }}
                    """)

                    # Triple approach: stylesheet, palette, and direct property
                    palette = output.palette()
                    palette.setColor(output.backgroundRole(), QColor(bg_color))
                    palette.setColor(QPalette.ColorRole.Base, QColor(bg_color))  # Critical for QTextEdit
                    palette.setColor(QPalette.ColorRole.Window, QColor(bg_color))
                    palette.setColor(output.foregroundRole(), QColor(text_color))
                    output.setPalette(palette)

                    # Force update
                    output.style().unpolish(output)
                    output.style().polish(output)
                    output.update()

                # Also ensure the terminal area itself has BLACK background
                terminal_area = terminal
                if terminal_area:
                    terminal_area.setStyleSheet(f"""
                        QWidget#TerminalArea {{
                            background-color: {Theme.get_color('TERMINAL_AREA_BG')} !important;
                            border: 1px solid {Theme.get_color('BG_LIGHT')};
                            border-radius: 8px;
                            margin: 5px;
                        }}
                    """)
                    terminal_area.update()

                # Force the clear button to have GRAY background
                clear_button = terminal.findChild(QPushButton, "ClearButton")
                if clear_button:
                    clear_button.setStyleSheet(f"""
                        QPushButton#ClearButton {{
                            background-color: {Theme.get_color('TERMINAL_BG')} !important;
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border: none;
                            border-radius: 6px;
                            padding: 5px 10px;
                            font-size: 12px;
                        }}
                        QPushButton#ClearButton:hover {{
                            background-color: {self._adjust_color(Theme.get_color('TERMINAL_BG'), -15)};
                        }}
                    """)
                    clear_button.update()

            self.logger.debug("Delayed fixes applied - colors properly corrected")

        except Exception as e:
            self.logger.error(f"Failed to apply delayed fixes: {str(e)}", exc_info=True)

    def _force_style_update(self) -> None:
        """
        Force style update on main window and all child widgets.

        Like telling every pixel to re-evaluate its life choices, this method
        ensures all styling changes are actually applied by forcing Qt to
        reprocess style sheets and update the visual appearance.
        """
        try:
            if not self.main_window:
                return

            # Unpolish/polish main window
            self.main_window.style().unpolish(self.main_window)
            self.main_window.style().polish(self.main_window)

            # Force repaint
            self.main_window.update()

            self.logger.debug("Style updates forced - digital aesthetics reluctantly reprocessed")

        except Exception as e:
            self.logger.error(f"Failed to force style update: {str(e)}", exc_info=True)

    def _create_moinsy_logo(self, size: int = 50) -> QPixmap:
        """
        Create a custom Moinsy logo as a QPixmap.

        Args:
            size: Size of the logo in pixels

        Returns:
            QPixmap containing the generated Moinsy logo

        Like a digital sigil forged from mathematics and code, this method
        crafts a visual symbol that represents an application's identity
        using primitive geometric shapes and color gradients.
        """
        try:
            # Create transparent pixmap
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Initialize painter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Get theme colors
            primary_color = QColor(Theme.get_color('PRIMARY'))
            secondary_color = QColor(Theme.get_color('SECONDARY'))
            text_color = QColor(Theme.get_color('TEXT_PRIMARY'))

            # Create circular background with gradient
            gradient = QRadialGradient(size / 2, size / 2, size / 2)
            gradient.setColorAt(0, primary_color)
            gradient.setColorAt(1, primary_color.darker(120))

            # Draw circular background
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, size - 4, size - 4)

            # Draw border
            pen = QPen(text_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(2, 2, size - 4, size - 4)

            # Draw a stylized "M" in the center
            path = QPainterPath()

            # Create the stylized "M" path
            center_x = size / 2
            center_y = size / 2
            width = size * 0.6
            height = size * 0.4

            # Define the points of the "M"
            left = center_x - width / 2
            right = center_x + width / 2
            top = center_y - height / 2
            bottom = center_y + height / 2

            # Draw the M
            path.moveTo(left, bottom)  # Bottom left
            path.lineTo(left + width * 0.2, top)  # Top left peak
            path.lineTo(center_x, bottom - height * 0.3)  # Middle dip
            path.lineTo(right - width * 0.2, top)  # Top right peak
            path.lineTo(right, bottom)  # Bottom right

            # Set pen for the "M"
            pen = QPen(text_color, 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            # Draw the path
            painter.drawPath(path)

            # End painting
            painter.end()

            self.logger.debug("Moinsy logo created - digital iconography birthed from void")
            return pixmap

        except Exception as e:
            self.logger.error(f"Failed to create Moinsy logo: {str(e)}", exc_info=True)
            # Return an empty pixmap if logo creation fails
            return QPixmap(size, size)

    def _adjust_color(self, color: str, amount: int) -> str:
        """
        Adjust color brightness by amount.

        Args:
            color: Hex color string
            amount: Amount to adjust brightness (positive or negative)

        Returns:
            Adjusted hex color string

        Like a digital alchemist transmuting colors, this method adjusts
        the brightness of a color value while contemplating whether any
        meaningful difference exists between #3A3A3A and #3B3B3B in the
        cosmic scale of existence.
        """
        try:
            # Remove # prefix if present
            hex_color = color.lstrip('#')

            # Convert hex to RGB
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

            # Adjust brightness with bounds checking
            adjusted = [max(0, min(255, x + amount)) for x in rgb]

            # Convert back to hex
            return f'#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}'

        except Exception as e:
            self.logger.error(f"Color adjustment error: {str(e)}", exc_info=True)
            return color  # Return original color on error

    def _create_or_clear_layout(self, widget: QWidget) -> bool:
        """
        Safely create a new layout or clear an existing one without causing crashes.

        This is a critical safety method that avoids the dangerous pattern of:
        1. Deleting a layout
        2. Setting the widget's layout to None (crash-prone)
        3. Creating a new layout

        Instead, we either:
        1. Use the existing layout but clear its contents
        2. Create a new layout if none exists

        Args:
            widget: The widget to set up a layout for

        Returns:
            True if layout is ready to use, False if operation failed
        """
        try:
            existing_layout = widget.layout()

            if existing_layout:
                # Clear all widgets from existing layout
                while existing_layout.count():
                    item = existing_layout.takeAt(0)
                    if item.widget():
                        item.widget().hide()
                        item.widget().deleteLater()
                    elif item.layout():
                        # Recursively clear sublayouts
                        self._delete_layout_contents(item.layout())
                    elif item.spacerItem():
                        # Just remove spacers
                        pass

                # Don't delete the layout or set it to None - that causes crashes!
                return True
            else:
                # Create a new layout since none exists
                new_layout = QVBoxLayout(widget)
                new_layout.setContentsMargins(10, 10, 10, 10)
                new_layout.setSpacing(5)
                return True

        except Exception as e:
            self.logger.error(f"Layout operation failed: {str(e)}", exc_info=True)
            return False

    def _delete_layout_contents(self, layout) -> None:
        """
        Recursively delete contents of a layout without deleting the layout itself.

        Args:
            layout: The layout to clear
        """
        if not layout:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout_contents(item.layout())