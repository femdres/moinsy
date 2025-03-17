"""Network configuration dialog window for Moinsy.

Like a bridge between human intention and machine configuration,
this dialog provides a graphical interface for manipulating the
invisible threads of network communication that bind our digital
existence to the broader universe of data—an attempt to impose
order on the entropic chaos of connection protocols.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QComboBox, QTabWidget, QWidget,
    QGridLayout, QScrollArea, QLineEdit, QSpinBox,
    QCheckBox, QMessageBox, QListWidget, QListWidgetItem,
    QSplitter, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
import logging
from typing import Optional, Dict, Any, List, Union

from core.tools.network_tool import NetworkTool
from gui.styles.theme import Theme


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

        # Initialize the network tool
        self.network_tool = NetworkTool(self)

        # Connect signals
        self.connect_signals()

        # Setup UI components
        self.setup_ui()

        # Load network interfaces
        self.load_interfaces()

        self.logger.debug("Network window initialized")

    def connect_signals(self) -> None:
        """Connect signals from network tool to UI updates."""
        try:
            # Connect network tool signals
            self.network_tool.log_output.connect(self.append_log)
            self.network_tool.error_occurred.connect(self.handle_error)
            self.network_tool.update_progress.connect(self.update_progress)
            self.network_tool.network_info_updated.connect(self.update_interface_info)
            self.network_tool.request_input.connect(self.handle_input_request)
        except Exception as e:
            self.logger.error(f"Error connecting signals: {str(e)}")

    def setup_ui(self) -> None:
        """Initialize the user interface components."""
        try:
            # Window properties
            self.setWindowTitle("Network Configuration")
            self.setMinimumSize(1000, 700)

            # Main layout
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
            basic_layout = QVBoxLayout(self)
            error_label = QLabel(f"Failed to initialize network UI: {str(e)}")
            error_label.setStyleSheet("color: red;")
            basic_layout.addWidget(error_label)

            retry_button = QPushButton("Retry")
            retry_button.clicked.connect(self.setup_ui)
            basic_layout.addWidget(retry_button)

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
                color: {Theme.get_color('TEXT_PRIMARY')};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)

        interfaces_layout = QVBoxLayout(interfaces_group)

        # Interface dropdown
        self.interface_combo = QComboBox()
        self.interface_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.get_color('CONTROL_BG')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                min-height: 30px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Theme.get_color('BG_MEDIUM')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                selection-background-color: {Theme.get_color('PRIMARY')};
            }}
        """)
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
        """
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                background-color: {Theme.get_color('BG_MEDIUM')};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {Theme.get_color('BG_LIGHT')};
                color: {Theme.get_color('TEXT_SECONDARY')};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {Theme.get_color('PRIMARY')};
                color: {Theme.get_color('TEXT_PRIMARY')};
            }}
        """)

        # Output/Log tab
        self.log_tab = QWidget()
        log_layout = QVBoxLayout(self.log_tab)

        # Terminal-style output area
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

        # Wireless networks tab
        self.wireless_tab = QWidget()
        wireless_layout = QVBoxLayout(self.wireless_tab)

        # Tools section
        tools_group = QGroupBox("Wireless Network Scan")
        tools_group.setStyleSheet(self._get_group_box_style())
        tools_layout = QVBoxLayout(tools_group)

        # Scan button
        scan_button = QPushButton("Scan for Wireless Networks")
        scan_button.clicked.connect(self.scan_wireless_networks)
        self._style_action_button(scan_button, Theme.get_color('PRIMARY'))
        tools_layout.addWidget(scan_button)

        wireless_layout.addWidget(tools_group, 0)

        # Networks list
        networks_group = QGroupBox("Available Networks")
        networks_group.setStyleSheet(self._get_group_box_style())
        networks_layout = QVBoxLayout(networks_group)

        self.networks_list = QListWidget()
        self.networks_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: none;
                border-radius: 4px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {Theme.get_color('BG_LIGHT')};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.get_color('PRIMARY')};
                color: {Theme.get_color('TEXT_PRIMARY')};
            }}
        """)
        self.networks_list.itemDoubleClicked.connect(self.on_network_double_clicked)
        networks_layout.addWidget(self.networks_list)

        wireless_layout.addWidget(networks_group, 1)

        # Connection status tab
        self.status_tab = QWidget()
        status_layout = QVBoxLayout(self.status_tab)

        # Connection details
        conn_group = QGroupBox("Connection Statistics")
        conn_group.setStyleSheet(self._get_group_box_style())
        conn_layout = QVBoxLayout(conn_group)

        # Show statistics button
        stats_button = QPushButton("Show Connection Statistics")
        stats_button.clicked.connect(self.show_connection_statistics)
        self._style_action_button(stats_button, Theme.get_color('PRIMARY'))
        conn_layout.addWidget(stats_button)

        # Add traceroute button
        trace_button = QPushButton("Run Traceroute")
        trace_button.clicked.connect(self.run_traceroute)
        self._style_action_button(trace_button, Theme.get_color('SECONDARY'))
        conn_layout.addWidget(trace_button)

        status_layout.addWidget(conn_group, 0)

        # Results area
        stats_group = QGroupBox("Connection Details")
        stats_group.setStyleSheet(self._get_group_box_style())
        stats_layout = QVBoxLayout(stats_group)

        self.stats_output = QTextEdit()
        self.stats_output.setReadOnly(True)
        self.stats_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
        """)
        stats_layout.addWidget(self.stats_output)

        status_layout.addWidget(stats_group, 1)

        # IP configuration tab
        self.ip_config_tab = QWidget()
        ip_config_layout = QVBoxLayout(self.ip_config_tab)

        # Configuration mode
        mode_group = QGroupBox("IP Configuration Mode")
        mode_group.setStyleSheet(self._get_group_box_style())
        mode_layout = QVBoxLayout(mode_group)

        # Radio buttons for DHCP vs Static
        self.mode_dhcp = QRadioButton("DHCP (Automatic IP Configuration)")
        self.mode_dhcp.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
        self.mode_dhcp.toggled.connect(self.on_ip_mode_changed)
        mode_layout.addWidget(self.mode_dhcp)

        self.mode_static = QRadioButton("Static IP Configuration")
        self.mode_static.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
        self.mode_static.toggled.connect(self.on_ip_mode_changed)
        mode_layout.addWidget(self.mode_static)

        # Group for radio buttons
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.mode_dhcp)
        self.mode_group.addButton(self.mode_static)

        # Set default to DHCP
        self.mode_dhcp.setChecked(True)

        ip_config_layout.addWidget(mode_group, 0)

        # Static IP settings
        self.static_settings_group = QGroupBox("Static IP Settings")
        self.static_settings_group.setStyleSheet(self._get_group_box_style())
        static_settings_layout = QGridLayout(self.static_settings_group)

        # IP address
        static_settings_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.ip_address_input = QLineEdit()
        self.ip_address_input.setPlaceholderText("192.168.1.100")
        self._style_line_edit(self.ip_address_input)
        static_settings_layout.addWidget(self.ip_address_input, 0, 1)

        # Prefix length
        static_settings_layout.addWidget(QLabel("Prefix Length:"), 1, 0)
        self.prefix_input = QSpinBox()
        self.prefix_input.setRange(1, 32)
        self.prefix_input.setValue(24)
        self._style_spin_box(self.prefix_input)
        static_settings_layout.addWidget(self.prefix_input, 1, 1)

        # Gateway
        static_settings_layout.addWidget(QLabel("Gateway:"), 2, 0)
        self.gateway_input = QLineEdit()
        self.gateway_input.setPlaceholderText("192.168.1.1")
        self._style_line_edit(self.gateway_input)
        static_settings_layout.addWidget(self.gateway_input, 2, 1)

        # DNS servers
        static_settings_layout.addWidget(QLabel("DNS Servers:"), 3, 0)
        self.dns_input = QLineEdit()
        self.dns_input.setPlaceholderText("8.8.8.8, 8.8.4.4")
        self._style_line_edit(self.dns_input)
        static_settings_layout.addWidget(self.dns_input, 3, 1)

        # Apply button
        self.apply_static_button = QPushButton("Apply Static IP Configuration")
        self.apply_static_button.clicked.connect(self.apply_static_ip)
        self._style_action_button(self.apply_static_button, Theme.get_color('PRIMARY'))
        static_settings_layout.addWidget(self.apply_static_button, 4, 0, 1, 2)

        ip_config_layout.addWidget(self.static_settings_group, 1)

        # Set initial state based on DHCP selection
        self.static_settings_group.setVisible(False)

        # Add tabs
        self.tab_widget.addTab(self.log_tab, "Log Output")
        self.tab_widget.addTab(self.ip_config_tab, "IP Configuration")
        self.tab_widget.addTab(self.wireless_tab, "Wireless Networks")
        self.tab_widget.addTab(self.status_tab, "Connection Status")

        right_layout.addWidget(self.tab_widget)

        return right_panel

    def setup_status_bar(self, layout: QVBoxLayout) -> None:
        """Setup status bar with progress information.

        Args:
            layout: Parent layout to add the status bar to
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
        # Main dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
            }}
            QLabel {{
                color: {Theme.get_color('TEXT_PRIMARY')};
            }}
            QGroupBox {{
                font-weight: bold;
            }}
        """)

    def _style_action_button(self, button: QPushButton, color: str) -> None:
        """Apply consistent styling to action buttons.

        Args:
            button: Button to style
            color: Background color for the button
        """
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

    def _style_line_edit(self, line_edit: QLineEdit) -> None:
        """Apply consistent styling to line edit fields.

        Args:
            line_edit: Line edit to style
        """
        line_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                padding: 8px;
                selection-background-color: {Theme.get_color('PRIMARY')};
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.get_color('PRIMARY')};
            }}
        """)
        line_edit.setMinimumHeight(36)

    def _style_spin_box(self, spin_box: QSpinBox) -> None:
        """Apply consistent styling to spin box fields.

        Args:
            spin_box: Spin box to style
        """
        spin_box.setStyleSheet(f"""
            QSpinBox {{
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                padding: 8px;
                selection-background-color: {Theme.get_color('PRIMARY')};
            }}
            QSpinBox:focus {{
                border: 1px solid {Theme.get_color('PRIMARY')};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                background-color: {Theme.get_color('BG_LIGHT')};
            }}
        """)
        spin_box.setMinimumHeight(36)

    def _get_group_box_style(self) -> str:
        """Get consistent style for group boxes.

        Returns:
            CSS styling string for group boxes
        """
        return f"""
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
        """

    def load_interfaces(self) -> None:
        """Load network interfaces from the system."""
        try:
            self.append_log("Loading network interfaces...", "white")
            self.status_label.setText("Loading interfaces...")

            # Clear existing interfaces
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

            # Add to combo box
            for ifname in sorted_interfaces:
                interface_type = interfaces[ifname].get("type", "unknown")
                self.interface_combo.addItem(f"{ifname} ({interface_type})", ifname)

            self.status_label.setText(f"Found {len(interfaces)} interfaces")

        except Exception as e:
            self.logger.error(f"Error loading interfaces: {str(e)}")
            self.append_log(f"Error loading interfaces: {str(e)}", "red")
            self.status_label.setText("Error loading interfaces")

    def update_interface_info(self, interfaces: Dict[str, Dict[str, Any]]) -> None:
        """Update interface information in the UI.

        Args:
            interfaces: Dictionary of interface information
        """
        try:
            # Check if an interface is selected
            selected_ifname = self.get_selected_interface()
            if not selected_ifname or selected_ifname not in interfaces:
                return

            # Get interface data
            interface = interfaces[selected_ifname]

            # Update interface details
            self.show_interface_details(selected_ifname, interface)

            # Update wireless networks if applicable
            if interface.get("wireless", False) and "available_networks" in interface:
                self.update_networks_list(interface["available_networks"])

        except Exception as e:
            self.logger.error(f"Error updating interface info: {str(e)}")

    def refresh_interfaces(self) -> None:
        """Refresh network interface information."""
        self.load_interfaces()

    def on_interface_selected(self, index: int) -> None:
        """Handle interface selection change.

        Args:
            index: Selected index in the combo box
        """
        if index < 0:
            return

        # Get the interface name
        ifname = self.interface_combo.itemData(index)
        if not ifname:
            return

        self.append_log(f"Selected interface: {ifname}", "cyan")

        # Select in network tool
        if self.network_tool.select_interface(ifname):
            # Enable interface-specific actions
            self._set_interface_action_state(True)

            # Get interface info
            interfaces = self.network_tool.interfaces
            if ifname in interfaces:
                # Show interface details
                self.show_interface_details(ifname, interfaces[ifname])

                # Check if wireless
                is_wireless = interfaces[ifname].get("wireless", False)
                self.wireless_button.setEnabled(is_wireless)

                # Switch to wireless tab if it's a wireless interface
                if is_wireless:
                    # Scan for networks after a delay
                    self.scan_wireless_networks()
        else:
            # Disable interface-specific actions
            self._set_interface_action_state(False)

    def show_interface_details(self, ifname: str, interface: Dict[str, Any]) -> None:
        """Display details about the selected interface.

        Args:
            ifname: Interface name
            interface: Interface information dictionary
        """
        try:
            # Clear existing content
            self._clear_layout(self.details_layout)

            # Hide placeholder
            self.details_placeholder.setVisible(False)

            # Interface name and type
            name_label = QLabel(f"<b>{ifname}</b>")
            name_label.setStyleSheet(f"color: {Theme.get_color('PRIMARY')}; font-size: 16px;")
            self.details_layout.addWidget(name_label)

            # Interface type
            type_label = QLabel(f"Type: {interface.get('type', 'unknown')}")
            type_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
            self.details_layout.addWidget(type_label)

            # MAC address
            if "mac_address" in interface:
                mac_label = QLabel(f"MAC: {interface['mac_address']}")
                mac_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                self.details_layout.addWidget(mac_label)

            # Status indicator
            state = interface.get("state", "unknown")
            state_color = "#4CAF50" if state == "UP" else "#FF5722"  # Green for UP, red for DOWN
            state_label = QLabel(f"Status: <span style='color:{state_color};'>{state}</span>")
            state_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
            self.details_layout.addWidget(state_label)

            # IP addresses section
            addresses = interface.get("addresses", [])
            if addresses:
                # Separator
                sep1 = QFrame()
                sep1.setFrameShape(QFrame.Shape.HLine)
                sep1.setFrameShadow(QFrame.Shadow.Sunken)
                sep1.setStyleSheet(f"background-color: {Theme.get_color('BG_LIGHT')};")
                self.details_layout.addWidget(sep1)

                # Address header
                addr_header = QLabel("<b>IP Addresses</b>")
                addr_header.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; margin-top: 10px;")
                self.details_layout.addWidget(addr_header)

                # Add each address
                for addr in addresses:
                    addr_type = addr.get("type", "").upper()
                    address = f"{addr.get('address', '')}/{addr.get('prefix', '')}"
                    addr_label = QLabel(f"{addr_type}: {address}")
                    addr_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                    self.details_layout.addWidget(addr_label)

            # Wireless details
            if interface.get("wireless", False):
                # Separator
                sep2 = QFrame()
                sep2.setFrameShape(QFrame.Shape.HLine)
                sep2.setFrameShadow(QFrame.Shadow.Sunken)
                sep2.setStyleSheet(f"background-color: {Theme.get_color('BG_LIGHT')};")
                self.details_layout.addWidget(sep2)

                # Wireless header
                wireless_header = QLabel("<b>Wireless Information</b>")
                wireless_header.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; margin-top: 10px;")
                self.details_layout.addWidget(wireless_header)

                # Wireless details
                wireless_info = interface.get("wireless_info", {})

                # SSID
                if "ssid" in wireless_info and wireless_info["ssid"]:
                    ssid_label = QLabel(f"Network: {wireless_info['ssid']}")
                    ssid_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                    self.details_layout.addWidget(ssid_label)
                else:
                    ssid_label = QLabel("Not connected to any network")
                    ssid_label.setStyleSheet(f"color: {Theme.get_color('WARNING')};")
                    self.details_layout.addWidget(ssid_label)

                # Other wireless details
                if "signal_level" in wireless_info and wireless_info["signal_level"]:
                    signal_label = QLabel(f"Signal: {wireless_info['signal_level']}")
                    signal_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                    self.details_layout.addWidget(signal_label)

                if "frequency" in wireless_info and wireless_info["frequency"]:
                    freq_label = QLabel(f"Frequency: {wireless_info['frequency']}")
                    freq_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                    self.details_layout.addWidget(freq_label)

                if "bit_rate" in wireless_info and wireless_info["bit_rate"]:
                    rate_label = QLabel(f"Bit Rate: {wireless_info['bit_rate']}")
                    rate_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                    self.details_layout.addWidget(rate_label)

            # Statistics section
            if "statistics" in interface:
                # Separator
                sep3 = QFrame()
                sep3.setFrameShape(QFrame.Shape.HLine)
                sep3.setFrameShadow(QFrame.Shadow.Sunken)
                sep3.setStyleSheet(f"background-color: {Theme.get_color('BG_LIGHT')};")
                self.details_layout.addWidget(sep3)

                # Statistics header
                stats_header = QLabel("<b>Traffic Statistics</b>")
                stats_header.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; margin-top: 10px;")
                self.details_layout.addWidget(stats_header)

                # Format byte counts
                stats = interface["statistics"]
                rx_mb = stats.get("rx_bytes", 0) / (1024 * 1024)
                tx_mb = stats.get("tx_bytes", 0) / (1024 * 1024)

                # Add statistics
                rx_label = QLabel(f"Received: {rx_mb:.2f} MB ({stats.get('rx_packets', 0)} packets)")
                rx_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                self.details_layout.addWidget(rx_label)

                tx_label = QLabel(f"Sent: {tx_mb:.2f} MB ({stats.get('tx_packets', 0)} packets)")
                tx_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                self.details_layout.addWidget(tx_label)

            # Add spacing
            self.details_layout.addStretch(1)

        except Exception as e:
            self.logger.error(f"Error showing interface details: {str(e)}")
            error_label = QLabel(f"Error loading interface details: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.details_layout.addWidget(error_label)

    def _clear_layout(self, layout: QLayout) -> None:
        """Clear all widgets from a layout.

        Args:
            layout: Layout to clear
        """
        if not layout:
            return

        # Remove all items from the layout
        while layout.count():
            item = layout.takeAt(0)

            # If the item is a widget
            if item.widget():
                # Hide it first
                item.widget().setVisible(False)
                # Then remove it from the layout
                item.widget().setParent(None)

            # If the item is a layout
            elif item.layout():
                self._clear_layout(item.layout())

            del item

    def _set_interface_action_state(self, enabled: bool) -> None:
        """Enable or disable interface-specific action buttons.

        Args:
            enabled: Whether to enable the buttons
        """
        # Quick action buttons
        self.dhcp_button.setEnabled(enabled)
        self.static_ip_button.setEnabled(enabled)

        # Wireless button is separately controlled based on interface type
        self.wireless_button.setEnabled(False)

        # Troubleshoot buttons
        self.test_connection_button.setEnabled(enabled)
        self.test_dns_button.setEnabled(enabled)
        self.show_routes_button.setEnabled(enabled)

    def get_selected_interface(self) -> Optional[str]:
        """Get the currently selected interface name.

        Returns:
            Selected interface name or None if no selection
        """
        index = self.interface_combo.currentIndex()
        if index < 0:
            return None

        return self.interface_combo.itemData(index)

    def append_log(self, message: str, color: str = "white") -> None:
        """Append a message to the log output.

        Args:
            message: Message to append
            color: Text color
        """
        try:
            # Add the message with the specified color
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
        """
        self.append_log(f"Error: {error_message}", "red")
        self.status_label.setText("Error")

    def update_progress(self, value: int) -> None:
        """Update progress indicator.

        Args:
            value: Progress value (0-100)
        """
        self.progress_label.setText(f"{value}%")

        if value == 0:
            self.status_label.setText("Ready")
        elif value == 100:
            self.status_label.setText("Completed")
        else:
            self.status_label.setText("Working...")

    def handle_input_request(self, prompt: str, callback: str) -> None:
        """Handle input requests from network tool.

        Args:
            prompt: Prompt to show user
            callback: Callback method name
        """
        # Not implemented - network tool doesn't currently use this
        self.append_log(prompt, "yellow")

    def update_networks_list(self, networks: List[Dict[str, Any]]) -> None:
        """Update the list of wireless networks.

        Args:
            networks: List of wireless network information dictionaries
        """
        try:
            # Clear the list
            self.networks_list.clear()

            if not networks:
                return

            # Add each network to the list
            for network in networks:
                ssid = network.get("ssid", "Unknown Network")
                signal = network.get("signal", 0)
                security = network.get("security", "")

                # Format for display - Unicode signal bars by signal strength
                signal_bars = self.network_tool._signal_strength_bars(signal)

                # Create list item
                item = QListWidgetItem(f"{ssid} - {signal_bars} {security}")
                item.setData(Qt.ItemDataRole.UserRole, network)

                self.networks_list.addItem(item)

        except Exception as e:
            self.logger.error(f"Error updating networks list: {str(e)}")

    def configure_dhcp(self) -> None:
        """Configure the selected interface to use DHCP."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Switch to Log Output tab to show progress
        self.tab_widget.setCurrentWidget(self.log_tab)

        # Execute DHCP configuration
        self.network_tool.configure_dhcp()

    def configure_static_ip(self) -> None:
        """Show static IP configuration interface."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Switch to IP Configuration tab
        self.tab_widget.setCurrentWidget(self.ip_config_tab)

        # Select static IP mode
        self.mode_static.setChecked(True)

        # Pre-fill current IP if available
        interface = self.network_tool.interfaces.get(ifname, {})
        addresses = interface.get("addresses", [])

        # Find an IPv4 address
        ipv4_address = next((addr for addr in addresses if addr.get("type") == "ipv4"), None)

        if ipv4_address:
            self.ip_address_input.setText(ipv4_address.get("address", ""))
            self.prefix_input.setValue(int(ipv4_address.get("prefix", 24)))

            # Try to guess the gateway - common pattern is .1 or .254 in the subnet
            ip_parts = ipv4_address.get("address", "").split('.')
            if len(ip_parts) == 4:
                gateway = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1"
                self.gateway_input.setText(gateway)

        # Fill in DNS servers
        dns_servers = self.network_tool.dns_servers
        if dns_servers:
            self.dns_input.setText(", ".join(dns_servers))

    def apply_static_ip(self) -> None:
        """Apply static IP configuration from user inputs."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Get values from form
        ip_address = self.ip_address_input.text().strip()
        prefix_len = self.prefix_input.value()
        gateway = self.gateway_input.text().strip()
        dns_servers_text = self.dns_input.text().strip()

        # Validate inputs
        if not ip_address:
            self.handle_error("IP address is required")
            return

        if not gateway:
            self.handle_error("Gateway is required")
            return

        # Parse DNS servers
        dns_servers = [srv.strip() for srv in dns_servers_text.split(',') if srv.strip()]

        # Switch to Log Output tab to show progress
        self.tab_widget.setCurrentWidget(self.log_tab)

        # Apply configuration
        self.network_tool.configure_static_ip(ip_address, prefix_len, gateway, dns_servers)

    def on_ip_mode_changed(self) -> None:
        """Handle IP configuration mode change."""
        # Show/hide static IP settings based on mode
        self.static_settings_group.setVisible(self.mode_static.isChecked())

        # If DHCP mode is selected, offer to apply DHCP immediately
        if self.mode_dhcp.isChecked():
            # Ask user if they want to apply DHCP now
            reply = QMessageBox.question(
                self,
                "Apply DHCP Configuration",
                "Do you want to apply DHCP configuration to the selected interface now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.configure_dhcp()

    def connect_wireless(self) -> None:
        """Connect to a wireless network."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Verify it's a wireless interface
        interface = self.network_tool.interfaces.get(ifname, {})
        if not interface.get("wireless", False):
            self.handle_error(f"Interface {ifname} is not a wireless interface")
            return

        # Switch to wireless tab
        self.tab_widget.setCurrentWidget(self.wireless_tab)

        # Scan for networks if we don't have any
        if not interface.get("available_networks"):
            self.scan_wireless_networks()
            return

        # If a network is already selected in the list, ask to connect to it
        selected_items = self.networks_list.selectedItems()
        if selected_items:
            self.on_network_double_clicked(selected_items[0])

    def on_network_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on wireless network item.

        Args:
            item: Selected list item
        """
        # Get network data
        network = item.data(Qt.ItemDataRole.UserRole)
        if not network:
            return

        ssid = network.get("ssid", "")
        has_security = bool(network.get("security", ""))

        # Show connection dialog
        if has_security:
            password, ok = self._show_wifi_password_dialog(ssid)
            if ok and password:
                # Switch to Log Output tab to show progress
                self.tab_widget.setCurrentWidget(self.log_tab)
                self.network_tool.connect_wireless(ssid, password)
        else:
            # Open network - confirm
            reply = QMessageBox.question(
                self,
                "Connect to Open Network",
                f"Connect to open (unsecured) network '{ssid}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Switch to Log Output tab to show progress
                self.tab_widget.setCurrentWidget(self.log_tab)
                self.network_tool.connect_wireless(ssid)

    def _show_wifi_password_dialog(self, ssid: str) -> Tuple[str, bool]:
        """Show dialog to enter wireless network password.

        Args:
            ssid: Network SSID

        Returns:
            Tuple of (password, whether OK was pressed)
        """
        from PyQt6.QtWidgets import QInputDialog

        password, ok = QInputDialog.getText(
            self,
            f"Connect to {ssid}",
            f"Enter password for wireless network '{ssid}':",
            QLineEdit.EchoMode.Password
        )

        return password, ok

    def scan_wireless_networks(self) -> None:
        """Scan for available wireless networks."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Check if it's a wireless interface
        interface = self.network_tool.interfaces.get(ifname, {})
        if not interface.get("wireless", False):
            self.handle_error(f"Interface {ifname} is not a wireless interface")
            return

        # Execute scan
        self.network_tool.scan_wireless_networks()

    def test_connection(self) -> None:
        """Test network connectivity."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Switch to Log Output tab to show progress
        self.tab_widget.setCurrentWidget(self.log_tab)

        # Run connection test
        self.network_tool.get_connection_status()

    def test_dns(self) -> None:
        """Test DNS resolution."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Switch to Log Output tab to show progress
        self.tab_widget.setCurrentWidget(self.log_tab)

        # Run DNS test
        self.network_tool.test_dns()

    def show_routing_table(self) -> None:
        """Show network routing table."""
        # Switch to Log Output tab to show progress
        self.tab_widget.setCurrentWidget(self.log_tab)

        # Get routing table
        self.network_tool.get_routing_table()

    def show_connection_statistics(self) -> None:
        """Show connection statistics."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Switch to Connection Status tab
        self.tab_widget.setCurrentWidget(self.status_tab)

        # Clear previous stats
        self.stats_output.clear()

        # Get statistics
        result = self.network_tool.get_connection_statistics()

        # Format and display statistics in the stats output area
        if result.get("success", False):
            stats = result.get("stats", {})
            connections = result.get("connections", {})

            # Format byte counts
            rx_mb = stats.get("rx_bytes", 0) / (1024 * 1024)
            tx_mb = stats.get("tx_bytes", 0) / (1024 * 1024)

            self.stats_output.append(f"<h3>Network Statistics for {ifname}</h3>")
            self.stats_output.append(f"<b>Received:</b> {rx_mb:.2f} MB ({stats.get('rx_packets', 0)} packets)")
            self.stats_output.append(f"<b>Sent:</b> {tx_mb:.2f} MB ({stats.get('tx_packets', 0)} packets)")
            self.stats_output.append(f"<b>Errors:</b> RX: {stats.get('rx_errors', 0)}, TX: {stats.get('tx_errors', 0)}")

            # Display connections
            tcp_count = result.get("tcp_count", 0)
            udp_count = result.get("udp_count", 0)

            self.stats_output.append(f"<h3>Active Connections</h3>")
            self.stats_output.append(f"<b>TCP Connections:</b> {tcp_count}")
            self.stats_output.append(f"<b>UDP Connections:</b> {udp_count}")

            # Show sample TCP connections
            if tcp_count > 0:
                self.stats_output.append("<h4>Sample TCP Connections:</h4>")
                for i, conn in enumerate(connections.get("tcp", [])[:5]):  # Show up to 5
                    self.stats_output.append(f"{conn['local']} → {conn['remote']} ({conn['state']})")

                if tcp_count > 5:
                    self.stats_output.append(f"... and {tcp_count - 5} more")

    def run_traceroute(self) -> None:
        """Run traceroute to a target."""
        ifname = self.get_selected_interface()
        if not ifname:
            self.handle_error("No interface selected")
            return

        # Get target from user
        from PyQt6.QtWidgets import QInputDialog

        target, ok = QInputDialog.getText(
            self,
            "Run Traceroute",
            "Enter hostname or IP address to trace:",
            QLineEdit.EchoMode.Normal,
            "1.1.1.1"
        )

        if ok and target:
            # Switch to Log Output tab to show progress
            self.tab_widget.setCurrentWidget(self.log_tab)

            # Run traceroute
            self.network_tool.run_traceroute(target)