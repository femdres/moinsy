#!/usr/bin/env python3
"""
Theme manager for handling application-wide theming with consistent styling.

This module provides the central coordination point for theme loading, saving,
and application across the entire UI. It serves as the bridge between user
preferences and the visual presentation of the application.

Like a cosmic choreographer directing the dance of colors and fonts across
our digital landscape, this manager ensures all UI elements move in aesthetic harmony.
"""

import os
import json
import logging
import shutil
from typing import Dict, Any, Optional, List, Union, Tuple, cast

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PyQt6.QtCore import QObject, pyqtSignal

from gui.styles.theme import Theme
from gui.styles.theme_events import get_theme_event_bus
from gui.styles.theme_loader import ThemeLoader


class ThemeManager(QObject):
    """
    Central manager for application theming functionality.

    This class coordinates theme loading, saving, and application across
    the entire UI, ensuring consistent visual appearance throughout the
    application lifecycle.

    Like an aesthetic oracle mediating between the realm of persistent configuration
    and the ephemeral manifestation of pixels, this class bridges user preferences
    and visual presentation.
    """

    # Signals
    theme_changed = pyqtSignal(str)  # theme_id

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the theme manager.

        Args:
            config_dir: Optional custom config directory. If not provided, uses default location.

        Like establishing the foundations of an aesthetic temple, this method
        prepares the essential structures needed for theme management.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Determine themes directory
        if config_dir:
            self.themes_dir = os.path.join(config_dir, "themes")
        else:
            self.themes_dir = os.path.expanduser("~/.config/moinsy/themes")

        # Ensure themes directory exists
        os.makedirs(self.themes_dir, exist_ok=True)

        # Initialize theme loader
        self.theme_loader = ThemeLoader(self.themes_dir)

        # Get event bus for theme change notifications
        self.event_bus = get_theme_event_bus()

        # Track current theme
        self._current_theme = "dark"  # Default theme

        self.logger.debug(f"ThemeManager initialized with themes directory: {self.themes_dir}")

    def get_available_themes(self) -> List[Dict[str, Any]]:
        """
        Get a list of available themes with metadata.

        Returns:
            List of theme information dictionaries

        Like taking inventory of our aesthetic wardrobe, this method
        catalogs all available visual identities.
        """
        return self.theme_loader.get_available_themes()

    def load_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a theme by its identifier.

        Args:
            theme_id: Theme identifier

        Returns:
            Theme data dictionary or None if not found

        Like retrieving blueprints for a specific visual identity, this method
        loads the definition of a particular theme from storage.
        """
        return self.theme_loader.load_theme(theme_id)

    def apply_theme(self, theme_id: str, app: Optional[QApplication] = None) -> bool:
        """
        Apply a theme to the application.

        Args:
            theme_id: Theme identifier
            app: Optional QApplication instance

        Returns:
            True if theme was applied successfully, False otherwise

        Like casting a spell that transforms the visual essence of our digital realm,
        this method applies a specific aesthetic to the entire application.
        """
        try:
            # Load theme data
            theme_data = self.load_theme(theme_id)
            if not theme_data:
                self.logger.error(f"Failed to load theme '{theme_id}' - aesthetic transformation aborted")
                return False

            # Store current theme ID
            self._current_theme = theme_id

            # Update Theme class with the theme data
            if "colors" in theme_data:
                Theme.COLORS[Theme.THEME_DARK] = theme_data["colors"]
                Theme.set_theme(Theme.THEME_DARK)

            # Update fonts if present
            if "fonts" in theme_data:
                Theme.FONTS = theme_data["fonts"]

            # Apply to application if provided
            if app:
                Theme.apply_base_styles(app)
                self.logger.debug(f"Applied theme '{theme_id}' to application")

            # Notify event listeners
            self.theme_changed.emit(theme_id)
            self.event_bus.notify_theme_change(theme_id)

            self.logger.info(f"Theme '{theme_id}' applied successfully - digital realm transformed")
            return True

        except Exception as e:
            self.logger.error(f"Error applying theme '{theme_id}': {str(e)}", exc_info=True)
            return False

    def get_current_theme(self) -> str:
        """
        Get the ID of the currently active theme.

        Returns:
            Current theme identifier

        Like asking which outfit our digital entity is currently wearing,
        this method reveals the active visual identity.
        """
        return self._current_theme

    def save_theme(self, theme_id: str, theme_data: Dict[str, Any]) -> bool:
        """
        Save a theme to permanent storage.

        Args:
            theme_id: Theme identifier
            theme_data: Theme data dictionary

        Returns:
            True if saved successfully, False otherwise

        Like preserving a particular aesthetic formula for posterity,
        this method commits a visual identity to persistent storage.
        """
        try:
            # Validate theme data
            if not isinstance(theme_data, dict):
                self.logger.error("Invalid theme data type - expected dictionary")
                return False

            if "colors" not in theme_data:
                self.logger.error("Invalid theme data - missing colors dictionary")
                return False

            if "name" not in theme_data:
                self.logger.error("Invalid theme data - missing name")
                return False

            # Ensure themes directory exists
            os.makedirs(self.themes_dir, exist_ok=True)

            # Save theme file
            theme_path = os.path.join(self.themes_dir, f"{theme_id}.theme.json")
            with open(theme_path, 'w') as f:
                json.dump(theme_data, f, indent=4)

            self.logger.info(f"Theme '{theme_id}' saved successfully - aesthetic formula preserved")
            return True

        except Exception as e:
            self.logger.error(f"Error saving theme '{theme_id}': {str(e)}", exc_info=True)
            return False

    def delete_theme(self, theme_id: str) -> bool:
        """
        Delete a theme from storage.

        Args:
            theme_id: Theme identifier

        Returns:
            True if deleted successfully, False otherwise

        Like erasing a particular aesthetic formula from existence,
        this method removes a visual identity from our collection.
        """
        return self.theme_loader.delete_theme(theme_id)

    def import_theme(self, source_path: str, parent: Optional[QWidget] = None) -> Optional[str]:
        """
        Import a theme from a file or URL.

        Args:
            source_path: Path or URL to theme file
            parent: Optional parent widget for error dialogs

        Returns:
            Theme ID if imported successfully, None otherwise

        Like acquiring a new aesthetic formula from an external source,
        this method adds a foreign visual identity to our collection.
        """
        theme_id = self.theme_loader.install_theme(source_path, parent)

        if theme_id:
            # Notify about new theme availability
            self.event_bus.notify_theme_change("theme_imported")

        return theme_id

    def export_theme(self, theme_id: str, destination: str) -> bool:
        """
        Export a theme to a file.

        Args:
            theme_id: Theme identifier
            destination: Destination file path

        Returns:
            True if exported successfully, False otherwise

        Like sharing an aesthetic formula with the outside world,
        this method packages a visual identity for external use.
        """
        return self.theme_loader.export_theme(theme_id, destination)

    def create_custom_theme(self, name: str, base_theme_id: str,
                            color_overrides: Dict[str, str]) -> Optional[str]:
        """
        Create a custom theme based on an existing theme.

        Args:
            name: Name for the new theme
            base_theme_id: Base theme identifier
            color_overrides: Dictionary of color keys and values to override

        Returns:
            New theme ID if created successfully, None otherwise

        Like creating a variation on an existing aesthetic formula,
        this method produces a new visual identity based on a template.
        """
        return self.theme_loader.create_custom_theme(name, base_theme_id, color_overrides)

    def show_theme_manager_dialog(self, parent: QWidget) -> None:
        """
        Show the theme manager dialog.

        Args:
            parent: Parent widget for the dialog

        Like opening the wardrobe of our digital entity, this method
        presents an interface for selecting and customizing visual identities.
        """
        try:
            from gui.styles.theme_manager import ThemeManagerDialog

            dialog = ThemeManagerDialog(self.themes_dir, self._current_theme, parent)

            # Connect to dialog's theme_changed signal
            dialog.theme_changed.connect(self._on_dialog_theme_changed)

            # Show dialog
            dialog.exec()

        except Exception as e:
            self.logger.error(f"Error showing theme manager dialog: {str(e)}", exc_info=True)
            QMessageBox.critical(
                parent,
                "Error",
                f"Could not open theme manager: {str(e)}\n\n"
                "Like Icarus flying too close to the sun, our aesthetic ambitions "
                "were thwarted by technical limitations."
            )

    def _on_dialog_theme_changed(self, theme_id: str) -> None:
        """
        Handle theme change from the theme manager dialog.

        Args:
            theme_id: Theme identifier selected in dialog

        Like responding to a wardrobe change request, this method
        processes the selection of a new visual identity.
        """
        # Notify about theme change
        self.theme_changed.emit(theme_id)

        # Apply theme
        app = QApplication.instance()
        if app:
            self.apply_theme(theme_id, app)