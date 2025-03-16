"""Terminal component for displaying output and handling user input."""

import logging
from typing import Optional, Union, List, Dict, Any, Tuple, cast
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QLineEdit, QSizePolicy, QFrame,
    QScrollBar
)
from PyQt6.QtGui import QTextCursor, QFont, QColor, QPalette, QFontDatabase
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QEvent

from gui.styles.theme import Theme


class TerminalArea(QWidget):
    """Terminal component for displaying output and handling user input.

    This class provides a terminal-like interface for command input and output display,
    with support for text coloring, scrolling, and buffer management.

    Like a digital oracle inscribing prophecies onto silicon tablets,
    this terminal accumulates the fragments of our operational narrative.
    """

    # Signals
    theme_changed = pyqtSignal(str)  # Emitted when theme is applied

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize terminal UI components.

        Args:
            parent: Parent widget for containment hierarchy
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.buffer_size = 1000  # Default buffer size
        self.current_theme = "dark"  # Default theme

        # Set object name for stylesheet targeting
        self.setObjectName("TerminalArea")

        # Setup UI components
        self.setup_ui()

        # Apply initial styling
        self.apply_base_styling()

        self.logger.debug("Terminal initialized - digital oracle awaits commands")

    def setup_ui(self) -> None:
        """Initialize terminal UI components."""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            # Terminal header - title and controls
            self.setup_header(layout)

            # Terminal output area - scrollable text display
            self.setup_output_area(layout)

            # Input area - command input field
            self.setup_input_area(layout)

        except Exception as e:
            self.logger.exception(f"Error setting up terminal UI: {str(e)}")
            # Create minimal UI on failure
            err_layout = QVBoxLayout(self)
            err_label = QLabel("Terminal initialization failed")
            err_label.setStyleSheet("color: red;")
            err_layout.addWidget(err_label)
            self.logger.error("Using fallback terminal layout")

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup terminal header with title and controls.

        Args:
            layout: Parent layout to add the header to
        """
        try:
            # Header container frame
            header = QFrame()
            header.setObjectName("TerminalHeader")

            # Header layout
            self.header_layout = QHBoxLayout(header)
            self.header_layout.setContentsMargins(15, 15, 15, 0)
            self.header_layout.setSpacing(10)

            # Title
            title = QLabel("Terminal Output")
            title.setObjectName("TerminalTitle")
            self.header_layout.addWidget(title)

            # Add spacer to push buttons to the right
            self.header_layout.addStretch()

            # Clear button
            clear_button = QPushButton("Clear")
            clear_button.setObjectName("ClearButton")
            clear_button.setFixedSize(80, 30)
            clear_button.clicked.connect(self.clear_terminal)
            self.header_layout.addWidget(clear_button)

            layout.addWidget(header)
            self.logger.debug("Terminal header created - command center established")
        except Exception as e:
            self.logger.error(f"Failed to create terminal header: {str(e)}")
            # Add a simple label as fallback
            layout.addWidget(QLabel("Terminal"))

    def setup_output_area(self, layout: QVBoxLayout) -> None:
        """Setup main terminal output area.

        Args:
            layout: Parent layout to add the output area to
        """
        try:
            # Output text area
            self.output = QTextEdit()
            self.output.setObjectName("TerminalOutput")
            self.output.setReadOnly(True)

            # Make terminal expand vertically with the window
            self.output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            layout.addWidget(self.output)
            self.logger.debug("Terminal output area created - digital canvas prepared")
        except Exception as e:
            self.logger.error(f"Failed to create terminal output area: {str(e)}")
            # Add a simple text edit as fallback
            layout.addWidget(QTextEdit())

    def setup_input_area(self, layout: QVBoxLayout) -> None:
        """Setup user input area.

        Args:
            layout: Parent layout to add the input area to
        """
        try:
            # Input container for styling
            input_container = QFrame()
            input_container.setObjectName("InputContainer")

            # Input layout
            input_layout = QHBoxLayout(input_container)
            input_layout.setContentsMargins(0, 0, 0, 0)
            input_layout.setSpacing(0)

            # Command prompt symbol
            self.prompt_label = QLabel("$")
            self.prompt_label.setObjectName("PromptLabel")
            self.prompt_label.setFixedWidth(20)
            self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input_layout.addWidget(self.prompt_label)

            # Input field
            self.input_entry = QLineEdit()
            self.input_entry.setObjectName("InputEntry")
            self.input_entry.setPlaceholderText("Type here...")
            input_layout.addWidget(self.input_entry)

            layout.addWidget(input_container)
            self.logger.debug("Terminal input area created - command interface ready")
        except Exception as e:
            self.logger.error(f"Failed to create terminal input area: {str(e)}")
            # Add a simple line edit as fallback
            layout.addWidget(QLineEdit())

    def apply_theme(self, theme_id: str) -> None:
        """Apply theme to all terminal components.

        Args:
            theme_id: Theme identifier to apply
        """
        try:
            self.current_theme = theme_id

            # Apply base styling first
            self.apply_base_styling()

            # Apply specific component styling
            self.apply_header_styling()
            self.apply_output_styling()
            self.apply_input_styling()

            # Emit theme changed signal
            self.theme_changed.emit(theme_id)
            self.logger.debug(f"Applied theme '{theme_id}' to terminal area")
        except Exception as e:
            self.logger.error(f"Error applying theme to terminal: {str(e)}")

    def apply_base_styling(self) -> None:
        """Apply base styling to the terminal."""
        try:
            # Set container styling
            self.setStyleSheet(f"""
                QWidget#TerminalArea {{
                    background-color: {Theme.get_color('BG_DARK')};
                }}
            """)
            self.logger.debug("Applied base styling to terminal area")
        except Exception as e:
            self.logger.error(f"Error applying base styling: {str(e)}")

    def apply_header_styling(self) -> None:
        """Apply styling to the terminal header."""
        try:
            # Find header components
            header = self.findChild(QFrame, "TerminalHeader")
            title = self.findChild(QLabel, "TerminalTitle")
            clear_button = self.findChild(QPushButton, "ClearButton")

            # Style header
            if header:
                header.setStyleSheet(f"""
                    QFrame#TerminalHeader {{
                        background-color: transparent;
                        border: none;
                    }}
                """)

            # Style title
            if title:
                title.setStyleSheet(f"""
                    QLabel#TerminalTitle {{
                        color: {Theme.get_color('TEXT_SECONDARY')};
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)

            # Style clear button
            if clear_button:
                clear_button.setStyleSheet(f"""
                    QPushButton#ClearButton {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: normal;
                        color: {Theme.get_color('TEXT_PRIMARY')};
                    }}
                    QPushButton#ClearButton:hover {{
                        background-color: {Theme.get_color('BG_LIGHT')};
                    }}
                """)

            self.logger.debug("Applied header styling")
        except Exception as e:
            self.logger.error(f"Error applying header styling: {str(e)}")

    def apply_output_styling(self) -> None:
        """Apply styling to the terminal output area."""
        try:
            # Get the font to use
            try:
                font = Theme.get_font('MONO')
            except (AttributeError, KeyError):
                # Fallback to default monospace font
                font = QFont('Consolas', 13)
                # Try to find a good monospace font on the system
                for family in ['JetBrains Mono', 'Consolas', 'Courier New', 'Courier', 'Monospace']:
                    if family in QFontDatabase.families():
                        font = QFont(family, 13)
                        break

            # Apply font to output area
            self.output.setFont(font)

            # Get appropriate background color based on theme
            theme_id = Theme.get_current_theme()
            if theme_id == Theme.THEME_LIGHT:
                # Light theme uses a light gray background that's darker than sidebar buttons
                bg_color = "#E0E0E0"  # A medium-light gray, darker than typical light theme buttons
            elif theme_id == Theme.THEME_HIGH_CONTRAST:
                # High contrast theme uses a black background
                bg_color = "#000000"
            else:
                # Dark theme (default) uses a dark background that's darker than sidebar but not pure black
                # Sidebar is typically BG_MEDIUM, so we need something between that and black
                bg_color = "#323234"  # Darker than BG_DARK but not pure black

            # Style the output area with theme-appropriate background
            self.output.setStyleSheet(f"""
                QTextEdit#TerminalOutput {{
                    background-color: {bg_color};
                    color: {Theme.get_color('TEXT_PRIMARY')};
                    border: none;
                    border-radius: 12px;
                    padding: 15px;
                    selection-background-color: {Theme.get_color('PRIMARY')};
                    selection-color: {Theme.get_color('TEXT_PRIMARY')};
                    line-height: 1.5;
                }}
            """)

            # Style scrollbars
            self._style_scrollbars(self.output.verticalScrollBar())

            self.logger.debug("Applied output styling - the digital canvas reconfigured")
        except Exception as e:
            self.logger.error(f"Error applying output styling: {str(e)}")

    def apply_input_styling(self) -> None:
        """Apply styling to the terminal input area."""
        try:
            # Get components
            input_container = self.findChild(QFrame, "InputContainer")

            # Style input container
            if input_container:
                input_container.setStyleSheet(f"""
                    QFrame#InputContainer {{
                        background-color: {Theme.get_color('BG_MEDIUM')};
                        border-radius: 8px;
                    }}
                """)

            # Style prompt
            if hasattr(self, 'prompt_label'):
                self.prompt_label.setStyleSheet(f"""
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
            if hasattr(self, 'input_entry'):
                # Get the font to use
                try:
                    font = Theme.get_font('MONO')
                except (AttributeError, KeyError):
                    # Fallback to default monospace font
                    font = QFont('Consolas', 13)

                # Apply font
                self.input_entry.setFont(font)

                # Apply styling
                self.input_entry.setStyleSheet(f"""
                    QLineEdit#InputEntry {{
                        background-color: transparent;
                        color: {Theme.get_color('SUCCESS')};
                        border: none;
                        font-size: 14px;
                        padding: 8px 12px;
                        selection-background-color: {Theme.get_color('PRIMARY')};
                        selection-color: {Theme.get_color('TEXT_PRIMARY')};
                    }}
                """)

            self.logger.debug("Applied input styling")
        except Exception as e:
            self.logger.error(f"Error applying input styling: {str(e)}")

    def _style_scrollbars(self, scrollbar: QScrollBar) -> None:
        """Apply styling to scrollbars.

        Args:
            scrollbar: The scrollbar to style
        """
        try:
            scrollbar.setStyleSheet(f"""
                QScrollBar:vertical {{
                    border: none;
                    background: {Theme.get_color('BG_MEDIUM')};
                    width: 8px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background: {Theme.get_color('BG_LIGHT')};
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
            """)
        except Exception as e:
            self.logger.error(f"Error styling scrollbar: {str(e)}")

    def append_output(self, message: str, color: str = "white") -> None:
        """Add text to terminal output with optional color.

        Args:
            message: Message to display
            color: Text color (name or hex value)

        Like a digital scribe documenting an ongoing narrative,
        this method appends new text to our terminal's history.
        """
        try:
            # Validate color to prevent HTML injection
            safe_color = self._sanitize_color(color)

            # Check buffer size limits
            if self.output.document().blockCount() > self.buffer_size:
                self._trim_buffer()

            # Append the text with color formatting
            self.output.append(f'<span style="color: {safe_color};">{message}</span>')

            # Auto-scroll to bottom
            self.output.verticalScrollBar().setValue(
                self.output.verticalScrollBar().maximum()
            )
        except Exception as e:
            self.logger.error(f"Error appending output: {str(e)}")
            # Try a basic append without styling as fallback
            try:
                self.output.append(message)
            except:
                pass

    def _sanitize_color(self, color: str) -> str:
        """Sanitize color value to prevent HTML injection.

        Args:
            color: Color string to sanitize

        Returns:
            Safe color string
        """
        # Check if it's a hex color
        if color.startswith('#'):
            # Validate hex format
            if len(color) in [4, 7] and all(c in '0123456789ABCDEFabcdef#' for c in color):
                return color

        # Check if it's a named color
        safe_colors = {
            'white', 'black', 'red', 'green', 'blue', 'yellow', 'orange',
            'purple', 'pink', 'brown', 'gray', 'cyan', 'magenta', 'lime',
            'olive', 'navy', 'teal', 'aqua', 'silver', 'gold'
        }

        if color.lower() in safe_colors:
            return color

        # If not safe, default to white
        return "white"

    def _trim_buffer(self) -> None:
        """Trim the terminal buffer to maintain the specified maximum size.

        Like a memory management system reclaiming space, this method
        ensures our terminal doesn't grow too large by removing old entries.
        """
        try:
            cursor = QTextCursor(self.output.document())
            cursor.movePosition(QTextCursor.MoveOperation.Start)

            # Remove lines until we're under the buffer size limit
            while self.output.document().blockCount() > self.buffer_size:
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # Delete the newline

            self.logger.debug(f"Trimmed terminal buffer to {self.buffer_size} lines")
        except Exception as e:
            self.logger.error(f"Error trimming buffer: {str(e)}")

    def clear_terminal(self) -> None:
        """Clear terminal output.

        Like hitting the reset button on a digital slate,
        this method wipes away all accumulated output.
        """
        try:
            self.output.clear()
            self.logger.debug("Terminal cleared - digital slate wiped clean")
        except Exception as e:
            self.logger.error(f"Error clearing terminal: {str(e)}")

    def set_font_size(self, size: int) -> None:
        """Change the terminal font size.

        Args:
            size: New font size in points

        Like adjusting one's reading glasses, this method resizes
        the text to accommodate different visual preferences.
        """
        try:
            # Validate size range
            if not isinstance(size, int) or size < 8 or size > 24:
                self.logger.warning(f"Invalid font size requested: {size}")
                return

            # Set output font size
            output_font = self.output.font()
            output_font.setPointSize(size)
            self.output.setFont(output_font)

            # Set input field font size
            input_font = self.input_entry.font()
            input_font.setPointSize(size)
            self.input_entry.setFont(input_font)

            self.logger.debug(f"Terminal font size set to {size}")

            # Update styling to match new font size
            self.apply_output_styling()
            self.apply_input_styling()

        except Exception as e:
            self.logger.error(f"Error setting font size: {str(e)}")

    def set_buffer_size(self, size: int) -> None:
        """Set the maximum number of lines to keep in terminal buffer.

        Args:
            size: Maximum number of lines

        Like setting the capacity of a digital scroll,
        this method defines how much history our terminal will remember.
        """
        try:
            # Validate buffer size
            if not isinstance(size, int) or size < 100:
                self.logger.warning(f"Invalid buffer size requested: {size}")
                return

            self.buffer_size = size
            self.logger.debug(f"Terminal buffer size set to {size} lines")

            # If current content exceeds buffer size, trim it
            if self.output.document().blockCount() > self.buffer_size:
                self._trim_buffer()

        except Exception as e:
            self.logger.error(f"Error setting buffer size: {str(e)}")