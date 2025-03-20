"""GUI window for configuring multiple PipeWire audio devices with advanced options.

Like a meticulous audiophile painstakingly arranging their sound system,
this module provides a visual interface for configuring the digital pathways
through which electrons are transformed into the illusion of sound - our futile
attempt to bridge the void between computational logic and sensory experience.
"""

import os
import logging
import json
import shutil
import subprocess
from typing import Dict, List, Optional, Set, Any, Tuple, Union, cast
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox,
    QLabel, QTabWidget, QWidget, QGridLayout, QComboBox,
    QScrollArea, QCheckBox, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QSlider, QSpinBox, QMessageBox, QFrame, QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

from gui.styles.theme import Theme

from config import get_resource_path

class DeviceConfigItem:
    """Represents a configurable audio device with settings.

    Like a digital audio passport, this class stores the identity and preferences
    of a sound-producing entity in our electronic ecosystem.
    """

    def __init__(self, name: str, nick: str, device_id: str, is_output: bool = True) -> None:
        """Initialize device configuration.

        Args:
            name: Full device node name
            nick: User-friendly device nickname
            device_id: Unique device identifier
            is_output: Whether this is an output (True) or input (False) device
        """
        self.name: str = name
        self.nick: str = nick
        self.device_id: str = device_id
        self.is_output: bool = is_output

        # Configuration options with defaults
        self.config: Dict[str, Any] = {
            "enabled": True,
            "priority": 1000,
            "default": False,
            "sample_rate": 96000,
            "allowed_rates": [44100, 48000, 96000, 192000],
            "bit_depth": "S32LE",
            "channels": 2,
            "resampler_quality": 8,
            "disable_batch": False,
            "disable_mmap": False,
            "position": "FL,FR",  # Default stereo
        }


class PipeWireConfigWindow(QDialog):
    """Dialog window for configuring PipeWire audio devices.

    Like the control room of a recording studio permanently under construction,
    this window offers an interface to the chaotic wilderness of audio device
    configurations - a user interface whose mere existence provides the comforting
    illusion that our auditory preferences will actually persist beyond the next
    software update.
    """

    # Signals - FIXED: Using 'dict' instead of Dict[str, Any] for signal type
    config_saved = pyqtSignal(dict)  # Emitted when configurations are saved

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the PipeWire configuration window.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Keep track of devices and their configurations
        self.devices: Dict[str, DeviceConfigItem] = {}
        self.username: Optional[str] = None
        self.output_devices: List[str] = []  # Device IDs for outputs
        self.input_devices: List[str] = []   # Device IDs for inputs
        self.config_path: str = ""

        # UI state tracking
        self._currently_selected_device: Optional[str] = None
        self._config_modified: bool = False

        # Set window properties
        self.setWindowTitle("PipeWire Audio Configuration")
        self.setMinimumSize(950, 680)

        # Set up UI components
        self.setup_ui()

        # Schedule detection of audio devices
        QTimer.singleShot(100, self.detect_audio_devices)

        self.logger.debug("PipeWire configuration window initialized")

    @property
    def username_prop(self) -> Optional[str]:
        """Get the current username.

        Returns:
            Current system username or None if not available
        """
        if self.username is None:
            try:
                username_file = get_resource_path("texts", "username.txt")
                with open(username_file, "r") as file:
                    self.username = file.read().strip()
                    self.logger.debug(f"Retrieved username: {self.username}")
            except Exception as e:
                self.logger.error(f"Error loading username: {str(e)}")
                self.username = None

        return self.username

    def setup_ui(self) -> None:
        """Set up the main UI components.

        Like an architect designing a control panel for a machine whose purpose
        is only vaguely understood, this method carefully arranges UI elements
        to create the comforting illusion of mastery over digital audio streams.
        """
        try:
            # Main layout
            main_layout = QVBoxLayout(self)
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(20, 20, 20, 20)

            # Header section
            self.setup_header(main_layout)

            # Main content area
            self.setup_content_area(main_layout)

            # Bottom buttons
            self.setup_bottom_buttons(main_layout)

            # Apply styling
            self.apply_styling()

            self.logger.debug("UI components initialized")

        except Exception as e:
            self.logger.exception(f"Error setting up UI: {str(e)}")
            # Create minimal error UI
            error_layout = QVBoxLayout(self)
            error_label = QLabel(f"Error initializing UI: {str(e)}")
            error_label.setStyleSheet("color: red;")
            error_layout.addWidget(error_label)
            self.logger.critical("Using fallback error UI")

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Set up the header section with title and description.

        Args:
            layout: Parent layout to add the header to
        """
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        # Title
        title_label = QLabel("PipeWire Audio Configuration")
        title_label.setFont(QFont('Segoe UI', 22, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {Theme.get_color('PRIMARY')};")
        header_layout.addWidget(title_label)

        # Subtitle with instruction
        subtitle = QLabel("Configure multiple audio devices with advanced options")
        subtitle.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-size: 14px;")
        header_layout.addWidget(subtitle)

        # Status message for device detection
        self.status_label = QLabel("Detecting audio devices...")
        self.status_label.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')}; font-size: 15px; margin-top: 10px;")
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

    def setup_content_area(self, layout: QVBoxLayout) -> None:
        """Set up the main content area with device list and settings.

        Args:
            layout: Parent layout to add the content to
        """
        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Device list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Device list section
        self.setup_device_list(left_layout)

        # Right panel - Device configuration
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Device configuration section
        self.setup_config_section(right_layout)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Set initial sizes (30% left, 70% right)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def setup_device_list(self, layout: QVBoxLayout) -> None:
        """Set up the device list section.

        Args:
            layout: Parent layout to add the device list to
        """
        # Device list group box
        devices_group = QGroupBox("Audio Devices")
        devices_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                padding-top: 16px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        devices_layout = QVBoxLayout(devices_group)

        # Tabs for input/output devices
        device_tabs = QTabWidget()
        device_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #2A2A2A;
                color: #888888;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)

        # Output devices tab
        output_tab = QWidget()
        output_layout = QVBoxLayout(output_tab)
        output_layout.setContentsMargins(0, 10, 0, 0)

        # Tree widget for output devices
        self.output_tree = QTreeWidget()
        self.output_tree.setHeaderLabels(["Output Devices"])
        self.output_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.output_tree.itemSelectionChanged.connect(self.on_device_selected)
        self.output_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e293b;
                border: none;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            QTreeWidget::item {
                height: 30px;
                padding: 5px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #2A2A2A;
            }
        """)
        output_layout.addWidget(self.output_tree)

        # Input devices tab
        input_tab = QWidget()
        input_layout = QVBoxLayout(input_tab)
        input_layout.setContentsMargins(0, 10, 0, 0)

        # Tree widget for input devices
        self.input_tree = QTreeWidget()
        self.input_tree.setHeaderLabels(["Input Devices"])
        self.input_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.input_tree.itemSelectionChanged.connect(self.on_device_selected)
        self.input_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e293b;
                border: none;
                border-radius: 4px;
                padding: 5px;
                color: white;
            }
            QTreeWidget::item {
                height: 30px;
                padding: 5px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #2A2A2A;
            }
        """)
        input_layout.addWidget(self.input_tree)

        # Add tabs to tab widget
        device_tabs.addTab(output_tab, "Output Devices")
        device_tabs.addTab(input_tab, "Input Devices")
        devices_layout.addWidget(device_tabs)

        # Add device action buttons
        device_buttons_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh Devices")
        self.refresh_btn.clicked.connect(self.detect_audio_devices)
        device_buttons_layout.addWidget(self.refresh_btn)

        # Add buttons layout
        devices_layout.addLayout(device_buttons_layout)

        # Add devices group to main layout
        layout.addWidget(devices_group)

    def setup_config_section(self, layout: QVBoxLayout) -> None:
        """Set up the device configuration section.

        Args:
            layout: Parent layout to add the configuration to
        """
        # Configuration group box
        config_group = QGroupBox("Device Configuration")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                padding-top: 16px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        config_layout = QVBoxLayout(config_group)

        # Scrollable config area
        config_scroll = QScrollArea()
        config_scroll.setWidgetResizable(True)
        config_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Container for configuration widgets
        self.config_container = QWidget()
        self.config_layout = QVBoxLayout(self.config_container)
        self.config_layout.setContentsMargins(5, 5, 5, 5)
        self.config_layout.setSpacing(15)
        config_scroll.setWidget(self.config_container)

        # Add a placeholder label when no device is selected
        self.no_device_label = QLabel("Select a device to configure")
        self.no_device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_device_label.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-size: 14px; padding: 20px;")
        self.config_layout.addWidget(self.no_device_label)

        # Basic settings group - initially hidden
        self.basic_group = QGroupBox("Basic Settings")
        self.basic_group.setVisible(False)
        basic_layout = QGridLayout(self.basic_group)
        basic_layout.setColumnStretch(1, 1)  # Make second column expandable

        # Device name (non-editable)
        basic_layout.addWidget(QLabel("Device Name:"), 0, 0)
        self.device_name_label = QLabel()
        self.device_name_label.setWordWrap(True)
        self.device_name_label.setStyleSheet("font-family: monospace;")
        basic_layout.addWidget(self.device_name_label, 0, 1)

        # Device nickname (editable)
        basic_layout.addWidget(QLabel("Nickname:"), 1, 0)
        self.nickname_edit = QLineEdit()
        self.nickname_edit.textChanged.connect(self.on_config_changed)
        basic_layout.addWidget(self.nickname_edit, 1, 1)

        # Enable device checkbox
        self.enable_checkbox = QCheckBox("Enable this device")
        self.enable_checkbox.toggled.connect(self.on_config_changed)
        basic_layout.addWidget(self.enable_checkbox, 2, 0, 1, 2)

        # Set as default device
        self.default_checkbox = QCheckBox("Set as default device")
        self.default_checkbox.toggled.connect(self.on_config_changed)
        basic_layout.addWidget(self.default_checkbox, 3, 0, 1, 2)

        # Priority setting
        basic_layout.addWidget(QLabel("Priority:"), 4, 0)
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(0, 9999)
        self.priority_spin.setSingleStep(100)
        self.priority_spin.setValue(1000)
        self.priority_spin.valueChanged.connect(self.on_config_changed)
        basic_layout.addWidget(self.priority_spin, 4, 1)

        self.config_layout.addWidget(self.basic_group)

        # Audio quality settings group - initially hidden
        self.quality_group = QGroupBox("Audio Quality Settings")
        self.quality_group.setVisible(False)
        quality_layout = QGridLayout(self.quality_group)
        quality_layout.setColumnStretch(1, 1)  # Make second column expandable

        # Sample rate
        quality_layout.addWidget(QLabel("Sample Rate:"), 0, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(['44100', '48000', '96000', '192000'])
        self.sample_rate_combo.setCurrentText('96000')
        self.sample_rate_combo.currentIndexChanged.connect(self.on_config_changed)
        quality_layout.addWidget(self.sample_rate_combo, 0, 1)

        # Bit depth
        quality_layout.addWidget(QLabel("Bit Depth:"), 1, 0)
        self.bit_depth_combo = QComboBox()
        self.bit_depth_combo.addItems(['S16LE', 'S24LE', 'S32LE', 'F32LE'])
        self.bit_depth_combo.setCurrentText('S32LE')
        self.bit_depth_combo.currentIndexChanged.connect(self.on_config_changed)
        quality_layout.addWidget(self.bit_depth_combo, 1, 1)

        # Channels
        quality_layout.addWidget(QLabel("Channels:"), 2, 0)
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 8)
        self.channels_spin.setValue(2)
        self.channels_spin.valueChanged.connect(self.on_config_changed)
        quality_layout.addWidget(self.channels_spin, 2, 1)

        # Channel position
        quality_layout.addWidget(QLabel("Channel Position:"), 3, 0)
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            'FL,FR',         # Stereo
            'FL,FR,LFE',     # 2.1
            'FL,FR,FC,LFE',  # 3.1
            'FL,FR,FC,LFE,RL,RR',  # 5.1
            'FL,FR,FC,LFE,SL,SR,RL,RR'  # 7.1
        ])
        self.position_combo.setCurrentText('FL,FR')
        self.position_combo.currentIndexChanged.connect(self.on_config_changed)
        quality_layout.addWidget(self.position_combo, 3, 1)

        # Resampler quality
        quality_layout.addWidget(QLabel("Resampler Quality:"), 4, 0)
        self.resampler_slider = QSlider(Qt.Orientation.Horizontal)
        self.resampler_slider.setRange(0, 15)
        self.resampler_slider.setValue(8)
        self.resampler_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.resampler_slider.setTickInterval(1)
        self.resampler_slider.valueChanged.connect(self.on_config_changed)
        quality_layout.addWidget(self.resampler_slider, 4, 1)

        self.config_layout.addWidget(self.quality_group)

        # Advanced settings group - initially hidden
        self.advanced_group = QGroupBox("Advanced Settings")
        self.advanced_group.setVisible(False)
        advanced_layout = QGridLayout(self.advanced_group)
        advanced_layout.setColumnStretch(1, 1)  # Make second column expandable

        # Disable memory mapping
        self.mmap_checkbox = QCheckBox("Disable memory mapping (may help with some drivers)")
        self.mmap_checkbox.toggled.connect(self.on_config_changed)
        advanced_layout.addWidget(self.mmap_checkbox, 0, 0, 1, 2)

        # Disable batch mode
        self.batch_checkbox = QCheckBox("Disable batch mode (may reduce latency but increase CPU)")
        self.batch_checkbox.toggled.connect(self.on_config_changed)
        advanced_layout.addWidget(self.batch_checkbox, 1, 0, 1, 2)

        # Config file name
        advanced_layout.addWidget(QLabel("Config Filename:"), 2, 0)
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("51-mydevice.lua")
        self.filename_edit.textChanged.connect(self.on_config_changed)
        advanced_layout.addWidget(self.filename_edit, 2, 1)

        self.config_layout.addWidget(self.advanced_group)

        # Add a stretch at the end to push everything to the top
        self.config_layout.addStretch()

        # Add scroll area to layout
        config_layout.addWidget(config_scroll)

        # Add config group to main layout
        layout.addWidget(config_group)

    def setup_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """Set up the bottom buttons section.

        Args:
            layout: Parent layout to add the buttons to
        """
        button_layout = QHBoxLayout()

        # Configuration path
        self.path_label = QLabel("Configuration path will be shown here")
        self.path_label.setStyleSheet(f"color: {Theme.get_color('TEXT_SECONDARY')}; font-style: italic;")
        button_layout.addWidget(self.path_label)

        button_layout.addStretch()

        # Save button
        self.save_btn = QPushButton("Save All Configurations")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_configurations)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.get_color('PRIMARY')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:disabled {{
                background-color: #3d3d3d;
                color: #777777;
            }}
        """)
        button_layout.addWidget(self.save_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.get_color('CONTROL_BG')};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.get_color('CONTROL_HOVER')};
            }}
        """)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def apply_styling(self) -> None:
        """Apply consistent styling to UI components.

        Like applying a layer of dark polish to a digital instrument panel,
        this method ensures our UI maintains the established aesthetic of
        nighttime computing - our preferred environment for manipulating
        the ethereal properties of audio signals.
        """
        # Dark theme colors
        bg_dark = Theme.get_color('BG_DARK')
        bg_medium = Theme.get_color('BG_MEDIUM')
        bg_light = Theme.get_color('BG_LIGHT')
        text_primary = Theme.get_color('TEXT_PRIMARY')
        text_secondary = Theme.get_color('TEXT_SECONDARY')

        # Main dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_dark};
                color: {text_primary};
            }}
            QLabel {{
                color: {text_primary};
            }}
            QGroupBox {{
                color: {text_primary};
            }}
            QComboBox {{
                background-color: {bg_medium};
                color: {text_primary};
                border: 1px solid {bg_light};
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_medium};
                color: {text_primary};
                selection-background-color: {Theme.get_color('PRIMARY')};
                selection-color: white;
            }}
            QLineEdit {{
                background-color: {bg_medium};
                color: {text_primary};
                border: 1px solid {bg_light};
                border-radius: 4px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.get_color('PRIMARY')};
            }}
            QSpinBox {{
                background-color: {bg_medium};
                color: {text_primary};
                border: 1px solid {bg_light};
                border-radius: 4px;
                padding: 5px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {bg_light};
                height: 8px;
                background: {bg_medium};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {Theme.get_color('PRIMARY')};
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QCheckBox {{
                color: {text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid {text_secondary};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {bg_medium};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Theme.get_color('PRIMARY')};
                border: 1px solid {Theme.get_color('PRIMARY')};
            }}
        """)

    def detect_audio_devices(self) -> None:
        """Detect available PipeWire audio devices.

        Like a digital zoologist cataloging the mysterious fauna of the audio
        ecosystem, this method scans the PipeWire wilderness to identify and
        classify the audio devices currently inhabiting the user's system.
        """
        try:
            self.status_label.setText("Detecting audio devices...")
            self.logger.info("Detecting PipeWire audio devices")

            # Clear existing device lists
            self.output_tree.clear()
            self.input_tree.clear()
            self.devices.clear()
            self.output_devices.clear()
            self.input_devices.clear()

            # Use pw-cli to list nodes - the proper, non-root way
            try:
                result = subprocess.run(
                    ["machinectl", "shell", f"{self.username_prop}@.host", "/usr/bin/pw-cli", "list-objects", "Node"],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    error_msg = f"Failed to detect audio devices: {result.stderr.strip()}"
                    self.logger.error(error_msg)
                    self.status_label.setText(f"Error: {error_msg}")
                    return

                # Success - process the output
                output_lines = result.stdout.split('\n')

                device_count = 0
                current_id = None
                current_device = {}

                for line in output_lines:
                    line = line.strip()

                    # Start of a new object
                    if line.startswith("id"):
                        # Process previous device if we have one
                        if current_id is not None and current_device:
                            self._process_device_info(current_id, current_device)
                            device_count += 1

                        # Extract ID for the new device
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_id = parts[1].strip()
                            current_device = {}

                    # Device property
                    elif ":" in line and current_id is not None:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip().strip('"')
                            current_device[key] = value

                # Process the last device
                if current_id is not None and current_device:
                    self._process_device_info(current_id, current_device)
                    device_count += 1

                # Update status with device count
                if device_count > 0:
                    self.status_label.setText(f"Found {len(self.output_devices)} output devices and {len(self.input_devices)} input devices")
                    self.logger.info(f"Detected {device_count} audio devices ({len(self.output_devices)} outputs, {len(self.input_devices)} inputs)")

                    # Update save button state
                    self.save_btn.setEnabled(len(self.devices) > 0)

                    # Update configuration path label
                    if self.config_path:
                        self.path_label.setText(f"Configuration path: {self.config_path}")
                else:
                    self.status_label.setText("No audio devices found")
                    self.logger.warning("No audio devices found")
                    self.save_btn.setEnabled(False)

                # Default select the first output device if available
                if self.output_devices and self.output_tree.topLevelItemCount() > 0:
                    self.output_tree.setCurrentItem(self.output_tree.topLevelItem(0))

            except FileNotFoundError:
                self.status_label.setText("Error: PipeWire CLI not found. Is PipeWire installed?")
                self.logger.error("pw-cli command not found. PipeWire may not be installed or initialized")

        except Exception as e:
            error_msg = f"Error detecting audio devices: {str(e)}"
            self.logger.exception(error_msg)
            self.status_label.setText(f"Error: {error_msg}")

    def _process_device_info(self, device_id: str, device_info: Dict[str, str]) -> None:
        """Process and categorize a detected audio device.

        Args:
            device_id: Device identifier
            device_info: Dictionary of device properties

        Like a meticulous customs agent sorting entities at the border between
        digital and physical realms, this method examines each device's
        properties to determine its nature and classification.
        """
        try:
            # Extract key device properties
            node_name = device_info.get('node.name', '')
            media_class = device_info.get('media.class', '')
            node_nick = device_info.get('node.nick', '')

            # Skip internal monitoring and non-audio devices
            if ('monitor' in node_name.lower() or
                not media_class or
                not node_name or
                'Stream' in node_name or
                'Proxy' in node_name):
                return

            # Determine if this is an input or output device
            is_output = 'Sink' in node_name or 'Output' in media_class or 'Audio/Sink' in media_class
            is_input = 'Source' in node_name or 'Input' in media_class or 'Audio/Source' in media_class

            # Skip if not clearly input or output
            if not is_input and not is_output:
                return

            # Use node.nick as display name if available, otherwise use node.name
            display_name = node_nick if node_nick else node_name

            # Create a device config item
            device = DeviceConfigItem(
                name=node_name,
                nick=display_name,
                device_id=device_id,
                is_output=is_output
            )

            # Generate a filename for this device
            safe_name = ''.join(c if c.isalnum() else '_' for c in display_name).lower()
            device.config['filename'] = f"51-{safe_name}.lua"

            # Add to the appropriate device list
            if is_output:
                self.output_devices.append(device_id)
                self._add_device_to_tree(self.output_tree, device)
            elif is_input:
                self.input_devices.append(device_id)
                self._add_device_to_tree(self.input_tree, device)

            # Add to devices dictionary
            self.devices[device_id] = device

        except Exception as e:
            self.logger.error(f"Error processing device {device_id}: {str(e)}")

    def _add_device_to_tree(self, tree_widget: QTreeWidget, device: DeviceConfigItem) -> None:
        """Add a device to the appropriate tree widget.

        Args:
            tree_widget: The tree widget to add the device to
            device: The device to add
        """
        item = QTreeWidgetItem([device.nick])
        item.setData(0, Qt.ItemDataRole.UserRole, device.device_id)
        tree_widget.addTopLevelItem(item)

    def on_device_selected(self) -> None:
        """Handle device selection in the tree widgets.

        Like a spotlight operator highlighting different performers on a stage,
        this method brings focus to the selected device's configuration options,
        allowing it to take center stage in the user's attention.
        """
        # Check which tree widget has the selection
        selected_tree = None
        if self.output_tree.selectedItems():
            selected_tree = self.output_tree
        elif self.input_tree.selectedItems():
            selected_tree = self.input_tree

        if not selected_tree or not selected_tree.selectedItems():
            # No selection, hide configuration
            self._currently_selected_device = None
            self.hide_device_config()
            return

        # Get the selected device ID
        selected_item = selected_tree.selectedItems()[0]
        device_id = selected_item.data(0, Qt.ItemDataRole.UserRole)

        if device_id not in self.devices:
            self.logger.error(f"Selected device ID not found: {device_id}")
            self.hide_device_config()
            return

        # Update currently selected device
        self._currently_selected_device = device_id

        # Show and populate configuration
        self.show_device_config(self.devices[device_id])

    def hide_device_config(self) -> None:
        """Hide device configuration when no device is selected."""
        self.no_device_label.setVisible(True)
        self.basic_group.setVisible(False)
        self.quality_group.setVisible(False)
        self.advanced_group.setVisible(False)

    def show_device_config(self, device: DeviceConfigItem) -> None:
        """Show and populate configuration for the selected device.

        Args:
            device: The device to configure
        """
        # Hide the placeholder
        self.no_device_label.setVisible(False)

        # Update basic settings
        self.device_name_label.setText(device.name)
        self.nickname_edit.setText(device.nick)
        self.enable_checkbox.setChecked(device.config.get('enabled', True))
        self.default_checkbox.setChecked(device.config.get('default', False))
        self.priority_spin.setValue(device.config.get('priority', 1000))

        # Update audio quality settings
        self.sample_rate_combo.setCurrentText(str(device.config.get('sample_rate', 96000)))
        self.bit_depth_combo.setCurrentText(device.config.get('bit_depth', 'S32LE'))
        self.channels_spin.setValue(device.config.get('channels', 2))
        self.position_combo.setCurrentText(device.config.get('position', 'FL,FR'))
        self.resampler_slider.setValue(device.config.get('resampler_quality', 8))

        # Update advanced settings
        self.mmap_checkbox.setChecked(device.config.get('disable_mmap', False))
        self.batch_checkbox.setChecked(device.config.get('disable_batch', False))
        self.filename_edit.setText(device.config.get('filename', f"51-{device.device_id.replace(':', '_')}.lua"))

        # Show the configuration groups
        self.basic_group.setVisible(True)
        self.quality_group.setVisible(True)
        self.advanced_group.setVisible(True)

        # Temporarily block signals to avoid triggering on_config_changed
        self._block_config_signals(True)

        # Re-enable signals
        self._block_config_signals(False)

    def _block_config_signals(self, block: bool) -> None:
        """Block or unblock signals from configuration widgets.

        Args:
            block: True to block signals, False to unblock

        Like a traffic controller temporarily stopping data flow to avoid
        congestion, this method prevents unwanted signal propagation during
        widget updates, protecting us from an infinite feedback loop of
        change notifications.
        """
        widgets = [
            self.nickname_edit, self.enable_checkbox, self.default_checkbox,
            self.priority_spin, self.sample_rate_combo, self.bit_depth_combo,
            self.channels_spin, self.position_combo, self.resampler_slider,
            self.mmap_checkbox, self.batch_checkbox, self.filename_edit
        ]

        for widget in widgets:
            widget.blockSignals(block)

    def on_config_changed(self) -> None:
        """Handle changes to device configuration settings.

        Like a fastidious accountant tracking every nudge of a widget,
        this method diligently updates our internal records to match the
        current UI state, ensuring our configuration model remains in
        perfect synchronization with the user's expressed intentions.
        """
        if not self._currently_selected_device:
            return

        device = self.devices.get(self._currently_selected_device)
        if not device:
            return

        # Update device configuration from UI
        try:
            # Basic settings
            device.nick = self.nickname_edit.text()
            device.config['enabled'] = self.enable_checkbox.isChecked()
            device.config['default'] = self.default_checkbox.isChecked()
            device.config['priority'] = self.priority_spin.value()

            # Audio quality settings
            device.config['sample_rate'] = int(self.sample_rate_combo.currentText())
            device.config['bit_depth'] = self.bit_depth_combo.currentText()
            device.config['channels'] = self.channels_spin.value()
            device.config['position'] = self.position_combo.currentText()
            device.config['resampler_quality'] = self.resampler_slider.value()

            # Advanced settings
            device.config['disable_mmap'] = self.mmap_checkbox.isChecked()
            device.config['disable_batch'] = self.batch_checkbox.isChecked()
            device.config['filename'] = self.filename_edit.text()

            # Update the device name in the tree
            if self.output_tree.selectedItems():
                self.output_tree.selectedItems()[0].setText(0, device.nick)
            elif self.input_tree.selectedItems():
                self.input_tree.selectedItems()[0].setText(0, device.nick)

            # Enable save button
            self.save_btn.setEnabled(True)
            self._config_modified = True

        except Exception as e:
            self.logger.error(f"Error updating device configuration: {str(e)}")

    def save_configurations(self) -> None:
        """Save all device configurations to files.

        Like a digital archivist cataloging the auditory preferences of a
        fleeting civilization, this method carefully transcribes our device
        configurations into the ancient Lua language, preserving them
        against the entropic forces that seek to return our audio settings
        to their chaotic defaults.
        """
        try:
            # Ensure we have a valid configuration path
            if not self.config_path:
                if not self.username_prop:
                    error_msg = "Cannot save configurations: username not detected"
                    self.logger.error(error_msg)
                    QMessageBox.critical(self, "Error", error_msg)
                    return

                # Set default path
                self.config_path = f"/home/{self.username_prop}/.config/wireplumber/main.lua.d"

            # Create config directory if it doesn't exist
            try:
                os.makedirs(self.config_path, exist_ok=True)
                self.logger.debug(f"Created configuration directory: {self.config_path}")
            except PermissionError:
                error_msg = f"Permission denied: Cannot create directory {self.config_path}"
                self.logger.error(error_msg)
                QMessageBox.critical(self, "Permission Error",
                                    f"{error_msg}\n\nTry running this application with sudo or as root.")
                return
            except Exception as e:
                error_msg = f"Cannot create configuration directory: {str(e)}"
                self.logger.error(error_msg)
                QMessageBox.critical(self, "Error", error_msg)
                return

            # Count how many configurations to save
            enabled_devices = [d for d in self.devices.values() if d.config.get('enabled', True)]
            if not enabled_devices:
                QMessageBox.warning(self, "No Devices", "No enabled devices to configure.")
                return

            # Track what we've saved
            saved_files = []
            default_output_set = False
            default_input_set = False

            # First, save any device marked as default
            for device in enabled_devices:
                if device.config.get('default', False):
                    if device.is_output and not default_output_set:
                        self._save_device_config(device, True)
                        saved_files.append(device.config.get('filename'))
                        default_output_set = True
                    elif not device.is_output and not default_input_set:
                        self._save_device_config(device, True)
                        saved_files.append(device.config.get('filename'))
                        default_input_set = True

            # Then save the rest of the enabled devices
            for device in enabled_devices:
                filename = device.config.get('filename')
                if filename not in saved_files:
                    self._save_device_config(device, False)
                    saved_files.append(filename)

            # Success message
            QMessageBox.information(
                self,
                "Configuration Saved",
                f"Saved {len(saved_files)} device configurations.\n\n"
                f"Configuration files are located in:\n{self.config_path}\n\n"
                "For the changes to take effect, restart PipeWire with:\n"
                "systemctl --user restart pipewire.service\n"
                "systemctl --user restart wireplumber.service"
            )

            # Reset modified flag
            self._config_modified = False
            self.save_btn.setEnabled(False)

            # Emit the config_saved signal
            self.config_saved.emit({
                'path': self.config_path,
                'devices': len(saved_files)
            })

        except Exception as e:
            error_msg = f"Error saving configurations: {str(e)}"
            self.logger.exception(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def _save_device_config(self, device: DeviceConfigItem, is_default: bool) -> None:
        """Save a device configuration to a Lua file.

        Args:
            device: The device to save
            is_default: Whether this is a default device
        """
        # Get filename - use device nickname for the filename if not specified
        filename = device.config.get('filename', f"51-{device.device_id.replace(':', '_')}.lua")

        # Make sure the filename has .lua extension
        if not filename.endswith('.lua'):
            filename += '.lua'

        # Full path to the file
        filepath = os.path.join(self.config_path, filename)

        # Generate the Lua configuration
        config_content = self._generate_lua_config(device, is_default)

        # Write the file
        with open(filepath, 'w') as f:
            f.write(config_content)

        self.logger.info(f"Saved device configuration to: {filepath}")

    def _generate_lua_config(self, device: DeviceConfigItem, is_default: bool) -> str:
        """Generate Lua configuration for a device.

        Args:
            device: The device to generate configuration for
            is_default: Whether this is a default device

        Returns:
            Lua configuration string

        Like a programmer poet crafting stanzas in the arcane language of Lua,
        this method translates the user's audio preferences into script form,
        infusing each line with meaning that only the WirePlumber daemon can
        truly comprehend.
        """
        # Common properties to apply
        properties = {
            "node.description": f"{device.nick}",
            "priority.driver": device.config.get('priority', 1000),
            "priority.session": device.config.get('priority', 1000),
            "node.pause-on-idle": False,
            "audio.format": device.config.get('bit_depth', 'S32LE'),
            "audio.rate": device.config.get('sample_rate', 96000),
            "audio.channels": device.config.get('channels', 2),
            "audio.position": device.config.get('position', 'FL,FR'),
            "resample.quality": device.config.get('resampler_quality', 8),
        }

        # Add advanced options if enabled
        if device.config.get('disable_mmap', False):
            properties["api.alsa.disable-mmap"] = True

        if device.config.get('disable_batch', False):
            properties["api.alsa.disable-batch"] = True

        # If this is a default device, add extra priority
        if is_default:
            properties["priority.driver"] = 2000
            properties["priority.session"] = 2000
            properties["node.description"] = f"Default {device.nick}"

        # Generate Lua table for properties
        props_lua = []
        for key, value in properties.items():
            if isinstance(value, bool):
                props_lua.append(f'    ["{key}"] = {str(value).lower()}')
            elif isinstance(value, (int, float)):
                props_lua.append(f'    ["{key}"] = {value}')
            else:
                props_lua.append(f'    ["{key}"] = "{value}"')

        # Combine properties
        props_str = ",\n".join(props_lua)

        # Create the full Lua configuration
        lua_config = f"""-- Generated by Moinsy PipeWire Configuration
-- Device: {device.nick}
-- Path: {device.name}

local rule = {{
  matches = {{
    {{
      {{ "node.name", "equals", "{device.name}" }},
    }},
  }},
  apply_properties = {{
{props_str}
  }},
}}

table.insert(alsa_monitor.rules, rule)
"""
        return lua_config

    def closeEvent(self, event) -> None:
        """Handle window close event.

        Args:
            event: Close event

        Like a conscientious digital janitor ensuring nothing of value is
        discarded accidentally, this method checks for unsaved changes before
        allowing the window to close, giving the user one last chance to
        preserve their audio configuration efforts from the void of oblivion.
        """
        # Check if there are unsaved changes
        if self._config_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved device configurations. Save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_configurations()
                event.accept()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()


# Utility function to launch the configuration window
def launch_audio_config(parent=None):
    """Launch the audio configuration window.

    Args:
        parent: Optional parent widget

    Returns:
        The configuration window instance
    """
    window = PipeWireConfigWindow(parent)
    window.show()
    return window