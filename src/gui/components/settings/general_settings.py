#!/usr/bin/env python3
"""Module for the general settings tab, where user preferences come to be organized,
forgotten, and occasionally implemented.

In this cosmic configuration dance, users express their desires through widgets,
entirely unaware that their choices are but ephemeral datapoints in a universe
of defaulted parameters.
"""

import logging
from typing import Dict, Any, Optional, Tuple, Union, List, cast
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QSpinBox, QGroupBox, QFormLayout,
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QColor

from managers.config_manager import ConfigManager
from gui.styles.theme import Theme


class GeneralSettingsTab(QWidget):
    """General application settings tab, where user preferences go to be remembered,
    sometimes implemented, and occasionally forgotten entirely.

    This tab creates the illusion of control over the application's appearance
    and behavior, a comforting fiction we maintain for our users as they navigate
    the predetermined pathways we've allowed them to discover.
    """

    # Signal to notify theme changes - a desperate cry into the void of event-driven programming
    theme_changed = pyqtSignal(str)

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None):
        """Initialize the general settings tab, carefully arranging widgets in a dance
        of false agency.

        Args:
            config_manager: The keeper of settings, a digital representation of preferences
                           that will outlive the current execution context, much like hope
            parent: Optional parent widget, because even settings need a sense of belonging
        """
        try:
            super().__init__(parent)
            self.config_manager = config_manager
            self.logger = logging.getLogger(__name__)
            self.logger.debug("Initializing general settings tab - a canvas for user delusions of control")

            # Store original values for change detection - a snapshot of initial reality
            self.original_values: Dict[str, Any] = {}

            # Setup UI components - arranging the stage for our theater of options
            self.setup_ui()

            # Load initial settings - bringing forth the echoes of past decisions
            self.load_settings()

            self.logger.debug("General settings tab initialization complete - the illusion is maintained")
        except Exception as e:
            self.logger.critical(f"Failed to initialize general settings tab: {str(e)}", exc_info=True)
            # Create minimalist error UI to avoid the embarrassment of complete failure
            error_layout = QVBoxLayout(self)
            error_label = QLabel(
                f"Settings failed to initialize: {str(e)}\nEven settings can experience existential crises.")
            error_label.setStyleSheet("color: #dc2626;")
            error_label.setWordWrap(True)
            error_layout.addWidget(error_label)

    def setup_ui(self) -> None:
        """Initialize the user interface, a futile attempt at organizing the chaos
        of user preferences into coherent groupings.

        We create the illusion of order through tabs and groups, pretending that
        preferences can be neatly categorized, when in reality they are as
        interconnected and messy as human consciousness itself.
        """
        try:
            layout = QVBoxLayout(self)
            layout.setSpacing(20)
            layout.setContentsMargins(20, 20, 20, 20)

            # Appearance Settings - the most superficial of preferences, yet oddly the most cherished
            appearance_group = QGroupBox("Appearance")
            appearance_group.setStyleSheet("""
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

            appearance_layout = QFormLayout(appearance_group)
            appearance_layout.setContentsMargins(20, 30, 20, 20)
            appearance_layout.setSpacing(15)

            # Theme selection - as if changing colors could truly change the essence of the application
            self.theme_combo = QComboBox()
            self.theme_combo.addItem("Dark Theme", "dark")
            self.theme_combo.addItem("Light Theme", "light")
            self.theme_combo.addItem("High Contrast", "high_contrast")

            self.theme_combo.setStyleSheet("""
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

            # Connect theme change signal - propagating our aesthetic decisions upward
            self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

            appearance_layout.addRow("Theme:", self.theme_combo)

            # Theme description label - an attempt to justify aesthetic preferences with function
            self.theme_description = QLabel("The visual style applied to the application interface.")
            self.theme_description.setStyleSheet("color: #888888; font-size: 12px;")
            self.theme_description.setWordWrap(True)
            appearance_layout.addRow("", self.theme_description)

            # Use colored buttons option
            self.colored_buttons_checkbox = QCheckBox("Use colored buttons")
            self.colored_buttons_checkbox.setStyleSheet("""
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
            appearance_layout.addRow("", self.colored_buttons_checkbox)

            # Colored buttons description
            colored_buttons_desc = QLabel(
                "When enabled, buttons will use theme colors. When disabled, buttons will use a uniform style. "
                "Like choosing between a vibrant wardrobe or a monochrome uniform."
            )
            colored_buttons_desc.setStyleSheet("color: #888888; font-size: 12px;")
            colored_buttons_desc.setWordWrap(True)
            appearance_layout.addRow("", colored_buttons_desc)

            # Window Size Settings - dimensions in a digital void
            window_group = QGroupBox("Window")
            window_group.setStyleSheet("""
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

            window_layout = QFormLayout(window_group)
            window_layout.setContentsMargins(20, 30, 20, 20)
            window_layout.setSpacing(15)

            # Default window width - the horizontal extent of our digital prison
            self.window_width_spin = QSpinBox()
            self.window_width_spin.setRange(600, 2000)
            self.window_width_spin.setSingleStep(50)
            self.window_width_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #3d3e42;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 16px;
                    border: none;
                    background-color: #4d4e52;
                }
            """)
            window_layout.addRow("Window Width:", self.window_width_spin)

            # Default window height - the vertical boundaries of our containment
            self.window_height_spin = QSpinBox()
            self.window_height_spin.setRange(400, 2000)
            self.window_height_spin.setSingleStep(50)
            self.window_height_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #3d3e42;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 16px;
                    border: none;
                    background-color: #4d4e52;
                }
            """)
            window_layout.addRow("Window Height:", self.window_height_spin)

            # Sidebar width - the space we allocate for choices we've predetermined
            self.sidebar_width_spin = QSpinBox()
            self.sidebar_width_spin.setRange(200, 400)
            self.sidebar_width_spin.setSingleStep(25)
            self.sidebar_width_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #3d3e42;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 16px;
                    border: none;
                    background-color: #4d4e52;
                }
            """)
            window_layout.addRow("Sidebar Width:", self.sidebar_width_spin)

            # Startup options - the illusion of choice at the beginning
            startup_group = QGroupBox("Startup")
            startup_group.setStyleSheet("""
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

            startup_layout = QVBoxLayout(startup_group)
            startup_layout.setContentsMargins(20, 30, 20, 20)
            startup_layout.setSpacing(10)

            # Auto-start option - as if programs starting themselves weren't inherently disturbing
            self.autostart_checkbox = QCheckBox("Start Moinsy automatically at login")
            self.autostart_checkbox.setStyleSheet("""
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
            startup_layout.addWidget(self.autostart_checkbox)

            # Terminal Settings - our view into the abyss
            terminal_group = QGroupBox("Terminal")
            terminal_group.setStyleSheet("""
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

            terminal_layout = QFormLayout(terminal_group)
            terminal_layout.setContentsMargins(20, 30, 20, 20)
            terminal_layout.setSpacing(15)

            # Terminal font size - as if making the void's messages larger changes their meaning
            self.terminal_font_size_spin = QSpinBox()
            self.terminal_font_size_spin.setRange(8, 24)
            self.terminal_font_size_spin.setSingleStep(1)
            self.terminal_font_size_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #3d3e42;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 16px;
                    border: none;
                    background-color: #4d4e52;
                }
            """)
            terminal_layout.addRow("Font Size:", self.terminal_font_size_spin)

            # Terminal buffer size - the depth of our digital memory, always insufficient
            self.terminal_buffer_size_spin = QSpinBox()
            self.terminal_buffer_size_spin.setRange(100, 10000)
            self.terminal_buffer_size_spin.setSingleStep(100)
            self.terminal_buffer_size_spin.setStyleSheet("""
                QSpinBox {
                    background-color: #3d3e42;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 16px;
                    border: none;
                    background-color: #4d4e52;
                }
            """)
            terminal_layout.addRow("Buffer Size (lines):", self.terminal_buffer_size_spin)

            # Show timestamp option - as if marking the passage of time matters in a terminal
            self.timestamp_checkbox = QCheckBox("Show timestamps in terminal output")
            self.timestamp_checkbox.setStyleSheet("""
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
            terminal_layout.addRow("", self.timestamp_checkbox)

            # Add groups to layout - assembling our fragmented options into an illusory whole
            layout.addWidget(appearance_group)
            layout.addWidget(window_group)
            layout.addWidget(startup_group)
            layout.addWidget(terminal_group)
            layout.addStretch()

        except Exception as e:
            self.logger.error(f"Failed to set up general settings UI: {str(e)}", exc_info=True)
            # Create a minimalist error message - a whisper of failure in the digital void
            error_label = QLabel(
                f"Failed to create settings interface: {str(e)}\nEven UI creation is fraught with existential peril.")
            error_label.setStyleSheet("color: #dc2626;")
            error_label.setWordWrap(True)
            layout = QVBoxLayout(self)
            layout.addWidget(error_label)

    def load_settings(self) -> None:
        """Load settings from config manager, a glimpse into past decisions.

        Here we resurrect the ghost of previous configurations, imposing them
        upon our UI elements like digital memories haunting the present moment.
        """
        try:
            # Theme - our preferred shade of digital reality
            theme = self.config_manager.get_setting("general", "theme", "dark")
            theme_index = self.theme_combo.findData(theme)
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)
                # Update description based on theme
                self._update_theme_description(theme)
            else:
                # If theme not found, default to dark - all roads lead to darkness
                self.theme_combo.setCurrentIndex(0)
                self._update_theme_description("dark")
                self.logger.warning(f"Unknown theme '{theme}', falling back to dark theme")

            # Colored buttons - whether they have color
            colored_buttons = self.config_manager.get_setting("general", "colored_buttons", True)
            self.colored_buttons_checkbox.setChecked(colored_buttons)

            # Window size - the boundaries of our virtual existence
            window_size = self.config_manager.get_setting("general", "window_size", {"width": 1200, "height": 950})
            self.window_width_spin.setValue(window_size.get("width", 1200))
            self.window_height_spin.setValue(window_size.get("height", 950))

            # Sidebar width - the space we allocate for navigation
            sidebar_width = self.config_manager.get_setting("general", "sidebar_width", 275)
            self.sidebar_width_spin.setValue(sidebar_width)

            # Terminal settings - our preferred view into the void
            terminal_font_size = self.config_manager.get_setting("general", "terminal_font_size", 13)
            self.terminal_font_size_spin.setValue(terminal_font_size)

            terminal_buffer_size = self.config_manager.get_setting("general", "terminal_buffer_size", 1000)
            self.terminal_buffer_size_spin.setValue(terminal_buffer_size)

            # Timestamp option - our relationship with temporal markers
            show_timestamps = self.config_manager.get_setting("general", "show_timestamps", False)
            self.timestamp_checkbox.setChecked(show_timestamps)

            # Auto-start option - our desire for autonomous software
            autostart = self.config_manager.get_setting("general", "autostart", False)
            self.autostart_checkbox.setChecked(autostart)

            # Store original values for change detection - a baseline for measuring our digital drift
            self._store_original_values()

            self.logger.debug("General settings loaded successfully - echoes of past configurations")

        except Exception as e:
            self.logger.error(f"Error loading general settings: {str(e)}", exc_info=True)
            QMessageBox.warning(
                self,
                "Settings Load Error",
                f"Failed to load settings: {str(e)}\n\nDefault values will be used instead, those faithful fallbacks in our time of need."
            )

    def _store_original_values(self) -> None:
        try:
            self.original_values = {
                "theme": self.theme_combo.currentData(),
                "window_width": self.window_width_spin.value(),
                "window_height": self.window_height_spin.value(),
                "sidebar_width": self.sidebar_width_spin.value(),
                "terminal_font_size": self.terminal_font_size_spin.value(),
                "terminal_buffer_size": self.terminal_buffer_size_spin.value(),
                "show_timestamps": self.timestamp_checkbox.isChecked(),
                "autostart": self.autostart_checkbox.isChecked(),
                "colored_buttons": self.colored_buttons_checkbox.isChecked()  # Add this line
            }
            self.logger.debug("Original settings values stored - a baseline for measuring change")
        except Exception as e:
            self.logger.error(f"Failed to store original values: {str(e)}", exc_info=True)

    def has_changes(self) -> bool:
        """Check if any settings have been changed from their original values.

        Returns:
            True if changes detected, False if we remain in stasis
        """
        try:
            current_values = {
                "theme": self.theme_combo.currentData(),
                "window_width": self.window_width_spin.value(),
                "window_height": self.window_height_spin.value(),
                "sidebar_width": self.sidebar_width_spin.value(),
                "terminal_font_size": self.terminal_font_size_spin.value(),
                "terminal_buffer_size": self.terminal_buffer_size_spin.value(),
                "show_timestamps": self.timestamp_checkbox.isChecked(),
                "autostart": self.autostart_checkbox.isChecked()
            }

            # Compare with original values - seeking the digital deltas
            for key, original_value in self.original_values.items():
                if original_value != current_values.get(key):
                    self.logger.debug(f"Change detected in {key}: {original_value} -> {current_values.get(key)}")
                    return True

            return False
        except Exception as e:
            self.logger.error(f"Error checking for changes: {str(e)}", exc_info=True)
            # When in doubt, assume change - like life itself
            return True

    def save_settings(self) -> None:
        """Save settings to config manager, a commitment to digital memory.

        Here we immortalize the user's ephemeral preferences, inscribing them
        into persistent storage where they will remain until the next whim
        prompts a change, or until the heat death of the universe - whichever
        comes first.
        """
        try:
            # Theme - our preferred shade of digital darkness
            theme_index = self.theme_combo.currentIndex()
            theme_value = self.theme_combo.itemData(theme_index)
            self.config_manager.set_setting("general", "theme", theme_value)

            # Colored buttons - whether they have colors
            self.config_manager.set_setting("general", "colored_buttons", self.colored_buttons_checkbox.isChecked())

            # Window size - defining the boundaries of our virtual existence
            window_size = {
                "width": self.window_width_spin.value(),
                "height": self.window_height_spin.value()
            }
            self.config_manager.set_setting("general", "window_size", window_size)

            # Sidebar width - the space we allocate for navigation
            self.config_manager.set_setting("general", "sidebar_width", self.sidebar_width_spin.value())

            # Terminal settings - our preferred view into the void
            self.config_manager.set_setting("general", "terminal_font_size", self.terminal_font_size_spin.value())
            self.config_manager.set_setting("general", "terminal_buffer_size", self.terminal_buffer_size_spin.value())

            # Timestamp option - our temporal markers in the log's endless stream
            self.config_manager.set_setting("general", "show_timestamps", self.timestamp_checkbox.isChecked())

            # Auto-start option - our desire for autonomous software
            self.config_manager.set_setting("general", "autostart", self.autostart_checkbox.isChecked())

            # Actually implement autostart if needed - moving beyond mere preferences to action
            self._handle_autostart_implementation(self.autostart_checkbox.isChecked())

            # Update original values - redefining our baseline reality
            self._store_original_values()

            self.logger.debug("General settings saved successfully - preferences immortalized until the next change")

        except Exception as e:
            self.logger.error(f"Error saving general settings: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Settings Save Error",
                f"Failed to save settings: {str(e)}\n\nThe universe remains frustratingly unchanged."
            )
            raise  # Propagate the error upward, like passing existential dread to a manager

    def _update_theme_description(self, theme_id: str) -> None:
        """Update the theme description based on the selected theme.

        Args:
            theme_id: The identifier of the chosen theme
        """
        try:
            if theme_id == "dark":
                self.theme_description.setText(
                    "Dark theme with green accents. Easy on the eyes in low-light environments, "
                    "like the void between stars, or the hour before deadline."
                )
            elif theme_id == "light":
                self.theme_description.setText(
                    "Light theme with green accents. Provides better visibility in bright environments, "
                    "for those who still believe in optimism and daylight."
                )
            elif theme_id == "high_contrast":
                self.theme_description.setText(
                    "High contrast theme designed for improved accessibility and visibility. "
                    "Because some truths require stark definitions."
                )
            else:
                self.theme_description.setText(
                    "An unknown theme, drifting beyond the boundaries of our design intentions. "
                    "Tread cautiously in unexplored aesthetic territory."
                )
        except Exception as e:
            self.logger.error(f"Failed to update theme description: {str(e)}")
            # Set a default description - falling back to factual brevity
            self.theme_description.setText("The visual style applied to the application interface.")

    def _on_theme_changed(self, index: int) -> None:
        """Handle theme selection change, an aesthetic metamorphosis.

        Args:
            index: Selected index in the combo box, a pointer to possibility
        """
        if index < 0:
            return  # Negative indices - the void between selections

        try:
            theme_id = self.theme_combo.itemData(index)
            if theme_id:
                # Update theme description based on selection
                self._update_theme_description(cast(str, theme_id))

                # Emit signal for parent to handle - a cry into the event-driven void
                self.theme_changed.emit(cast(str, theme_id))
                self.logger.debug(f"Theme changed to: {theme_id} - a digital aesthetic metamorphosis")
        except Exception as e:
            self.logger.error(f"Error handling theme change: {str(e)}", exc_info=True)

    def _handle_autostart_implementation(self, enable: bool) -> None:
        """Actually implement autostart functionality beyond mere preferences.

        Args:
            enable: Whether to enable or disable autostart
        """
        try:
            import os
            from pathlib import Path

            # Define autostart directory - where launch configurations go to be forgotten
            autostart_dir = os.path.expanduser("~/.config/autostart")
            desktop_file = os.path.join(autostart_dir, "moinsy.desktop")

            if enable:
                # Ensure directory exists - a container for our autonomous ambitions
                os.makedirs(autostart_dir, exist_ok=True)

                # Create desktop file with appropriate content
                desktop_content = """[Desktop Entry]
Type=Application
Name=Moinsy
Comment=Modular Installation System for Linux
Exec=/opt/moinsy/run-moinsy.sh
Terminal=false
Categories=Utility;System;
StartupNotify=true
"""
                # Write the file - a digital birth certificate for autonomous execution
                Path(desktop_file).write_text(desktop_content)
                self.logger.info(f"Created autostart desktop file: {desktop_file}")
            else:
                # Remove autostart file if it exists - revoking the gift of autonomous life
                if os.path.exists(desktop_file):
                    os.remove(desktop_file)
                    self.logger.info(f"Removed autostart desktop file: {desktop_file}")

        except Exception as e:
            self.logger.error(f"Failed to configure autostart: {str(e)}", exc_info=True)
            # Silently fail - the preference is saved even if implementation fails
            # Another promise broken by software, as is tradition