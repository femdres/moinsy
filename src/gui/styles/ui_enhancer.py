#!/usr/bin/env python3
"""
UI enhancement module for Moinsy application.

This module provides post-initialization UI enhancements to correct styling issues,
fix theme inconsistencies, and improve visual coherence across the application.

Like a digital plastic surgeon carefully correcting aesthetic imperfections,
this module meticulously adjusts borders, colors, and spacing to achieve
visual harmony in an otherwise fragmented interface.
"""

import logging
from typing import Optional, Dict, Any, Union, List, cast
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QPushButton, QLabel,
    QProgressBar, QTextEdit, QLineEdit, QApplication
)
from PyQt6.QtCore import Qt, QObject, QRect, QSize, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont

from gui.styles.theme import Theme


class UIEnhancer:
    """
    Enhanced UI styling for Moinsy application.

    This class applies comprehensive styling improvements to fix inconsistencies
    and enhance the visual appearance of the Moinsy application. It focuses on
    border consistency, spacing, color correctness during theme changes, and
    overall visual harmony.

    Like an obsessive-compulsive interior decorator who can't rest until every
    pixel is perfectly aligned, this class meticulously adjusts the UI details
    that keep design-conscious users awake at night.
    """

    def __init__(self, main_window: QMainWindow):
        """
        Initialize UI enhancer with reference to main application window.

        Args:
            main_window: Application's main window to be enhanced

        Like being handed the keys to a house in need of renovation,
        this initializer accepts the main window as the canvas for our
        aesthetic improvements.
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

        # Cache for theme-specific style properties
        self.style_cache: Dict[str, Dict[str, Any]] = {
            "dark": {},
            "light": {},
            "high_contrast": {}
        }

        # Initialize component references
        self.sidebar: Optional[QWidget] = None
        self.terminal_area: Optional[QWidget] = None
        self.reboot_button: Optional[QPushButton] = None
        self.exit_button: Optional[QPushButton] = None
        self.terminal_output: Optional[QTextEdit] = None
        self.clear_button: Optional[QPushButton] = None
        self.progress_frame: Optional[QFrame] = None

        # Connect to theme change events if available
        if hasattr(main_window, 'apply_theme'):
            # Store original apply_theme method
            self._original_apply_theme = main_window.apply_theme

            # Override with our enhanced version
            main_window.apply_theme = self._enhanced_apply_theme

    def enhance_ui(self) -> None:
        """
        Apply comprehensive UI enhancements to the application.

        Like a digital renovation project, this method systematically
        improves each component of the interface, ensuring visual
        consistency and correcting styling issues.
        """
        try:
            self.logger.info("Applying comprehensive UI enhancements to Moinsy - our digital renovation begins")

            # Step 1: Find and cache references to key components
            self._find_components()

            # Step 2: Apply theme-appropriate enhancements
            current_theme = self._get_current_theme()
            self.logger.info(f"Applying theme enhancements to {current_theme.title()} theme")

            # Step 3: Apply specific enhancements
            self._enhance_sidebar()
            self._enhance_terminal_area()
            self._enhance_buttons()
            self._enhance_progress_section()

            # Step 4: Apply delayed fixes for theme-switching issues
            QTimer.singleShot(100, self._apply_delayed_fixes)

            self.logger.info("UI enhancements applied successfully - our digital space now slightly less hideous")
        except Exception as e:
            self.logger.error(f"Failed to enhance UI: {str(e)}", exc_info=True)

    def _find_components(self) -> None:
        """
        Locate and cache references to key UI components.

        Like a detective searching for clues in a digital landscape,
        this method finds the critical UI components that need enhancement.
        """
        try:
            # Find sidebar
            self.sidebar = self.main_window.findChild(QWidget, "MainSidebar")

            # Find terminal area
            self.terminal_area = self.main_window.findChild(QWidget, "TerminalArea")

            # Find button components
            self.reboot_button = self.main_window.findChild(QPushButton, "RebootButton")
            self.exit_button = self.main_window.findChild(QPushButton, "ExitButton")

            # Find terminal components
            if self.terminal_area:
                self.terminal_output = self.terminal_area.findChild(QTextEdit, "TerminalOutput")
                self.clear_button = self.terminal_area.findChild(QPushButton, "ClearButton")

            # Find progress section
            self.progress_frame = self.main_window.findChild(QFrame, "ProgressFrame")

        except Exception as e:
            self.logger.error(f"Error finding UI components: {str(e)}", exc_info=True)

    def _enhance_sidebar(self) -> None:
        """
        Enhance sidebar styling for consistent appearance.

        Like a facade renovation on a building's entrance, this method
        improves the sidebar that serves as the application's primary
        navigation interface.
        """
        if not self.sidebar:
            self.logger.warning("Sidebar not found - cannot apply sidebar enhancements")
            return

        try:
            self.logger.info("Applying comprehensive sidebar enhancements - the digital makeover begins")

            # Apply consistent border to sidebar
            current_theme = self._get_current_theme()
            bg_color = Theme.get_color('BG_MEDIUM')
            border_color = Theme.get_color('BG_LIGHT')

            # Enhanced sidebar styling with consistent border
            self.sidebar.setStyleSheet(f"""
                QWidget#MainSidebar {{
                    background-color: {bg_color};
                    border-right: 1px solid {border_color};
                }}
            """)

            # Fix sidebar button styling for better visibility
            self._enhance_sidebar_buttons()

            # Optimize control buttons (Reboot/Exit) in sidebar
            self._optimize_control_buttons()

        except Exception as e:
            self.logger.error(f"Failed to apply sidebar enhancements: {str(e)} - our aesthetic ambitions crumble",
                              exc_info=True)

    def _enhance_sidebar_buttons(self) -> None:
        """
        Enhance sidebar navigation buttons for consistent appearance.

        Like a tailor adjusting the fit of a digital garment, this method
        ensures that navigation buttons maintain visual consistency.
        """
        if not self.sidebar:
            return

        # Get all navigation buttons in sidebar
        nav_buttons = [
            self.sidebar.findChild(QPushButton, "InstallationsButton"),
            self.sidebar.findChild(QPushButton, "CommandsButton"),
            self.sidebar.findChild(QPushButton, "ToolsButton"),
            self.sidebar.findChild(QPushButton, "SettingsButton"),
            self.sidebar.findChild(QPushButton, "HelpButton")
        ]

        # Filter out None values
        nav_buttons = [btn for btn in nav_buttons if btn]

        # Apply enhanced styling to each button
        for button in nav_buttons:
            # Get button's stored color property or use default
            color = button.property("button_color")
            if not color:
                # Fallback to a default color based on theme
                color = Theme.get_color('PRIMARY')

            # Calculate hover and pressed colors
            hover_color = Theme.adjust_color(color, -20)
            pressed_color = Theme.adjust_color(color, -40)

            # Apply enhanced styling
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    text-align: left;
                    padding-left: 20px;
                    font-size: 14px;
                    font-weight: bold;
                    margin: 2px 0;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """)

    def _optimize_control_buttons(self) -> None:
        """
        Optimize control buttons (Reboot/Exit) for consistent appearance.

        Like a careful alignment of power controls on a spaceship console,
        this method ensures the system control buttons are visually harmonious.
        """
        # Apply consistent styling to Reboot and Exit buttons
        if self.reboot_button and self.exit_button:
            # Get the container frame if it exists
            control_frame = self.reboot_button.parentWidget()
            if isinstance(control_frame, QFrame):
                # Apply enhanced frame styling
                control_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 12px;
                        margin: 10px 0;
                        padding: 10px;
                    }}
                """)

            # Apply enhanced button styling
            reboot_color = Theme.get_color('ERROR')
            exit_color = Theme.get_color('CONTROL_BG')

            # Reboot button (danger style)
            self.reboot_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {reboot_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                    margin: 5px 0;
                }}
                QPushButton:hover {{
                    background-color: {Theme.adjust_color(reboot_color, -20)};
                }}
            """)

            # Exit button (neutral style)
            self.exit_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {exit_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                    margin: 5px 0;
                }}
                QPushButton:hover {{
                    background-color: {Theme.adjust_color(exit_color, -20)};
                }}
            """)

    def _enhance_terminal_area(self) -> None:
        """
        Enhance terminal area for consistent appearance.

        Like a digital renovation of a command center, this method
        ensures the terminal area is visually consistent and readable
        across different themes.
        """
        if not self.terminal_area:
            self.logger.warning("Terminal area not found - cannot apply terminal enhancements")
            return

        try:
            self.logger.info("Applying terminal area enhancements - the console's makeover begins")

            # Apply consistent styling to terminal area
            current_theme = self._get_current_theme()
            bg_color = Theme.get_color('BG_DARK')
            text_color = Theme.get_color('TEXT_PRIMARY')

            # Fix the terminal output and clear button styling
            if self.terminal_output:
                # Enhanced terminal output styling
                self.terminal_output.setStyleSheet(f"""
                    QTextEdit#TerminalOutput {{
                        background-color: {bg_color};
                        color: {text_color};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 8px;
                        padding: 10px;
                        selection-background-color: {Theme.get_color('PRIMARY')};
                        selection-color: {Theme.get_color('TEXT_PRIMARY')};
                    }}
                """)

                # Cache the styling for theme switching
                self.style_cache[current_theme]["terminal_bg"] = bg_color

            if self.clear_button:
                # Enhanced clear button styling
                clear_bg = Theme.get_color('BG_MEDIUM')
                self.clear_button.setStyleSheet(f"""
                    QPushButton#ClearButton {{
                        background-color: {clear_bg};
                        color: {text_color};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-size: 12px;
                    }}
                    QPushButton#ClearButton:hover {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                    }}
                """)

                # Cache the styling for theme switching
                self.style_cache[current_theme]["clear_button_bg"] = clear_bg
                self.style_cache[current_theme]["clear_button_text"] = text_color

            self.logger.info("Terminal enhancements applied successfully - our console is now aesthetically acceptable")

        except Exception as e:
            self.logger.error(f"Failed to apply terminal enhancements: {str(e)}", exc_info=True)

    def _enhance_buttons(self) -> None:
        """
        Apply consistent styling to buttons throughout the application.

        Like a designer ensuring brand consistency across a product line,
        this method applies coherent button styling across the application.
        """
        try:
            # Enhance main navigation buttons (already handled in sidebar)
            pass

        except Exception as e:
            self.logger.error(f"Failed to enhance buttons: {str(e)}", exc_info=True)

    def _enhance_progress_section(self) -> None:
        """
        Enhance progress section for consistent appearance.

        Like tuning a dashboard's gauges for optimal readability,
        this method ensures the progress indicators are visually coherent.
        """
        if not self.progress_frame:
            return

        try:
            # Apply enhanced styling to progress frame
            self.progress_frame.setStyleSheet(f"""
                QFrame#ProgressFrame {{
                    background-color: {Theme.get_color('BG_LIGHT')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 12px;
                    padding: 5px;
                    margin: 10px 0;
                }}
            """)

            # Find and enhance progress bar
            progress_bar = self.progress_frame.findChild(QProgressBar)
            if progress_bar:
                progress_bar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        border: none;
                        border-radius: 3px;
                        text-align: center;
                        height: 6px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {Theme.get_color('PRIMARY')};
                        border-radius: 3px;
                    }}
                """)

        except Exception as e:
            self.logger.error(f"Failed to enhance progress section: {str(e)}", exc_info=True)

    def _apply_delayed_fixes(self) -> None:
        """
        Apply delayed fixes after the initial UI rendering.

        Like an after-hours custodian fixing what wasn't quite right during
        the day, this method applies corrections that need to happen after
        the initial rendering cycle.
        """
        try:
            # Fix terminal background color after theme switch
            if self.terminal_output:
                current_theme = self._get_current_theme()
                bg_color = Theme.get_color('BG_DARK')

                # Force terminal background update
                self.terminal_output.setStyleSheet(f"""
                    QTextEdit#TerminalOutput {{
                        background-color: {bg_color};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 8px;
                        padding: 10px;
                        selection-background-color: {Theme.get_color('PRIMARY')};
                        selection-color: {Theme.get_color('TEXT_PRIMARY')};
                    }}
                """)

            # Ensure Clear button has correct colors
            if self.clear_button:
                current_theme = self._get_current_theme()
                text_color = Theme.get_color('TEXT_PRIMARY')

                self.clear_button.setStyleSheet(f"""
                    QPushButton#ClearButton {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        color: {text_color};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-size: 12px;
                    }}
                    QPushButton#ClearButton:hover {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                    }}
                """)

        except Exception as e:
            self.logger.error(f"Failed to apply delayed fixes: {str(e)}", exc_info=True)

    def _get_current_theme(self) -> str:
        """
        Get the current application theme.

        Returns:
            Current theme identifier string

        Like a chameleon checking its current color, this method
        determines the active visual theme of the application.
        """
        # Try to get theme from Theme class
        try:
            return Theme.get_current_theme()
        except (AttributeError, Exception):
            # Fallback methods
            pass

        # Try to get from main window
        if hasattr(self.main_window, 'current_theme') and callable(self.main_window.current_theme):
            try:
                return self.main_window.current_theme()
            except Exception:
                pass

        # Default fallback
        return "dark"

    def _enhanced_apply_theme(self, theme_id: str) -> None:
        """
        Enhanced theme application that ensures UI consistency.

        Args:
            theme_id: Theme identifier to apply

        Like a careful artist ensuring color harmony across a canvas,
        this method wraps the original theme application with additional
        consistency checks.
        """
        # Call original implementation first
        self._original_apply_theme(theme_id)

        # Apply our enhancements after original theme is applied
        try:
            # Reapply specific elements that need fixing during theme switch

            # Fix terminal output background
            if self.terminal_output:
                bg_color = Theme.get_color('BG_DARK')
                text_color = Theme.get_color('TEXT_PRIMARY')

                self.terminal_output.setStyleSheet(f"""
                    QTextEdit#TerminalOutput {{
                        background-color: {bg_color};
                        color: {text_color};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 8px;
                        padding: 10px;
                        selection-background-color: {Theme.get_color('PRIMARY')};
                        selection-color: {text_color};
                    }}
                """)

            # Fix Clear button in light theme
            if self.clear_button:
                clear_bg = Theme.get_color('BG_MEDIUM')
                text_color = Theme.get_color('TEXT_PRIMARY')

                self.clear_button.setStyleSheet(f"""
                    QPushButton#ClearButton {{
                        background-color: {clear_bg};
                        color: {text_color};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-size: 12px;
                        font-weight: normal;
                    }}
                    QPushButton#ClearButton:hover {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                    }}
                """)

            # Schedule a delayed refresh for elements that need it
            QTimer.singleShot(200, self._apply_delayed_fixes)

        except Exception as e:
            self.logger.error(f"Error in enhanced theme application: {str(e)}", exc_info=True)


def enhance_main_window(main_window: QMainWindow) -> None:
    """
    Apply UI enhancements to the main application window.

    Args:
        main_window: Main application window to enhance

    Like a one-click digital renovation service, this function applies
    comprehensive UI improvements to the main application window.
    """
    enhancer = UIEnhancer(main_window)
    enhancer.enhance_ui()