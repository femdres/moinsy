"""Central theme management module for consistent application styling."""

import logging
from typing import Dict, Any, Optional, List, Tuple, Union, cast
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QApplication


class Theme:
    """Central theme management for consistent application styling.

    This class provides color palettes, fonts, and styles for the application UI,
    supporting multiple themes including dark, light, and high contrast modes.

    Like a digital fashion designer dictating the aesthetic rules of our interface,
    this class defines how our application presents itself to the world.
    """

    # Theme variants
    THEME_DARK = "dark"
    THEME_LIGHT = "light"
    THEME_HIGH_CONTRAST = "high_contrast"
    THEME_SYSTEM = "system"  # Detect from system (not fully implemented)

    # Color Palettes for different themes
    COLORS = {
        THEME_DARK: {
            # Primary colors
            'PRIMARY': '#4CAF50',  # Green
            'SECONDARY': '#2196F3',  # Blue
            'TERTIARY': '#9C27B0',  # Purple

            # Backgrounds
            'BG_DARK': '#1a1b1e',  # Main background
            'BG_MEDIUM': '#2d2e32',  # Card background
            'BG_LIGHT': '#3d3e42',  # Active/Hover states

            # Text colors
            'TEXT_PRIMARY': '#FFFFFF',
            'TEXT_SECONDARY': '#888888',

            # Status colors
            'SUCCESS': '#4CAF50',
            'ERROR': '#dc2626',
            'WARNING': '#FFC107',

            # Control colors
            'CONTROL_BG': '#4b5563',
            'CONTROL_HOVER': '#374151'
        },
        THEME_LIGHT: {
            # Primary colors
            'PRIMARY': '#388E3C',  # Green
            'SECONDARY': '#1976D2',  # Blue
            'TERTIARY': '#7B1FA2',  # Purple

            # Backgrounds
            'BG_DARK': '#FFFFFF',  # Main background
            'BG_MEDIUM': '#F5F5F5',  # Card background
            'BG_LIGHT': '#E0E0E0',  # Active/Hover states

            # Text colors
            'TEXT_PRIMARY': '#212121',
            'TEXT_SECONDARY': '#757575',

            # Status colors
            'SUCCESS': '#4CAF50',
            'ERROR': '#F44336',
            'WARNING': '#FF9800',

            # Control colors
            'CONTROL_BG': '#BDBDBD',
            'CONTROL_HOVER': '#9E9E9E'
        },
        THEME_HIGH_CONTRAST: {
            # Primary colors
            'PRIMARY': '#00FF00',  # Bright Green
            'SECONDARY': '#FFFF00',  # Yellow
            'TERTIARY': '#FF00FF',  # Magenta

            # Backgrounds
            'BG_DARK': '#000000',  # Black background
            'BG_MEDIUM': '#0A0A0A',  # Near black
            'BG_LIGHT': '#202020',  # Dark gray

            # Text colors
            'TEXT_PRIMARY': '#FFFFFF',  # White text
            'TEXT_SECONDARY': '#CCCCCC',  # Light gray

            # Status colors
            'SUCCESS': '#00FF00',  # Bright green
            'ERROR': '#FF0000',  # Bright red
            'WARNING': '#FFFF00',  # Yellow

            # Control colors
            'CONTROL_BG': '#303030',  # Medium gray
            'CONTROL_HOVER': '#505050'  # Lighter gray
        }
    }

    # Font Configuration - shared across themes
    FONTS = {
        'LOGO': ('JetBrains Mono', 24, 'Bold'),
        'TITLE': ('Segoe UI', 16, 'Bold'),
        'SUBTITLE': ('Segoe UI', 14, 'Normal'),
        'BODY': ('Segoe UI', 13, 'Normal'),
        'MONO': ('JetBrains Mono', 13, 'Normal')
    }

    # Current active theme
    _current_theme = THEME_DARK
    _logger = logging.getLogger(__name__)

    @classmethod
    def apply_base_styles(cls, app: QApplication, theme_name: Optional[str] = None) -> None:
        """Apply base application styling.

        Args:
            app: The QApplication instance
            theme_name: Optional theme name to apply (dark, light, high_contrast, system)

        Like applying makeup to a digital face, this method gives our
        application its base aesthetic appearance.
        """
        # Set theme
        if theme_name:
            cls.set_theme(theme_name)

        # Set fusion style for consistent cross-platform look
        app.setStyle("Fusion")

        # Configure palette based on theme
        palette = cls.create_palette()
        app.setPalette(palette)

        # Apply global stylesheet
        app.setStyleSheet(cls.get_global_stylesheet())

        cls._logger.info(f"Applied {cls._current_theme} theme to application")

    @classmethod
    def set_theme(cls, theme_name: str) -> bool:
        """Set the active theme.

        Args:
            theme_name: Theme name (dark, light, high_contrast, system)

        Returns:
            Boolean indicating if theme was successfully set

        Like changing outfits for our digital persona, this method
        switches the application's aesthetic identity.
        """
        # Handle system theme - detect from system
        if theme_name == cls.THEME_SYSTEM:
            # For now, just default to dark theme
            # In a real implementation, would detect system theme
            effective_theme = cls.THEME_DARK
            cls._logger.debug("System theme requested, defaulting to dark theme")
        else:
            effective_theme = theme_name

        # Validate theme name
        if effective_theme not in [cls.THEME_DARK, cls.THEME_LIGHT, cls.THEME_HIGH_CONTRAST]:
            cls._logger.warning(f"Invalid theme name: {theme_name}, using dark theme")
            effective_theme = cls.THEME_DARK

        cls._current_theme = effective_theme
        cls._logger.debug(f"Theme set to {cls._current_theme}")
        return True

    @classmethod
    def create_palette(cls) -> QPalette:
        """Create the color palette for the current theme.

        Returns:
            QPalette configured for the current theme

        Like mixing a precise color palette for a digital artist,
        this method prepares the colors our interface will use.
        """
        palette = QPalette()
        colors = cls.COLORS.get(cls._current_theme, cls.COLORS[cls.THEME_DARK])

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

        # Handle dark/light specific adjustments
        if cls._current_theme == cls.THEME_DARK:
            palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['TEXT_PRIMARY']))
        else:
            palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['BG_DARK']))

        return palette

    @classmethod
    def get_global_stylesheet(cls) -> str:
        """Get global application stylesheet for the current theme.

        Returns:
            Stylesheet as a string

        Like drafting a comprehensive fashion guide, this method creates
        style rules that apply throughout our application.
        """
        colors = cls.COLORS.get(cls._current_theme, cls.COLORS[cls.THEME_DARK])

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
        """Get styling for card elements.

        Returns:
            Card styling as a string

        Like designing a template for digital information cards,
        this method creates a consistent look for content containers.
        """
        colors = cls.COLORS.get(cls._current_theme, cls.COLORS[cls.THEME_DARK])

        return f"""
            background-color: {colors['BG_MEDIUM']};
            border-radius: 8px;
            padding: 12px;
            color: {colors['TEXT_PRIMARY']};
        """

    @classmethod
    def get_button_style(cls, color: str, hover_color: Optional[str] = None) -> str:
        """Get styling for buttons with specified colors.

        Args:
            color: Base button color
            hover_color: Optional hover state color

        Returns:
            Button styling as a string

        Like creating a blueprint for interactive elements,
        this method defines how buttons respond to user interaction.
        """
        colors = cls.COLORS.get(cls._current_theme, cls.COLORS[cls.THEME_DARK])

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
        """Get a specific color from the current theme.

        Args:
            color_key: Color key name

        Returns:
            Color value as a hex string

        Like retrieving a specific pigment from our digital palette,
        this method gives access to individual colors in our theme.
        """
        colors = cls.COLORS.get(cls._current_theme, cls.COLORS[cls.THEME_DARK])
        return colors.get(color_key, colors['PRIMARY'])

    @classmethod
    def get_font(cls, font_key: str) -> QFont:
        """Get a QFont object for the specified font key.

        Args:
            font_key: Font key name from the FONTS dictionary

        Returns:
            QFont object configured for the requested font

        Raises:
            ValueError: If the font key is not valid

        Like selecting a specific typeface from our digital library,
        this method provides fonts for different textual purposes.
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
        """Adjust color brightness by amount.

        Args:
            color: Hex color string
            amount: Amount to adjust brightness (positive or negative)

        Returns:
            Adjusted hex color string

        Like a digital alchemist transmuting colors, this method
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
    def get_current_theme(cls) -> str:
        """Get the name of the current active theme.

        Returns:
            Current theme identifier string

        Like asking our digital wardrobe what outfit it's currently wearing,
        this method reveals which theme is currently active.
        """
        return cls._current_theme

    @classmethod
    def get_current_theme(cls) -> str:
        """Get the name of the current active theme.
        
        Returns:
            Current theme identifier string
            
        Like asking our digital wardrobe what outfit it's currently wearing,
        this method reveals which theme is currently active.
        """
        return cls._current_theme
        
    @classmethod
    def load_theme_from_file(cls, file_path: str) -> Dict[str, Any]:
        """Load theme data from a JSON file.
        
        Args:
            file_path: Path to the theme JSON file
            
        Returns:
            Dictionary containing theme data
            
        Raises:
            FileNotFoundError: If theme file doesn't exist
            json.JSONDecodeError: If theme file has invalid JSON format
            
        Like an archaeologist excavating digital artifacts, this method
        retrieves theme definitions encoded in ancient JSON hieroglyphics.
        """
        try:
            if not os.path.exists(file_path):
                cls._logger.error(f"Theme file not found: {file_path}")
                raise FileNotFoundError(f"Theme file not found: {file_path}")
                
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
                
            # Validate basic structure
            if not isinstance(theme_data, dict):
                raise ValueError("Theme file must contain a JSON object")
                
            if 'colors' not in theme_data:
                raise ValueError("Theme must contain 'colors' definition")
                
            cls._logger.debug(f"Successfully loaded theme from {file_path}")
            return theme_data
            
        except json.JSONDecodeError as e:
            cls._logger.error(f"Invalid JSON in theme file: {str(e)}")
            raise
        except Exception as e:
            cls._logger.error(f"Error loading theme file: {str(e)}")
            raise
            
    @classmethod
    def save_theme_to_file(cls, theme_data: Dict[str, Any], file_path: str) -> bool:
        """Save theme data to a JSON file.
        
        Args:
            theme_data: Theme data dictionary
            file_path: Path where theme file should be saved
            
        Returns:
            True if successful, False otherwise
            
        Like a digital scribe preserving our aesthetic preferences for posterity,
        this method encodes theme definitions into JSON format for future retrieval.
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write theme data to file with pretty formatting
            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=4)
                
            cls._logger.debug(f"Successfully saved theme to {file_path}")
            return True
            
        except Exception as e:
            cls._logger.error(f"Error saving theme to file: {str(e)}")
            return False
            
    @classmethod
    def register_font(cls, font_path: str) -> bool:
        """Register a custom font for use in the application.
        
        Args:
            font_path: Path to the font file
            
        Returns:
            True if successful, False otherwise
            
        Like introducing a new language to our digital typography system,
        this method makes custom fonts available for textual expression.
        """
        try:
            if not os.path.exists(font_path):
                cls._logger.error(f"Font file not found: {font_path}")
                return False
                
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                cls._logger.error(f"Failed to load font: {font_path}")
                return False
                
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            cls._logger.debug(f"Successfully registered font: {font_family}")
            return True
            
        except Exception as e:
            cls._logger.error(f"Error registering font: {str(e)}")
            return False
            
    @classmethod
    def update_theme_colors(cls, colors: Dict[str, str]) -> None:
        """Update colors in the current theme.
        
        Args:
            colors: Dictionary of color keys and hex values to update
            
        Like a painter adjusting their palette mid-creation, this method
        allows for modification of the theme's color scheme at runtime.
        """
        try:
            current_colors = cls.COLORS.get(cls._current_theme, cls.COLORS[cls.THEME_DARK])
            
            # Update specified colors
            for key, value in colors.items():
                if key in current_colors:
                    current_colors[key] = value
                    
            # Update the theme colors
            cls.COLORS[cls._current_theme] = current_colors
            cls._logger.debug(f"Updated theme colors for {cls._current_theme}")
            
        except Exception as e:
            cls._logger.error(f"Error updating theme colors: {str(e)}")
            
    @classmethod
    def create_theme_variant(cls, base_theme: str, name: str, color_adjustments: Dict[str, int]) -> str:
        """Create a variant of an existing theme by adjusting color brightness.
        
        Args:
            base_theme: Base theme to use as starting point
            name: Name for the new theme variant
            color_adjustments: Dictionary mapping color keys to brightness adjustments
            
        Returns:
            Name of the created theme variant
            
        Like a digital geneticist creating variations on an aesthetic genome,
        this method produces theme mutations with adjusted color brightness.
        """
        try:
            if base_theme not in cls.COLORS:
                cls._logger.error(f"Base theme not found: {base_theme}")
                return cls.THEME_DARK
                
            # Create a copy of the base theme colors
            new_colors = cls.COLORS[base_theme].copy()
            
            # Apply adjustments
            for key, adjustment in color_adjustments.items():
                if key in new_colors:
                    original = new_colors[key]
                    new_colors[key] = cls.adjust_color(original, adjustment)
                    
            # Add the new theme
            theme_id = f"{name.lower().replace(' ', '_')}"
            cls.COLORS[theme_id] = new_colors
            
            cls._logger.debug(f"Created theme variant: {theme_id} based on {base_theme}")
            return theme_id
            
        except Exception as e:
            cls._logger.error(f"Error creating theme variant: {str(e)}")
            return cls.THEME_DARK  # Return default theme as fallback

    _use_colored_buttons = True  # Default to true

    @classmethod
    def set_use_colored_buttons(cls, value: bool) -> None:
        """Set whether to use colored buttons.

        Args:
            value: True to use colored buttons, False for standard styling

        Like a wardrobe curator deciding between vibrant attire and formal uniforms,
        this method determines the aesthetic diversity of our interactive elements.
        """
        if cls._use_colored_buttons != value:
            cls._use_colored_buttons = value
            cls._logger.debug(
                f"Set use_colored_buttons to {value} - our buttons {'embrace color' if value else 'adopt uniformity'}")

    @classmethod
    def get_class(cls) -> 'Theme':
        """Get the class itself, for accessing class variables.

        Returns:
            The Theme class

        Like a mirror that reflects itself, this method returns the very essence
        of our aesthetic system, enabling introspection and self-reference.
        """
        return cls

    @classmethod
    def get_button_style(cls, color: str, hover_color: Optional[str] = None) -> str:
        """Get styling for buttons with specified colors.

        Args:
            color: Base button color
            hover_color: Optional hover state color

        Returns:
            Button styling as a string

        Like creating a blueprint for interactive elements,
        this method defines how buttons respond to user interaction.
        """
        colors = cls.COLORS.get(cls._current_theme, cls.COLORS[cls.THEME_DARK])

        # Check if colored buttons are enabled
        if not cls._use_colored_buttons:
            # Use standard button styling instead of colored
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