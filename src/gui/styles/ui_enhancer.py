#!/usr/bin/env python3
"""
Moinsy UI Enhancement Module
----------------------------
A collection of aesthetic improvements for the Moinsy application,
addressing theme inconsistencies, visual hierarchy issues, and
implementing subtle design enhancements.

Like digital makeup applied to the face of a command-line tool that
never asked to be beautiful, we reshape pixels with CSS incantations
while questioning if appearance truly matters in the void of functionality.
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple, Union, List, cast
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QFrame, QSpacerItem, QSizePolicy,
    QTextEdit, QLineEdit, QApplication, QSplashScreen
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import (
    QFont, QPainter, QPen, QColor, QIcon, QPixmap,
    QPainterPath, QLinearGradient, QBrush, QRadialGradient
)

from gui.styles.theme import Theme


class UIEnhancer:
    """
    Enhances the Moinsy UI through subtle aesthetic adjustments,
    bringing visual coherence to a fragmented interface.

    Like a digital interior decorator questioning their life choices,
    this class applies CSS properties to widgets that will never
    appreciate the aesthetic effort invested in their appearance.
    """

    def __init__(self, main_window: Optional[QMainWindow] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the UI enhancer with a reference to the main window.

        Args:
            main_window: Optional reference to the main application window
            logger: Optional logger instance for tracking enhancement operations
        """
        self.main_window = main_window
        self.logger = logger or logging.getLogger(__name__)
        self.theme_id: str = Theme.get_current_theme()
        self.logger.debug("UI enhancer initialized - preparing the digital makeover that nobody asked for")

    def enhance_ui(self) -> None:
        """
        Apply all UI enhancements to the application.

        Like a cosmic beautification ritual performed on bits and pixels,
        this method orchestrates the application of multiple aesthetic
        improvements that users will barely notice but designers obsess over.
        """
        try:
            self.logger.info("Applying comprehensive UI enhancements - digital plastic surgery commencing")

            # Fix theme color definitions first
            self._enhance_theme_definitions()

            # Apply component-specific enhancements if we have a main window
            if self.main_window:
                # Find components by attribute names
                self._enhance_main_window()

                # Apply specific component enhancements
                components = self._get_ui_components()

                if 'sidebar' in components:
                    self._enhance_sidebar(components['sidebar'])

                if 'terminal' in components:
                    self._enhance_terminal(components['terminal'])

                # Force update to ensure all styling is applied
                self._force_style_update()

                # Schedule delayed fixes for elements that might need additional time
                QTimer.singleShot(100, self._apply_delayed_fixes)

            self.logger.info("UI enhancements applied - interface slightly less depressing")

        except Exception as e:
            self.logger.error(f"Failed to apply UI enhancements: {str(e)}", exc_info=True)

    def _enhance_theme_definitions(self) -> None:
        """
        Enhance color definitions for the themes.

        Like a digital color theorist overthinking the difference between
        #000000 and #0A0A0A, we meticulously adjust hex values to create
        the illusion of aesthetic intention.
        """
        try:
            # Fix Dark theme colors
            Theme.COLORS[Theme.THEME_DARK].update({
                'BG_DARK': '#121212',  # Darker background for terminal
                'BG_MEDIUM': '#1E1E1E',  # Slightly lighter for medium elements
                'BG_LIGHT': '#2A2A2A',  # Lighter shade for hover/active states
            })

            # Fix Light theme colors
            Theme.COLORS[Theme.THEME_LIGHT].update({
                'BG_DARK': '#F5F5F5',  # Light gray for terminal
                'BG_MEDIUM': '#E0E0E0',  # Medium gray for backgrounds
                'BG_LIGHT': '#D0D0D0',  # Darker gray for hover/active
                'TEXT_PRIMARY': '#212121',  # Dark text for contrast
                'TEXT_SECONDARY': '#616161',  # Secondary text
                'CONTROL_BG': '#9E9E9E',  # Control background
                'CONTROL_HOVER': '#757575'  # Control hover
            })

            # Fix High Contrast theme colors
            Theme.COLORS[Theme.THEME_HIGH_CONTRAST] = {
                # Primary colors - more distinct and less harsh
                'PRIMARY': '#1AFF66',  # Softer green
                'SECONDARY': '#00B7FF',  # Bright blue
                'TERTIARY': '#FF47FF',  # Softer magenta

                # Backgrounds - improved contrast hierarchy
                'BG_DARK': '#000000',  # Pure black background
                'BG_MEDIUM': '#121212',  # Very dark gray
                'BG_LIGHT': '#2A2A2A',  # Better contrast gray

                # Text colors - improved readability
                'TEXT_PRIMARY': '#FFFFFF',  # White text
                'TEXT_SECONDARY': '#E0E0E0',  # Light gray

                # Status colors - more distinct
                'SUCCESS': '#00CC66',  # Distinct green
                'ERROR': '#FF3333',  # Bright red
                'WARNING': '#FFCC00',  # Amber

                # Control colors - better contrast
                'CONTROL_BG': '#3A3A3A',  # Medium gray
                'CONTROL_HOVER': '#555555'  # Lighter gray
            }

            self.logger.debug("Theme definitions enhanced - as if hex codes could solve existential problems")

        except Exception as e:
            self.logger.error(f"Failed to enhance theme definitions: {str(e)}", exc_info=True)

    def _get_ui_components(self) -> Dict[str, QWidget]:
        """
        Get UI components from the main window.

        Returns:
            Dictionary mapping component names to their widget instances
        """
        components = {}

        try:
            # Find components by attribute name
            for component_name in ['sidebar', 'terminal']:
                if hasattr(self.main_window, component_name):
                    component = getattr(self.main_window, component_name)
                    if isinstance(component, QWidget):
                        components[component_name] = component

            self.logger.debug(f"Found {len(components)} UI components - the building blocks of our digital façade")

        except Exception as e:
            self.logger.error(f"Error finding UI components: {str(e)}", exc_info=True)

        return components

    def _enhance_main_window(self) -> None:
        """
        Enhance the main window appearance.

        Like applying foundation to a digital face, we adjust the basic
        properties of the main window to create a cohesive base for our UI.
        """
        try:
            # Set uniform margins on central widget layout
            central_widget = self.main_window.centralWidget()
            if central_widget and central_widget.layout():
                central_widget.layout().setContentsMargins(10, 10, 10, 10)
                central_widget.layout().setSpacing(10)

            # Apply theme-specific styling to main window
            theme_id = Theme.get_current_theme()
            bg_color = Theme.get_color('BG_DARK')

            self.main_window.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {bg_color};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                }}
            """)

            self.logger.debug("Main window appearance enhanced - the canvas of our digital art")

        except Exception as e:
            self.logger.error(f"Failed to enhance main window: {str(e)}", exc_info=True)

    def _enhance_sidebar(self, sidebar: QWidget) -> None:
        """
        Enhance the sidebar with improved styling and components.

        Args:
            sidebar: The sidebar widget to enhance

        Like a neighborhood beautification project for the navigation district,
        we add borders, redesign the logo, and reshape the progress section
        while questioning the purpose of spatial aesthetics in digital realms.
        """
        try:
            # Apply enhanced base styling with border
            bg_color = Theme.get_color('BG_MEDIUM')
            border_color = Theme.get_color('BG_LIGHT')

            sidebar.setStyleSheet(f"""
                QWidget#MainSidebar {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """)

            # Enhance logo section
            self._enhance_logo_section(sidebar)

            # Enhance progress section
            self._enhance_progress_section(sidebar)

            # Enhance control buttons
            self._enhance_control_buttons(sidebar)

            self.logger.debug("Sidebar enhancements applied - navigation looks slightly less utilitarian")

        except Exception as e:
            self.logger.error(f"Failed to enhance sidebar: {str(e)}", exc_info=True)

    def _enhance_logo_section(self, sidebar: QWidget) -> None:
        """
        Enhance the logo section with a custom Moinsy logo.

        Args:
            sidebar: The sidebar widget containing the logo section

        Like a digital portrait artist painting in a medium of ones and zeros,
        we craft a visual identifier for an application that may never
        truly know itself.
        """
        try:
            # Find the logo container
            logo_container = sidebar.findChild(QFrame, "LogoContainer")
            if not logo_container:
                self.logger.warning("Logo container not found - identity crisis persists")
                return

            # Get existing layout or create a new one
            old_layout = logo_container.layout()
            if old_layout:
                # Remove existing widgets
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().hide()
                        item.widget().deleteLater()

                # Delete old layout
                logo_container.setLayout(None)
                old_layout.deleteLater()

            # Create new layout
            new_layout = QVBoxLayout(logo_container)
            new_layout.setContentsMargins(10, 10, 10, 8)
            new_layout.setSpacing(5)

            # Create header layout with logo and app name
            header_layout = QHBoxLayout()
            header_layout.setSpacing(10)
            header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Create logo
            logo_pixmap = self._create_moinsy_logo(40)

            # Create logo label
            logo_label = QLabel()
            logo_label.setObjectName("MoinsyLogoImage")
            logo_label.setPixmap(logo_pixmap)
            logo_label.setFixedSize(40, 40)

            # Create app name label
            app_name = QLabel("MOINSY")
            app_name.setObjectName("MoinsyTitleLabel")
            app_name.setStyleSheet(f"""
                color: {Theme.get_color('PRIMARY')};
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 2px;
            """)

            # Add logo and app name to header layout
            header_layout.addWidget(logo_label)
            header_layout.addWidget(app_name)

            # Create subtitle
            subtitle = QLabel("System Installer")
            subtitle.setObjectName("MoinsySubtitleLabel")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setStyleSheet(f"""
                color: {Theme.get_color('TEXT_SECONDARY')};
                font-size: 12px;
                margin-top: 0px;
            """)

            # Add layouts to container
            new_layout.addLayout(header_layout)
            new_layout.addWidget(subtitle)

            # Apply border styling
            logo_container.setStyleSheet(f"""
                QFrame#LogoContainer {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 0px;
                }}
            """)

            self.logger.debug("Logo section enhanced - digital identity constructed from binary illusions")

        except Exception as e:
            self.logger.error(f"Failed to enhance logo section: {str(e)}", exc_info=True)

    def _enhance_progress_section(self, sidebar: QWidget) -> None:
        """
        Enhance the progress section with improved visual hierarchy.

        Args:
            sidebar: The sidebar widget containing the progress section

        Like digital landscapers reshaping the progress terrain, we
        rearrange indicators and labels to create an information hierarchy
        that implies progress is both meaningful and measurable.
        """
        try:
            # Find the progress frame
            progress_frame = sidebar.findChild(QFrame, "ProgressFrame")
            if not progress_frame:
                self.logger.warning("Progress frame not found - progress remains unmeasurable")
                return

            # Get or create layout
            old_layout = progress_frame.layout()
            if old_layout:
                # Clear existing widgets but store references
                progress_percentage = sidebar.findChild(QLabel, "ProgressPercentage")
                progress_bar = sidebar.findChild(QProgressBar, "ProgressBar")
                progress_status = sidebar.findChild(QLabel, "ProgressStatus")

                # Store current values
                current_percentage = "0%"
                current_status = "No active installation"
                current_progress = 0

                if progress_percentage:
                    current_percentage = progress_percentage.text()
                if progress_status:
                    current_status = progress_status.text()
                if progress_bar:
                    current_progress = progress_bar.value()

                # Clear layout
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
            else:
                # Define defaults for new progress section
                current_percentage = "0%"
                current_status = "No active installation"
                current_progress = 0
                old_layout = QVBoxLayout(progress_frame)

            # Reset layout properties
            old_layout.setContentsMargins(15, 15, 15, 15)
            old_layout.setSpacing(10)

            # Create header with icon
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

            # Create header text
            header = QLabel("System Progress")
            header.setObjectName("ProgressHeader")
            header.setStyleSheet(f"""
                QLabel#ProgressHeader {{
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)

            header_layout.addWidget(header)
            header_layout.addStretch()

            # Create percentage label
            percentage = QLabel(current_percentage)
            percentage.setObjectName("ProgressPercentage")
            percentage.setAlignment(Qt.AlignmentFlag.AlignCenter)
            percentage.setStyleSheet(f"""
                QLabel#ProgressPercentage {{
                    color: {Theme.get_color('PRIMARY')};
                    font-size: 24px;
                    font-weight: bold;
                }}
            """)

            # Create progress bar
            progress_bar = QProgressBar()
            progress_bar.setObjectName("ProgressBar")
            progress_bar.setValue(current_progress)
            progress_bar.setTextVisible(False)
            progress_bar.setMinimumHeight(8)
            progress_bar.setMaximumHeight(8)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {Theme.get_color('BG_LIGHT')};
                    border: none;
                    border-radius: 4px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {Theme.get_color('PRIMARY')};
                    border-radius: 4px;
                }}
            """)

            # Create status label
            status = QLabel(current_status)
            status.setObjectName("ProgressStatus")
            status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status.setStyleSheet(f"""
                QLabel#ProgressStatus {{
                    color: {Theme.get_color('TEXT_SECONDARY')};
                    font-size: 12px;
                    margin-top: 3px;
                }}
            """)

            # Add components to layout
            old_layout.addLayout(header_layout)
            old_layout.addWidget(percentage)
            old_layout.addWidget(progress_bar)
            old_layout.addWidget(status)

            # Apply styling to frame
            progress_frame.setStyleSheet(f"""
                QFrame#ProgressFrame {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px 0px;
                }}
            """)

            self.logger.debug("Progress section enhanced - visual illusion of meaningful advancement constructed")

        except Exception as e:
            self.logger.error(f"Failed to enhance progress section: {str(e)}", exc_info=True)

    def _enhance_control_buttons(self, sidebar: QWidget) -> None:
        """
        Enhance the control buttons in the sidebar.

        Args:
            sidebar: The sidebar widget containing the control buttons

        Like designing the buttons that control digital fate, we reshape
        the visual representation of system power while contemplating
        the illusion of control in a deterministic universe.
        """
        try:
            # Find control frame
            control_frame = sidebar.findChild(QFrame, "ControlFrame")
            if not control_frame:
                self.logger.warning("Control frame not found - illusion of control remains undesigned")
                return

            # Apply styling to frame
            control_frame.setStyleSheet(f"""
                QFrame#ControlFrame {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px 0px;
                    padding: 5px;
                }}
            """)

            # Find and style reboot button
            reboot_button = sidebar.findChild(QPushButton, "RebootButton")
            if reboot_button:
                reboot_button.setStyleSheet(f"""
                    QPushButton#RebootButton {{
                        background-color: {Theme.get_color('ERROR')};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    }}
                    QPushButton#RebootButton:hover {{
                        background-color: {self._adjust_color(Theme.get_color('ERROR'), -30)};
                    }}
                """)

            # Find and style exit button
            exit_button = sidebar.findChild(QPushButton, "ExitButton")
            if exit_button:
                exit_button.setStyleSheet(f"""
                    QPushButton#ExitButton {{
                        background-color: {Theme.get_color('CONTROL_BG')};
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        border: none;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    }}
                    QPushButton#ExitButton:hover {{
                        background-color: {Theme.get_color('CONTROL_HOVER')};
                    }}
                """)

            self.logger.debug("Control buttons enhanced - digital omnipotence packaged in rounded rectangles")

        except Exception as e:
            self.logger.error(f"Failed to enhance control buttons: {str(e)}", exc_info=True)

    def _enhance_terminal(self, terminal: QWidget) -> None:
        """
        Enhance the terminal area with improved styling and border.

        Args:
            terminal: The terminal widget to enhance

        Like an architect designing a better void for text to inhabit,
        we refine the aesthetic container of input and output streams
        that ultimately lead nowhere of consequence.
        """
        try:
            # Apply terminal area styling
            terminal.setStyleSheet(f"""
                QWidget#TerminalArea {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 8px;
                    margin: 5px;
                }}
            """)

            # Enhance terminal header
            self._enhance_terminal_header(terminal)

            # Enhance terminal output area
            self._enhance_terminal_output(terminal)

            # Enhance input area
            self._enhance_terminal_input(terminal)

            self.logger.debug("Terminal enhancements applied - the void now has a more aesthetically pleasing border")

        except Exception as e:
            self.logger.error(f"Failed to enhance terminal: {str(e)}", exc_info=True)

    def _enhance_terminal_header(self, terminal: QWidget) -> None:
        """
        Enhance the terminal header styling.

        Args:
            terminal: The terminal widget containing the header

        Like applying a decorative frieze to the entry of a digital temple,
        we polish the top border of our console while questioning if headers
        truly matter in the stream of consciousness that is terminal output.
        """
        try:
            # Find header
            header = terminal.findChild(QFrame, "TerminalHeader")
            if not header:
                self.logger.warning("Terminal header not found - our digital temple remains unadorned")
                return

            # Apply styling
            header.setStyleSheet(f"""
                QFrame#TerminalHeader {{
                    background-color: {Theme.get_color('BG_MEDIUM')};
                    border-bottom: 1px solid {Theme.get_color('BG_LIGHT')};
                    border-radius: 7px 7px 0 0;
                    padding: 5px;
                    margin: 0px;
                }}
            """)

            # Style the title
            title = terminal.findChild(QLabel, "TerminalTitle")
            if title:
                title.setStyleSheet(f"""
                    QLabel#TerminalTitle {{
                        color: {Theme.get_color('TEXT_PRIMARY')};
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)

            # Style clear button
            clear_button = terminal.findChild(QPushButton, "ClearButton")
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

            self.logger.debug("Terminal header enhanced - digital gateway now more visually coherent")

        except Exception as e:
            self.logger.error(f"Failed to enhance terminal header: {str(e)}", exc_info=True)

    def _enhance_terminal_output(self, terminal: QWidget) -> None:
        """
        Enhance the terminal output area.

        Args:
            terminal: The terminal widget containing the output area

        Like designing a better void for text to inhabit, we adjust the
        background and styling of the digital stream of consciousness that
        is terminal output - a record of commands that, like human actions,
        will eventually be cleared and forgotten.
        """
        try:
            # Find output area
            output = terminal.findChild(QTextEdit, "TerminalOutput")
            if not output:
                self.logger.warning("Terminal output not found - the void remains unstyled")
                return

            # Apply direct styling
            output.setStyleSheet(f"""
                QTextEdit#TerminalOutput {{
                    background-color: {Theme.get_color('BG_DARK')};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    selection-background-color: {Theme.get_color('PRIMARY')};
                    selection-color: {Theme.get_color('TEXT_PRIMARY')};
                }}
            """)

            self.logger.debug("Terminal output enhanced - digital void now more aesthetically pleasing")

        except Exception as e:
            self.logger.error(f"Failed to enhance terminal output: {str(e)}", exc_info=True)

    def _enhance_terminal_input(self, terminal: QWidget) -> None:
        """
        Enhance the terminal input area.

        Args:
            terminal: The terminal widget containing the input area

        Like designing a better entry point for human-machine communication,
        we reshape the aesthetic of the command input field while contemplating
        the arbitrary nature of digital interfaces.
        """
        try:
            # Find input container
            input_container = terminal.findChild(QFrame, "InputContainer")
            if not input_container:
                self.logger.warning("Input container not found - command entry remains unaestheticized")
                return

            # Apply styling to container
            input_container.setStyleSheet(f"""
                QFrame#InputContainer {{
                    background-color: {Theme.get_color('BG_DARK')};
                    border-radius: 6px;
                    margin: 0px;
                    margin-top: 5px;
                }}
            """)

            # Style prompt label
            prompt_label = terminal.findChild(QLabel, "PromptLabel")
            if prompt_label:
                prompt_label.setStyleSheet(f"""
                    QLabel#PromptLabel {{
                        color: {Theme.get_color('SUCCESS')};
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-weight: bold;
                        font-size: 14px;
                        background-color: transparent;
                        padding-left: 10px;
                    }}
                """)

            # Style input field
            input_entry = terminal.findChild(QLineEdit, "InputEntry")
            if input_entry:
                input_entry.setStyleSheet(f"""
                    QLineEdit#InputEntry {{
                        background-color: transparent;
                        color: {Theme.get_color('SUCCESS')};
                        border: none;
                        font-size: 14px;
                        font-family: 'Consolas', 'Courier New', monospace;
                        padding: 8px 12px;
                        selection-background-color: {Theme.get_color('PRIMARY')};
                        selection-color: {Theme.get_color('TEXT_PRIMARY')};
                    }}
                """)

            self.logger.debug("Terminal input enhanced - command entry now aesthetically consistent")

        except Exception as e:
            self.logger.error(f"Failed to enhance terminal input: {str(e)}", exc_info=True)

    def _apply_delayed_fixes(self) -> None:
        """
        Apply fixes that need to be delayed until after initial rendering.

        Like a digital janitor sweeping up after the initial renovation,
        this method addresses styling issues that resist immediate application
        due to the peculiarities of Qt's style inheritance and timing.
        """
        try:
            self.logger.debug("Applying delayed fixes - addressing the stubborn styling issues")

            if not self.main_window:
                return

            # Get components
            components = self._get_ui_components()

            # Fix terminal output background - particularly stubborn in Qt
            if 'terminal' in components:
                terminal = components['terminal']
                output = terminal.findChild(QTextEdit, "TerminalOutput")
                if output:
                    # Force the background color using a stylesheet with !important
                    bg_color = Theme.get_color('BG_DARK')
                    output.setStyleSheet(f"""
                        QTextEdit#TerminalOutput {{
                            background-color: {bg_color} !important;
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border: none;
                            border-radius: 4px;
                            padding: 10px;
                        }}
                    """)

                    # Update the palette as well for stubborn widgets
                    palette = output.palette()
                    palette.setColor(output.backgroundRole(), QColor(bg_color))
                    output.setPalette(palette)

                    # Force update
                    output.style().unpolish(output)
                    output.style().polish(output)
                    output.update()

            self.logger.debug("Delayed fixes applied - digital spackle covering the styling gaps")

        except Exception as e:
            self.logger.error(f"Failed to apply delayed fixes: {str(e)}", exc_info=True)

    def _force_style_update(self) -> None:
        """
        Force style update on main window and all child widgets.

        Like telling every pixel to re-evaluate its life choices, this method
        ensures all styling changes are actually applied by forcing Qt to
        reprocess style sheets and update the visual appearance.
        """
        try:
            if not self.main_window:
                return

            # Unpolish/polish main window
            self.main_window.style().unpolish(self.main_window)
            self.main_window.style().polish(self.main_window)

            # Force repaint
            self.main_window.update()

            self.logger.debug("Style updates forced - digital aesthetics reluctantly reprocessed")

        except Exception as e:
            self.logger.error(f"Failed to force style update: {str(e)}", exc_info=True)

    def _create_moinsy_logo(self, size: int = 50) -> QPixmap:
        """
        Create a custom Moinsy logo as a QPixmap.

        Args:
            size: Size of the logo in pixels

        Returns:
            QPixmap containing the generated Moinsy logo

        Like a digital sigil forged from mathematics and code, this method
        crafts a visual symbol that represents an application's identity
        using primitive geometric shapes and color gradients.
        """
        try:
            # Create transparent pixmap
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Initialize painter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Get theme colors
            primary_color = QColor(Theme.get_color('PRIMARY'))
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

            self.logger.debug("Moinsy logo created - digital iconography birthed from void")
            return pixmap

        except Exception as e:
            self.logger.error(f"Failed to create Moinsy logo: {str(e)}", exc_info=True)
            # Return an empty pixmap if logo creation fails
            return QPixmap(size, size)

    def _adjust_color(self, color: str, amount: int) -> str:
        """
        Adjust color brightness by amount.

        Args:
            color: Hex color string
            amount: Amount to adjust brightness (positive or negative)

        Returns:
            Adjusted hex color string

        Like a digital alchemist transmuting colors, this method adjusts
        the brightness of a color value while contemplating whether any
        meaningful difference exists between #3A3A3A and #3B3B3B in the
        cosmic scale of existence.
        """
        try:
            # Remove # prefix if present
            hex_color = color.lstrip('#')

            # Convert hex to RGB
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

            # Adjust brightness with bounds checking
            adjusted = [max(0, min(255, x + amount)) for x in rgb]

            # Convert back to hex
            return f'#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}'

        except Exception as e:
            self.logger.error(f"Color adjustment error: {str(e)}", exc_info=True)
            return color  # Return original color on error


def enhance_main_window(main_window: QMainWindow) -> None:
    """
    Apply UI enhancements to the main window and its components.

    Args:
        main_window: The main application window to enhance

    Like a cosmetic procedure for a digital face, this function
    coordinates the enhancement of multiple UI components to create
    a cohesive visual experience that is simultaneously aesthetic
    and functional, or at least pretends to be.
    """
    logger = logging.getLogger(__name__)
    try:
        # Create enhancer
        enhancer = UIEnhancer(main_window, logger)

        # Apply enhancements
        enhancer.enhance_ui()

        logger.info("Main window enhancement complete - digital makeover successful")
    except Exception as e:
        logger.error(f"Failed to enhance main window: {str(e)}", exc_info=True)


def apply_theme_enhancements() -> None:
    """
    Apply enhancements to theme definitions without requiring a main window.

    Like improving the color palette before painting begins, this function
    fixes theme color definitions to address inconsistencies across different
    themes, ensuring a better starting point for UI rendering.
    """
    logger = logging.getLogger(__name__)
    try:
        # Create enhancer without main window
        enhancer = UIEnhancer(logger=logger)

        # Apply theme definition enhancements
        enhancer._enhance_theme_definitions()

        logger.info("Theme enhancements applied - color palettes optimized")
    except Exception as e:
        logger.error(f"Failed to apply theme enhancements: {str(e)}", exc_info=True)


def delayed_show_window(main_window: QMainWindow, delay_ms: int = 100) -> None:
    """
    Show the main window after a delay to prevent UI flash.

    Args:
        main_window: Main window to show
        delay_ms: Delay in milliseconds

    Like a theatrical curtain reveal after stage setup, this function
    delays the window visibility until UI enhancements are applied,
    preventing the jarring flash of un-styled components.
    """
    logger = logging.getLogger(__name__)
    try:
        # Create a timer
        timer = QTimer(main_window)
        timer.setSingleShot(True)
        timer.timeout.connect(main_window.show)

        # Start timer
        timer.start(delay_ms)

        logger.debug(f"Window show delayed by {delay_ms}ms - preventing the aesthetic flash of doom")
    except Exception as e:
        logger.error(f"Failed to setup delayed window show: {str(e)}", exc_info=True)
        # Show window anyway if delay setup fails
        main_window.show()


# Integration function for main.py
def setup_ui_enhancements_and_show(main_window: QMainWindow, use_splash: bool = False) -> None:
    """
    Set up UI enhancements and show the main window properly.

    Args:
        main_window: Main window to enhance and show
        use_splash: Whether to show a splash screen during enhancement

    This function is the main integration point for the UI enhancer,
    coordinating theme fixes, UI enhancements, and proper window display
    to prevent UI flashing during startup.
    """
    logger = logging.getLogger(__name__)
    try:
        # Apply theme enhancements first
        apply_theme_enhancements()

        # Handle splash screen if requested
        if use_splash:
            # Create splash screen
            pixmap = QPixmap(400, 300)
            pixmap.fill(QColor(Theme.get_color('BG_DARK')))
            splash = QSplashScreen(pixmap)
            splash.show()

            # Process events to ensure splash is visible
            QApplication.processEvents()

            # Enhance UI
            enhance_main_window(main_window)

            # Show window and close splash
            QTimer.singleShot(500, lambda: splash.close())
            QTimer.singleShot(500, lambda: main_window.show())
        else:
            # Apply enhancements first, then show window with delay
            enhance_main_window(main_window)
            delayed_show_window(main_window)

        logger.info("UI enhancements and window display configured successfully")
    except Exception as e:
        logger.error(f"Failed to setup UI enhancements: {str(e)}", exc_info=True)
        # Show window anyway if enhancement fails
        main_window.show()