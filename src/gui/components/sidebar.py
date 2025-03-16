"""Sidebar component for navigation and status display."""

import logging
from typing import Optional, Dict, Any, Tuple, Union, List, cast
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QFrame, QMessageBox, QApplication,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QIcon, QPixmap
import psutil
import os
import subprocess

from gui.styles.theme import Theme


class Sidebar(QWidget):
    """Main sidebar widget containing all navigation and control elements.

    The sidebar provides navigation buttons, progress indicators, and
    system control functions, serving as the primary navigation panel
    for the application.

    Like the control panel of a digital spaceship, this sidebar offers
    access to various systems while displaying the vessel's status.
    """

    # Signals
    theme_changed = pyqtSignal(str)  # Emitted when a theme change affects the sidebar

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the sidebar widget.

        Args:
            parent: Parent widget for containment hierarchy
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        # Set object name for stylesheet targeting
        self.setObjectName("MainSidebar")

        # Track sidebar state
        self._current_theme = "dark"  # Default theme
        self._is_expanded = True  # Track expansion state

        # Setup UI components
        self.setup_ui()

    def setup_ui(self) -> None:
        """Initialize and arrange all UI elements."""
        try:
            # Main layout with standard spacing
            layout = QVBoxLayout(self)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # Logo/title section
            self.setup_logo_section(layout)

            # Main navigation buttons
            self.setup_main_buttons(layout)

            # Progress section for installation tracking
            self.setup_progress_section(layout)

            # Control buttons (reboot/exit)
            self.setup_control_buttons(layout)

            # Apply base styling
            self.apply_base_styling()

            self.logger.debug("Sidebar UI setup complete - navigation panel assembled")
        except Exception as e:
            self.logger.exception(f"Error setting up sidebar UI: {str(e)}")
            # Create minimal UI in case of failure
            err_layout = QVBoxLayout(self)
            err_label = QLabel("Sidebar initialization failed")
            err_label.setStyleSheet("color: red;")
            err_layout.addWidget(err_label)
            self.logger.error("Using fallback sidebar layout due to initialization error")

    def setup_logo_section(self, layout: QVBoxLayout) -> None:
        """Setup the logo section at the top with the actual Moinsy PNG icon.

        Args:
            layout: Parent layout to add the logo section to

        Like a philosopher who realizes the futility of abstract representation
        when physical reality is readily available, we abandon our generative art
        in favor of a pre-rendered icon - an admission that sometimes the thing
        itself is superior to our symbolic approximation of it.
        """
        try:
            # Create a frame for the logo section
            logo_container = QFrame()
            logo_container.setObjectName("LogoContainer")
            logo_container.setFixedHeight(60)  # Reduced height without subtitle

            # Logo layout
            logo_layout = QHBoxLayout(logo_container)
            logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_layout.setContentsMargins(10, 10, 10, 10)
            logo_layout.setSpacing(10)

            # Load the actual icon file from resources
            icon_path = os.path.join(self.program_dir, "resources", "icons", "moinsy.png")
            alt_path = os.path.join(self.program_dir, "src", "resources", "icons", "moinsy.png")

            # Create logo image label
            logo_label = QLabel()
            logo_label.setObjectName("MoinsyLogoImage")

            # Try to load the icon file with robust error handling
            pixmap = None
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                self.logger.debug(f"Loaded Moinsy icon from: {icon_path}")
            elif os.path.exists(alt_path):
                pixmap = QPixmap(alt_path)
                self.logger.debug(f"Loaded Moinsy icon from alternate path: {alt_path}")
            else:
                self.logger.warning(f"Moinsy icon not found at {icon_path} or {alt_path}")

            if pixmap is not None:
                # Scale the image while preserving aspect ratio
                scaled_pixmap = pixmap.scaled(
                    40, 40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setFixedSize(40, 40)
            else:
                # If icon not found, use a colored circle as fallback
                self.logger.warning("Using fallback colored circle for logo")
                logo_label.setText("M")
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                logo_label.setStyleSheet(f"""
                    background-color: {Theme.get_color('PRIMARY')}; 
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 20px;
                """)
                logo_label.setFixedSize(40, 40)

            # Logo text - Application name
            self.logo_label = QLabel("MOINSY")
            self.logo_label.setObjectName("LogoLabel")
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_label.setStyleSheet(f"""
                color: {Theme.get_color('PRIMARY')};
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 2px;
            """)

            # Add components to layout
            logo_layout.addWidget(logo_label)
            logo_layout.addWidget(self.logo_label)

            # Note: No subtitle "SYSTEM INSTALLER" as requested

            # Style the container
            logo_container.setStyleSheet(f"""
                QFrame#LogoContainer {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px 0px;
                }}
            """)

            layout.addWidget(logo_container)
            self.logger.debug("Logo section created with physical icon - identity anchored in digital reality")
        except Exception as e:
            self.logger.error(f"Failed to create logo section: {str(e)}", exc_info=True)
            # Add a simple label as fallback - a testament to the fragility of our visual ambitions
            fallback_label = QLabel("MOINSY")
            fallback_label.setStyleSheet("color: white; font-weight: bold;")
            layout.addWidget(fallback_label)
            self.logger.debug("Created fallback logo after failure - simplicity emerges from complexity's collapse")

    def setup_main_buttons(self, layout: QVBoxLayout) -> None:
        """Create and add main navigation buttons.

        Args:
            layout: Parent layout to add the navigation buttons to
        """
        try:
            # Create buttons with distinct colors and set object names for styling
            self.installations_button = self.create_sidebar_button(
                "Installations", Theme.get_color('PRIMARY'), "package"
            )
            self.installations_button.setObjectName("InstallationsButton")

            self.commands_button = self.create_sidebar_button(
                "Command Builder", "#BA4D45", "terminal"
            )
            self.commands_button.setObjectName("CommandsButton")

            self.tools_button = self.create_sidebar_button(
                "System Tools", Theme.get_color('WARNING'), "tool"
            )
            self.tools_button.setObjectName("ToolsButton")

            self.settings_button = self.create_sidebar_button(
                "Settings", Theme.get_color('SECONDARY'), "settings"
            )
            self.settings_button.setObjectName("SettingsButton")

            self.help_button = self.create_sidebar_button(
                "Help", Theme.get_color('TERTIARY'), "help-circle"
            )
            self.help_button.setObjectName("HelpButton")

            # Add buttons to layout with proper spacing
            layout.addWidget(self.installations_button)
            layout.addWidget(self.commands_button)
            layout.addWidget(self.tools_button)
            layout.addWidget(self.settings_button)
            layout.addWidget(self.help_button)

            self.logger.debug("Navigation buttons created - control interface established")
        except Exception as e:
            self.logger.error(f"Failed to create navigation buttons: {str(e)}")
            # Add a simple button as fallback
            fallback = QPushButton("Navigation Failed")
            fallback.setStyleSheet("color: red;")
            layout.addWidget(fallback)

    def setup_progress_section(self, layout: QVBoxLayout) -> None:
        """Setup the installation progress section.

        Args:
            layout: Parent layout to add the progress section to
        """
        try:
            # Create a frame for the progress section
            progress_frame = QFrame()
            progress_frame.setObjectName("ProgressFrame")

            # Progress layout
            progress_layout = QVBoxLayout(progress_frame)
            progress_layout.setSpacing(10)
            progress_layout.setContentsMargins(15, 15, 15, 15)

            # Header for progress section
            header = QLabel("System Progress")
            header.setObjectName("ProgressHeader")
            progress_layout.addWidget(header)

            # Progress percentage display
            self.progress_percentage = QLabel("0%")
            self.progress_percentage.setObjectName("ProgressPercentage")
            self.progress_percentage.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_layout.addWidget(self.progress_percentage)

            # Progress bar for visual indicator
            self.progress_bar = QProgressBar()
            self.progress_bar.setObjectName("ProgressBar")
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setMaximumHeight(6)
            progress_layout.addWidget(self.progress_bar)

            # Status text below progress bar
            self.progress_status = QLabel("No active installation")
            self.progress_status.setObjectName("ProgressStatus")
            self.progress_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_layout.addWidget(self.progress_status)

            layout.addWidget(progress_frame)
            self.logger.debug("Progress section created - operational status display online")
        except Exception as e:
            self.logger.error(f"Failed to create progress section: {str(e)}")
            # Add a simple label as fallback
            layout.addWidget(QLabel("Progress tracking unavailable"))

    def setup_control_buttons(self, layout: QVBoxLayout) -> None:
        """Setup system control buttons (reboot/exit).

        Args:
            layout: Parent layout to add the control buttons to
        """
        try:
            # Create a frame for the control section
            control_frame = QFrame()
            control_frame.setObjectName("ControlFrame")

            # Control layout
            control_layout = QVBoxLayout(control_frame)
            control_layout.setSpacing(10)
            control_layout.setContentsMargins(15, 15, 15, 15)

            # Reboot button
            self.reboot_button = QPushButton("Reboot System")
            self.reboot_button.setObjectName("RebootButton")
            self.reboot_button.clicked.connect(self.confirm_reboot)
            control_layout.addWidget(self.reboot_button)

            # Exit button
            self.exit_button = QPushButton("Exit")
            self.exit_button.setObjectName("ExitButton")
            self.exit_button.clicked.connect(QApplication.instance().quit)
            control_layout.addWidget(self.exit_button)

            layout.addWidget(control_frame)
            self.logger.debug("Control buttons created - system operation controls available")
        except Exception as e:
            self.logger.error(f"Failed to create control buttons: {str(e)}")
            # Add a simple button as fallback
            layout.addWidget(QPushButton("Exit"))

    def create_sidebar_button(self, text: str, color: str, icon_name: Optional[str] = None) -> QPushButton:
        """Create styled sidebar button.

        Args:
            text: Button text to display
            color: Button color as hex or name
            icon_name: Optional icon name to display

        Returns:
            Styled button widget ready for use
        """
        button = QPushButton(text)
        button.setMinimumHeight(60)

        # Set size policy for proper expansion
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # This will be styled through the apply_theme method
        # Store the intended color as a property for theme changes
        button.setProperty("button_color", color)
        button.setProperty("icon_name", icon_name)

        return button

    def apply_theme(self, theme_id: str) -> None:
        """Apply theme to all sidebar components.

        Args:
            theme_id: Theme identifier to apply
        """
        try:
            self._current_theme = theme_id

            # Apply colors from theme
            self.apply_base_styling()

            # Apply specific component styling
            self.apply_logo_styling()
            self.apply_button_styling()
            self.apply_progress_styling()

            # Emit theme changed signal
            self.theme_changed.emit(theme_id)
            self.logger.debug(f"Applied theme '{theme_id}' to sidebar")
        except Exception as e:
            self.logger.error(f"Error applying theme to sidebar: {str(e)}")

    def apply_base_styling(self) -> None:
        """Apply base styling to the sidebar."""
        try:
            # Get colors from Theme
            bg_color = Theme.get_color('BG_MEDIUM')

            # Set base sidebar styling
            self.setStyleSheet(f"""
                QWidget#MainSidebar {{
                    background-color: {bg_color};
                    border-right: 1px solid {Theme.get_color('BG_LIGHT')};
                }}
            """)
            self.logger.debug("Applied base styling to sidebar")
        except Exception as e:
            self.logger.error(f"Error applying base styling: {str(e)}")

    def apply_logo_styling(self) -> None:
        """Apply styling to the logo section."""
        try:
            # Style logo container
            if hasattr(self, 'logo_label'):
                # Use Theme font if available
                try:
                    self.logo_label.setFont(Theme.get_font('LOGO'))
                except (AttributeError, KeyError):
                    # Fallback font
                    self.logo_label.setFont(QFont('JetBrains Mono', 24, QFont.Weight.Bold))

                # Style with Theme colors
                self.logo_label.setStyleSheet(f"""
                    color: {Theme.get_color('PRIMARY')};
                    font-weight: bold;
                    letter-spacing: 2px;
                """)

            # Style subtitle
            if hasattr(self, 'subtitle'):
                # Use Theme font if available
                try:
                    self.subtitle.setFont(Theme.get_font('SUBTITLE'))
                except (AttributeError, KeyError):
                    # Fallback font
                    self.subtitle.setFont(QFont('Segoe UI', 10))

                # Style with Theme colors
                self.subtitle.setStyleSheet(f"""
                    color: {Theme.get_color('TEXT_SECONDARY')};
                """)

            # Style the logo container frame
            logo_container = self.findChild(QFrame, "LogoContainer")
            if logo_container:
                logo_container.setStyleSheet(f"""
                    QFrame#LogoContainer {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        border-radius: 12px;
                        margin-bottom: 5px;
                    }}
                """)

            self.logger.debug("Applied logo styling")
        except Exception as e:
            self.logger.error(f"Error applying logo styling: {str(e)}")

    def apply_button_styling(self) -> None:
        """Apply styling to all navigation and control buttons."""
        try:
            # Style the navigation buttons with their specific colors
            self._style_navigation_button(self.installations_button, "green")
            self._style_navigation_button(self.commands_button, "red")
            self._style_navigation_button(self.tools_button, "yellow")
            self._style_navigation_button(self.settings_button, "blue")
            self._style_navigation_button(self.help_button, "purple")

            # Style control buttons
            self._style_control_button(self.reboot_button, "danger")
            self._style_control_button(self.exit_button, "neutral")

            # Style control frame
            control_frame = self.findChild(QFrame, "ControlFrame")
            if control_frame:
                control_frame.setStyleSheet(f"""
                    QFrame#ControlFrame {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border-radius: 12px;
                        padding: 5px;
                    }}
                """)

            self.logger.debug("Applied button styling")
        except Exception as e:
            self.logger.error(f"Error applying button styling: {str(e)}")

    def _style_navigation_button(self, button: QPushButton, color_theme: str) -> None:
        """Apply specific styling to a navigation button.

        Args:
            button: The button to style
            color_theme: Color theme identifier (green, red, blue, etc.)
        """
        try:
            # Get color from property or use predefined colors
            stored_color = button.property("button_color")

            # Allow override by specific color themes
            if color_theme == "green":
                color = Theme.get_color('PRIMARY')
            elif color_theme == "red":
                color = "#BA4D45"  # Custom red not in theme
            elif color_theme == "yellow":
                color = Theme.get_color('WARNING')
            elif color_theme == "blue":
                color = Theme.get_color('SECONDARY')
            elif color_theme == "purple":
                color = Theme.get_color('TERTIARY')
            else:
                # Use the stored color or fallback
                color = stored_color if stored_color else Theme.get_color('PRIMARY')

            # Adjust hover color
            hover_color = self.adjust_color(color, -20)
            pressed_color = self.adjust_color(color, -40)

            # Apply styling
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """)
        except Exception as e:
            self.logger.error(f"Error styling navigation button: {str(e)}")

    def _style_control_button(self, button: QPushButton, button_type: str) -> None:
        """Apply specific styling to a control button.

        Args:
            button: The button to style
            button_type: Button type (danger, primary, neutral)
        """
        try:
            if button_type == "danger":
                color = Theme.get_color('ERROR')
                hover_color = self.adjust_color(color, -10)
                text_color = "white"
            elif button_type == "primary":
                color = Theme.get_color('PRIMARY')
                hover_color = self.adjust_color(color, -10)
                text_color = "white"
            else:  # neutral
                color = Theme.get_color('CONTROL_BG')
                hover_color = Theme.get_color('CONTROL_HOVER')
                text_color = "white"

            # Apply styling
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {text_color};
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    text-align: center;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)
        except Exception as e:
            self.logger.error(f"Error styling control button: {str(e)}")

    def apply_progress_styling(self) -> None:
        """Apply styling to the progress section."""
        try:
            # Style progress frame
            progress_frame = self.findChild(QFrame, "ProgressFrame")
            if progress_frame:
                progress_frame.setStyleSheet(f"""
                    QFrame#ProgressFrame {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border-radius: 12px;
                        padding: 5px;
                    }}
                """)

            # Style progress header
            progress_header = self.findChild(QLabel, "ProgressHeader")
            if progress_header:
                progress_header.setStyleSheet(f"""
                    color: {Theme.get_color('TEXT_SECONDARY')};
                    font-size: 14px;
                    font-weight: bold;
                """)

            # Style progress percentage
            if hasattr(self, 'progress_percentage'):
                self.progress_percentage.setStyleSheet(f"""
                    color: {Theme.get_color('PRIMARY')};
                    font-size: 24px;
                    font-weight: bold;
                """)

            # Style progress bar
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border: none;
                        border-radius: 3px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {Theme.get_color('PRIMARY')};
                        border-radius: 3px;
                    }}
                """)

            # Style progress status
            if hasattr(self, 'progress_status'):
                self.progress_status.setStyleSheet(f"""
                    color: {Theme.get_color('TEXT_SECONDARY')};
                    margin-top: 5px;
                    font-size: 12px;
                """)

            self.logger.debug("Applied progress styling")
        except Exception as e:
            self.logger.error(f"Error applying progress styling: {str(e)}")

    def update_progress(self, value: int, status: Optional[str] = None) -> None:
        """Update installation progress display.

        Args:
            value: Progress percentage (0-100)
            status: Optional status message
        """
        try:
            # Update percentage display
            self.progress_percentage.setText(f"{value}%")
            self.progress_bar.setValue(value)

            # Update status message if provided
            if status:
                self.progress_status.setText(status)
            elif value == 0:
                self.progress_status.setText("No active installation")
            elif value == 100:
                self.progress_status.setText("Installation complete")
            else:
                self.progress_status.setText("Installing...")

            # Update progress bar color based on status
            self._update_progress_color(value, status)

            self.logger.debug(f"Updated progress: {value}% - {status if status else 'No status'}")
        except Exception as e:
            self.logger.error(f"Failed to update progress: {str(e)}")

    def _update_progress_color(self, value: int, status: Optional[str] = None) -> None:
        """Update progress bar color based on status and value.

        Args:
            value: Progress percentage (0-100)
            status: Optional status message
        """
        try:
            if value == 100:
                # Green for complete
                self.progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border: none;
                        border-radius: 3px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {Theme.get_color('SUCCESS')};
                        border-radius: 3px;
                    }}
                """)
            elif status and "error" in status.lower():
                # Red for error
                self.progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border: none;
                        border-radius: 3px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {Theme.get_color('ERROR')};
                        border-radius: 3px;
                    }}
                """)
            else:
                # Default color
                self.progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border: none;
                        border-radius: 3px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {Theme.get_color('PRIMARY')};
                        border-radius: 3px;
                    }}
                """)
        except Exception as e:
            self.logger.error(f"Error updating progress color: {str(e)}")

    def confirm_reboot(self) -> None:
        """Show confirmation dialog and handle system reboot."""
        try:
            # Ask for confirmation before rebooting
            reply = QMessageBox.question(
                self,
                'Confirm Reboot',
                'Are you sure you want to reboot the system?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.logger.info("User initiated system reboot")
                try:
                    subprocess.run(["sudo", "reboot"], check=True)
                except subprocess.CalledProcessError as e:
                    error_msg = f"Failed to reboot system: {str(e)}"
                    self.logger.error(error_msg)
                    QMessageBox.critical(self, "Error", error_msg)
        except Exception as e:
            self.logger.error(f"Error in reboot confirmation: {str(e)}")

    def adjust_color(self, color: str, amount: int) -> str:
        """Adjust color brightness by amount.

        Args:
            color: Hex color string
            amount: Amount to adjust brightness (positive or negative)

        Returns:
            Adjusted hex color string

        Like a digital alchemist adjusting the luminosity of a magical essence,
        this method transforms colors by modifying their brightness values.
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
            self.logger.error(f"Color adjustment error: {str(e)}")
            return color  # Return original color on error