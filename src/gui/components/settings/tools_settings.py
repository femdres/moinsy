#!/usr/bin/env python3
"""Module for the tools settings tab."""

import logging
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QCheckBox, QGroupBox, QFormLayout,
    QSpinBox, QSlider
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from managers.config_manager import ConfigManager


class ToolsSettingsTab(QWidget):
    """Tools settings configuration tab."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None):
        """Initialize the tools settings tab.

        Args:
            config_manager: The application configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Update Settings
        update_group = QGroupBox("Updates")
        update_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3d3e42;
                border-radius: 8px;
                margin-top: 16px;
                font-weight: bold;
                color: #888888;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        update_layout = QVBoxLayout(update_group)
        update_layout.setContentsMargins(20, 30, 20, 20)
        update_layout.setSpacing(15)

        # Check for updates on startup
        self.update_check_checkbox = QCheckBox("Check for system updates on application startup")
        self.update_check_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #888888;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }
        """)
        update_layout.addWidget(self.update_check_checkbox)

        update_note = QLabel(
            "If enabled, the application will automatically check for available "
            "system updates when it starts."
        )
        update_note.setStyleSheet("color: #888888; font-size: 12px;")
        update_note.setWordWrap(True)
        update_layout.addWidget(update_note)

        # Hardware Monitor Settings
        hwmon_group = QGroupBox("Hardware Monitor")
        hwmon_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3d3e42;
                border-radius: 8px;
                margin-top: 16px;
                font-weight: bold;
                color: #888888;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        hwmon_layout = QVBoxLayout(hwmon_group)
        hwmon_layout.setContentsMargins(20, 30, 20, 20)
        hwmon_layout.setSpacing(15)

        # Refresh rate with slider and spin box
        refresh_layout = QHBoxLayout()

        refresh_label = QLabel("Refresh Rate:")
        refresh_label.setStyleSheet("color: white;")
        refresh_layout.addWidget(refresh_label)

        self.refresh_slider = QSlider(Qt.Orientation.Horizontal)
        self.refresh_slider.setRange(500, 5000)
        self.refresh_slider.setSingleStep(100)
        self.refresh_slider.setPageStep(500)
        self.refresh_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.refresh_slider.setTickInterval(500)
        self.refresh_slider.setStyleSheet("""
            QSlider {
                height: 30px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #3d3e42;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: none;
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 4px;
            }
        """)
        refresh_layout.addWidget(self.refresh_slider, 1)

        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(500, 5000)
        self.refresh_spin.setSingleStep(100)
        self.refresh_spin.setSuffix(" ms")
        self.refresh_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3d3e42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 16px;
                border: none;
                background-color: #4d4e52;
            }
        """)
        refresh_layout.addWidget(self.refresh_spin)

        # Connect slider and spin box to update each other
        self.refresh_slider.valueChanged.connect(self.refresh_spin.setValue)
        self.refresh_spin.valueChanged.connect(self.refresh_slider.setValue)

        hwmon_layout.addLayout(refresh_layout)

        refresh_note = QLabel(
            "Sets how frequently the hardware monitor updates (in milliseconds). "
            "Lower values provide more real-time data but may use more system resources."
        )
        refresh_note.setStyleSheet("color: #888888; font-size: 12px;")
        refresh_note.setWordWrap(True)
        hwmon_layout.addWidget(refresh_note)

        # Service Manager Settings
        service_group = QGroupBox("Service Manager")
        service_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3d3e42;
                border-radius: 8px;
                margin-top: 16px;
                font-weight: bold;
                color: #888888;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        service_layout = QVBoxLayout(service_group)
        service_layout.setContentsMargins(20, 30, 20, 20)
        service_layout.setSpacing(15)

        # Show all services option
        self.show_all_checkbox = QCheckBox("Show all services (including inactive and disabled)")
        self.show_all_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #888888;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }
        """)
        service_layout.addWidget(self.show_all_checkbox)

        service_note = QLabel(
            "When enabled, all system services will be shown in the Service Manager. "
            "Otherwise, only active services will be displayed."
        )
        service_note.setStyleSheet("color: #888888; font-size: 12px;")
        service_note.setWordWrap(True)
        service_layout.addWidget(service_note)

        # Command Builder Settings
        command_group = QGroupBox("Command Builder")
        command_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3d3e42;
                border-radius: 8px;
                margin-top: 16px;
                font-weight: bold;
                color: #888888;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        command_layout = QVBoxLayout(command_group)
        command_layout.setContentsMargins(20, 30, 20, 20)
        command_layout.setSpacing(15)

        # Command execution confirmation checkbox (added for future implementation)
        self.command_confirm_checkbox = QCheckBox("Confirm before executing commands")
        self.command_confirm_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #888888;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }
        """)
        command_layout.addWidget(self.command_confirm_checkbox)

        command_note = QLabel(
            "When enabled, a confirmation dialog will appear before executing commands "
            "from the Command Builder. This provides an additional safety check."
        )
        command_note.setStyleSheet("color: #888888; font-size: 12px;")
        command_note.setWordWrap(True)
        command_layout.addWidget(command_note)

        # Add groups to layout
        layout.addWidget(update_group)
        layout.addWidget(hwmon_group)
        layout.addWidget(service_group)
        layout.addWidget(command_group)
        layout.addStretch()

    def load_settings(self) -> None:
        """Load settings from config manager."""
        try:
            # Update settings
            update_check = self.config_manager.get_setting("tools", "update_check_on_startup", True)
            self.update_check_checkbox.setChecked(update_check)

            # Hardware monitor settings
            refresh_rate = self.config_manager.get_setting("tools", "hardware_monitor_refresh_rate", 1000)
            self.refresh_spin.setValue(refresh_rate)
            self.refresh_slider.setValue(refresh_rate)  # This will update both due to the connection

            # Service manager settings
            show_all = self.config_manager.get_setting("tools", "service_manager_show_all", False)
            self.show_all_checkbox.setChecked(show_all)

            # Command builder settings (for future implementation)
            # Using a default setting name that can be implemented later
            command_confirm = self.config_manager.get_setting("tools", "command_confirm_execution", True)
            self.command_confirm_checkbox.setChecked(command_confirm)

            self.logger.debug("Tools settings loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading tools settings: {str(e)}")

    def save_settings(self) -> None:
        """Save settings to config manager."""
        try:
            # Update settings
            self.config_manager.set_setting("tools", "update_check_on_startup",
                                            self.update_check_checkbox.isChecked())

            # Hardware monitor settings
            self.config_manager.set_setting("tools", "hardware_monitor_refresh_rate",
                                            self.refresh_spin.value())

            # Service manager settings
            self.config_manager.set_setting("tools", "service_manager_show_all",
                                            self.show_all_checkbox.isChecked())

            # Command builder settings (for future implementation)
            self.config_manager.set_setting("tools", "command_confirm_execution",
                                            self.command_confirm_checkbox.isChecked())

            self.logger.debug("Tools settings saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving tools settings: {str(e)}")
            raise