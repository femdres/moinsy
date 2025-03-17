"""Network configuration dialog window for Moinsy.

Like a bridge between human intention and machine configuration,
this dialog provides a graphical interface for manipulating the
invisible threads of network communication that bind our digital
existence to the broader universe of data—an attempt to impose
order on the entropic chaos of connection protocols.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QScrollArea, QWidget, QGridLayout,
    QLineEdit, QSpinBox, QCheckBox, QMessageBox, QListWidget,
    QListWidgetItem, QSplitter, QGroupBox, QRadioButton,
    QButtonGroup, QTextEdit, QStyledItemDelegate, QStyle,
    QComboBox, QTabWidget
)
from PyQt6.QtGui import (
    QFont, QIcon, QPixmap, QColor, QPen, QBrush
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QSize, QRect
)

import logging
import time
from typing import Optional, Dict, Any, List, Union, Tuple, cast

from core.tools.network_tool import NetworkTool
from gui.styles.theme import Theme
from config import get_resource_path

class NetworkWindow(QDialog):
    """Network configuration and management window.

    This dialog presents network interfaces and provides
    tools for diagnostics, configuration, and testing.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the network configuration window.

        Args:
            parent: Optional parent widget

        Like all user interfaces, we prepare a stage upon which
        the drama of human-computer interaction will unfold.
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Pre-initialize UI elements that might be accessed by event handlers
        self.static_settings_group = None
        self._monitoring_active = False
        self._monitoring_data = []

        # Initialize attributes to prevent the void from staring back
        self.status_label = None  # Will be properly created in setup_status_bar
        self.log_output = None    # Will be properly created in setup_output_area

        # Initialize the network tool
        self.network_tool = NetworkTool(self)

        # Setup UI components - but carefully, for the universe is a fragile place
        try:
            self.setup_ui()
            # Only after UI is set up, connect signals
            self.connect_signals()
            # And only then load interfaces
            self.load_interfaces()
            self.logger.debug("Network window initialized")
        except Exception as e:
            self.logger.error(f"Error during initialization: {str(e)}", exc_info=True)
            # Create a minimal error UI
            self._create_error_ui(str(e))

    def connect_signals(self) -> None:
        """Connect signals from network tool to UI updates.

        Like synapses forming in a digital brain, these connections
        allow information to flow between disparate components.
        """
        try:
            # Connect network tool signals
            self.network_tool.log_output.connect(self.append_log)
            self.network_tool.error_occurred.connect(self.handle_error)
            self.network_tool.update_progress.connect(self.update_progress)
            self.network_tool.network_info_updated.connect(self.update_interface_info)
            self.network_tool.request_input.connect(self.handle_input_request)
        except Exception as e:
            self.logger.error(f"Error connecting signals: {str(e)}")

    def _create_error_ui(self, error_message: str) -> None:
        """Create a minimal UI when initialization fails.

        When the digital abyss opens before us, we craft a simple bridge
        across it - a minimal interface to acknowledge our failure.
        """
        # Clear any existing layout
        if self.layout():
            # The old layout must be deleted as layouts cannot be reused
            old_layout = self.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old_layout)  # This transfers ownership of the layout

        # Create new error layout
        error_layout = QVBoxLayout(self)
        error_label = QLabel(f"Error initializing network window: {error_message}")
        error_label.setStyleSheet("color: #dc2626; padding: 20px;")
        error_label.setWordWrap(True)
        error_layout.addWidget(error_label)

        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        error_layout.addWidget(close_button)

    def setup_ui(self) -> None:
        """Initialize the user interface components."""
        try:
            # Window properties
            self.setWindowTitle("Network Configuration")
            self.setMinimumSize(1000, 800)

            # Create a new main layout from scratch (avoid nested layout issues)
            if self.layout():
                # Remove any existing layout first
                old_layout = self.layout()
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                QWidget().setLayout(old_layout)  # Transfer ownership

            # Create fresh main layout
            main_layout = QVBoxLayout(self)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(15, 15, 15, 15)

            # Header section
            self.setup_header(main_layout)

            # Main content - split view
            splitter = QSplitter(Qt.Orientation.Horizontal)

            # Left panel - interface selection and info
            left_panel = self.create_left_panel()
            splitter.addWidget(left_panel)

            # Right panel - tabs for various tools
            right_panel = self.create_right_panel()
            splitter.addWidget(right_panel)

            # Set initial sizes - left panel smaller
            splitter.setSizes([300, 700])

            main_layout.addWidget(splitter, 1)

            # Status bar
            self.setup_status_bar(main_layout)

            # Apply styling
            self.apply_styling()
        except Exception as e:
            self.logger.error(f"Error setting up UI: {str(e)}", exc_info=True)
            # Create minimal UI in case of failure
            self._create_error_ui(str(e))

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup the header with title and refresh button.

        Args:
            layout: Parent layout to add the header to
        """
        header_layout = QHBoxLayout()

        # Title
        title = QLabel("Network Configuration")
        title.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Theme.get_color('PRIMARY')};")
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Monitor and configure network interfaces")
        subtitle.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')};")
        header_layout.addWidget(subtitle)

        header_layout.addStretch()

        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.get_color('CONTROL_BG')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {Theme.get_color('CONTROL_HOVER')};
            }}
        """)
        refresh_button.setFixedSize(100, 30)
        refresh_button.clicked.connect(self.refresh_interfaces)
        header_layout.addWidget(refresh_button)

        layout.addLayout(header_layout)

        # Add horizontal line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"background-color: {Theme.get_color('BG_LIGHT')};")
        layout.addWidget(line)

    def create_left_panel(self) -> QWidget:
        """Create the left panel with interface selection and details.

        Returns:
            Widget containing left panel components

        Like a digital cartographer's compass, this panel provides
        the means to select which network territory to explore.
        """
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Interface selection
        interfaces_group = QGroupBox("Network Interfaces")
        interfaces_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                margin-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Theme.get_color('PRIMARY')};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        interfaces_layout = QVBoxLayout(interfaces_group)

        # ===== Enhanced Interface Dropdown =====
        # Create a label above the dropdown to clearly indicate its purpose
        dropdown_label = QLabel("Select Network Interface:")
        dropdown_label.setStyleSheet(f"""
            color: {Theme.get_color('TEXT_PRIMARY')};
            font-weight: bold;
            margin-bottom: 4px;
        """)
        interfaces_layout.addWidget(dropdown_label)

        # Interface dropdown with enhanced styling
        self.interface_combo = QComboBox()
        self.interface_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.get_color('CONTROL_BG')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};  /* Added border */
                border-radius: 4px;
                padding: 8px 28px 8px 12px;  /* Increased right padding for arrow */
                min-height: 36px;  /* Increased height for better visibility */
                font-weight: bold;  /* Make text bold */
            }}
            
            /* Highlight on hover to indicate interactivity */
            QComboBox:hover {{
                background-color: {Theme.get_color('CONTROL_HOVER')};
                border: 1px solid {Theme.get_color('PRIMARY')};
            }}
            
            /* Style the drop-down arrow section */
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-left: 1px solid {Theme.get_color('BG_LIGHT')};  /* Vertical separator */
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: {Theme.get_color('PRIMARY')};  /* Colored background */
            }}
            
            /* Make the arrow more visible */
            QComboBox::down-arrow {{
                width: 14px;
                height: 14px;
            }}
            
            /* Style the dropdown menu */
            QComboBox QAbstractItemView {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                selection-background-color: {Theme.get_color('PRIMARY')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                padding: 4px;
            }}
        """)

        # Connect signal before adding to layout (to prevent signals from firing during setup)
        self.interface_combo.currentIndexChanged.connect(self.on_interface_selected)
        interfaces_layout.addWidget(self.interface_combo)

        # Interface details area
        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                width: 8px;
            }}
            QScrollBar::handle {{
                background-color: {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                height: 0px;
            }}
        """)

        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)

        # Placeholder when no interface is selected
        self.details_placeholder = QLabel("Select a network interface to view details")
        self.details_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_placeholder.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')};")
        self.details_placeholder.setWordWrap(True)
        self.details_layout.addWidget(self.details_placeholder)

        details_scroll.setWidget(self.details_widget)
        interfaces_layout.addWidget(details_scroll)

        left_layout.addWidget(interfaces_group)

        # Quick actions section
        actions_group = QGroupBox("Quick Actions")
        actions_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                margin-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Theme.get_color('TEXT_PRIMARY')};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        actions_layout = QVBoxLayout(actions_group)

        # DHCP button
        self.dhcp_button = QPushButton("Configure DHCP")
        self.dhcp_button.clicked.connect(self.configure_dhcp)
        self._style_action_button(self.dhcp_button, Theme.get_color('SUCCESS'))
        actions_layout.addWidget(self.dhcp_button)

        # Static IP button
        self.static_ip_button = QPushButton("Configure Static IP")
        self.static_ip_button.clicked.connect(self.configure_static_ip)
        self._style_action_button(self.static_ip_button, Theme.get_color('PRIMARY'))
        actions_layout.addWidget(self.static_ip_button)

        # Wireless connect button
        self.wireless_button = QPushButton("Connect to Wireless")
        self.wireless_button.clicked.connect(self.connect_wireless)
        self._style_action_button(self.wireless_button, Theme.get_color('SECONDARY'))
        actions_layout.addWidget(self.wireless_button)

        left_layout.addWidget(actions_group)

        # Add Troubleshoot section
        troubleshoot_group = QGroupBox("Network Troubleshooting")
        troubleshoot_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                margin-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {Theme.get_color('TEXT_PRIMARY')};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        troubleshoot_layout = QVBoxLayout(troubleshoot_group)

        # Connection test button
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self.test_connection)
        self._style_action_button(self.test_connection_button, Theme.get_color('WARNING'))
        troubleshoot_layout.addWidget(self.test_connection_button)

        # DNS test button
        self.test_dns_button = QPushButton("Test DNS Resolution")
        self.test_dns_button.clicked.connect(self.test_dns)
        self._style_action_button(self.test_dns_button, Theme.get_color('TERTIARY'))
        troubleshoot_layout.addWidget(self.test_dns_button)

        # Add other troubleshooting buttons
        self.show_routes_button = QPushButton("Show Routing Table")
        self.show_routes_button.clicked.connect(self.show_routing_table)
        self._style_action_button(self.show_routes_button, Theme.get_color('CONTROL_BG'))
        troubleshoot_layout.addWidget(self.show_routes_button)

        left_layout.addWidget(troubleshoot_group)

        # Initial state - disable buttons until interface is selected
        self._set_interface_action_state(False)

        return left_panel

    def create_right_panel(self) -> QWidget:
        """Create the right panel with tabbed sections for different tools.

        Returns:
            Widget containing right panel components

        Like a book with chapters of network mysteries, this panel
        presents different facets of our digital connection.
        """
        # Create the right panel - a simplified stub to be expanded later
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget (simplified for now)
        self.tab_widget = QTabWidget()

        # Output/Log tab - a basic starting point
        self.log_tab = QWidget()
        log_layout = QVBoxLayout(self.log_tab)

        # Add terminal-style output area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.get_color('TERMINAL_BG')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
        """)
        log_layout.addWidget(self.log_output)

        self.tab_widget.addTab(self.log_tab, "Log Output")
        right_layout.addWidget(self.tab_widget)

        return right_panel

    def setup_status_bar(self, layout: QVBoxLayout) -> None:
        """Setup status bar with progress information.

        Args:
            layout: Parent layout to add the status bar to

        Like a dashboard in a ship navigating digital seas,
        this status bar provides essential navigational information.
        """
        # Create status bar frame
        status_bar = QFrame()
        status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
            }}
        """)

        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 5, 10, 5)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        # Progress indicator
        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet(f"color: {Theme.get_color('PRIMARY')};")
        status_layout.addWidget(self.progress_label)

        # Add to main layout
        layout.addWidget(status_bar)

    def apply_styling(self) -> None:
        """Apply consistent styling to the dialog."""
        # Apply main dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
            }}
            QLabel {{
                color: {Theme.get_color('TEXT_PRIMARY')};
            }}
        """)

    def _style_action_button(self, button: QPushButton, color: str) -> None:
        """Apply consistent styling to action buttons."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.adjust_color(color, -20)};
            }}
            QPushButton:disabled {{
                background-color: {Theme.get_color('BG_LIGHT')};
                color: {Theme.get_color('TEXT_SECONDARY')};
            }}
        """)
        button.setMinimumHeight(36)

    def _set_interface_action_state(self, enabled: bool) -> None:
        """Enable or disable interface-specific action buttons."""
        # Helper method to prevent the void of undefined buttons
        if hasattr(self, 'dhcp_button'):
            self.dhcp_button.setEnabled(enabled)
        if hasattr(self, 'static_ip_button'):
            self.static_ip_button.setEnabled(enabled)
        if hasattr(self, 'wireless_button'):
            self.wireless_button.setEnabled(False)  # Always start this disabled
        if hasattr(self, 'test_connection_button'):
            self.test_connection_button.setEnabled(enabled)
        if hasattr(self, 'test_dns_button'):
            self.test_dns_button.setEnabled(enabled)
        if hasattr(self, 'show_routes_button'):
            self.show_routes_button.setEnabled(enabled)

    def on_interface_selected(self, index: int) -> None:
        """Handle interface selection change.

        Args:
            index: Selected index in the combo box

        Like a lighthouse keeper switching their focus to a new
        section of the sea, we pivot our attention to a different interface.
        """
        if index < 0:
            # The void of no selection - handle gracefully
            return

        # Get the interface name - our digital identifier
        ifname = self.interface_combo.itemData(index)
        if not ifname:
            # Another void - an empty identifier
            return

        # Log the selection
        self.append_log(f"Selected interface: {ifname}", "cyan")

        # Enable or disable appropriate actions
        self._set_interface_action_state(True)

        # Let the network tool know our selection
        if hasattr(self.network_tool, 'select_interface'):
            self.network_tool.select_interface(ifname)

    def append_log(self, message: str, color: str = "white") -> None:
        """Append a message to the log output.

        Args:
            message: Message to append
            color: Text color

        Like a digital scribe recording the epic of our networking journey,
        this method captures the narrative of our attempts to connect.
        """
        try:
            # Add the message with the specified color
            if hasattr(self, 'log_output') and self.log_output is not None:
                self.log_output.append(f'<span style="color: {color};">{message}</span>')

                # Auto-scroll to bottom
                scrollbar = self.log_output.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            self.logger.error(f"Error appending to log: {str(e)}")

    def handle_error(self, error_message: str) -> None:
        """Handle and display error messages.

        Args:
            error_message: Error message to display

        Like a digital therapist acknowledging our technological trauma,
        this method processes the emotional impact of network failures.
        """
        self.append_log(f"Error: {error_message}", "red")
        if hasattr(self, 'status_label') and self.status_label is not None:
            self.status_label.setText("Error")

    def update_progress(self, value: int) -> None:
        """Update progress indicator.

        Args:
            value: Progress value (0-100)

        Like the slow progress bar of existence itself, this method
        marks our journey through digital time and space.
        """
        if hasattr(self, 'progress_label') and self.progress_label is not None:
            self.progress_label.setText(f"{value}%")

        if value == 0 and hasattr(self, 'status_label') and self.status_label is not None:
            self.status_label.setText("Ready")
        elif value == 100 and hasattr(self, 'status_label') and self.status_label is not None:
            self.status_label.setText("Completed")

    def handle_input_request(self, prompt: str, callback: str) -> None:
        """Handle input requests from network tool."""
        # A placeholder for future input request handling
        self.append_log(prompt, "yellow")

    def update_interface_info(self, interfaces: Dict[str, Dict[str, Any]]) -> None:
        """Update interface information in the UI."""
        # We'll implement this properly later
        pass

    def load_interfaces(self) -> None:
        """Load network interfaces from the system."""
        try:
            if hasattr(self, 'status_label') and self.status_label is not None:
                self.status_label.setText("Loading interfaces...")

            self.append_log("Loading network interfaces...", "white")

            # Clear existing interfaces
            if hasattr(self, 'interface_combo'):
                self.interface_combo.clear()

            # Get interfaces from network tool
            interfaces = self.network_tool.get_network_interfaces()

            if not interfaces:
                self.append_log("No network interfaces found.", "yellow")
                return

            # Sort interfaces - put ethernet and wireless first
            sorted_interfaces = sorted(
                interfaces.keys(),
                key=lambda x: (
                    0 if interfaces[x].get("type") == "ethernet" else
                    1 if interfaces[x].get("type") == "wireless" else
                    2
                )
            )

            # Add to combo box - with visually distinct styling
            for ifname in sorted_interfaces:
                interface_type = interfaces[ifname].get("type", "unknown")
                self.interface_combo.addItem(f"{ifname} ({interface_type})", ifname)

            if hasattr(self, 'status_label') and self.status_label is not None:
                self.status_label.setText(f"Found {len(interfaces)} interfaces")

        except Exception as e:
            self.logger.error(f"Error loading interfaces: {str(e)}")
            self.append_log(f"Error loading interfaces: {str(e)}", "red")
            if hasattr(self, 'status_label') and self.status_label is not None:
                self.status_label.setText("Error loading interfaces")

    def refresh_interfaces(self) -> None:
        """Refresh network interface information."""
        self.load_interfaces()

    # Stub methods for actions - to be implemented later
    def configure_dhcp(self) -> None:
        """Configure the selected interface to use DHCP."""
        self.append_log("DHCP configuration requested...", "green")
        # Will be implemented later

    def configure_static_ip(self) -> None:
        """Show static IP configuration interface."""
        self.append_log("Static IP configuration requested...", "blue")
        # Will be implemented later

    def connect_wireless(self) -> None:
        """Connect to a wireless network."""
        self.append_log("Wireless connection requested...", "purple")
        # Will be implemented later

    def test_connection(self) -> None:
        """Test network connectivity."""
        self.append_log("Connection test requested...", "yellow")
        # Will be implemented later

    def test_dns(self) -> None:
        """Test DNS resolution."""
        self.append_log("DNS test requested...", "purple")
        # Will be implemented later

    def show_routing_table(self) -> None:
        """Show network routing table."""
        self.append_log("Routing table requested...", "gray")
        # Will be implemented later