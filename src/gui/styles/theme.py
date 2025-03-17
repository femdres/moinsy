#!/usr/bin/env python3
"""
Theme definition module for Moinsy - Dark Theme Only Edition.

This streamlined module provides color definitions and styling utilities
exclusively for the dark theme, removing the existential burden of choice
that plagued earlier versions.
"""

import logging
from typing import Dict, Any, Optional, List, Union, cast
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


class Theme:
    """
    Dark theme management for consistent application styling.

    Like a digital nightclub where the lights never come on, this class
    provides exclusively dark-themed color palettes and styling utilities
    while still allowing for the philosophical toggle between colored and
    grayscale navigation buttons.
    """

    # Dark theme - our singular reality
    THEME_DARK = "dark"

    # Colors for the dark theme - our only reality now
    COLORS = {
        # Primary colors
        'PRIMARY': '#4CAF50',  # Green
        'SECONDARY': '#2196F3',  # Blue
        'TERTIARY': '#9C27B0',  # Purple

        # Backgrounds
        'BG_DARK': '#121212',  # Main background
        'BG_MEDIUM': '#1E1E1E',  # Card background
        'BG_LIGHT': '#2A2A2A',  # Active/Hover states

        # Text colors
        'TEXT_PRIMARY': '#FFFFFF',
        'TEXT_SECONDARY': '#888888',

        # Status colors
        'SUCCESS': '#4CAF50',
        'ERROR': '#dc2626',
        'WARNING': '#FFC107',

        # Control colors
        'CONTROL_BG': '#4b5563',
        'CONTROL_HOVER': '#374151',

        # Terminal colors - the digital stage where our existential output performs
        'TERMINAL_BG': '#323234',  # Gray for the terminal output and controls
        'TERMINAL_AREA_BG': '#323234',  # Black for the terminal area background
    }

    # Font Configuration
    FONTS = {
        'LOGO': ('JetBrains Mono', 28, 'Bold'),
        'TITLE': ('Segoe UI', 16, 'Bold'),
        'SUBTITLE': ('Segoe UI', 14, 'Normal'),
        'BODY': ('Segoe UI', 13, 'Normal'),
        'MONO': ('JetBrains Mono', 13, 'Normal')
    }

    # Private class variables
    _logger = logging.getLogger(__name__)
    _use_colored_buttons: bool = True  # Default to colored buttons - a fleeting moment of optimism

    @classmethod
    def apply_base_styles(cls, app: QApplication) -> None:
        """
        Apply dark theme styling to the application.

        Args:
            app: The QApplication instance to style

        Like applying digital makeup to a nocturnal creature, this method
        gives our application its base aesthetic appearance - exclusively dark.
        """
        try:
            # Set fusion style for consistent cross-platform look
            app.setStyle("Fusion")

            # Configure palette based on dark theme
            palette = cls.create_palette()
            app.setPalette(palette)

            # Apply global stylesheet
            app.setStyleSheet(cls.get_global_stylesheet())

            cls._logger.info("Applied dark theme to application")
        except Exception as e:
            cls._logger.error(f"Failed to apply base styles: {str(e)}")

    @classmethod
    def create_palette(cls) -> QPalette:
        """
        Create the color palette for the dark theme.

        Returns:
            QPalette configured for dark theme

        Like mixing a precise, monochromatic color palette, this method
        prepares the dark colors our interface will use - darkness being
        the only certainty in our digital universe.
        """
        try:
            palette = QPalette()
            colors = cls.COLORS

            # Set color roles
            palette.setColor(QPalette.ColorRole.Window, QColor(colors['BG_DARK']))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['TEXT_PRIMARY']))
            palette.setColor(QPalette.ColorRole.Base, QColor(colors['BG_MEDIUM']))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['BG_LIGHT']))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['TEXT_PRIMARY']))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['TEXT_PRIMARY']))
            palette.setColor(QPalette.ColorRole.Text, QColor(colors['TEXT_PRIMARY']))
            palette.setColor(QPalette.ColorRole.Button, QColor(colors['BG_MEDIUM']))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['TEXT_PRIMARY']))
            palette.setColor(QPalette.ColorRole.Link, QColor(colors['SECONDARY']))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['SECONDARY']))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['TEXT_PRIMARY']))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['TEXT_PRIMARY']))

            return palette
        except Exception as e:
            cls._logger.error(f"Failed to create palette: {str(e)}")
            # Return default palette as fallback
            return QPalette()

    @classmethod
    def get_global_stylesheet(cls) -> str:
        """
        Get global application stylesheet for the dark theme.

        Returns:
            Stylesheet as a string

        Like drafting a comprehensive fashion guide for shadows, this method
        creates style rules that apply throughout our perpetually dark application.
        """
        colors = cls.COLORS

        return f"""
            /* Base Widget Styling */
            QWidget {{
                font-family: 'Segoe UI', Arial;
                font-size: 13px;
                color: {colors['TEXT_PRIMARY']};
            }}

            /* Button Styling */
            QPushButton {{
                background-color: {colors['CONTROL_BG']};
                color: {colors['TEXT_PRIMARY']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {colors['CONTROL_HOVER']};
            }}

            QPushButton:pressed {{
                background-color: {cls.adjust_color(colors['CONTROL_HOVER'], -20)};
            }}

            /* Progress Bar Styling */
            QProgressBar {{
                background-color: {colors['BG_LIGHT']};
                border: none;
                border-radius: 3px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background-color: {colors['PRIMARY']};
                border-radius: 3px;
            }}

            /* Text Input Styling */
            QLineEdit {{
                background-color: {colors['BG_MEDIUM']};
                color: {colors['TEXT_PRIMARY']};
                border: 1px solid {colors['BG_LIGHT']};
                border-radius: 4px;
                padding: 6px 10px;
            }}

            QLineEdit:focus {{
                border-color: {colors['PRIMARY']};
            }}

            QTextEdit {{
                background-color: {colors['BG_MEDIUM']};
                color: {colors['TEXT_PRIMARY']};
                border: 1px solid {colors['BG_LIGHT']};
                border-radius: 4px;
                padding: 6px;
            }}

            /* Scrollbar Styling */
            QScrollBar:vertical {{
                border: none;
                background: {colors['BG_MEDIUM']};
                width: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {colors['BG_LIGHT']};
                min-height: 20px;
                border-radius: 4px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                border: none;
                background: {colors['BG_MEDIUM']};
                height: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:horizontal {{
                background: {colors['BG_LIGHT']};
                min-width: 20px;
                border-radius: 4px;
            }}

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* Frame Styling */
            QFrame {{
                border-radius: 8px;
            }}

            /* Label Styling */
            QLabel {{
                color: {colors['TEXT_PRIMARY']};
            }}

            /* ComboBox Styling */
            QComboBox {{
                background-color: {colors['BG_MEDIUM']};
                color: {colors['TEXT_PRIMARY']};
                border: 1px solid {colors['BG_LIGHT']};
                border-radius: 4px;
                padding: 6px 10px;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {colors['BG_MEDIUM']};
                color: {colors['TEXT_PRIMARY']};
                selection-background-color: {colors['PRIMARY']};
            }}

            /* TabWidget Styling */
            QTabWidget::pane {{
                border: 1px solid {colors['BG_LIGHT']};
                background-color: {colors['BG_MEDIUM']};
                border-radius: 4px;
            }}

            QTabBar::tab {{
                background-color: {colors['BG_MEDIUM']};
                color: {colors['TEXT_SECONDARY']};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background-color: {colors['PRIMARY']};
                color: {colors['TEXT_PRIMARY']};
            }}
        """

    @classmethod
    def get_card_style(cls) -> str:
        """Get styling for card elements."""
        colors = cls.COLORS
        return f"""
            background-color: {colors['BG_MEDIUM']};
            border-radius: 8px;
            padding: 12px;
            color: {colors['TEXT_PRIMARY']};
        """

    @classmethod
    def get_button_style(cls, color: str, hover_color: Optional[str] = None) -> str:
        """
        Get styling for buttons with specified colors - or grayscale if colorless mode is active.

        Args:
            color: Base button color (ignored in grayscale mode)
            hover_color: Optional hover state color (ignored in grayscale mode)

        Returns:
            Button styling as a string

        Like a digital artist deciding between vibrance and monotone, this method
        provides either colorful or grayscale button styles based on the current setting.
        """
        colors = cls.COLORS

        # Check if colored buttons are enabled
        if not cls._use_colored_buttons:
            # Use standard button styling instead of colored - embracing the grayscale void
            return f"""
                QPushButton {{
                    background-color: {colors['CONTROL_BG']};
                    color: {colors['TEXT_PRIMARY']};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['CONTROL_HOVER']};
                }}
                QPushButton:pressed {{
                    background-color: {cls.adjust_color(colors['CONTROL_HOVER'], -20)};
                }}
            """

        # Original colored button styling logic
        if not hover_color:
            hover_color = cls.adjust_color(color, -20)

        # Calculate pressed color
        pressed_color = cls.adjust_color(hover_color, -20)

        return f"""
            QPushButton {{
                background-color: {color};
                color: {colors['TEXT_PRIMARY']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """

    @classmethod
    def get_color(cls, color_key: str) -> str:
        """
        Get a specific color from the dark theme.

        Args:
            color_key: Color key name

        Returns:
            Color value as a hex string

        Like retrieving a specific pigment from our digital palette,
        this method gives access to individual colors in our darkened theme.
        """
        return cls.COLORS.get(color_key, cls.COLORS['PRIMARY'])

    @classmethod
    def get_font(cls, font_key: str) -> QFont:
        """
        Get a QFont object for the specified font key.

        Args:
            font_key: Font key name from the FONTS dictionary

        Returns:
            QFont object configured for the requested font

        Raises:
            ValueError: If the font key is not valid
        """
        try:
            if font_key not in cls.FONTS:
                cls._logger.warning(f"Invalid font key: {font_key}, using BODY font")
                font_key = 'BODY'

            family, size, style = cls.FONTS[font_key]
            font = QFont(family, size)

            # Apply font style
            if style.lower() == 'bold':
                font.setBold(True)
            elif style.lower() == 'italic':
                font.setItalic(True)
            elif style.lower() == 'light':
                font.setWeight(QFont.Weight.Light)

            cls._logger.debug(f"Created font for key: {font_key}")
            return font

        except Exception as e:
            cls._logger.error(f"Error creating font: {str(e)}")
            # Return a default font as fallback
            return QFont('Segoe UI', 13)

    @classmethod
    def adjust_color(cls, color: str, amount: int) -> str:
        """
        Adjust color brightness by amount.

        Args:
            color: Hex color string
            amount: Amount to adjust brightness (positive or negative)

        Returns:
            Adjusted hex color string

        Like a digital alchemist transmuting colors in the darkness, this method
        adjusts the brightness of a color by a specified amount.
        """
        try:
            # Remove # if present
            hex_color = color.lstrip('#')

            # Convert hex to RGB
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

            # Adjust with bounds checking
            adjusted = [max(0, min(255, x + amount)) for x in rgb]

            # Convert back to hex
            return f'#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}'
        except Exception as e:
            cls._logger.error(f"Error adjusting color: {str(e)}")
            return color  # Return original on error

    @classmethod
    def set_use_colored_buttons(cls, value: bool) -> None:
        """
        Set whether to use colored buttons or grayscale buttons.

        Args:
            value: True for colored buttons, False for grayscale

        Like choosing between vivid dreams and monotone reality, this setting
        determines whether our buttons will shine with unique colors or conform
        to the grayscale uniformity that mirrors our existential condition.
        """
        if cls._use_colored_buttons != value:
            cls._use_colored_buttons = value
            cls._logger.debug(
                f"Set use_colored_buttons to {value} - our buttons {'embrace color' if value else 'adopt grayscale uniformity'}")

    @classmethod
    def get_use_colored_buttons(cls) -> bool:
        """
        Get the current button color setting.

        Returns:
            Whether buttons are currently set to use color
        """
        return cls._use_colored_buttons

    @classmethod
    def get_current_theme(cls) -> str:
        """
        Get the current theme - which is always dark.

        Returns:
            The eternal darkness of our singular theme

        This method exists purely to satisfy any code that might expect
        multiple themes to exist in our simplified reality.
        """
        return cls.THEME_DARK