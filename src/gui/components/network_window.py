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
    QComboBox, QTabWidget, QFormLayout, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import (
    QFont, QIcon, QPixmap, QColor, QPen, QBrush
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QSize, QRect, QTimer
)

import logging
import time
import re
import ipaddress
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

            # Set initial sizes - panels same size
            splitter.setSizes([500, 500])

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

        # Add monitoring tab
        self.monitoring_tab = self.create_monitoring_tab()
        self.tab_widget.addTab(self.monitoring_tab, "Network Monitoring")

        # Add connections tab
        self.connections_tab = self.create_connections_tab()
        self.tab_widget.addTab(self.connections_tab, "Active Connections")

        return right_panel

    def create_monitoring_tab(self) -> QWidget:
        """Create tab for network monitoring.

        Returns:
            Widget containing monitoring components

        Like a digital observatory tracking the movement of binary stars,
        this tab allows us to witness the ebb and flow of network traffic.
        """
        monitoring_tab = QWidget()
        mon_layout = QVBoxLayout(monitoring_tab)

        # Controls for monitoring
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        controls_layout = QHBoxLayout(controls_frame)

        # Start/Stop monitoring button
        self.monitor_toggle_button = QPushButton("Start Monitoring")
        self.monitor_toggle_button.clicked.connect(self.toggle_monitoring)
        self._style_action_button(self.monitor_toggle_button, Theme.get_color('SUCCESS'))
        self.monitor_toggle_button.setEnabled(False)  # Disabled until interface selected
        controls_layout.addWidget(self.monitor_toggle_button)

        # Interval selector
        interval_label = QLabel("Update interval:")
        interval_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
        controls_layout.addWidget(interval_label)

        self.interval_combo = QComboBox()
        self.interval_combo.addItem("1 second", 1)
        self.interval_combo.addItem("3 seconds", 3)
        self.interval_combo.addItem("5 seconds", 5)
        self.interval_combo.addItem("10 seconds", 10)
        self.interval_combo.setCurrentIndex(2)  # Default to 5 seconds
        self.interval_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.get_color('CONTROL_BG')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: none;
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        controls_layout.addWidget(self.interval_combo)

        # Export data button
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_monitoring_data)
        self._style_action_button(self.export_button, Theme.get_color('CONTROL_BG'))
        self.export_button.setEnabled(False)
        controls_layout.addWidget(self.export_button)

        controls_layout.addStretch()
        mon_layout.addWidget(controls_frame)

        # Traffic display
        self.traffic_display = QTextEdit()
        self.traffic_display.setReadOnly(True)
        self.traffic_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.get_color('TERMINAL_BG')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
        """)
        mon_layout.addWidget(self.traffic_display)

        return monitoring_tab

    def create_connections_tab(self) -> QWidget:
        """Create tab for active connections.

        Returns:
            Widget containing connections table

        Like a census taker counting digital citizens, this tab
        catalogs the active network connections traversing our interface.
        """
        connections_tab = QWidget()
        conn_layout = QVBoxLayout(connections_tab)

        # Controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        controls_layout = QHBoxLayout(controls_frame)

        # Refresh button
        refresh_connections_button = QPushButton("Refresh Connections")
        refresh_connections_button.clicked.connect(self.refresh_connections)
        self._style_action_button(refresh_connections_button, Theme.get_color('CONTROL_BG'))
        controls_layout.addWidget(refresh_connections_button)

        controls_layout.addStretch()
        conn_layout.addWidget(controls_frame)

        # Connections table
        self.connections_table = QTableWidget(0, 4)  # Rows, Columns
        self.connections_table.setHorizontalHeaderLabels(["Protocol", "Local Address", "Remote Address", "State"])
        self.connections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.connections_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only
        self.connections_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                gridline-color: {Theme.get_color('BG_LIGHT')};
                border: none;
                border-radius: 4px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {Theme.get_color('CONTROL_BG')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                padding: 5px;
                border: none;
            }}
        """)
        conn_layout.addWidget(self.connections_table)

        return connections_tab

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
        if hasattr(self, 'monitor_toggle_button'):
            self.monitor_toggle_button.setEnabled(enabled)

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
            success = self.network_tool.select_interface(ifname)

            # Check if interface is wireless to enable/disable wireless button
            if success and hasattr(self, 'wireless_button'):
                interface_info = self.network_tool.interfaces.get(ifname, {})
                is_wireless = interface_info.get("wireless", False)
                self.wireless_button.setEnabled(is_wireless)

                if is_wireless:
                    self.append_log("Wireless interface detected - wireless options enabled", "green")
                else:
                    self.append_log("Not a wireless interface - wireless options disabled", "yellow")

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

    def update_interface_info(self, info: Dict[str, Any]) -> None:
        """Update interface information in the UI.

        Args:
            info: Dictionary containing interface information

        Like a curator updating an exhibition of digital artifacts,
        this method refreshes our display of network information.
        """
        try:
            # Check if we received monitoring data
            if "monitor_data" in info:
                self.update_monitoring_display(info["monitor_data"])
                return

            # For interface updates, refresh the details view
            self.refresh_interface_details()

        except Exception as e:
            self.logger.error(f"Error updating interface info: {str(e)}")
            self.handle_error(f"Failed to update interface information: {str(e)}")

    def refresh_interface_details(self) -> None:
        """Refresh the interface details display.

        Like a necromancer attempting to resurrect digital UI elements
        that may have already crossed into the void of garbage collection,
        this method carefully creates new widgets while ensuring old ones
        are properly laid to rest.
        """
        # Store widget references to prevent premature deletion
        self._detail_widgets = []  # Type: List[QWidget]

        try:
            # First verify we have a valid interface selected
            index = self.interface_combo.currentIndex()
            if index < 0:
                self.logger.debug("No interface selected, skipping details refresh")
                return

            ifname = self.interface_combo.itemData(index)
            if not ifname or ifname not in self.network_tool.interfaces:
                self.logger.debug(f"Interface {ifname} not found, skipping details refresh")
                return

            # Check if our layout container still exists in the realm of the living
            if not hasattr(self, 'details_layout') or not self.details_layout:
                self.logger.warning("Details layout doesn't exist, cannot refresh interface details")
                return

            # Safely clear existing details - a digital funeral for the previous widgets
            self._safely_clear_layout(self.details_layout)

            # Get interface details from the cosmic network database
            interface = self.network_tool.interfaces[ifname]

            # Create details frame - a new vessel for our interface information
            details_frame = QFrame()
            self._detail_widgets.append(details_frame)  # Prevent premature deletion

            details_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 10px;
                }}
            """)

            details_layout = QVBoxLayout(details_frame)

            # Interface name and type - our digital identity
            header = QLabel(f"{ifname} ({interface.get('type', 'unknown')})")
            self._detail_widgets.append(header)  # Prevent garbage collection
            header.setStyleSheet(f"color: {Theme.get_color('PRIMARY')}; font-size: 16px; font-weight: bold;")
            details_layout.addWidget(header)

            # MAC address - the immutable name given at birth
            mac_addr = interface.get('mac_address', 'Unknown')
            mac = QLabel(f"MAC Address: {mac_addr}")
            self._detail_widgets.append(mac)
            mac.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
            details_layout.addWidget(mac)

            # State - our existential condition in the network
            state_text = interface.get('state', 'unknown')
            state_color = '#4CAF50' if state_text == 'UP' else '#FFC107' if state_text == 'UNKNOWN' else '#dc2626'
            state = QLabel(f"State: {state_text}")
            self._detail_widgets.append(state)
            state.setStyleSheet(f"color: {state_color}; font-size: 14px; font-weight: bold;")
            details_layout.addWidget(state)

            # Divider - the void separating sections of our existence
            divider = QFrame()
            self._detail_widgets.append(divider)
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setFrameShadow(QFrame.Shadow.Sunken)
            divider.setStyleSheet(f"background-color: {Theme.get_color('BG_LIGHT')};")
            details_layout.addWidget(divider)

            # Addresses - our locations in the digital universe
            addresses = interface.get('addresses', [])
            addr_label = QLabel("IP Addresses:")
            self._detail_widgets.append(addr_label)
            addr_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 14px; font-weight: bold;")
            details_layout.addWidget(addr_label)

            if addresses:
                for addr in addresses:
                    addr_text = f"{addr.get('address', 'Unknown')}/{addr.get('prefix', '')}"
                    addr_type = addr.get('type', 'unknown')
                    addr_item = QLabel(f"{addr_text} ({addr_type})")
                    self._detail_widgets.append(addr_item)
                    addr_item.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
                    details_layout.addWidget(addr_item)
            else:
                no_addr = QLabel("No IP addresses configured")
                self._detail_widgets.append(no_addr)
                no_addr.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-size: 12px;")
                details_layout.addWidget(no_addr)

            # Add wireless info if relevant - our ethereal connection to the digital ether
            if interface.get('wireless', False):
                # Divider
                divider2 = QFrame()
                self._detail_widgets.append(divider2)
                divider2.setFrameShape(QFrame.Shape.HLine)
                divider2.setFrameShadow(QFrame.Shadow.Sunken)
                divider2.setStyleSheet(f"background-color: {Theme.get_color('BG_LIGHT')};")
                details_layout.addWidget(divider2)

                # Wireless header
                wireless_label = QLabel("Wireless Information:")
                self._detail_widgets.append(wireless_label)
                wireless_label.setStyleSheet(f"color: {Theme.get_color('SECONDARY')}; font-size: 14px; font-weight: bold;")
                details_layout.addWidget(wireless_label)

                # Wireless details
                wireless_info = interface.get('wireless_info', {})
                if wireless_info:
                    ssid = wireless_info.get('ssid', '')
                    if ssid:
                        ssid_label = QLabel(f"SSID: {ssid}")
                        self._detail_widgets.append(ssid_label)
                        ssid_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
                        details_layout.addWidget(ssid_label)

                        # Signal strength - our tenuous connection to the wireless essence
                        signal = wireless_info.get('signal_level', '')
                        if signal:
                            signal_label = QLabel(f"Signal: {signal}")
                            self._detail_widgets.append(signal_label)
                            signal_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
                            details_layout.addWidget(signal_label)

                        # Frequency - the vibration of our digital soul
                        freq = wireless_info.get('frequency', '')
                        if freq:
                            freq_label = QLabel(f"Frequency: {freq}")
                            self._detail_widgets.append(freq_label)
                            freq_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
                            details_layout.addWidget(freq_label)
                    else:
                        no_conn = QLabel("Not connected to any wireless network")
                        self._detail_widgets.append(no_conn)
                        no_conn.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-size: 12px;")
                        details_layout.addWidget(no_conn)
                else:
                    no_info = QLabel("No wireless information available")
                    self._detail_widgets.append(no_info)
                    no_info.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-size: 12px;")
                    details_layout.addWidget(no_info)

            # Add statistics if available - the accounting of our digital transactions
            stats = interface.get('statistics', {})
            if stats:
                # Divider
                divider3 = QFrame()
                self._detail_widgets.append(divider3)
                divider3.setFrameShape(QFrame.Shape.HLine)
                divider3.setFrameShadow(QFrame.Shadow.Sunken)
                divider3.setStyleSheet(f"background-color: {Theme.get_color('BG_LIGHT')};")
                details_layout.addWidget(divider3)

                # Stats header
                stats_label = QLabel("Traffic Statistics:")
                self._detail_widgets.append(stats_label)
                stats_label.setStyleSheet(f"color: {Theme.get_color('WARNING')}; font-size: 14px; font-weight: bold;")
                details_layout.addWidget(stats_label)

                # Calculate MB
                rx_bytes = stats.get('rx_bytes', 0)
                tx_bytes = stats.get('tx_bytes', 0)
                rx_mb = rx_bytes / (1024 * 1024) if rx_bytes else 0
                tx_mb = tx_bytes / (1024 * 1024) if tx_bytes else 0

                rx_label = QLabel(f"Received: {rx_mb:.2f} MB ({stats.get('rx_packets', 0)} packets)")
                self._detail_widgets.append(rx_label)
                rx_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
                details_layout.addWidget(rx_label)

                tx_label = QLabel(f"Sent: {tx_mb:.2f} MB ({stats.get('tx_packets', 0)} packets)")
                self._detail_widgets.append(tx_label)
                tx_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
                details_layout.addWidget(tx_label)

                errors_label = QLabel(f"Errors - RX: {stats.get('rx_errors', 0)}, TX: {stats.get('tx_errors', 0)}")
                self._detail_widgets.append(errors_label)
                errors_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 12px;")
                details_layout.addWidget(errors_label)

            # Finally, add the details frame to the main layout - our container rejoins the hierarchy
            if self.details_layout is not None:
                self.details_layout.addWidget(details_frame)

                # Hide placeholder if it exists and hasn't been garbage collected
                if hasattr(self, 'details_placeholder') and self.details_placeholder is not None:
                    try:
                        self.details_placeholder.setVisible(False)
                    except RuntimeError:
                        # Widget may have been deleted, just continue
                        self.logger.debug("Details placeholder widget already deleted")

        except RuntimeError as e:
            # Special handling for Qt C++ object deleted errors
            if "C/C++ object" in str(e) and "deleted" in str(e):
                self.logger.warning(f"Qt widget reference error during refresh: {str(e)}")
                # Silently fail - this is often harmless and happens during UI transitions
            else:
                self.logger.error(f"Runtime error refreshing interface details: {str(e)}")
                self.handle_error(f"Interface display error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error refreshing interface details: {str(e)}")
            self.handle_error(f"Failed to refresh interface details: {str(e)}")

    def _safely_clear_layout(self, layout: QVBoxLayout) -> None:
        """Safely clear all widgets from a layout without causing reference errors.

        Args:
            layout: The layout to clear

        Like a careful archaeologist removing artifacts without damaging them,
        this method removes widgets from a layout while ensuring they're
        properly deleted to prevent memory leaks or reference errors.
        """
        if layout is None:
            return

        try:
            # Take one item at a time from the layout until it's empty
            while layout.count():
                # Get the first item
                item = layout.takeAt(0)

                # Check if the item has a widget
                if item.widget():
                    # Schedule the widget for deletion rather than deleting immediately
                    # This helps prevent "wrapped C/C++ object deleted" errors
                    widget = item.widget()
                    widget.setParent(None)  # Detach from parent hierarchy
                    widget.deleteLater()  # Schedule for deletion when event loop processes events

                # If item has a layout, recursively clear it
                elif item.layout():
                    self._safely_clear_layout(item.layout())

                # Delete the layout item itself
                del item
        except Exception as e:
            self.logger.warning(f"Error during layout clearing: {str(e)}")
            # Continue even if errors occur - best effort clearing

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

    def configure_dhcp(self) -> None:
        """Configure the selected interface to use DHCP.

        Like submitting to the chaotic whims of the network gods,
        this method surrenders IP configuration to the DHCP server's
        arbitrary decisions - a surrender of control that ironically
        often yields greater connectivity.
        """
        try:
            # Get current interface
            index = self.interface_combo.currentIndex()
            if index < 0:
                self.handle_error("No interface selected")
                return

            ifname = self.interface_combo.itemData(index)
            if not ifname:
                self.handle_error("Invalid interface selection")
                return

            # Confirm with user
            confirm = QMessageBox.question(
                self,
                "Configure DHCP",
                f"Are you sure you want to configure {ifname} to use DHCP?\n\nThis will replace any static IP configuration.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No  # Default to No - prevent accidental changes
            )

            if confirm != QMessageBox.StandardButton.Yes:
                self.append_log("DHCP configuration cancelled.", "yellow")
                return

            # Configure DHCP
            self.append_log(f"Configuring {ifname} to use DHCP...", "green")

            if not hasattr(self.network_tool, 'configure_dhcp'):
                self.handle_error("DHCP configuration not implemented in network tool")
                return

            success = self.network_tool.configure_dhcp()

            if success:
                self.append_log("DHCP configuration successful.", "green")
                # Refresh interface details
                self.refresh_interface_details()
            else:
                self.handle_error("DHCP configuration failed")

        except Exception as e:
            self.logger.error(f"Error configuring DHCP: {str(e)}")
            self.handle_error(f"DHCP configuration error: {str(e)}")

    def configure_static_ip(self) -> None:
        """Show static IP configuration interface.

        Like a digital hermit staking a permanent claim in the
        wilderness of the network, this method allows a user to
        assign a fixed address amidst the chaos of dynamic allocation.
        """
        try:
            # Get current interface
            index = self.interface_combo.currentIndex()
            if index < 0:
                self.handle_error("No interface selected")
                return

            ifname = self.interface_combo.itemData(index)
            if not ifname:
                self.handle_error("Invalid interface selection")
                return

            # Create static IP dialog
            static_dialog = QDialog(self)
            static_dialog.setWindowTitle(f"Configure Static IP for {ifname}")
            static_dialog.setMinimumWidth(400)
            static_dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {Theme.get_color('BG_DARK')};
                }}
                QLabel {{
                    color: {Theme.get_color('TEXT_PRIMARY')};
                }}
                QLineEdit {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 8px;
                }}
                QSpinBox {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)

            # Create form layout
            layout = QVBoxLayout(static_dialog)

            # Form content
            form_layout = QFormLayout()
            form_layout.setSpacing(10)

            # IP Address
            ip_label = QLabel("IP Address:")
            self.ip_edit = QLineEdit()
            self.ip_edit.setPlaceholderText("192.168.1.100")
            form_layout.addRow(ip_label, self.ip_edit)

            # Subnet Mask (as CIDR prefix)
            prefix_label = QLabel("Subnet Prefix Length:")
            self.prefix_spin = QSpinBox()
            self.prefix_spin.setRange(0, 32)
            self.prefix_spin.setValue(24)  # Common default
            self.prefix_spin.setToolTip("CIDR notation bits (e.g., 24 for 255.255.255.0)")
            form_layout.addRow(prefix_label, self.prefix_spin)

            # Gateway
            gateway_label = QLabel("Gateway:")
            self.gateway_edit = QLineEdit()
            self.gateway_edit.setPlaceholderText("192.168.1.1")
            form_layout.addRow(gateway_label, self.gateway_edit)

            # DNS Servers
            dns_label = QLabel("DNS Servers:")
            self.dns_edit = QLineEdit()
            self.dns_edit.setPlaceholderText("8.8.8.8, 8.8.4.4")
            self.dns_edit.setToolTip("Comma-separated list of DNS server IPs")
            form_layout.addRow(dns_label, self.dns_edit)

            # Add form to dialog
            layout.addLayout(form_layout)

            # Add validation message area
            self.validation_label = QLabel("")
            self.validation_label.setStyleSheet("color: #dc2626;")
            self.validation_label.setWordWrap(True)
            layout.addWidget(self.validation_label)

            # Add buttons
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(lambda: self.apply_static_ip(static_dialog, ifname))
            button_box.rejected.connect(static_dialog.reject)

            # Style buttons
            for button in button_box.buttons():
                if button_box.buttonRole(button) == QDialogButtonBox.ButtonRole.AcceptRole:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('PRIMARY')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)
                else:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('CONTROL_BG')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)

            layout.addWidget(button_box)

            # Try to pre-fill with current IP if available
            self.prefill_static_ip_form(ifname)

            # Show dialog
            static_dialog.exec()

        except Exception as e:
            self.logger.error(f"Error setting up static IP dialog: {str(e)}")
            self.handle_error(f"Failed to show static IP configuration: {str(e)}")

    def prefill_static_ip_form(self, ifname: str) -> None:
        """Pre-fill the static IP form with current interface settings.

        Args:
            ifname: Interface name

        Like an archaeologist reconstructing an ancient artifact,
        this method attempts to discern the current configuration
        and present it for potential modification.
        """
        try:
            # Get interface details
            interface = self.network_tool.interfaces.get(ifname, {})

            # Find IPv4 address if available
            addresses = interface.get('addresses', [])
            for addr in addresses:
                if addr.get('type') == 'ipv4':
                    # Found an IPv4 address
                    if hasattr(self, 'ip_edit'):
                        self.ip_edit.setText(addr.get('address', ''))

                    # Set prefix
                    if hasattr(self, 'prefix_spin'):
                        prefix = addr.get('prefix')
                        if prefix and isinstance(prefix, int):
                            self.prefix_spin.setValue(prefix)

                    # We got what we need
                    break

            # Try to guess gateway (not always accurate)
            # A proper implementation would get this from the routing table
            if hasattr(self, 'gateway_edit') and hasattr(self, 'ip_edit'):
                ip = self.ip_edit.text()
                if ip and '.' in ip:
                    # Crude heuristic: assume gateway is .1 in the subnet
                    parts = ip.split('.')
                    if len(parts) == 4:
                        parts[3] = '1'
                        gateway = '.'.join(parts)
                        self.gateway_edit.setText(gateway)

            # Pre-fill DNS with common servers if no better option
            if hasattr(self, 'dns_edit'):
                dns_servers = self.network_tool.dns_servers
                if dns_servers:
                    self.dns_edit.setText(', '.join(dns_servers))
                else:
                    # Fallback to common DNS servers
                    self.dns_edit.setText("8.8.8.8, 8.8.4.4")

        except Exception as e:
            self.logger.error(f"Error pre-filling static IP form: {str(e)}")
            # Non-fatal error, continue without pre-filling

    def apply_static_ip(self, dialog: QDialog, ifname: str) -> None:
        """Apply static IP configuration to the selected interface.

        Args:
            dialog: The dialog containing configuration inputs
            ifname: Interface name to configure

        Like a digital architect laying the foundation of a network presence,
        this method attempts to establish a fixed address in the flowing
        river of IP allocations.
        """
        try:
            # Validate input
            if not self.validate_static_ip_input():
                # Validation failed - error message is shown by validate method
                return

            # Get values from form
            ip_address = self.ip_edit.text().strip()
            prefix_len = self.prefix_spin.value()
            gateway = self.gateway_edit.text().strip()

            # Parse DNS servers
            dns_servers = []
            dns_text = self.dns_edit.text().strip()
            if dns_text:
                for dns in re.split(r',\s*', dns_text):
                    dns = dns.strip()
                    if dns:
                        dns_servers.append(dns)

            # Confirm with user
            confirm_msg = f"Apply the following configuration to {ifname}?\n\n"
            confirm_msg += f"IP Address: {ip_address}/{prefix_len}\n"
            confirm_msg += f"Gateway: {gateway}\n"
            confirm_msg += f"DNS Servers: {', '.join(dns_servers)}\n\n"
            confirm_msg += "This will replace any existing configuration."

            confirm = QMessageBox.question(
                dialog,
                "Confirm Static IP Configuration",
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No  # Default to No - prevent accidental changes
            )

            if confirm != QMessageBox.StandardButton.Yes:
                return

            # Close the dialog
            dialog.accept()

            # Apply the configuration
            self.append_log(f"Applying static IP configuration to {ifname}...", "blue")

            if not hasattr(self.network_tool, 'configure_static_ip'):
                self.handle_error("Static IP configuration not implemented in network tool")
                return

            success = self.network_tool.configure_static_ip(
                ip_address, prefix_len, gateway, dns_servers
            )

            if success:
                self.append_log("Static IP configuration successful.", "green")
                # Refresh interface details
                self.refresh_interface_details()
            else:
                self.handle_error("Static IP configuration failed")

        except Exception as e:
            self.logger.error(f"Error applying static IP: {str(e)}")
            self.handle_error(f"Static IP configuration error: {str(e)}")

    def validate_static_ip_input(self) -> bool:
        """Validate static IP configuration input.

        Returns:
            True if input is valid, False otherwise

        Like a meticulous bureaucrat scrutinizing paperwork,
        this method ensures our network configuration adheres
        to the strict protocols of IP addressing.
        """
        try:
            # Clear previous validation message
            if hasattr(self, 'validation_label'):
                self.validation_label.setText("")

            # Validate IP address
            if not hasattr(self, 'ip_edit'):
                raise ValueError("IP address field not found")

            ip_address = self.ip_edit.text().strip()
            if not ip_address:
                self.validation_label.setText("IP address is required")
                return False

            try:
                ipaddress.IPv4Address(ip_address)
            except ipaddress.AddressValueError:
                self.validation_label.setText("Invalid IP address format")
                return False

            # Validate gateway
            if not hasattr(self, 'gateway_edit'):
                raise ValueError("Gateway field not found")

            gateway = self.gateway_edit.text().strip()
            if not gateway:
                self.validation_label.setText("Gateway address is required")
                return False

            try:
                ipaddress.IPv4Address(gateway)
            except ipaddress.AddressValueError:
                self.validation_label.setText("Invalid gateway address format")
                return False

            # Validate DNS servers
            if not hasattr(self, 'dns_edit'):
                raise ValueError("DNS field not found")

            dns_text = self.dns_edit.text().strip()
            if dns_text:
                dns_servers = re.split(r',\s*', dns_text)
                for dns in dns_servers:
                    dns = dns.strip()
                    if dns:
                        try:
                            ipaddress.IPv4Address(dns)
                        except ipaddress.AddressValueError:
                            self.validation_label.setText(f"Invalid DNS server address: {dns}")
                            return False
            else:
                self.validation_label.setText("At least one DNS server is required")
                return False

            # All validation passed
            return True

        except Exception as e:
            self.logger.error(f"Error validating static IP input: {str(e)}")
            if hasattr(self, 'validation_label'):
                self.validation_label.setText(f"Validation error: {str(e)}")
            return False

    def connect_wireless(self) -> None:
        """Connect to a wireless network.

        Like a digital courtship ritual, this method initiates
        the process of wooing a wireless network with credentials,
        hoping for a successful connection.
        """
        try:
            # Get current interface
            index = self.interface_combo.currentIndex()
            if index < 0:
                self.handle_error("No interface selected")
                return

            ifname = self.interface_combo.itemData(index)
            if not ifname:
                self.handle_error("Invalid interface selection")
                return

            # Check if interface is wireless
            interface = self.network_tool.interfaces.get(ifname, {})
            if not interface.get('wireless', False):
                self.handle_error(f"Interface {ifname} is not a wireless interface")
                return

            # Scan for networks first
            self.append_log(f"Scanning for wireless networks on {ifname}...", "blue")

            if not hasattr(self.network_tool, 'scan_wireless_networks'):
                self.handle_error("Wireless scanning not implemented in network tool")
                return

            networks = self.network_tool.scan_wireless_networks()

            if not networks:
                self.handle_error("No wireless networks found or scanning failed")
                return

            # Create wireless dialog
            wireless_dialog = QDialog(self)
            wireless_dialog.setWindowTitle(f"Connect to Wireless Network - {ifname}")
            wireless_dialog.setMinimumWidth(450)
            wireless_dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {Theme.get_color('BG_DARK')};
                }}
                QLabel {{
                    color: {Theme.get_color('TEXT_PRIMARY')};
                }}
                QLineEdit {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)

            # Create layout
            layout = QVBoxLayout(wireless_dialog)

            # Network selection
            selection_label = QLabel("Available Networks:")
            selection_label.setStyleSheet(f"color: {Theme.get_color('SECONDARY')}; font-weight: bold;")
            layout.addWidget(selection_label)

            # Create network list
            self.network_list = QListWidget()
            self.network_list.setStyleSheet(f"""
                QListWidget {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 5px;
                }}
                QListWidget::item {{
                    padding: 10px;
                    border-bottom: 1px solid {Theme.get_color('BG_LIGHT')};
                }}
                QListWidget::item:selected {{
                    background-color: {Theme.get_color('SECONDARY')};
                    color: white;
                }}
            """)

            # Add networks to list
            for i, network in enumerate(networks):
                ssid = network.get('ssid', f'Unknown Network {i}')
                signal = network.get('signal', 0)
                security = network.get('security', '')

                # Format item text
                text = f"{ssid}"
                if security:
                    text += f" 🔒"  # Lock icon for secured networks

                # Create signal strength indicator
                signal_strength = self.network_tool._signal_strength_bars(signal)

                # Create list item
                item = QListWidgetItem(f"{text}  {signal_strength}  ({signal}%)")

                # Store network data
                item.setData(Qt.ItemDataRole.UserRole, network)

                # Add to list
                self.network_list.addItem(item)

            # Select first item
            if self.network_list.count() > 0:
                self.network_list.setCurrentRow(0)

            # Set reasonable height for list
            self.network_list.setMinimumHeight(200)
            layout.addWidget(self.network_list)

            # Connection form
            form_layout = QFormLayout()

            # Password field
            password_label = QLabel("Password:")
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow(password_label, self.password_edit)

            # Add form to layout
            layout.addLayout(form_layout)

            # Add validation message area
            self.wireless_validation_label = QLabel("")
            self.wireless_validation_label.setStyleSheet("color: #dc2626;")
            self.wireless_validation_label.setWordWrap(True)
            layout.addWidget(self.wireless_validation_label)

            # Add buttons
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(lambda: self.apply_wireless_connection(wireless_dialog, ifname))
            button_box.rejected.connect(wireless_dialog.reject)

            # Style buttons
            for button in button_box.buttons():
                if button_box.buttonRole(button) == QDialogButtonBox.ButtonRole.AcceptRole:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('SECONDARY')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)
                else:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('CONTROL_BG')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)

            layout.addWidget(button_box)

            # Show dialog
            wireless_dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing wireless connection dialog: {str(e)}")
            self.handle_error(f"Failed to show wireless connection dialog: {str(e)}")

    def apply_wireless_connection(self, dialog: QDialog, ifname: str) -> None:
        """Apply wireless connection to the selected network.

        Args:
            dialog: The dialog containing connection inputs
            ifname: Interface name to configure

        Like a diplomat establishing relations with a foreign network,
        this method negotiates a connection using the provided credentials.
        """
        try:
            # Get selected network
            if not hasattr(self, 'network_list'):
                raise ValueError("Network list not found")

            current_item = self.network_list.currentItem()
            if not current_item:
                if hasattr(self, 'wireless_validation_label'):
                    self.wireless_validation_label.setText("Please select a network")
                return

            network_data = current_item.data(Qt.ItemDataRole.UserRole)
            if not network_data:
                if hasattr(self, 'wireless_validation_label'):
                    self.wireless_validation_label.setText("Invalid network selection")
                return

            ssid = network_data.get('ssid')
            if not ssid:
                if hasattr(self, 'wireless_validation_label'):
                    self.wireless_validation_label.setText("Selected network has no SSID")
                return

            # Get password if applicable
            password = ""
            if hasattr(self, 'password_edit'):
                password = self.password_edit.text()

            # Determine if password is required based on security
            security = network_data.get('security', '')
            needs_password = security and security != 'NONE'

            if needs_password and not password:
                if hasattr(self, 'wireless_validation_label'):
                    self.wireless_validation_label.setText("Password is required for this network")
                return

            # Confirm connection
            confirm_msg = f"Connect to wireless network '{ssid}'?"
            if needs_password:
                confirm_msg += "\n\nThis network requires a password."

            confirm = QMessageBox.question(
                dialog,
                "Confirm Wireless Connection",
                confirm_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if confirm != QMessageBox.StandardButton.Yes:
                return

            # Close the dialog
            dialog.accept()

            # Connect to wireless network
            self.append_log(f"Connecting to wireless network '{ssid}' on {ifname}...", "purple")

            if not hasattr(self.network_tool, 'connect_wireless'):
                self.handle_error("Wireless connection not implemented in network tool")
                return

            # Default to WPA-PSK
            success = self.network_tool.connect_wireless(ssid, password, "wpa-psk")

            if success:
                self.append_log(f"Successfully connected to '{ssid}'.", "green")
                # Refresh interface details
                self.refresh_interface_details()
            else:
                self.handle_error(f"Failed to connect to '{ssid}'")

        except Exception as e:
            self.logger.error(f"Error connecting to wireless network: {str(e)}")
            self.handle_error(f"Wireless connection error: {str(e)}")

    def test_connection(self) -> None:
        """Test network connectivity.

        Like a digital explorer sending forth a probe into
        the vast unknown, this method tests if our packets can
        traverse the network to reach a distant host.
        """
        try:
            # Create dialog for connection test options
            test_dialog = QDialog(self)
            test_dialog.setWindowTitle("Connection Test")
            test_dialog.setMinimumWidth(400)
            test_dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {Theme.get_color('BG_DARK')};
                }}
                QLabel {{
                    color: {Theme.get_color('TEXT_PRIMARY')};
                }}
                QLineEdit {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)

            # Create layout
            layout = QVBoxLayout(test_dialog)

            # Target selection
            form_layout = QFormLayout()

            # Target field
            target_label = QLabel("Target Host/IP:")
            self.target_edit = QLineEdit()
            self.target_edit.setText("1.1.1.1")  # Default to Cloudflare DNS
            target_tooltip = "IP address or hostname to test connectivity. Default is Cloudflare DNS."
            self.target_edit.setToolTip(target_tooltip)
            target_label.setToolTip(target_tooltip)
            form_layout.addRow(target_label, self.target_edit)

            # Add quick target options
            targets_frame = QFrame()
            targets_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)
            targets_layout = QVBoxLayout(targets_frame)

            targets_label = QLabel("Common Targets:")
            targets_label.setStyleSheet("font-weight: bold;")
            targets_layout.addWidget(targets_label)

            targets_grid = QGridLayout()
            targets_grid.setSpacing(5)

            # Quick target buttons
            common_targets = [
                ("Cloudflare DNS", "1.1.1.1"),
                ("Google DNS", "8.8.8.8"),
                ("Google", "www.google.com"),
                ("Default Gateway", "auto")  # Will be handled specially
            ]

            for i, (name, target) in enumerate(common_targets):
                target_btn = QPushButton(name)
                target_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 4px;
                        padding: 6px;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.get_color('CONTROL_HOVER')};
                    }}
                """)

                # For "auto" gateway, determine the actual value
                if target == "auto":
                    # Get current interface
                    index = self.interface_combo.currentIndex()
                    ifname = self.interface_combo.itemData(index) if index >= 0 else None

                    if ifname:
                        # For a real implementation, get the gateway from routing table
                        # Here we'll just set it to a placeholder
                        interfaces = self.network_tool.interfaces
                        if ifname in interfaces:
                            # Try to guess gateway from addresses
                            addresses = interfaces[ifname].get('addresses', [])
                            for addr in addresses:
                                if addr.get('type') == 'ipv4':
                                    ip = addr.get('address', '')
                                    if ip and '.' in ip:
                                        parts = ip.split('.')
                                        if len(parts) == 4:
                                            parts[3] = '1'
                                            target = '.'.join(parts)
                                            break

                # Connect button to action
                target_copy = target  # Create a copy for the lambda
                target_btn.clicked.connect(lambda _, t=target_copy: self.set_test_target(t))

                # Add to grid
                row = i // 2
                col = i % 2
                targets_grid.addWidget(target_btn, row, col)

            targets_layout.addLayout(targets_grid)
            layout.addLayout(form_layout)
            layout.addWidget(targets_frame)

            # Add buttons
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(lambda: self.run_connection_test(test_dialog))
            button_box.rejected.connect(test_dialog.reject)

            # Style buttons
            for button in button_box.buttons():
                if button_box.buttonRole(button) == QDialogButtonBox.ButtonRole.AcceptRole:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('WARNING')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)
                else:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('CONTROL_BG')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)

            layout.addWidget(button_box)

            # Show dialog
            test_dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing connection test dialog: {str(e)}")
            self.handle_error(f"Failed to show connection test dialog: {str(e)}")

    def set_test_target(self, target: str) -> None:
        """Set the target for connection test.

        Args:
            target: Target hostname or IP address

        Like a cartographer marking a destination on a map,
        this method sets the target for our digital journey.
        """
        try:
            if hasattr(self, 'target_edit'):
                self.target_edit.setText(target)
        except Exception as e:
            self.logger.error(f"Error setting test target: {str(e)}")

    def run_connection_test(self, dialog: QDialog) -> None:
        """Run the connection test.

        Args:
            dialog: The dialog containing test configuration

        Like a messenger delivering a letter and awaiting a response,
        this method sends packets to a destination and waits for their return.
        """
        try:
            # Get target
            if not hasattr(self, 'target_edit'):
                raise ValueError("Target field not found")

            target = self.target_edit.text().strip()
            if not target:
                QMessageBox.warning(dialog, "Invalid Target", "Please enter a target host or IP address.")
                return

            # Close dialog
            dialog.accept()

            # Run the test
            self.append_log(f"Testing connection to {target}...", "yellow")

            if not hasattr(self.network_tool, 'get_connection_status'):
                self.handle_error("Connection testing not implemented in network tool")
                return

            result = self.network_tool.get_connection_status(target)

            if result.get('success', False):
                packet_loss = result.get('packet_loss', 100)
                rtt_avg = result.get('rtt_avg')

                success_msg = f"Connection to {target} successful!"
                if rtt_avg is not None:
                    success_msg += f" Average round-trip time: {rtt_avg:.2f} ms"
                if packet_loss > 0:
                    success_msg += f" (Packet loss: {packet_loss}%)"

                self.append_log(success_msg, "green")
            else:
                error_msg = f"Connection to {target} failed."
                if 'error' in result:
                    error_msg += f" Error: {result['error']}"

                self.handle_error(error_msg)

            # Display raw output if available
            if 'output' in result:
                self.append_log("\nPing Output:", "blue")
                for line in result['output'].splitlines():
                    self.append_log(line)

        except Exception as e:
            self.logger.error(f"Error running connection test: {str(e)}")
            self.handle_error(f"Connection test error: {str(e)}")

    def test_dns(self) -> None:
        """Test DNS resolution.

        Like a linguist translating between human and machine languages,
        this method tests the system's ability to convert domain names
        into the numerical addresses machines understand.
        """
        try:
            # Create dialog for DNS test options
            dns_dialog = QDialog(self)
            dns_dialog.setWindowTitle("DNS Resolution Test")
            dns_dialog.setMinimumWidth(400)
            dns_dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {Theme.get_color('BG_DARK')};
                }}
                QLabel {{
                    color: {Theme.get_color('TEXT_PRIMARY')};
                }}
                QLineEdit {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)

            # Create layout
            layout = QVBoxLayout(dns_dialog)

            # Domain selection
            form_layout = QFormLayout()

            # Domain field
            domain_label = QLabel("Domain to Resolve:")
            self.domain_edit = QLineEdit()
            self.domain_edit.setText("www.google.com")  # Default domain
            form_layout.addRow(domain_label, self.domain_edit)

            # Add quick domain options
            domains_frame = QFrame()
            domains_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 4px;
                    padding: 8px;
                }}
            """)
            domains_layout = QVBoxLayout(domains_frame)

            domains_label = QLabel("Common Domains:")
            domains_label.setStyleSheet("font-weight: bold;")
            domains_layout.addWidget(domains_label)

            domains_grid = QGridLayout()
            domains_grid.setSpacing(5)

            # Quick domain buttons
            common_domains = [
                ("Google", "www.google.com"),
                ("Cloudflare", "www.cloudflare.com"),
                ("GitHub", "github.com"),
                ("Wikipedia", "www.wikipedia.org")
            ]

            for i, (name, domain) in enumerate(common_domains):
                domain_btn = QPushButton(name)
                domain_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 4px;
                        padding: 6px;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.get_color('CONTROL_HOVER')};
                    }}
                """)

                # Connect button to action
                domain_copy = domain  # Create a copy for the lambda
                domain_btn.clicked.connect(lambda _, d=domain_copy: self.set_test_domain(d))

                # Add to grid
                row = i // 2
                col = i % 2
                domains_grid.addWidget(domain_btn, row, col)

            domains_layout.addLayout(domains_grid)
            layout.addLayout(form_layout)
            layout.addWidget(domains_frame)

            # Add buttons
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(lambda: self.run_dns_test(dns_dialog))
            button_box.rejected.connect(dns_dialog.reject)

            # Style buttons
            for button in button_box.buttons():
                if button_box.buttonRole(button) == QDialogButtonBox.ButtonRole.AcceptRole:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('TERTIARY')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)
                else:
                    button.setStyleSheet(f"""
                        background-color: {Theme.get_color('CONTROL_BG')};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                    """)

            layout.addWidget(button_box)

            # Show dialog
            dns_dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing DNS test dialog: {str(e)}")
            self.handle_error(f"Failed to show DNS test dialog: {str(e)}")

    def set_test_domain(self, domain: str) -> None:
        """Set the domain for DNS test.

        Args:
            domain: Domain name to resolve

        Like a secretary updating a lawyer's case file,
        this method sets the domain to be examined in our DNS inquiry.
        """
        try:
            if hasattr(self, 'domain_edit'):
                self.domain_edit.setText(domain)
        except Exception as e:
            self.logger.error(f"Error setting test domain: {str(e)}")

    def run_dns_test(self, dialog: QDialog) -> None:
        """Run the DNS resolution test.

        Args:
            dialog: The dialog containing test configuration

        Like a detective tracing information through complex databases,
        this method attempts to resolve a domain name through DNS servers.
        """
        try:
            # Get domain
            if not hasattr(self, 'domain_edit'):
                raise ValueError("Domain field not found")

            domain = self.domain_edit.text().strip()
            if not domain:
                QMessageBox.warning(dialog, "Invalid Domain", "Please enter a domain to resolve.")
                return

            # Close dialog
            dialog.accept()

            # Run the test
            self.append_log(f"Testing DNS resolution for {domain}...", "purple")

            if not hasattr(self.network_tool, 'test_dns'):
                self.handle_error("DNS testing not implemented in network tool")
                return

            result = self.network_tool.test_dns(domain)

            if result.get('success', False):
                ip_address = result.get('ip')
                resolution_time = result.get('time')

                success_msg = f"Successfully resolved {domain} to {ip_address}"
                if resolution_time is not None:
                    success_msg += f" in {resolution_time:.3f} seconds"

                self.append_log(success_msg, "green")

                # If multiple IPs were found
                all_ips = result.get('all_ips', [])
                if all_ips and len(all_ips) > 1:
                    self.append_log("\nAll resolved IP addresses:", "blue")
                    for ip in all_ips:
                        self.append_log(f"  {ip}")
            else:
                error_msg = f"Failed to resolve {domain}"
                if 'error' in result:
                    error_msg += f" Error: {result['error']}"

                self.handle_error(error_msg)

        except Exception as e:
            self.logger.error(f"Error running DNS test: {str(e)}")
            self.handle_error(f"DNS test error: {str(e)}")

    def show_routing_table(self) -> None:
        """Show network routing table.

        Like an explorer studying a map of digital landscapes,
        this method reveals the hidden pathways of network traffic,
        showing how packets navigate from source to destination.
        """
        try:
            # Get the routing table
            self.append_log("Retrieving routing table...", "gray")

            if not hasattr(self.network_tool, 'get_routing_table'):
                self.handle_error("Routing table retrieval not implemented in network tool")
                return

            result = self.network_tool.get_routing_table()

            if not result.get('success', False):
                error_msg = "Failed to retrieve routing table"
                if 'error' in result:
                    error_msg += f" Error: {result['error']}"

                self.handle_error(error_msg)
                return

            # Display the routing table in a dialog
            routes_dialog = QDialog(self)
            routes_dialog.setWindowTitle("Routing Table")
            routes_dialog.setMinimumSize(700, 500)
            routes_dialog.setStyleSheet(f"""
                QDialog {{
                    background-color: {Theme.get_color('BG_DARK')};
                }}
                QLabel {{
                    color: {Theme.get_color('TEXT_PRIMARY')};
                }}
            """)

            # Create layout
            layout = QVBoxLayout(routes_dialog)

            # Create table
            routes_table = QTableWidget(0, 4)  # Rows, Columns
            routes_table.setHorizontalHeaderLabels(["Destination", "Gateway", "Interface", "Flags"])
            routes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            routes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Read-only
            routes_table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    gridline-color: {Theme.get_color('BG_LIGHT')};
                    border: none;
                    border-radius: 4px;
                }}
                QTableWidget::item {{
                    padding: 5px;
                }}
                QHeaderView::section {{
                    background-color: {Theme.get_color('CONTROL_BG')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    padding: 5px;
                    border: none;
                }}
            """)

            # Add routes to table
            routes = result.get('routes', [])
            routes_table.setRowCount(len(routes))

            for i, route in enumerate(routes):
                # Destination
                dst = route.get("dst", "default")
                dst_item = QTableWidgetItem(dst)
                if dst == "default":
                    dst_item.setForeground(QColor(Theme.get_color('SUCCESS')))
                routes_table.setItem(i, 0, dst_item)

                # Gateway
                gateway = route.get("gateway", "direct")
                routes_table.setItem(i, 1, QTableWidgetItem(gateway))

                # Interface
                dev = route.get("dev", "")
                routes_table.setItem(i, 2, QTableWidgetItem(dev))

                # Flags/Scope
                flags = []
                if "scope" in route:
                    flags.append(f"scope:{route['scope']}")
                if "prefsrc" in route:
                    flags.append(f"src:{route['prefsrc']}")
                if route.get("type"):
                    flags.append(route["type"])

                routes_table.setItem(i, 3, QTableWidgetItem(", ".join(flags)))

            layout.addWidget(routes_table)

            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(routes_dialog.accept)
            close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.get_color('CONTROL_BG')};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.get_color('CONTROL_HOVER')};
                }}
            """)

            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)

            # Show dialog
            routes_dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing routing table: {str(e)}")
            self.handle_error(f"Failed to show routing table: {str(e)}")

    def toggle_monitoring(self) -> None:
        """Toggle network traffic monitoring.

        Like a digital sentinel deciding whether to keep watch,
        this method toggles the monitoring of network traffic.
        """
        try:
            # Check if monitoring is active
            if self._monitoring_active:
                # Stop monitoring
                if hasattr(self.network_tool, 'stop_monitoring'):
                    self.network_tool.stop_monitoring()

                # Update UI
                self._monitoring_active = False
                if hasattr(self, 'monitor_toggle_button'):
                    self.monitor_toggle_button.setText("Start Monitoring")
                    self._style_action_button(self.monitor_toggle_button, Theme.get_color('SUCCESS'))

                if hasattr(self, 'export_button'):
                    self.export_button.setEnabled(len(self._monitoring_data) > 0)

                self.append_log("Network monitoring stopped.", "yellow")
            else:
                # Start monitoring
                # Get update interval
                interval = 5  # Default to 5 seconds
                if hasattr(self, 'interval_combo') and self.interval_combo.currentData() is not None:
                    interval = self.interval_combo.currentData()

                # Clear traffic display
                if hasattr(self, 'traffic_display'):
                    self.traffic_display.clear()

                # Reset monitoring data if not keeping history
                self._monitoring_data = []

                # Start the monitoring in the network tool
                if hasattr(self.network_tool, 'start_monitoring'):
                    success = self.network_tool.start_monitoring(interval)

                    if success:
                        # Update UI
                        self._monitoring_active = True
                        if hasattr(self, 'monitor_toggle_button'):
                            self.monitor_toggle_button.setText("Stop Monitoring")
                            self._style_action_button(self.monitor_toggle_button, Theme.get_color('ERROR'))

                        if hasattr(self, 'export_button'):
                            self.export_button.setEnabled(False)  # Will be enabled once we have data

                        self.append_log(f"Network monitoring started. Updates every {interval} seconds.", "green")
                    else:
                        self.handle_error("Failed to start network monitoring")
                else:
                    self.handle_error("Network monitoring not implemented in network tool")
        except Exception as e:
            self.logger.error(f"Error toggling monitoring: {str(e)}")
            self.handle_error(f"Monitoring toggle error: {str(e)}")

    def update_monitoring_display(self, data: Dict[str, Any]) -> None:
        """Update the monitoring display with new data.

        Args:
            data: Dictionary containing monitoring data

        Like a digital meteorologist tracking subtle shifts in the data climate,
        this method updates our visualization of network traffic patterns.
        """
        try:
            # Format monitoring data for display
            if not hasattr(self, 'traffic_display'):
                return

            # Format the update
            rx_rate = data.get('rx_rate', 0)
            tx_rate = data.get('tx_rate', 0)
            rx_packets = data.get('rx_packets', 0)
            tx_packets = data.get('tx_packets', 0)

            # Format rates with units
            if rx_rate > 1024:
                rx_display = f"{rx_rate/1024:.2f} MB/s"
            else:
                rx_display = f"{rx_rate:.2f} KB/s"

            if tx_rate > 1024:
                tx_display = f"{tx_rate/1024:.2f} MB/s"
            else:
                tx_display = f"{tx_rate:.2f} KB/s"

            # Create timestamp
            timestamp = time.strftime("%H:%M:%S", time.localtime(data.get('timestamp', time.time())))

            # Format update text
            update_text = (
                f"[{timestamp}] "
                f"↓ {rx_display} ({rx_packets} packets) | "
                f"↑ {tx_display} ({tx_packets} packets)"
            )

            # Color code based on activity level
            if rx_rate > 100 or tx_rate > 100:  # High activity
                self.traffic_display.append(f'<span style="color: #4CAF50;">{update_text}</span>')
            elif rx_rate > 10 or tx_rate > 10:  # Medium activity
                self.traffic_display.append(f'<span style="color: #FFC107;">{update_text}</span>')
            else:  # Low activity
                self.traffic_display.append(f'<span style="color: #BDBDBD;">{update_text}</span>')

            # Store data for potential export
            self._monitoring_data.append(data)

            # Enable export button once we have data
            if hasattr(self, 'export_button'):
                self.export_button.setEnabled(True)

            # Auto-scroll to bottom
            scrollbar = self.traffic_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

            # Limit stored data to avoid memory issues
            # Keep only the last 1000 data points
            if len(self._monitoring_data) > 1000:
                self._monitoring_data = self._monitoring_data[-1000:]

            # Also refresh the connections table periodically
            # Every 10 data points to avoid excessive updates
            if len(self._monitoring_data) % 10 == 0:
                self.refresh_connections()

        except Exception as e:
            self.logger.error(f"Error updating monitoring display: {str(e)}")
            # Don't show error message for every update

    def export_monitoring_data(self) -> None:
        """Export monitoring data to a CSV file.

        Like an archivist preserving digital fossils for future analysis,
        this method saves a record of network activity to a permanent file.
        """
        try:
            # Check if we have data to export
            if not self._monitoring_data:
                self.handle_error("No monitoring data available to export")
                return

            # Get current interface
            index = self.interface_combo.currentIndex()
            if index < 0:
                self.handle_error("No interface selected")
                return

            ifname = self.interface_combo.itemData(index)
            if not ifname:
                self.handle_error("Invalid interface selection")
                return

            # Create filename with timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
            default_filename = f"network_monitoring_{ifname}_{timestamp}.csv"

            # Show file dialog
            from PyQt6.QtWidgets import QFileDialog
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Export Monitoring Data",
                default_filename,
                "CSV Files (*.csv)"
            )

            if not filepath:
                # User cancelled
                return

            # Write the data to CSV
            if hasattr(self.network_tool, 'export_monitoring_log'):
                success = self.network_tool.export_monitoring_log(filepath, self._monitoring_data)

                if success:
                    self.append_log(f"Monitoring data exported to: {filepath}", "green")
                else:
                    self.handle_error(f"Failed to export monitoring data")
            else:
                # Fallback implementation if network tool doesn't have the method
                import csv
                from datetime import datetime

                try:
                    with open(filepath, 'w', newline='') as csvfile:
                        # Define CSV headers
                        fieldnames = [
                            "Timestamp", "Interface", "State",
                            "Download (KB/s)", "Upload (KB/s)",
                            "Download Packets", "Upload Packets"
                        ]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()

                        # Write data rows
                        for entry in self._monitoring_data:
                            timestamp = datetime.fromtimestamp(entry.get('timestamp', 0)).strftime("%Y-%m-%d %H:%M:%S")
                            writer.writerow({
                                "Timestamp": timestamp,
                                "Interface": entry.get('interface', 'unknown'),
                                "State": entry.get('state', 'unknown'),
                                "Download (KB/s)": entry.get('rx_rate', 0),
                                "Upload (KB/s)": entry.get('tx_rate', 0),
                                "Download Packets": entry.get('rx_packets', 0),
                                "Upload Packets": entry.get('tx_packets', 0)
                            })

                    self.append_log(f"Monitoring data exported to: {filepath}", "green")
                except Exception as csv_error:
                    self.logger.error(f"Error writing CSV: {str(csv_error)}")
                    self.handle_error(f"Failed to write CSV file: {str(csv_error)}")

        except Exception as e:
            self.logger.error(f"Error exporting monitoring data: {str(e)}")
            self.handle_error(f"Export error: {str(e)}")

    def refresh_connections(self) -> None:
        """Refresh the active connections table.

        Like a census taker updating population records, this method
        refreshes our catalog of active network connections.
        """
        try:
            # Check if connections table exists
            if not hasattr(self, 'connections_table'):
                return

            # Get current interface
            index = self.interface_combo.currentIndex()
            if index < 0:
                return

            ifname = self.interface_combo.itemData(index)
            if not ifname:
                return

            # Get connection statistics
            if not hasattr(self.network_tool, 'get_connection_statistics'):
                # Clear table if we can't get stats
                self.connections_table.setRowCount(0)
                return

            result = self.network_tool.get_connection_statistics()

            if not result.get('success', False):
                # Clear table if we couldn't get stats
                self.connections_table.setRowCount(0)
                return

            # Get connections
            connections = result.get('connections', {})

            # Combine TCP and UDP connections for display
            all_connections = []

            # Process TCP connections
            for conn in connections.get('tcp', []):
                all_connections.append({
                    'protocol': 'TCP',
                    'local': conn.get('local', ''),
                    'remote': conn.get('remote', ''),
                    'state': conn.get('state', '')
                })

            # Process UDP connections
            for conn in connections.get('udp', []):
                all_connections.append({
                    'protocol': 'UDP',
                    'local': conn.get('local', ''),
                    'remote': conn.get('remote', ''),
                    'state': 'n/a'  # UDP is stateless
                })

            # Update table
            self.connections_table.setRowCount(len(all_connections))

            # Sort connections - TCP first, then by remote address
            all_connections.sort(key=lambda c: (0 if c['protocol'] == 'TCP' else 1, c['remote']))

            # Fill the table
            for i, conn in enumerate(all_connections):
                # Protocol
                protocol_item = QTableWidgetItem(conn['protocol'])
                if conn['protocol'] == 'TCP':
                    protocol_item.setForeground(QColor(Theme.get_color('PRIMARY')))
                else:
                    protocol_item.setForeground(QColor(Theme.get_color('SECONDARY')))
                self.connections_table.setItem(i, 0, protocol_item)

                # Local address
                self.connections_table.setItem(i, 1, QTableWidgetItem(conn['local']))

                # Remote address
                self.connections_table.setItem(i, 2, QTableWidgetItem(conn['remote']))

                # State
                state_item = QTableWidgetItem(conn['state'])
                if conn['state'] == 'ESTABLISHED':
                    state_item.setForeground(QColor(Theme.get_color('SUCCESS')))
                elif conn['state'] == 'LISTEN':
                    state_item.setForeground(QColor(Theme.get_color('WARNING')))
                self.connections_table.setItem(i, 3, state_item)

        except Exception as e:
            self.logger.error(f"Error refreshing connections: {str(e)}")
            # Don't show error message for every update attempt