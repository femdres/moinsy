#!/usr/bin/env python3
"""
Theme style constants for consistent UI appearance in Moinsy.

This module provides centralized style constants for UI components, ensuring
consistent appearance across different parts of the application regardless
of which theme is currently active.

Like a well-organized wardrobe that ensures you never mismatch your socks,
this module maintains style consistency across the application's many components.
Though in the grand scheme of the universe, whether your UI is pixel-perfect
remains a question of dubious cosmic significance.
"""
import logging
from typing import Dict, Any, Optional, Union, Literal, cast
from PyQt6.QtWidgets import QWidget, QFrame, QPushButton, QLineEdit, QTextEdit
from gui.styles.theme import Theme

# Style Constants
BORDER_STYLES = {
    "standard": {
        "radius": "8px",
        "width": "1px"
    },
    "container": {
        "radius": "12px",
        "width": "1px"
    },
    "button": {
        "radius": "8px",
        "width": "0px"  # Buttons typically don't have borders
    },
    "input": {
        "radius": "4px",
        "width": "1px"
    }
}

SPACING = {
    "xs": "5px",
    "sm": "10px",
    "md": "15px",
    "lg": "20px",
    "xl": "25px"
}

FONT_SIZES = {
    "xs": "10px",
    "sm": "12px",
    "md": "14px",
    "lg": "16px",
    "xl": "20px",
    "xxl": "24px"
}


def get_button_style(button_type: str = "standard", theme_id: Optional[str] = None) -> str:
    """
    Get consistent button styling based on button type and theme.

    Args:
        button_type: Type of button ('standard', 'primary', 'danger', 'warning', etc.)
        theme_id: Optional theme override, or None to use current theme

    Returns:
        CSS styling string for the specified button type

    Like a fashion consultant providing outfit recommendations based on occasion,
    this function delivers the appropriate styling for each type of button.
    Though in the end, all buttons face the same existential reality: to be
    pressed or not to be pressed, that is their only question.
    """
    # Use current theme if none specified
    if theme_id is None:
        try:
            theme_id = Theme.get_current_theme()
        except (AttributeError, Exception):
            theme_id = "dark"  # Default fallback

    # Get theme colors
    if button_type == "primary":
        color = Theme.get_color('PRIMARY')
        hover_color = Theme.adjust_color(color, -20)
        text_color = "white"
    elif button_type == "danger":
        color = Theme.get_color('ERROR')
        hover_color = Theme.adjust_color(color, -20)
        text_color = "white"
    elif button_type == "warning":
        color = Theme.get_color('WARNING')
        hover_color = Theme.adjust_color(color, -20)
        text_color = "black" if theme_id == "light" else "white"
    elif button_type == "secondary":
        color = Theme.get_color('SECONDARY')
        hover_color = Theme.adjust_color(color, -20)
        text_color = "white"
    else:  # standard
        color = Theme.get_color('CONTROL_BG')
        hover_color = Theme.get_color('CONTROL_HOVER')
        text_color = Theme.get_color('TEXT_PRIMARY')

    # Create button style
    return f"""
        QPushButton {{
            background-color: {color};
            color: {text_color};
            border: none;
            border-radius: {BORDER_STYLES["button"]["radius"]};
            padding: {SPACING["sm"]};
            font-size: {FONT_SIZES["md"]};
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {Theme.adjust_color(hover_color, -20)};
        }}
    """


def get_container_style(container_type: str = "standard", theme_id: Optional[str] = None) -> str:
    """
    Get consistent container styling based on container type and theme.

    Args:
        container_type: Type of container ('standard', 'card', 'panel', etc.)
        theme_id: Optional theme override, or None to use current theme

    Returns:
        CSS styling string for the specified container type

    Like an architect designing rooms for different purposes, this function
    provides the appropriate styling for each type of container. The containers
    themselves, of course, remain blissfully unaware of their aesthetic imprisonment.
    """
    # Use current theme if none specified
    if theme_id is None:
        try:
            theme_id = Theme.get_current_theme()
        except (AttributeError, Exception):
            theme_id = "dark"  # Default fallback

    # Get theme colors
    if container_type == "card":
        bg_color = Theme.get_color('BG_MEDIUM')
        border_color = Theme.get_color('BG_LIGHT')
        border_radius = BORDER_STYLES["container"]["radius"]
    elif container_type == "panel":
        bg_color = Theme.get_color('BG_DARK')
        border_color = Theme.get_color('BG_LIGHT')
        border_radius = BORDER_STYLES["container"]["radius"]
    else:  # standard
        bg_color = Theme.get_color('BG_MEDIUM')
        border_color = Theme.adjust_color(bg_color, 20)
        border_radius = BORDER_STYLES["standard"]["radius"]

    # Create container style
    return f"""
        QFrame {{
            background-color: {bg_color};
            border: {BORDER_STYLES["container"]["width"]} solid {border_color};
            border-radius: {border_radius};
            padding: {SPACING["sm"]};
        }}
    """


def get_input_style(input_type: str = "standard", theme_id: Optional[str] = None) -> str:
    """
    Get consistent input styling based on input type and theme.

    Args:
        input_type: Type of input ('text', 'search', 'password', etc.)
        theme_id: Optional theme override, or None to use current theme

    Returns:
        CSS styling string for the specified input type

    Like a careful craftsman creating forms for different materials,
    this function provides the appropriate styling for each type of input.
    The inputs themselves serve as digital confessionals, passively awaiting
    our deepest secrets and mundane queries alike.
    """
    # Use current theme if none specified
    if theme_id is None:
        try:
            theme_id = Theme.get_current_theme()
        except (AttributeError, Exception):
            theme_id = "dark"  # Default fallback

    # Get theme colors
    bg_color = Theme.get_color('BG_MEDIUM')
    text_color = Theme.get_color('TEXT_PRIMARY')
    border_color = Theme.get_color('BG_LIGHT')
    focus_color = Theme.get_color('PRIMARY')

    # Adjust for input type
    if input_type == "search":
        border_radius = "15px"  # More rounded for search fields
        padding = f"{SPACING['xs']} {SPACING['md']}"
    else:  # standard, password, etc.
        border_radius = BORDER_STYLES["input"]["radius"]
        padding = SPACING["sm"]

    # Create input style
    return f"""
        QLineEdit, QTextEdit {{
            background-color: {bg_color};
            color: {text_color};
            border: {BORDER_STYLES["input"]["width"]} solid {border_color};
            border-radius: {border_radius};
            padding: {padding};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {focus_color};
        }}
    """


def apply_consistent_style(widget: QWidget, style_type: str = "standard") -> None:
    """
    Apply consistent styling to a widget based on its type.

    Args:
        widget: The widget to style
        style_type: The type of style to apply ('standard', 'primary', etc.)

    Like a digital stylist dressing widgets for their on-screen appearance,
    this function applies the appropriate style to each UI element.
    The widgets, forever trapped in their virtual existence, can only
    accept the styling imposed upon them - a fitting metaphor for our own
    constrained reality.
    """
    try:
        # Determine appropriate style based on widget type
        if isinstance(widget, QPushButton.__class__):
            widget.setStyleSheet(get_button_style(style_type))
        elif isinstance(widget, QFrame.__class__):
            widget.setStyleSheet(get_container_style(style_type))
        elif isinstance(widget, (QLineEdit.__class__, QTextEdit.__class__)):
            widget.setStyleSheet(get_input_style(style_type))
        else:
            # Apply generic styling
            widget.setStyleSheet(f"""
                color: {Theme.get_color('TEXT_PRIMARY')};
                font-size: {FONT_SIZES["md"]};
            """)
    except Exception as e:
        # Like a stylist giving up on a particularly difficult client,
        # we gracefully handle our inability to style this widget
        logging.getLogger(__name__).error(f"Failed to apply style to widget: {str(e)}")