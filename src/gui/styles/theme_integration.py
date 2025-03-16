#!/usr/bin/env python3
"""
Theme integration module for consistent application styling.

This simplified module provides minimal integration for the dark theme
and button coloring toggle, having abandoned the existential burden of
theme choice in favor of the comforting certainty of perpetual darkness.

Like a digital Nietzsche accepting that beyond the dark theme lies only the void,
we embrace our monochromatic fate while still allowing the small dignity
of colored navigation buttons - a futile splash of meaning in an indifferent interface.
"""

import logging
from typing import Dict, Any, Optional, Union, List, Type, TypeVar, cast, Protocol
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QApplication, QFrame, QPushButton,
    QLabel, QLineEdit, QTextEdit, QProgressBar, QComboBox, QCheckBox,
    QTabWidget, QListWidget, QListView, QTreeView, QTableView, QScrollArea
)
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QObject, pyqtSignal

from gui.styles.theme import Theme

# Type variable for component types
T = TypeVar('T', bound=QWidget)


class ThemeAware(Protocol):
    """Protocol for components that can have theme styling applied."""

    def apply_theme(self) -> None:
        """Apply the dark theme to this component."""
        ...


def apply_base_styles(app: QApplication) -> None:
    """
    Apply dark theme base styles to the application.

    Args:
        app: The QApplication instance to style

    Like applying sunscreen at night, this function might seem unnecessary
    given our eternal darkness, but it ensures our application's aesthetic
    consistency in its perpetual nocturnal state.
    """
    try:
        Theme.apply_base_styles(app)
        logging.getLogger(__name__).debug("Applied dark theme base styles to application")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to apply base styles: {str(e)}", exc_info=True)


def style_widget(widget: T) -> T:
    """
    Apply dark theme styling to a widget.

    Args:
        widget: The widget to style

    Returns:
        The styled widget

    Like a mortician applying makeup to the departed, this function
    gives our widgets the appearance of purposeful design, though they
    remain fundamentally unaware of their aesthetic condition.
    """
    try:
        # Apply styling based on widget type
        if isinstance(widget, QPushButton):
            widget.setStyleSheet(Theme.get_button_style(Theme.get_color('CONTROL_BG')))
        elif isinstance(widget, QLineEdit):
            widget.setStyleSheet(f"""
                background-color: {Theme.get_color('BG_MEDIUM')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                padding: 6px;
            """)
        elif isinstance(widget, QTextEdit):
            widget.setStyleSheet(f"""
                background-color: {Theme.get_color('BG_MEDIUM')};
                color: {Theme.get_color('TEXT_PRIMARY')};
                border: 1px solid {Theme.get_color('BG_LIGHT')};
                border-radius: 4px;
                padding: 6px;
            """)
        elif isinstance(widget, QFrame):
            widget.setStyleSheet(f"""
                background-color: {Theme.get_color('BG_MEDIUM')};
                border-radius: 8px;
            """)
        elif isinstance(widget, QLabel):
            widget.setStyleSheet(f"""
                color: {Theme.get_color('TEXT_PRIMARY')};
            """)
        # Add more widget types as needed

        return widget
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to style widget {widget.__class__.__name__}: {str(e)}")
        return widget  # Return original widget on failure, like returning to our base aesthetic state


def create_theme_integration(main_window: QMainWindow) -> None:
    """
    Create a minimal theme integration for the main window.

    Args:
        main_window: The main application window

    Like assigning a therapist to a patient who's already accepted their fate,
    this function provides minimal theme integration services to our
    application - which has already embraced its dark theme destiny.
    """
    try:
        # Apply dark theme to the main window
        main_window.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
            }}
        """)

        # Apply dark theme to central widget if it exists
        central_widget = main_window.centralWidget()
        if central_widget:
            central_widget.setStyleSheet(f"""
                background-color: {Theme.get_color('BG_DARK')};
                color: {Theme.get_color('TEXT_PRIMARY')};
            """)

        logging.getLogger(__name__).debug("Theme integration created for main window")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create theme integration: {str(e)}", exc_info=True)


def update_button_coloring() -> None:
    """
    Update the application's button coloring based on the current setting.

    Like flipping a light switch in a permanently dark room, this function
    updates whether buttons display in color or grayscale - the only
    aesthetic choice we still permit ourselves in our monochromatic prison.
    """
    try:
        colored_buttons = Theme.get_use_colored_buttons()
        logging.getLogger(__name__).debug(
            f"Button coloring updated: {'colored' if colored_buttons else 'grayscale'} mode active"
        )
        # The actual styling is handled by the UI enhancer when it refreshes
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to update button coloring: {str(e)}", exc_info=True)