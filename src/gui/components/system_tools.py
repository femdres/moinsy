from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging
from typing import Optional, Dict, Any, List, Callable

from managers.config_manager import ConfigManager


class SystemToolsWindow(QDialog):
    """Dialog window for system utility functions"""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the system tools window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent_window = parent
        self.logger = logging.getLogger(__name__)

        # Get config manager from parent
        if hasattr(parent, 'config_manager'):
            self.config_manager = parent.config_manager
        else:
            self.logger.warning("Parent doesn't have config_manager, creating new instance")
            from core.settings.config_manager import ConfigManager
            self.config_manager = ConfigManager()

        self.setWindowTitle("System Tools")
        self.setMinimumSize(800, 600)
        self.setup_ui()

        self.logger.debug("System Tools window initialized")

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.setup_header(layout)

        # Tools Grid
        self.setup_tools_grid(layout)

        # Bottom buttons
        self.setup_bottom_buttons(layout)

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup the header section."""
        header = QLabel("System Tools")
        header.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #FFC107;")
        layout.addWidget(header)

        description = QLabel("Select a tool to perform system maintenance and configuration tasks")
        description.setStyleSheet("color: #888888; font-size: 14px;")
        layout.addWidget(description)

    def setup_tools_grid(self, layout: QVBoxLayout) -> None:
        """Setup the scrollable grid of tool buttons."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        container = QWidget()
        self.tools_grid = QGridLayout(container)
        self.tools_grid.setSpacing(15)

        # Add tool buttons with their corresponding functions
        tools = [
            ("System Update", "Update system packages and applications", "#4CAF50",
             lambda: self.launch_tool(self.start_system_update)),
            ("Disk Cleanup", "Remove temporary and unused files to free up space", "#2196F3",
             lambda: self.launch_tool(self.start_disk_cleanup)),
            ("Network Tools", "Network diagnostics and configuration", "#9C27B0",
             lambda: self.launch_tool(self.start_network_tool)),
            ("Service Manager", "Manage system services", "#FF9800",
             lambda: self.launch_tool(self.start_service_manager)),
            ("Backup Tools", "System backup and restore options", "#00BCD4",
             lambda: self.launch_tool(None)),
            ("Log Viewer", "View system logs and messages", "#795548",
             lambda: self.launch_tool(None)),
            ("Hardware Monitor", "Real-time hardware performance monitoring", "#3F51B5",
             lambda: self.launch_hardware_monitor()),
        ]

        for i, (name, description, color, callback) in enumerate(tools):
            row = i // 2  # 2 buttons per row
            col = i % 2

            tool_button = self.create_tool_button(name, description, color)
            if callback:
                tool_button.clicked.connect(callback)
            self.tools_grid.addWidget(tool_button, row, col)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def create_tool_button(self, name: str, description: str, color: str) -> QPushButton:
        """Create a styled tool button.

        Args:
            name: Button name/title
            description: Button description
            color: Button color hex code

        Returns:
            Styled button widget
        """
        button = QPushButton()
        button.setMinimumHeight(100)

        # Button layout
        button_layout = QVBoxLayout(button)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel(name)
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

        return button

    def setup_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """Setup bottom control buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        close_button = QPushButton("Close")
        close_button.setFixedSize(120, 40)
        close_button.clicked.connect(self.close)
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

        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def adjust_color(self, color: str, amount: int) -> str:
        """Adjust color brightness by amount.

        Args:
            color: Hex color string
            amount: Amount to adjust brightness

        Returns:
            Adjusted hex color string
        """
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        adjusted = [max(0, min(255, x + amount)) for x in rgb]
        return f'#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}'

    def launch_tool(self, tool_function: Optional[Callable]) -> None:
        """Launch a tool and close the System Tools window.

        Args:
            tool_function: Function to execute when launching the tool
        """
        if tool_function:
            self.close()
            try:
                tool_function()
                self.logger.debug(f"Launched tool: {tool_function.__name__}")
            except Exception as e:
                self.logger.exception(f"Error launching tool: {str(e)}")
        else:
            self.close()
            self.logger.debug("Tool not implemented yet")

    def launch_hardware_monitor(self) -> None:
        """Launch the hardware monitor window."""
        from gui.components.hardware_monitor import HardwareMonitorWindow

        try:
            hardware_monitor = HardwareMonitorWindow(self.config_manager, self)
            hardware_monitor.setStyleSheet("""
                QDialog {
                    background-color: #1a1b1e;
                }
            """)
            self.close()
            hardware_monitor.exec()
            self.logger.debug("Hardware monitor launched")
        except Exception as e:
            self.logger.exception(f"Error launching hardware monitor: {str(e)}")

    def start_system_update(self) -> None:
        """Start the system update process."""
        if hasattr(self.parent_window, 'start_system_update'):
            self.parent_window.start_system_update()
        else:
            self.logger.error("Parent window doesn't have start_system_update method")

    def start_service_manager(self) -> None:
        """Start the service manager."""
        if hasattr(self.parent_window, 'start_service_manager'):
            self.parent_window.start_service_manager()
        else:
            self.logger.error("Parent window doesn't have start_service_manager method")

    def start_disk_cleanup(self) -> None:
        """Start the disk cleanup tool.

        Like a digital waste management technician commanding a fleet of
        binary garbage trucks, this method initiates the process of purging
        the filesystem of computational refuse - temporary files, log rollovers,
        and cached data that clutters our digital existence.
        """
        if hasattr(self.parent_window, 'start_disk_cleanup'):
            self.parent_window.start_disk_cleanup()
        else:
            self.logger.error("Parent window doesn't have start_disk_cleanup method")

    def start_network_tool(self):
        """Launch the network configuration tool.

        Like a digital pilgrim embarking on a journey through invisible pathways,
        this method initiates the user's quest to tame the chaotic realm of
        network configurations.
        """
        if hasattr(self.parent_window, 'start_network_tool'):
            self.parent_window.start_network_tool()
        else:
            self.logger.error("Parent window doesn't have start_network_tool method")