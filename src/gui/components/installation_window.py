"""Dialog window for installation options selection."""

import os
import logging
from typing import Optional, Dict, Any, List, Callable, Union, Tuple

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from gui.styles.theme import Theme


class InstallationWindow(QDialog):
    """Dialog window for installation options.

    This class provides a selection of installation packages that can
    be configured by the user.
    """

    # Signals
    installation_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the installation window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = logging.getLogger(__name__)

        # Get program directory
        try:
            self.program_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        except Exception as e:
            self.logger.error(f"Error determining program directory: {str(e)}")
            self.program_dir = ""

        self.setWindowTitle("Installation Options")
        self.setMinimumSize(800, 600)

        try:
            self.setup_ui()
            self.logger.debug("Installation window UI initialized")
        except Exception as e:
            self.logger.exception(f"Error setting up installation window UI: {str(e)}")
            # Create a minimal UI in case of error
            error_layout = QVBoxLayout(self)
            error_label = QLabel("Error initializing installation window. Check logs for details.")
            error_label.setStyleSheet("color: #dc2626;")
            error_layout.addWidget(error_label)

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.setup_header(layout)

        # Installation options grid
        self.setup_installations_grid(layout)

        # Bottom buttons
        self.setup_bottom_buttons(layout)

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup the header section.

        Args:
            layout: Parent layout to add the header to
        """
        try:
            header = QLabel("Installation Options")
            # Use the get_font method safely with error handling
            try:
                header_font = Theme.get_font('TITLE')
                header.setFont(header_font)
            except (AttributeError, ValueError) as e:
                self.logger.warning(f"Could not set header font, using fallback: {str(e)}")
                # Fallback to manually created font
                header.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))

            # Set color from theme
            try:
                primary_color = Theme.get_color('PRIMARY')
                header.setStyleSheet(f"color: {primary_color};")
            except (AttributeError, ValueError):
                # Fallback color
                header.setStyleSheet("color: #4CAF50;")

            layout.addWidget(header)

            description = QLabel("Select an installation package to configure your system")
            # Try to use theme for secondary text color
            try:
                secondary_color = Theme.get_color('TEXT_SECONDARY')
                description.setStyleSheet(f"color: {secondary_color}; font-size: 14px;")
            except (AttributeError, ValueError):
                # Fallback styling
                description.setStyleSheet("color: #888888; font-size: 14px;")

            layout.addWidget(description)

        except Exception as e:
            self.logger.exception(f"Error setting up header: {str(e)}")
            # Add a basic header in case of error
            error_header = QLabel("Installation Options")
            error_header.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
            layout.addWidget(error_header)

    def setup_installations_grid(self, layout: QVBoxLayout) -> None:
        """Setup the scrollable grid of installation options.

        Args:
            layout: Parent layout to add the grid to
        """
        try:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
            """)

            container = QWidget()
            grid_layout = QGridLayout(container)
            grid_layout.setSpacing(15)

            # Add installation options
            installations = [
                ("Programs",
                 "Install multiple applications from a curated selection",
                 "#4CAF50",
                 "Programs"),

                ("PipeWire",
                 "Modern audio server with improved quality and Bluetooth support",
                 "#2196F3",
                 "PipeWire"),

                ("OneDrive",
                 "Microsoft cloud storage integration for Linux",
                 "#9C27B0",
                 "OneDrive"),

                ("Development Tools",
                 "Programming languages, IDEs, and developer utilities",
                 "#FF9800",
                 "Development"),

                ("Media Applications",
                 "Audio and video editing, streaming, and playback software",
                 "#00BCD4",
                 "Media"),

                ("Productivity Suite",
                 "Office applications, note-taking, and organizational tools",
                 "#795548",
                 "Productivity"),
            ]

            for i, (name, description, color, identifier) in enumerate(installations):
                row = i // 2  # 2 buttons per row
                col = i % 2

                install_button = self.create_installation_button(name, description, color, identifier)
                grid_layout.addWidget(install_button, row, col)

            scroll.setWidget(container)
            layout.addWidget(scroll)

        except Exception as e:
            self.logger.exception(f"Error setting up installations grid: {str(e)}")
            # Add error message to layout
            error_label = QLabel("Could not load installation options. Check logs for details.")
            error_label.setStyleSheet("color: #dc2626;")
            layout.addWidget(error_label)

    def create_installation_button(self, name: str, description: str,
                                   color: str, identifier: str) -> QPushButton:
        """Create a styled installation button.

        Args:
            name: Button title
            description: Button description
            color: Button color
            identifier: Installation identifier

        Returns:
            Styled QPushButton instance
        """
        try:
            button = QPushButton()
            button.setMinimumHeight(100)

            # Button layout
            button_layout = QVBoxLayout(button)
            button_layout.setSpacing(5)
            button_layout.setContentsMargins(15, 15, 15, 15)

            # Title
            title = QLabel(name)
            try:
                title_font = Theme.get_font('SUBTITLE')
                title.setFont(title_font)
            except (AttributeError, ValueError):
                # Fallback font
                title.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))

            title.setStyleSheet("color: white;")
            button_layout.addWidget(title)

            # Description
            desc = QLabel(description)
            desc.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            desc.setWordWrap(True)
            button_layout.addWidget(desc)

            button_layout.addStretch()

            # Style
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: none;
                    border-radius: 12px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {self.adjust_color(color, -20)};
                }}
            """)

            # Connect button to emit signal with identifier
            button.clicked.connect(lambda: self.on_installation_selected(identifier))

            return button

        except Exception as e:
            self.logger.exception(f"Error creating installation button: {str(e)}")
            # Return a simple button as fallback
            fallback = QPushButton(name)
            fallback.setStyleSheet("background-color: #4CAF50; color: white;")
            fallback.clicked.connect(lambda: self.on_installation_selected(identifier))
            return fallback

    def on_installation_selected(self, identifier: str) -> None:
        """Handle installation selection.

        Args:
            identifier: Installation identifier
        """
        try:
            self.logger.info(f"Installation selected: {identifier}")
            self.installation_selected.emit(identifier)
            self.close()
        except Exception as e:
            self.logger.exception(f"Error handling installation selection: {str(e)}")

    def setup_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """Setup bottom control buttons.

        Args:
            layout: Parent layout to add the buttons to
        """
        try:
            button_layout = QHBoxLayout()
            button_layout.setSpacing(10)

            button_layout.addStretch()

            # Close button
            close_button = QPushButton("Close")
            close_button.setFixedSize(120, 40)
            close_button.clicked.connect(self.close)

            try:
                # Get control colors from theme
                control_bg = Theme.get_color('CONTROL_BG')
                control_hover = Theme.get_color('CONTROL_HOVER')
                close_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {control_bg};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {control_hover};
                    }}
                """)
            except (AttributeError, ValueError):
                # Fallback styling
                close_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4b5563;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #374151;
                    }
                """)

            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

        except Exception as e:
            self.logger.exception(f"Error setting up bottom buttons: {str(e)}")
            # Add a simple close button as fallback
            fallback_button = QPushButton("Close")
            fallback_button.clicked.connect(self.close)
            layout.addWidget(fallback_button)

    def adjust_color(self, color: str, amount: int) -> str:
        """Adjust color brightness by amount.

        Args:
            color: Hex color string
            amount: Amount to adjust brightness

        Returns:
            Adjusted hex color string
        """
        try:
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            adjusted = [max(0, min(255, x + amount)) for x in rgb]
            return f'#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}'
        except Exception as e:
            self.logger.error(f"Error adjusting color: {str(e)}")
            return color  # Return original color in case of error