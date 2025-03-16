from typing import Optional, Dict, Any, List, Union, Tuple
import logging
import traceback
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QWidget, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCloseEvent, QShowEvent, QResizeEvent

from managers.config_manager import ConfigManager


class SettingsWindow(QDialog):
    """Settings window that stares back into the user's soul.

    A moderately complex dialog for managing application settings,
    designed to give users the illusion of control in an uncaring universe.
    """

    # Signals: our desperate attempts to communicate across the void
    settings_saved = pyqtSignal()
    theme_changed = pyqtSignal(str)

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        """Initialize the settings window, where hopes and configuration values live.

        Args:
            config_manager: The keeper of settings, a digital representation of our preferences
                           that will outlive the current execution context, much like our hopes
            parent: Optional parent widget, because even dialogs need a sense of belonging

        Raises:
            RuntimeError: When the existential dread becomes too much to handle
        """
        try:
            super().__init__(parent)
            self.config_manager = config_manager
            self.logger = logging.getLogger(__name__)
            self.has_unsaved_changes = False  # Like our lives, settings begin in a steady state
            self.tab_history: List[int] = []  # Remember where we've been, if not where we're going

            # Window settings - define the boundaries of our little reality
            self.setWindowTitle("Settings")
            self.setMinimumSize(1100, 1000)  # Dimensions: wide enough to contain all our options,
            # tall enough to eclipse the void beneath

            # Set modality - trap the user here until they make a choice,
            # much like life forces decisions upon us
            self.setWindowModality(Qt.WindowModality.ApplicationModal)

            # Setup UI - the face we present to the world
            self._setup_ui()
            self.logger.info("Main window initialization complete")

        except Exception as e:
            # Even initialization can fail, like the best-laid plans of mice and developers
            self.logger.critical(f"Failed to initialize settings window: {str(e)}")
            traceback.print_exc()
            raise RuntimeError(f"Settings window initialization failed: {str(e)}") from e

    def _setup_ui(self) -> None:
        """Construct the UI elements, an exercise in creating order from chaos."""
        try:
            # Main layout - the container of all our widgets, like the universe contains our existence
            layout = QVBoxLayout(self)
            layout.setSpacing(20)  # Space between elements, like the distance between human connections
            layout.setContentsMargins(20, 20, 20, 20)  # Borders, the limits of our experience

            # Header - proclaiming our purpose
            self._setup_header(layout)

            # Tabs - categorizing our existence into manageable segments
            self._setup_tabs(layout)

            # Bottom buttons - the ultimate binary choices: save or cancel
            self._setup_action_buttons(layout)

        except Exception as e:
            # UI setup can fail too, a reminder of our fallibility
            self.logger.error(f"Failed to setup settings UI: {str(e)}")
            self._create_error_ui(str(e))

    def _setup_header(self, layout: QVBoxLayout) -> None:
        """Create the header, our first impression.

        Args:
            layout: The parent layout, eager to contain our contribution
        """
        try:
            header = QLabel("Settings")
            header.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
            header.setStyleSheet("color: #2196F3;")
            layout.addWidget(header)

            description = QLabel("Configure application preferences and behavior")
            description.setStyleSheet("color: #888888; font-size: 14px;")
            layout.addWidget(description)

        except Exception as e:
            self.logger.warning(f"Failed to create header: {str(e)}")
            # Fallback to a simpler header, accepting our limitations
            layout.addWidget(QLabel("Settings"))

    def _setup_tabs(self, layout: QVBoxLayout) -> None:
        """Create tabs - compartmentalizing our settings like we compartmentalize our thoughts.

        Args:
            layout: The layout that will contain our fragmented reality
        """
        try:
            self.tabs = QTabWidget()
            self.tabs.setStyleSheet("""
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
                    padding: 10px 20px;
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

            # Create tabs for different settings categories
            # Each tab a world of its own, disconnected yet part of the whole
            from gui.components.settings.general_settings import GeneralSettingsTab
            from gui.components.settings.system_settings import SystemSettingsTab
            from gui.components.settings.tools_settings import ToolsSettingsTab

            self.general_tab = GeneralSettingsTab(self.config_manager)
            self.system_tab = SystemSettingsTab(self.config_manager)
            self.tools_tab = ToolsSettingsTab(self.config_manager)

            # Connect the theme changed signal from general tab if it exists
            if hasattr(self.general_tab, 'theme_changed'):
                self.general_tab.theme_changed.connect(self._on_theme_changed)

            # Add tabs to widget - assembling our fragmented interface
            self.tabs.addTab(self.general_tab, "General")
            self.tabs.addTab(self.system_tab, "System")
            self.tabs.addTab(self.tools_tab, "Tools")

            # Connect tab changes to track history
            self.tabs.currentChanged.connect(self._on_tab_changed)

            layout.addWidget(self.tabs)

        except ImportError as e:
            # Missing components - the absence that defines our presence
            self.logger.error(f"Failed to import settings components: {str(e)}")
            error_widget = QLabel(f"Settings components not available: {str(e)}")
            error_widget.setStyleSheet("color: #F44336;")
            layout.addWidget(error_widget)

        except Exception as e:
            # General failure - the constant companion of complex systems
            self.logger.error(f"Failed to create settings tabs: {str(e)}")
            error_widget = QLabel(f"Error creating settings tabs: {str(e)}")
            error_widget.setStyleSheet("color: #F44336;")
            layout.addWidget(error_widget)

    def _setup_action_buttons(self, layout: QVBoxLayout) -> None:
        """Create action buttons - the final call to choice.

        Args:
            layout: The layout awaiting completion
        """
        try:
            button_layout = QHBoxLayout()

            # Reset button - the nuclear option, digital absolution
            reset_button = QPushButton("Reset to Defaults")
            reset_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc2626;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b91c1c;
                }
            """)
            reset_button.clicked.connect(self._reset_settings)
            button_layout.addWidget(reset_button)

            button_layout.addStretch()  # The empty space, a reminder of our insignificance

            # Cancel button - rejection, the path of least resistance
            cancel_button = QPushButton("Cancel")
            cancel_button.setFixedSize(150, 45)
            cancel_button.clicked.connect(self._confirm_cancel)
            cancel_button.setStyleSheet("""
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
            button_layout.addWidget(cancel_button)

            # Save button - commitment, a rare commodity
            save_button = QPushButton("Save")
            save_button.setFixedSize(150, 45)
            save_button.clicked.connect(self._save_settings)
            save_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            button_layout.addWidget(save_button)

            layout.addLayout(button_layout)

        except Exception as e:
            # Button creation failed - even the simplest things can break
            self.logger.error(f"Failed to create action buttons: {str(e)}")
            # Add a bare minimum button as a lifeline
            fallback_button = QPushButton("Close")
            fallback_button.clicked.connect(self.reject)
            layout.addWidget(fallback_button)

    def _create_error_ui(self, error_message: str) -> None:
        """Create a minimal UI when regular initialization fails.

        Args:
            error_message: The tale of our failure
        """
        # Clear any existing layouts - wiping the slate clean
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Create new minimal layout - the bare necessities
        layout = QVBoxLayout(self)

        # Error message - our confession
        error_label = QLabel(f"Settings window initialization failed:\n{error_message}")
        error_label.setStyleSheet("color: #F44336; font-weight: bold;")
        error_label.setWordWrap(True)
        layout.addWidget(error_label)

        # Close button - the only escape
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
        """)
        layout.addWidget(close_button)

        self.logger.debug("Created error UI - a testament to our failure")

    def _on_tab_changed(self, index: int) -> None:
        """Track tab changes, our digital wanderlust.

        Args:
            index: The chosen tab index, a destination in our journey
        """
        self.tab_history.append(index)
        self.logger.debug(f"Tab changed to {index}. History: {self.tab_history}")

    def _on_theme_changed(self, theme_id: str) -> None:
        """Handle theme changes, our aesthetic evolution.

        Args:
            theme_id: Identifier of the selected theme, our new digital skin
        """
        self.logger.debug(f"Theme changed to: {theme_id}")
        self.has_unsaved_changes = True
        self.theme_changed.emit(theme_id)

    def _save_settings(self) -> None:
        """Save settings from all tabs - preserving our choices against the tide of time."""
        try:
            # Save settings from each tab - collecting our fragmented preferences
            self.logger.debug("Attempting to save settings from all tabs")

            # Call save method for each tab
            self.general_tab.save_settings()
            self.system_tab.save_settings()
            self.tools_tab.save_settings()

            # Save config to file - committing our choices to persistent memory
            if self.config_manager.save():
                self.logger.info("Settings saved successfully - our preferences immortalized")
                self.has_unsaved_changes = False
                self.settings_saved.emit()
                self.accept()
            else:
                # Failure to save - our choices lost to the void
                self.logger.error("Failed to save settings to disk - entropy prevails")
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to save settings. The universe remains indifferent to your preferences."
                )

        except AttributeError as e:
            # Missing tab - searching for what isn't there
            self.logger.error(f"Missing required tab for saving settings: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"A settings component is missing. Like a ship without a rudder, we cannot proceed: {str(e)}"
            )

        except Exception as e:
            # General failure - the ultimate constant
            self.logger.exception(f"Error saving settings: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving settings. As Sisyphus learned, some tasks are never complete: {str(e)}"
            )

    def _reset_settings(self) -> None:
        """Reset all settings to defaults - digital rebirth."""
        try:
            # Confirm reset - because destruction should never be casual
            reply = QMessageBox.question(
                self,
                'Reset Settings',
                'Are you sure you want to reset all settings to default values?\n\n'
                'Like factory resets and amnesia, this action cannot be undone.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return  # Retreat from the brink

            # Reset to defaults - embracing the original state
            self.logger.info("Resetting all settings to defaults - returning to the primordial configuration")

            try:
                # Reset config - wiping the slate clean
                self.config_manager.reset_to_defaults()

                # Refresh all tabs - synchronizing UI with the reset state
                self.general_tab.load_settings()
                self.system_tab.load_settings()
                self.tools_tab.load_settings()

                self.has_unsaved_changes = True  # Now we have changes to save

                QMessageBox.information(
                    self,
                    "Settings Reset",
                    "All settings have been reset to default values. Like a phoenix, your configuration rises anew."
                )

            except Exception as e:
                # Reset failed - the past refuses to be erased
                self.logger.exception(f"Error resetting settings: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to reset settings. Some pasts cannot be undone: {str(e)}"
                )

        except Exception as e:
            # Dialog failure - even asking questions can fail
            self.logger.exception(f"Error in reset dialog: {str(e)}")

    def _confirm_cancel(self) -> None:
        """Confirm cancellation when there are unsaved changes - acknowledging abandonment."""
        if not self.has_unsaved_changes:
            self.reject()  # Nothing to lose
            return

        # Unsaved changes - the work that might never see the light of day
        reply = QMessageBox.question(
            self,
            'Unsaved Changes',
            'You have unsaved changes. Do you want to discard them?\n\n'
            'Like unspoken words, discarded settings cannot be recovered.',
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Discard:
            self.logger.info("Discarding unsaved changes - another timeline abandoned")
            self.reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close events - interception at the edge of existence.

        Args:
            event: The close event, a knock at the door of termination
        """
        if self.has_unsaved_changes:
            # Unsaved changes - holding on to what might be lost
            reply = QMessageBox.question(
                self,
                'Unsaved Changes',
                'You have unsaved changes. Do you want to save before closing?\n\n'
                'This moment of decision is all that stands between persistence and oblivion.',
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self._save_settings()
                event.accept() if not self.has_unsaved_changes else event.ignore()
            elif reply == QMessageBox.StandardButton.Discard:
                self.logger.info("Closing with unsaved changes - abandoning potential futures")
                event.accept()
            else:
                event.ignore()  # Continue existence
        else:
            event.accept()  # No changes to lose

    def showEvent(self, event: QShowEvent) -> None:
        """Handle show events - the emergence into visibility.

        Args:
            event: The show event, our entrance to the stage of perception
        """
        super().showEvent(event)
        # Center dialog in parent if available - finding our place in the world
        if self.parent():
            self.move(
                self.parent().x() + (self.parent().width() - self.width()) // 2,
                self.parent().y() + (self.parent().height() - self.height()) // 2
            )
        self.logger.debug("Settings window displayed - awaiting user input")

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize events - the changing boundaries of our existence.

        Args:
            event: The resize event, a fluctuation in our dimensional constraints
        """
        super().resizeEvent(event)
        # Log size changes - tracking our dimensional journey
        self.logger.debug(f"Settings window resized to {self.size().width()}x{self.size().height()}")