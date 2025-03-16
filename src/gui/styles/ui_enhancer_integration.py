#!/usr/bin/env python3
"""
Integration module for UI enhancements in Moinsy application.

This module provides the integration points to apply UI enhancements to the
Moinsy application, ensuring they're applied at the appropriate lifecycle stages
without causing crashes or layout issues.
"""

import logging
from typing import Optional, Dict, Any, Union, List, cast
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QTimer, QObject, pyqtSlot

# Import the UI enhancer (we'll fix this later)
from gui.styles.ui_enhancer import UIEnhancer


class MoinsyUIManager(QObject):
    """
    UI Management service for the Moinsy application.

    This class coordinates UI enhancement application throughout the
    application lifecycle, including settings updates and color mode changes.
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
        self.enhancement_attempts = 0
        self.max_attempts = 3

        # Connect to lifecycle events
        self._connect_lifecycle_events()

        # Schedule initial enhancement after UI is visible
        QTimer.singleShot(500, self.apply_enhancements)

    def _connect_lifecycle_events(self) -> None:
        """
        Connect to application lifecycle events for settings changes.

        Like a vigilant sentinel guarding against the ever-shifting tides of user
        preferences, this method establishes connections to system events that
        might require aesthetic reconsideration.
        """
        try:
            # Connect to settings_changed signal if it exists
            if hasattr(self.main_window, 'settings_changed'):
                self.main_window.settings_changed.connect(self.on_settings_changed)
                self.logger.debug("Connected to settings_changed signal")
        except Exception as e:
            self.logger.warning(f"Could not connect to lifecycle events: {str(e)}.")
            self.logger.debug("UI enhancements will still be applied, but may not update with settings changes.")

    def apply_enhancements(self) -> None:
        """
        Apply UI enhancements to the application.

        Like the final polish of a craftsman's work, this method applies
        our aesthetic enhancements to the otherwise utilitarian interface,
        but does so with the humility to step back if the process seems risky.
        """
        try:
            # Safety check - don't attempt too many times
            if self.enhancement_attempts >= self.max_attempts:
                self.logger.warning("Maximum enhancement attempts reached. Giving up to avoid instability.")
                return

            self.enhancement_attempts += 1

            if not self.enhancements_applied:
                # Create enhancer if needed
                if not self.enhancer:
                    self.enhancer = UIEnhancer(self.main_window)

                # Apply UI enhancements with careful error handling
                try:
                    self.enhancer.enhance_ui()
                    self.enhancements_applied = True
                    self.logger.info(f"UI enhancements applied successfully at attempt #{self.enhancement_attempts}")
                except Exception as e:
                    self.logger.error(f"Error during enhancement attempt #{self.enhancement_attempts}: {str(e)}",
                                      exc_info=True)
                    # Schedule another attempt with exponential backoff if we haven't hit max
                    if self.enhancement_attempts < self.max_attempts:
                        delay = 500 * (2 ** (self.enhancement_attempts - 1))  # 500, 1000, 2000ms...
                        self.logger.info(f"Will retry enhancement in {delay}ms")
                        QTimer.singleShot(delay, self.apply_enhancements)
            else:
                # Just refresh certain components if already applied
                if self.enhancer:
                    try:
                        self.enhancer._apply_delayed_fixes()
                        self.logger.debug("UI enhancements refreshed")
                    except Exception as e:
                        self.logger.warning(f"Minor error refreshing UI: {str(e)}")
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
            QTimer.singleShot(300, self.apply_enhancements)
            self.logger.debug("UI refresh scheduled after settings change")
        except Exception as e:
            self.logger.error(f"Error handling settings change: {str(e)}")


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
    logger = logging.getLogger(__name__)

    try:
        # Create and return UI manager
        ui_manager = MoinsyUIManager(main_window)
        logger.info("UI enhancement system initialized successfully")
        return ui_manager
    except Exception as e:
        logger.error(f"Failed to setup UI enhancements: {str(e)}", exc_info=True)
        logger.info("Application will continue without UI enhancements")
        return None