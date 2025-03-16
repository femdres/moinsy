#!/usr/bin/env python3
"""Module for the system settings tab."""

import logging
import os
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QCheckBox, QGroupBox, QFormLayout,
    QLineEdit, QFileDialog, QListWidget, QListWidgetItem,
    QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from managers.config_manager import ConfigManager


class SystemSettingsTab(QWidget):
    """System settings configuration tab."""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None):
        """Initialize the system settings tab.

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

        # Security Settings
        security_group = QGroupBox("Security")
        security_group.setStyleSheet("""
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

        security_layout = QVBoxLayout(security_group)
        security_layout.setContentsMargins(20, 30, 20, 20)
        security_layout.setSpacing(15)

        # Sudo credentials checkbox
        self.sudo_remember_checkbox = QCheckBox("Remember sudo credentials for current session")
        self.sudo_remember_checkbox.setStyleSheet("""
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
        security_layout.addWidget(self.sudo_remember_checkbox)

        security_layout.addSpacing(10)

        security_warning = QLabel(
            "Note: Enabling this option may reduce the number of password prompts "
            "during the current session. For security, credentials are never stored permanently."
        )
        security_warning.setStyleSheet("color: #888888; font-size: 12px;")
        security_warning.setWordWrap(True)
        security_layout.addWidget(security_warning)

        # Package Managers Settings
        package_group = QGroupBox("Package Management")
        package_group.setStyleSheet("""
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

        package_layout = QVBoxLayout(package_group)
        package_layout.setContentsMargins(20, 30, 20, 20)
        package_layout.setSpacing(15)

        package_layout.addWidget(QLabel("Package Manager Priority:"))

        # Package manager priority list
        self.package_manager_list = QListWidget()
        self.package_manager_list.setStyleSheet("""
            QListWidget {
                background-color: #3d3e42;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #4d4e52;
            }
        """)

        # Add package managers
        self.package_managers = ["apt", "flatpak", "snap"]
        for pm in self.package_managers:
            item = QListWidgetItem(pm)
            self.package_manager_list.addItem(item)

        package_layout.addWidget(self.package_manager_list)

        # Up/Down buttons for reordering
        buttons_layout = QHBoxLayout()

        move_up_button = QPushButton("Move Up")
        move_up_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3e42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4d4e52;
            }
        """)
        move_up_button.clicked.connect(self.move_item_up)

        move_down_button = QPushButton("Move Down")
        move_down_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3e42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4d4e52;
            }
        """)
        move_down_button.clicked.connect(self.move_item_down)

        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        package_layout.addLayout(buttons_layout)

        pm_explanation = QLabel(
            "Determines which package manager to use when multiple options are available. "
            "Arranging the list sets the priority (highest at top)."
        )
        pm_explanation.setStyleSheet("color: #888888; font-size: 12px;")
        pm_explanation.setWordWrap(True)
        package_layout.addWidget(pm_explanation)

        # Logging Settings
        logging_group = QGroupBox("Logging")
        logging_group.setStyleSheet("""
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

        logging_layout = QFormLayout(logging_group)
        logging_layout.setContentsMargins(20, 30, 20, 20)
        logging_layout.setSpacing(15)

        # Log level selection
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setStyleSheet("""
            QComboBox {
                background-color: #3d3e42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #3d3e42;
                color: white;
                selection-background-color: #4CAF50;
            }
        """)
        logging_layout.addRow("Log Level:", self.log_level_combo)

        # Log file path
        log_path_layout = QHBoxLayout()

        self.log_file_edit = QLineEdit()
        self.log_file_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3e42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        log_path_layout.addWidget(self.log_file_edit, 1)

        browse_button = QToolButton()
        browse_button.setText("...")
        browse_button.setStyleSheet("""
            QToolButton {
                background-color: #3d3e42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #4d4e52;
            }
        """)
        browse_button.clicked.connect(self.browse_log_file)
        log_path_layout.addWidget(browse_button)

        logging_layout.addRow("Log File:", log_path_layout)

        # Add a note about log file
        log_note = QLabel(
            "Leave empty to use the default log file location. "
            "Changes will take effect after restarting the application."
        )
        log_note.setStyleSheet("color: #888888; font-size: 12px;")
        log_note.setWordWrap(True)
        logging_layout.addRow("", log_note)

        # Add groups to layout
        layout.addWidget(security_group)
        layout.addWidget(package_group)
        layout.addWidget(logging_group)
        layout.addStretch()

    def load_settings(self) -> None:
        """Load settings from config manager."""
        try:
            # Security settings
            sudo_remember = self.config_manager.get_setting("system", "sudo_remember_credentials", True)
            self.sudo_remember_checkbox.setChecked(sudo_remember)

            # Package manager priority
            pm_priority = self.config_manager.get_setting("system", "package_manager_priority",
                                                          ["apt", "flatpak", "snap"])

            # Clear and rebuild the list according to priority
            self.package_manager_list.clear()
            for pm in pm_priority:
                if pm in self.package_managers:
                    item = QListWidgetItem(pm)
                    self.package_manager_list.addItem(item)

            # Make sure any remaining package managers are added to the end
            for pm in self.package_managers:
                if pm not in pm_priority:
                    item = QListWidgetItem(pm)
                    self.package_manager_list.addItem(item)

            # Logging settings
            log_level = self.config_manager.get_setting("system", "log_level", "INFO")
            level_index = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}.get(log_level, 1)
            self.log_level_combo.setCurrentIndex(level_index)

            log_file = self.config_manager.get_setting("system", "log_file", "")
            self.log_file_edit.setText(log_file)

            self.logger.debug("System settings loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading system settings: {str(e)}")

    def save_settings(self) -> None:
        """Save settings to config manager."""
        try:
            # Security settings
            self.config_manager.set_setting("system", "sudo_remember_credentials",
                                            self.sudo_remember_checkbox.isChecked())

            # Package manager priority
            pm_priority = []
            for i in range(self.package_manager_list.count()):
                pm_priority.append(self.package_manager_list.item(i).text())

            self.config_manager.set_setting("system", "package_manager_priority", pm_priority)

            # Logging settings
            log_level = self.log_level_combo.currentText()
            self.config_manager.set_setting("system", "log_level", log_level)

            log_file = self.log_file_edit.text().strip()
            self.config_manager.set_setting("system", "log_file", log_file)

            self.logger.debug("System settings saved successfully")

        except Exception as e:
            self.logger.error(f"Error saving system settings: {str(e)}")
            raise

    def move_item_up(self) -> None:
        """Move the selected item up in the list."""
        current_row = self.package_manager_list.currentRow()
        if current_row > 0:
            current_item = self.package_manager_list.takeItem(current_row)
            self.package_manager_list.insertItem(current_row - 1, current_item)
            self.package_manager_list.setCurrentRow(current_row - 1)

    def move_item_down(self) -> None:
        """Move the selected item down in the list."""
        current_row = self.package_manager_list.currentRow()
        if current_row < self.package_manager_list.count() - 1:
            current_item = self.package_manager_list.takeItem(current_row)
            self.package_manager_list.insertItem(current_row + 1, current_item)
            self.package_manager_list.setCurrentRow(current_row + 1)

    def browse_log_file(self) -> None:
        """Open file dialog to select log file path."""
        default_path = self.log_file_edit.text()
        if not default_path:
            # Use home directory if no path specified
            default_path = os.path.expanduser("~")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File",
            default_path,
            "Log Files (*.log);;All Files (*)"
        )

        if file_path:
            self.log_file_edit.setText(file_path)