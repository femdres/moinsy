#!/usr/bin/env python3
"""
Moinsy UI Enhancement Implementation
-----------------------------------
This module provides updates to the Moinsy UI, improving visual hierarchy,
adding borders, redesigning the system progress section, and fixing the
High Contrast theme's readability issues.

Like digital cosmetic surgery, we carefully reshape the application's
aesthetic structure while preserving its underlying functionality.
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple, Union
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import (
    QFont, QPainter, QPen, QColor, QIcon, QPixmap,
    QPainterPath, QLinearGradient, QBrush, QRadialGradient
)

from gui.styles.theme import Theme


class UIEnhancer:
    """
    Enhances the UI of the Moinsy application by implementing
    visual improvements to borders, components, and themes.

    Like a digital interior decorator, this class applies aesthetic
    changes to transform the application's visual appeal.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the UI enhancer.

        Args:
            logger: Optional logger instance for tracking enhancement operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("Initializing UI enhancer - preparing aesthetic transformation")

    def enhance_high_contrast_theme(self) -> Dict[str, str]:
        """
        Create an improved color palette for the High Contrast theme
        that's more readable and visually appealing.

        Returns:
            Dictionary containing the enhanced High Contrast color palette
        """
        self.logger.debug("Enhancing High Contrast theme colors - refining the digital palette")

        # Define an improved color palette that maintains high contrast
        # while being more visually appealing and addressing readability
        return {
            # Primary colors - more distinct and less harsh
            'PRIMARY': '#1AFF66',  # Softer green (was #00FF00)
            'SECONDARY': '#00B7FF',  # Bright blue (was #FFFF00)
            'TERTIARY': '#FF47FF',  # Softer magenta (was #FF00FF)

            # Backgrounds - slightly improved contrast hierarchy
            'BG_DARK': '#000000',  # Black background
            'BG_MEDIUM': '#121212',  # Slightly lighter (was #0A0A0A)
            'BG_LIGHT': '#2A2A2A',  # Better contrast gray (was #202020)

            # Text colors - improved readability
            'TEXT_PRIMARY': '#FFFFFF',  # White text
            'TEXT_SECONDARY': '#E0E0E0',  # Lighter gray for better visibility

            # Status colors - more distinct from each other
            'SUCCESS': '#00CC66',  # Distinct green (was #00FF00)
            'ERROR': '#FF3333',  # Bright red (was #FF0000)
            'WARNING': '#FFCC00',  # Amber (was #FFFF00)

            # Control colors - better contrast
            'CONTROL_BG': '#3A3A3A',  # Medium gray (was #303030)
            'CONTROL_HOVER': '#555555'  # Lighter gray (was #505050)
        }

    def apply_theme_enhancements(self) -> None:
        """
        Apply enhancements to the Theme class's color definitions.

        Replaces the existing High Contrast theme with the improved version.
        """
        try:
            self.logger.info("Applying theme enhancements to High Contrast theme")

            # Update the High Contrast theme colors
            enhanced_colors = self.enhance_high_contrast_theme()
            Theme.COLORS[Theme.THEME_HIGH_CONTRAST] = enhanced_colors

            self.logger.debug("High Contrast theme enhancements applied successfully")
        except Exception as e:
            self.logger.error(f"Failed to apply theme enhancements: {str(e)}")
            # Continue with other enhancements even if theme update fails

    def create_moinsy_logo(self, size: int = 50) -> QPixmap:
        """
        Create a custom Moinsy logo as a QPixmap.

        Args:
            size: Size of the logo in pixels

        Returns:
            QPixmap containing the generated Moinsy logo
        """
        try:
            # Create pixmap with transparent background
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Initialize painter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Get theme colors
            primary_color = QColor(Theme.get_color('PRIMARY'))
            secondary_color = QColor(Theme.get_color('SECONDARY'))
            text_color = QColor(Theme.get_color('TEXT_PRIMARY'))

            # Create circular background with gradient
            gradient = QRadialGradient(size / 2, size / 2, size / 2)
            gradient.setColorAt(0, primary_color)
            gradient.setColorAt(1, primary_color.darker(120))

            # Draw circular background
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, size - 4, size - 4)

            # Draw border
            pen = QPen(text_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(2, 2, size - 4, size - 4)

            # Draw a stylized "M" in the center
            path = QPainterPath()

            # Create the stylized "M" path
            center_x = size / 2
            center_y = size / 2
            width = size * 0.6
            height = size * 0.4

            # Define the points of the "M"
            left = center_x - width / 2
            right = center_x + width / 2
            top = center_y - height / 2
            bottom = center_y + height / 2

            # Draw the M
            path.moveTo(left, bottom)  # Bottom left
            path.lineTo(left + width * 0.2, top)  # Top left peak
            path.lineTo(center_x, bottom - height * 0.3)  # Middle dip
            path.lineTo(right - width * 0.2, top)  # Top right peak
            path.lineTo(right, bottom)  # Bottom right

            # Set pen for the "M"
            pen = QPen(text_color, 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            # Draw the path
            painter.drawPath(path)

            # End painting
            painter.end()

            self.logger.debug("Moinsy logo created successfully")
            return pixmap

        except Exception as e:
            self.logger.error(f"Failed to create Moinsy logo: {str(e)}")
            # Return an empty pixmap if logo creation fails
            return QPixmap(size, size)

    def enhance_sidebar_styling(self) -> str:
        """
        Generate enhanced styling for the sidebar.

        Returns:
            CSS-like stylesheet string for the sidebar
        """
        try:
            # Get theme colors
            bg_color = Theme.get_color('BG_MEDIUM')
            border_color = Theme.get_color('BG_LIGHT')

            # Create enhanced sidebar styling with border
            stylesheet = f"""
                QWidget#MainSidebar {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """

            self.logger.debug("Enhanced sidebar styling generated")
            return stylesheet

        except Exception as e:
            self.logger.error(f"Failed to generate sidebar styling: {str(e)}")
            # Return minimal styling as fallback
            return "QWidget#MainSidebar { background-color: #2d2e32; }"

    def enhance_terminal_styling(self) -> str:
        """
        Generate enhanced styling for the terminal area.

        Returns:
            CSS-like stylesheet string for the terminal
        """
        try:
            # Get theme colors
            bg_color = Theme.get_color('BG_DARK')
            border_color = Theme.get_color('BG_LIGHT')

            # Create enhanced terminal styling with border
            stylesheet = f"""
                QWidget#TerminalArea {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """

            self.logger.debug("Enhanced terminal styling generated")
            return stylesheet

        except Exception as e:
            self.logger.error(f"Failed to generate terminal styling: {str(e)}")
            # Return minimal styling as fallback
            return "QWidget#TerminalArea { background-color: #1a1b1e; }"

    def generate_progress_section_styling(self) -> Dict[str, str]:
        """
        Generate styling for the enhanced progress section components.

        Returns:
            Dictionary mapping component IDs to their stylesheet strings
        """
        try:
            # Get theme colors
            primary_color = Theme.get_color('PRIMARY')
            bg_medium = Theme.get_color('BG_MEDIUM')
            bg_light = Theme.get_color('BG_LIGHT')
            text_primary = Theme.get_color('TEXT_PRIMARY')
            text_secondary = Theme.get_color('TEXT_SECONDARY')

            # Create styles for components
            styles = {
                # Frame container
                "ProgressFrame": f"""
                    QFrame#ProgressFrame {{
                        background-color: {bg_medium};
                        border: 1px solid {bg_light};
                        border-radius: 8px;
                        padding: 10px;
                        margin: 5px;
                    }}
                """,

                # Progress header
                "ProgressHeader": f"""
                    QLabel#ProgressHeader {{
                        color: {text_primary};
                        font-size: 14px;
                        font-weight: bold;
                        padding-left: 5px;
                    }}
                """,

                # Progress percentage
                "ProgressPercentage": f"""
                    QLabel#ProgressPercentage {{
                        color: {primary_color};
                        font-size: 28px;
                        font-weight: bold;
                        padding: 5px;
                    }}
                """,

                # Progress bar
                "ProgressBar": f"""
                    QProgressBar {{
                        background-color: {bg_light};
                        border: none;
                        border-radius: 4px;
                        text-align: center;
                        margin-top: 5px;
                        margin-bottom: 5px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {primary_color};
                        border-radius: 4px;
                    }}
                """,

                # Status text
                "ProgressStatus": f"""
                    QLabel#ProgressStatus {{
                        color: {text_secondary};
                        font-size: 12px;
                        margin-top: 3px;
                    }}
                """
            }

            self.logger.debug("Progress section styling generated successfully")
            return styles

        except Exception as e:
            self.logger.error(f"Failed to generate progress section styling: {str(e)}")
            # Return empty dict as fallback
            return {}


class SidebarEnhancer:
    """
    Enhances the Sidebar component with improved styling and layout.

    Like an aesthetic architect redesigning the navigational framework,
    this class transforms the sidebar's visual organization.
    """

    def __init__(self, sidebar: QWidget, logger: Optional[logging.Logger] = None):
        """
        Initialize the sidebar enhancer.

        Args:
            sidebar: The sidebar widget to enhance
            logger: Optional logger instance
        """
        self.sidebar = sidebar
        self.logger = logger or logging.getLogger(__name__)
        self.ui_enhancer = UIEnhancer(self.logger)
        self.logger.debug("Sidebar enhancer initialized - preparing navigational facelift")

    def apply_enhancements(self) -> None:
        """
        Apply all sidebar enhancements at once.

        This includes border styling, logo redesign, and progress section improvements.
        """
        try:
            self.logger.info("Applying comprehensive sidebar enhancements")

            # Apply base styling with border
            self.enhance_base_styling()

            # Redesign the logo section
            self.enhance_logo_section()

            # Redesign the progress section
            self.enhance_progress_section()

            self.logger.info("Sidebar enhancements applied successfully")
        except Exception as e:
            self.logger.error(f"Failed to apply sidebar enhancements: {str(e)}")

    def enhance_base_styling(self) -> None:
        """
        Apply enhanced base styling to the sidebar.
        """
        try:
            # Get enhanced sidebar styling
            stylesheet = self.ui_enhancer.enhance_sidebar_styling()

            # Apply styling to sidebar
            self.sidebar.setStyleSheet(stylesheet)
            self.logger.debug("Enhanced sidebar base styling applied")
        except Exception as e:
            self.logger.error(f"Failed to apply sidebar base styling: {str(e)}")

    def enhance_logo_section(self) -> None:
        """
        Redesign the logo section with a custom Moinsy logo.
        """
        try:
            # Find the logo container
            logo_container = self.sidebar.findChild(QFrame, "LogoContainer")
            if not logo_container:
                self.logger.warning("Logo container not found - skipping logo enhancement")
                return

            # Find the logo label
            logo_label = self.sidebar.findChild(QLabel, "LogoLabel")
            if not logo_label:
                self.logger.warning("Logo label not found - skipping logo enhancement")
                return

            # Create logo pixmap
            logo_pixmap = self.ui_enhancer.create_moinsy_logo(50)

            # Create a new logo label
            new_logo_label = QLabel()
            new_logo_label.setObjectName("MoinsyLogoImage")
            new_logo_label.setPixmap(logo_pixmap)
            new_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_logo_label.setFixedSize(50, 50)

            # Insert the new logo before the text logo
            logo_layout = logo_container.layout()
            if logo_layout:
                # Insert at the beginning with alignment
                logo_layout.insertWidget(0, new_logo_label, 0, Qt.AlignmentFlag.AlignCenter)

                # Enhance the text logo styling
                logo_label.setStyleSheet(f"""
                    color: {Theme.get_color('PRIMARY')};
                    font-size: 18px;
                    font-weight: bold;
                    letter-spacing: 2px;
                    margin-top: 8px;
                """)

                # Apply border and rounded corners to the container
                logo_container.setStyleSheet(f"""
                    QFrame#LogoContainer {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        border: 1px solid {Theme.get_color('BG_LIGHT')};
                        border-radius: 8px;
                        padding: 10px;
                        margin: 5px;
                    }}
                """)

                self.logger.debug("Logo section enhanced successfully")
            else:
                self.logger.warning("Logo container layout not found")

        except Exception as e:
            self.logger.error(f"Failed to enhance logo section: {str(e)}")

    def enhance_progress_section(self) -> None:
        """
        Redesign the progress section with improved visual hierarchy.
        """
        try:
            # Find the progress frame
            progress_frame = self.sidebar.findChild(QFrame, "ProgressFrame")
            if not progress_frame:
                self.logger.warning("Progress frame not found - skipping progress enhancement")
                return

            # Find progress components
            progress_bar = self.sidebar.findChild(QProgressBar, "ProgressBar")
            progress_percentage = self.sidebar.findChild(QLabel, "ProgressPercentage")
            progress_status = self.sidebar.findChild(QLabel, "ProgressStatus")

            if not all([progress_bar, progress_percentage, progress_status]):
                self.logger.warning("Progress components not found - skipping progress enhancement")
                return

            # Generate component styles
            styles = self.ui_enhancer.generate_progress_section_styling()

            # Apply styles to components
            progress_frame.setStyleSheet(styles.get("ProgressFrame", ""))

            if progress_percentage:
                progress_percentage.setStyleSheet(styles.get("ProgressPercentage", ""))
                # Make the percentage more prominent
                font = progress_percentage.font()
                font.setPointSize(18)
                font.setBold(True)
                progress_percentage.setFont(font)

            if progress_bar:
                progress_bar.setStyleSheet(styles.get("ProgressBar", ""))
                # Make the progress bar a bit taller for better visibility
                progress_bar.setMinimumHeight(8)
                progress_bar.setMaximumHeight(8)

            if progress_status:
                progress_status.setStyleSheet(styles.get("ProgressStatus", ""))

            # Find or create the header
            progress_header = progress_frame.findChild(QLabel, "ProgressHeader")
            if progress_header:
                progress_header.setStyleSheet(styles.get("ProgressHeader", ""))

            # Add a mini-icon to the header if not already present
            if progress_frame.layout():
                header_layout = None

                # Check if there's a header layout already
                for i in range(progress_frame.layout().count()):
                    item = progress_frame.layout().itemAt(i)
                    if isinstance(item, QHBoxLayout):
                        header_layout = item
                        break

                # If no header layout found, create one and add it to the beginning
                if not header_layout:
                    # Create header layout
                    header_layout = QHBoxLayout()
                    header_layout.setSpacing(8)

                    # Create icon
                    icon_label = QLabel()
                    icon_label.setObjectName("ProgressIcon")
                    icon_label.setFixedSize(16, 16)
                    icon_label.setStyleSheet(f"""
                        QLabel#ProgressIcon {{
                            background-color: {Theme.get_color('PRIMARY')};
                            border-radius: 8px;
                        }}
                    """)
                    header_layout.addWidget(icon_label)

                    # Create header text (if not already there)
                    if not progress_header:
                        progress_header = QLabel("System Progress")
                        progress_header.setObjectName("ProgressHeader")
                        progress_header.setStyleSheet(styles.get("ProgressHeader", ""))

                    header_layout.addWidget(progress_header)
                    header_layout.addStretch()

                    # Insert header layout at the beginning
                    progress_frame.layout().insertLayout(0, header_layout)

            self.logger.debug("Progress section enhanced successfully")

        except Exception as e:
            self.logger.error(f"Failed to enhance progress section: {str(e)}")


class TerminalEnhancer:
    """
    Enhances the Terminal component with improved styling and border.

    Like a digital interior designer refining the command center's
    aesthetic, this class elevates the terminal's visual presence.
    """

    def __init__(self, terminal: QWidget, logger: Optional[logging.Logger] = None):
        """
        Initialize the terminal enhancer.

        Args:
            terminal: The terminal widget to enhance
            logger: Optional logger instance
        """
        self.terminal = terminal
        self.logger = logger or logging.getLogger(__name__)
        self.ui_enhancer = UIEnhancer(self.logger)
        self.logger.debug("Terminal enhancer initialized - preparing command center refinement")

    def apply_enhancements(self) -> None:
        """
        Apply all terminal enhancements at once.

        Adds border styling and improves internal component visuals.
        """
        try:
            self.logger.info("Applying terminal area enhancements")

            # Apply base styling with border
            stylesheet = self.ui_enhancer.enhance_terminal_styling()
            self.terminal.setStyleSheet(stylesheet)

            # Enhance the terminal header
            self.enhance_terminal_header()

            self.logger.info("Terminal enhancements applied successfully")
        except Exception as e:
            self.logger.error(f"Failed to apply terminal enhancements: {str(e)}")

    def enhance_terminal_header(self) -> None:
        """
        Enhance the terminal header styling.
        """
        try:
            # Find the terminal header
            header = self.terminal.findChild(QFrame, "TerminalHeader")
            if not header:
                self.logger.warning("Terminal header not found - skipping header enhancement")
                return

            # Apply enhanced styling
            header.setStyleSheet(f"""
                QFrame#TerminalHeader {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border-bottom: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px 8px 0 0;
                    padding: 5px;
                }}
            """)

            # Find the title label
            title = self.terminal.findChild(QLabel, "TerminalTitle")
            if title:
                title.setStyleSheet(f"""
                    QLabel#TerminalTitle {{
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)

            # Find the clear button
            clear_button = self.terminal.findChild(QPushButton, "ClearButton")
            if clear_button:
                clear_button.setStyleSheet(f"""
                    QPushButton#ClearButton {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-size: 12px;
                    }}
                    QPushButton#ClearButton:hover {{
                        background-color: {Theme.get_color('CONTROL_HOVER')};
                    }}
                """)

            self.logger.debug("Terminal header enhanced successfully")
        except Exception as e:
            self.logger.error(f"Failed to enhance terminal header: {str(e)}")


def apply_ui_enhancements(
        main_window: QWidget,
        sidebar_name: str = "sidebar",
        terminal_name: str = "terminal"
) -> None:
    """
    Apply all UI enhancements to the main window and its components.

    Args:
        main_window: The main application window
        sidebar_name: Attribute name for the sidebar component
        terminal_name: Attribute name for the terminal component
    """
    logger = logging.getLogger(__name__)
    logger.info("Applying comprehensive UI enhancements to Moinsy")

    ui_enhancer = UIEnhancer(logger)

    try:
        # Apply theme enhancements
        ui_enhancer.apply_theme_enhancements()

        # Apply sidebar enhancements if available
        if hasattr(main_window, sidebar_name):
            sidebar = getattr(main_window, sidebar_name)
            sidebar_enhancer = SidebarEnhancer(sidebar, logger)
            sidebar_enhancer.apply_enhancements()
        else:
            logger.warning(f"Sidebar '{sidebar_name}' not found - skipping sidebar enhancements")

        # Apply terminal enhancements if available
        if hasattr(main_window, terminal_name):
            terminal = getattr(main_window, terminal_name)
            terminal_enhancer = TerminalEnhancer(terminal, logger)
            terminal_enhancer.apply_enhancements()
        else:
            logger.warning(f"Terminal '{terminal_name}' not found - skipping terminal enhancements")

        logger.info("UI enhancements applied successfully")

    except Exception as e:
        logger.error(f"Failed to apply UI enhancements: {str(e)}")
        # Even if we fail, we don't want to crash the application