"""Dialog window for displaying help information."""

import os
import logging
from typing import Optional, Dict, Any, List, Union

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTabWidget, QWidget, QScrollArea, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from gui.styles.theme import Theme


class HelpWindow(QDialog):
    """Dialog window for displaying help information.

    This class provides a tabbed interface for accessing different
    help documentation sections.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the help window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Get program directory
        try:
            self.program_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        except Exception as e:
            self.logger.error(f"Error determining program directory: {str(e)}")
            self.program_dir = ""

        self.setWindowTitle("Moinsy Help")
        self.setMinimumSize(1000, 700)

        try:
            self.setup_ui()
            self.logger.debug("Help window UI initialized")
        except Exception as e:
            self.logger.exception(f"Error setting up help window UI: {str(e)}")
            # Create a minimal UI in case of error
            error_layout = QVBoxLayout(self)
            error_label = QLabel("Error initializing help window. Check logs for details.")
            error_label.setStyleSheet("color: #dc2626;")
            error_layout.addWidget(error_label)

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.setup_header(layout)

        # Tab widget for different help sections
        self.tabs = self.create_tabs()
        if self.tabs:
            layout.addWidget(self.tabs)

        # Bottom buttons
        self.setup_bottom_buttons(layout)

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup the header section.

        Args:
            layout: Parent layout to add the header to
        """
        try:
            # Create header layout
            header_layout = QHBoxLayout()

            # Title
            header = QLabel("Moinsy Help Center")
            try:
                # Try to use theme font
                header_font = Theme.get_font('TITLE')
                header.setFont(header_font)
            except (AttributeError, ValueError) as e:
                self.logger.warning(f"Could not set header font, using fallback: {str(e)}")
                # Fallback to manually created font
                header.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))

            # Set header color using Theme.get_color with fallback
            try:
                header.setStyleSheet(f"color: {Theme.get_color('PRIMARY')};")
            except (AttributeError, KeyError, ValueError) as e:
                self.logger.warning(f"Could not set header color from theme: {str(e)}")
                # Fallback color
                header.setStyleSheet("color: #4CAF50;")

            header_layout.addWidget(header)

            # Version
            version = QLabel("v1.0")
            try:
                version.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-size: 14px;")
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                version.setStyleSheet("color: #888888; font-size: 14px;")

            version.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
            header_layout.addWidget(version)

            layout.addLayout(header_layout)

            # Description
            description = QLabel("Find information about using the Modular Installation System")
            try:
                description.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-size: 14px;")
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                description.setStyleSheet("color: #888888; font-size: 14px;")

            layout.addWidget(description)

        except Exception as e:
            self.logger.exception(f"Error setting up header: {str(e)}")
            # Add a basic header in case of error
            error_header = QLabel("Moinsy Help Center")
            error_header.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
            layout.addWidget(error_header)

    def create_tabs(self) -> Optional[QTabWidget]:
        """Create and configure the tab widget for help content.

        Returns:
            Configured QTabWidget or None if an error occurred
        """
        try:
            tabs = QTabWidget()
            # Try to use theme colors for styling
            try:
                bg_medium = Theme.get_color('BG_MEDIUM')
                bg_light = Theme.get_color('BG_LIGHT')
                text_secondary = Theme.get_color('TEXT_SECONDARY')
                primary = Theme.get_color('PRIMARY')
                text_primary = Theme.get_color('TEXT_PRIMARY')

                tabs.setStyleSheet(f"""
                    QTabWidget::pane {{
                        border: 1px solid {bg_light};
                        background-color: {bg_medium};
                        border-radius: 8px;
                    }}
                    QTabBar::tab {{
                        background-color: {bg_light};
                        color: {text_secondary};
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                        padding: 8px 15px;
                        margin-right: 2px;
                    }}
                    QTabBar::tab:selected {{
                        background-color: {primary};
                        color: {text_primary};
                    }}
                    QTabBar::tab:hover:!selected {{
                        background-color: #4d4e52;
                        color: white;
                    }}
                """)
            except (AttributeError, KeyError, ValueError) as e:
                self.logger.warning(f"Could not style tabs with theme colors: {str(e)}")
                # Fallback styling
                tabs.setStyleSheet("""
                    QTabWidget::pane {
                        border: 1px solid #3d3e42;
                        background-color: #2d2e32;
                        border-radius: 8px;
                    }
                    QTabBar::tab {
                        background-color: #3d3e42;
                        color: #888888;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                        padding: 8px 15px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected {
                        background-color: #4CAF50;
                        color: white;
                    }
                    QTabBar::tab:hover:!selected {
                        background-color: #4d4e52;
                        color: white;
                    }
                """)

            # Create tabs
            install_tab = self.create_installation_tab()
            tools_tab = self.create_tools_tab()
            faq_tab = self.create_faq_tab()

            # Add tabs to the widget
            tabs.addTab(install_tab, "Installations")
            tabs.addTab(tools_tab, "System Tools")
            tabs.addTab(faq_tab, "FAQ")

            return tabs

        except Exception as e:
            self.logger.exception(f"Error creating tabs: {str(e)}")
            return None

    def create_installation_tab(self) -> QWidget:
        """Create the installation help tab.

        Returns:
            Widget containing installation documentation
        """
        try:
            install_tab = QWidget()
            tab_layout = QVBoxLayout(install_tab)

            content = QTextEdit()
            content.setReadOnly(True)
            content.setHtml("""
            <h2>Installation Options</h2>

            <h3>Programs Installation</h3>
            <p>The Programs Installation allows you to select and install multiple applications at once:</p>
            <ul>
                <li>Choose from a curated list of useful applications</li>
                <li>Install multiple programs in a single operation</li>
                <li>All installations are handled automatically</li>
            </ul>

            <h3>PipeWire Audio Installation</h3>
            <p>PipeWire is a modern audio and video server for Linux:</p>
            <ul>
                <li>Better sound quality and lower latency than PulseAudio</li>
                <li>Improved Bluetooth audio support</li>
                <li>Compatible with both ALSA and PulseAudio applications</li>
                <li>Configure input and output devices easily</li>
            </ul>

            <h3>OneDrive Installation</h3>
            <p>Sync your Microsoft OneDrive cloud storage with Linux:</p>
            <ul>
                <li>Automatic synchronization with your OneDrive account</li>
                <li>Starts with your computer and syncs in the background</li>
                <li>Includes a launcher for the interface in your applications menu</li>
            </ul>

            <h3>Installation Process</h3>
            <p>When installing any component:</p>
            <ol>
                <li>Click the "Installations" button in the sidebar</li>
                <li>Select the desired installation option</li>
                <li>Follow the on-screen instructions in the terminal area</li>
                <li>The progress bar will show the overall installation progress</li>
                <li>Reboot your system after installation is complete</li>
            </ol>
            """)

            # Style content pane
            try:
                content.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 14px;
                        padding: 10px;
                    }}
                """)
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                content.setStyleSheet("""
                    QTextEdit {
                        background-color: #2d2e32;
                        color: white;
                        border: none;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 14px;
                        padding: 10px;
                    }
                """)

            tab_layout.addWidget(content)
            return install_tab

        except Exception as e:
            self.logger.exception(f"Error creating installation tab: {str(e)}")
            # Create error widget
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading installation documentation")
            error_label.setStyleSheet("color: #dc2626;")
            error_layout.addWidget(error_label)
            return error_widget

    def create_tools_tab(self) -> QWidget:
        """Create the system tools help tab.

        Returns:
            Widget containing tools documentation
        """
        try:
            tools_tab = QWidget()
            tab_layout = QVBoxLayout(tools_tab)

            content = QTextEdit()
            content.setReadOnly(True)
            content.setHtml("""
            <h2>System Tools</h2>

            <p>Moinsy provides several system management and maintenance tools:</p>

            <h3>System Update</h3>
            <p>Keep your system up to date with the latest packages:</p>
            <ul>
                <li>Updates all system packages via apt</li>
                <li>Updates Flatpak applications</li>
                <li>Updates Snap packages</li>
                <li>Performs cleanup of unused packages</li>
            </ul>

            <h3>Service Manager</h3>
            <p>Manage system services with an easy-to-use interface:</p>
            <ul>
                <li>View all system services and their current status</li>
                <li>Start, stop, or restart services</li>
                <li>Enable or disable services at system startup</li>
                <li>View detailed service status information</li>
            </ul>

            <h3>Disk Cleanup</h3>
            <p>Free up disk space by removing unnecessary files (coming soon):</p>
            <ul>
                <li>Remove temporary files</li>
                <li>Clean package caches</li>
                <li>Remove old kernels</li>
                <li>Clean up log files</li>
            </ul>

            <h3>Network Tools</h3>
            <p>Network diagnostics and configuration tools (coming soon):</p>
            <ul>
                <li>Test network connectivity</li>
                <li>View network statistics</li>
                <li>Configure network settings</li>
            </ul>

            <h3>Using System Tools</h3>
            <ol>
                <li>Click the "System Tools" button in the sidebar</li>
                <li>Select the desired tool from the grid</li>
                <li>Follow the on-screen instructions for each tool</li>
            </ol>
            """)

            # Style content pane
            try:
                content.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 14px;
                        padding: 10px;
                    }}
                """)
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                content.setStyleSheet("""
                    QTextEdit {
                        background-color: #2d2e32;
                        color: white;
                        border: none;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 14px;
                        padding: 10px;
                    }
                """)

            tab_layout.addWidget(content)
            return tools_tab

        except Exception as e:
            self.logger.exception(f"Error creating tools tab: {str(e)}")
            # Create error widget
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading tools documentation")
            error_label.setStyleSheet("color: #dc2626;")
            error_layout.addWidget(error_label)
            return error_widget

    def create_faq_tab(self) -> QWidget:
        """Create the FAQ help tab.

        Returns:
            Widget containing FAQ documentation
        """
        try:
            faq_tab = QWidget()
            tab_layout = QVBoxLayout(faq_tab)

            content = QTextEdit()
            content.setReadOnly(True)
            content.setHtml("""
            <h2>Frequently Asked Questions</h2>

            <h3>Why should I reboot after installation?</h3>
            <p>Rebooting ensures that all installed components are properly initialized and 
            that any system changes take effect. This is especially important for components 
            like PipeWire that interact with system services.</p>

            <h3>Are my existing programs and settings affected?</h3>
            <p>No, Moinsy is designed to safely add new components without disrupting your 
            existing system configuration. However, when replacing components (like switching from 
            PulseAudio to PipeWire), some settings may need reconfiguration.</p>

            <h3>Can I uninstall components installed by Moinsy?</h3>
            <p>Yes, you can uninstall any component using standard system package management tools
            like apt, flatpak, or snap. Moinsy doesn't include an uninstaller at this time.</p>

            <h3>Where are the logs and configuration files stored?</h3>
            <p>Moinsy stores its configuration files in the /opt/moinsy directory. System components 
            installed by Moinsy store their configuration in standard system locations.</p>

            <h3>How do I update Moinsy itself?</h3>
            <p>Moinsy doesn't currently include an auto-update feature. To update Moinsy,
            download the latest version and install it using the same process you used for the 
            initial installation.</p>

            <h3>Why does Moinsy need administrator privileges?</h3>
            <p>Moinsy requires administrator privileges (sudo) to install system packages
            and configure system services. This is necessary for installing software system-wide
            and modifying system configurations.</p>
            """)

            # Style content pane
            try:
                content.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 14px;
                        padding: 10px;
                    }}
                """)
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                content.setStyleSheet("""
                    QTextEdit {
                        background-color: #2d2e32;
                        color: white;
                        border: none;
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 14px;
                        padding: 10px;
                    }
                """)

            tab_layout.addWidget(content)
            return faq_tab

        except Exception as e:
            self.logger.exception(f"Error creating FAQ tab: {str(e)}")
            # Create error widget
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel("Error loading FAQ documentation")
            error_label.setStyleSheet("color: #dc2626;")
            error_layout.addWidget(error_label)
            return error_widget

    def setup_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """Setup bottom control buttons.

        Args:
            layout: Parent layout to add the buttons to
        """
        try:
            button_layout = QHBoxLayout()

            # Feedback button
            feedback_button = QPushButton("Send Feedback")
            try:
                # Try to style with theme colors
                feedback_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.get_color('SECONDARY')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #1976D2;
                    }}
                """)
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                feedback_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 20px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)

            feedback_button.clicked.connect(self.show_feedback)
            button_layout.addWidget(feedback_button)

            button_layout.addStretch()

            # Close button
            close_button = QPushButton("Close")
            close_button.setFixedSize(120, 40)
            close_button.clicked.connect(self.close)

            try:
                # Try to style with theme colors
                close_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.get_color('CONTROL_BG')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.get_color('CONTROL_HOVER')};
                    }}
                """)
            except (AttributeError, KeyError, ValueError):
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

    def show_feedback(self) -> None:
        """Show feedback dialog."""
        try:
            feedback_dialog = QDialog(self)
            feedback_dialog.setWindowTitle("Feedback")
            feedback_dialog.setMinimumSize(400, 200)

            layout = QVBoxLayout(feedback_dialog)

            message = QLabel("Feedback functionality will be implemented in a future update.")
            try:
                message.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 14px;")
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                message.setStyleSheet("color: white; font-size: 14px;")

            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(message)

            close_button = QPushButton("Close")
            close_button.clicked.connect(feedback_dialog.close)

            try:
                close_button.setStyleSheet(f"""
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
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                close_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4b5563;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #374151;
                    }
                """)

            layout.addWidget(close_button)

            try:
                feedback_dialog.setStyleSheet(f"background-color: {Theme.get_color('BG_MEDIUM')};")
            except (AttributeError, KeyError, ValueError):
                # Fallback styling
                feedback_dialog.setStyleSheet("background-color: #2d2e32;")

            feedback_dialog.exec()

        except Exception as e:
            self.logger.exception(f"Error showing feedback dialog: {str(e)}")
            # Simple error message
            self.logger.error("Failed to show feedback dialog")