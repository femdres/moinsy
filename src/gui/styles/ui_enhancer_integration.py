#!/usr/bin/env python3
"""
Integration module for UI enhancements in Moinsy application.

This module provides the integration points to apply UI enhancements to the
Moinsy application, ensuring they're applied at the appropriate lifecycle stages.

Like a bridge connecting the realm of aesthetic ideals with the concrete
implementation of pixels on screen, this module ensures our UI enhancements
are applied at the right moment in the application lifecycle.
"""

import logging
from typing import Optional, Dict, Any, Union, List, cast
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QTimer, QObject, pyqtSlot

# Import the enhancer
from gui.styles.ui_enhancer import UIEnhancer, enhance_main_window


class MoinsyUIManager(QObject):
    """
    UI Management service for the Moinsy application.

    This class coordinates UI enhancement application throughout the
    application lifecycle, including startup, theme changes, and
    settings updates.

    Like an attentive stage manager ensuring every set piece is perfectly
    positioned before the curtain rises, this class coordinates the
    application of our UI enhancements at precisely the right moments.
    """

    def __init__(self, main_window: QMainWindow):
        """
        Initialize UI manager with reference to main application window.

        Args:
            main_window: Reference to the main application window
        """
        super().__init__()
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.enhancer: Optional[UIEnhancer] = None

        # Track if enhancements have been applied
        self.enhancements_applied = False

        # Connect to lifecycle events
        if hasattr(main_window, 'settings_changed'):
            main_window.settings_changed.connect(self.on_settings_changed)

        if hasattr(main_window, 'theme_changed'):
            main_window.theme_changed.connect(self.on_theme_changed)

        # Schedule initial enhancement after UI is visible
        QTimer.singleShot(500, self.apply_enhancements)

    def apply_enhancements(self) -> None:
        """
        Apply UI enhancements to the application.

        Like the final polish of a craftsman's work, this method applies
        our aesthetic enhancements to the otherwise utilitarian interface.
        """
        try:
            if not self.enhancements_applied:
                # Create and apply enhancer
                self.enhancer = UIEnhancer(self.main_window)
                self.enhancer.enhance_ui()
                self.enhancements_applied = True
                self.logger.info("UI enhancements applied at startup")
            else:
                # Reapply if needed
                if self.enhancer:
                    # Just refresh certain components
                    self.enhancer._apply_delayed_fixes()
                    self.logger.debug("UI enhancements refreshed")
        except Exception as e:
            self.logger.error(f"Failed to apply UI enhancements: {str(e)}", exc_info=True)

    @pyqtSlot()
    def on_settings_changed(self) -> None:
        """
        Handle settings changes that may affect UI.

        Like a vigilant observer responding to shifts in the digital landscape,
        this method ensures UI adjustments are reapplied when settings change.
        """
        try:
            # Schedule enhancement refresh after settings update
            QTimer.singleShot(200, self.apply_enhancements)
            self.logger.debug("UI refresh scheduled after settings change")
        except Exception as e:
            self.logger.error(f"Error handling settings change: {str(e)}", exc_info=True)

    @pyqtSlot(str)
    def on_theme_changed(self, theme_id: str) -> None:
        """
        Handle theme changes to ensure UI consistency.

        Args:
            theme_id: Identifier of the new theme

        Like a chameleon adjusting to a new environment, this method ensures
        our UI adaptations are correctly applied when the theme changes.
        """
        try:
            # Schedule enhancement refresh after theme change
            QTimer.singleShot(200, self.apply_enhancements)
            self.logger.debug(f"UI refresh scheduled after theme change to {theme_id}")
        except Exception as e:
            self.logger.error(f"Error handling theme change: {str(e)}", exc_info=True)


def setup_ui_enhancements(main_window: QMainWindow) -> Optional[MoinsyUIManager]:
    """
    Set up UI enhancements for the Moinsy application.

    Args:
        main_window: Reference to the main application window

    Returns:
        UI manager instance or None if setup fails

    Like an initialization ritual for aesthetic improvement, this function
    establishes the UI enhancement system for the application.
    """
    try:
        # Create and return UI manager
        return MoinsyUIManager(main_window)
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to setup UI enhancements: {str(e)}", exc_info=True)
        return None