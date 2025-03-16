#!/usr/bin/env python3
"""
Theme integration module for consistent application styling.

This module provides the infrastructure for applying themes consistently across
all application components, maintaining visual coherence during theme changes.

Like the nervous system of our digital organism, this module coordinates the 
aesthetic responses of all components to thematic stimuli.
"""

import logging
from enum import Enum, auto
from typing import Dict, Any, Optional, Union, List, Type, TypeVar, cast, Protocol
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QDialog, QApplication, QFrame, QPushButton, 
    QLabel, QLineEdit, QTextEdit, QProgressBar, QComboBox, QCheckBox,
    QTabWidget, QListWidget, QListView, QTreeView, QTableView, QScrollArea
)
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QObject, pyqtSignal

from managers.theme_manager import ThemeManager
from gui.styles.theme import Theme


# Type variable for component types
T = TypeVar('T', bound=QWidget)


class ComponentType(Enum):
    """Classification of UI component types for targeted styling."""
    WINDOW = auto()
    DIALOG = auto()
    BUTTON = auto()
    INPUT = auto()
    DISPLAY = auto()
    CONTAINER = auto()
    PROGRESS = auto()
    VIEW = auto()
    CUSTOM = auto()


class ThemeAware(Protocol):
    """Protocol for components that can have themes applied."""
    def apply_theme(self, theme_id: str) -> None:
        """Apply the specified theme to this component."""
        ...


class ThemeIntegrator:
    """
    Central coordinator for theme application across the application.
    
    This class manages the application of themes to all registered components,
    ensuring visual consistency throughout the application during theme changes.
    
    Like a symphony conductor coordinating musicians, this class ensures
    all UI elements play in thematic harmony.
    """
    
    def __init__(self, main_window: QMainWindow, theme_manager: ThemeManager):
        """
        Initialize the theme integrator.
        
        Args:
            main_window: The application's main window
            theme_manager: Manager for theme loading and access
        """
        self.logger = logging.getLogger(__name__)
        self.main_window = main_window
        self.theme_manager = theme_manager
        self.components: Dict[ComponentType, List[QWidget]] = {
            comp_type: [] for comp_type in ComponentType
        }
        
        # Register core application components
        self._register_core_components()
        self.logger.debug("Theme integrator initialized with core components")
    
    def _register_core_components(self) -> None:
        """Register the core application components for theme application."""
        try:
            # Register main window
            self.register_component(self.main_window, ComponentType.WINDOW)
            
            # Register direct child components if available
            if hasattr(self.main_window, 'sidebar'):
                self.register_component(self.main_window.sidebar, ComponentType.CONTAINER)
            
            if hasattr(self.main_window, 'terminal'):
                self.register_component(self.main_window.terminal, ComponentType.CUSTOM)
                
            self.logger.debug("Core components registered for theme integration")
        except Exception as e:
            self.logger.error(f"Error registering core components: {str(e)}", exc_info=True)
    
    def register_component(self, component: QWidget, component_type: ComponentType) -> None:
        """
        Register a component for theme application.
        
        Args:
            component: UI component to register
            component_type: Type classification of the component
        """
        if component not in self.components[component_type]:
            self.components[component_type].append(component)
            self.logger.debug(f"Registered {component.__class__.__name__} as {component_type.name}")
    
    def unregister_component(self, component: QWidget, component_type: Optional[ComponentType] = None) -> None:
        """
        Unregister a component from theme application.
        
        Args:
            component: UI component to unregister
            component_type: Optional type classification to check
        """
        if component_type:
            if component in self.components[component_type]:
                self.components[component_type].remove(component)
                self.logger.debug(f"Unregistered {component.__class__.__name__} from {component_type.name}")
        else:
            # Search all component types
            for comp_type, components in self.components.items():
                if component in components:
                    components.remove(component)
                    self.logger.debug(f"Unregistered {component.__class__.__name__} from {comp_type.name}")
    
    def apply_theme(self, theme_id: str) -> None:
        """
        Apply a theme to all registered components.
        
        Args:
            theme_id: Identifier of the theme to apply
        """
        try:
            self.logger.info(f"Applying theme '{theme_id}' to all components")
            
            # Load theme data
            theme_data = self.theme_manager.load_theme(theme_id)
            if not theme_data:
                self.logger.error(f"Failed to load theme: {theme_id}")
                return
            
            # Apply to Theme class for global access
            Theme.COLORS[Theme.THEME_DARK] = theme_data.get("colors", {})
            Theme.set_theme(Theme.THEME_DARK)
            
            # Apply fonts if present
            if "fonts" in theme_data:
                Theme.FONTS = theme_data["fonts"]
            
            # Apply to application
            app = QApplication.instance()
            if app:
                Theme.apply_base_styles(app)
                self.logger.debug("Applied theme to application instance")
            
            # Apply to components by type
            self._apply_to_windows(theme_id)
            self._apply_to_dialogs(theme_id)
            self._apply_to_buttons(theme_id)
            self._apply_to_inputs(theme_id)
            self._apply_to_displays(theme_id)
            self._apply_to_containers(theme_id)
            self._apply_to_progress_indicators(theme_id)
            self._apply_to_views(theme_id)
            self._apply_to_custom_components(theme_id)
            
            self.logger.info(f"Theme '{theme_id}' applied successfully to all components")
            
        except Exception as e:
            self.logger.error(f"Error applying theme '{theme_id}': {str(e)}", exc_info=True)
    
    def _apply_to_windows(self, theme_id: str) -> None:
        """Apply theme to window components."""
        try:
            for window in self.components[ComponentType.WINDOW]:
                if isinstance(window, ThemeAware):
                    window.apply_theme(theme_id)
                else:
                    # Default window styling
                    window.setStyleSheet(f"""
                        QMainWindow {{
                            background-color: {Theme.get_color('BG_DARK')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                    """)
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.WINDOW])} windows")
        except Exception as e:
            self.logger.error(f"Error applying theme to windows: {str(e)}")
    
    def _apply_to_dialogs(self, theme_id: str) -> None:
        """Apply theme to dialog components."""
        try:
            for dialog in self.components[ComponentType.DIALOG]:
                if isinstance(dialog, ThemeAware):
                    dialog.apply_theme(theme_id)
                else:
                    # Default dialog styling
                    dialog.setStyleSheet(f"""
                        QDialog {{
                            background-color: {Theme.get_color('BG_DARK')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                    """)
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.DIALOG])} dialogs")
        except Exception as e:
            self.logger.error(f"Error applying theme to dialogs: {str(e)}")
    
    def _apply_to_buttons(self, theme_id: str) -> None:
        """Apply theme to button components."""
        try:
            for button in self.components[ComponentType.BUTTON]:
                if isinstance(button, QPushButton):
                    # Check for contextual buttons through object name
                    if "primary" in button.objectName().lower():
                        button.setStyleSheet(Theme.get_button_style(Theme.get_color('PRIMARY')))
                    elif "danger" in button.objectName().lower() or "delete" in button.objectName().lower():
                        button.setStyleSheet(Theme.get_button_style(Theme.get_color('ERROR')))
                    elif "warning" in button.objectName().lower():
                        button.setStyleSheet(Theme.get_button_style(Theme.get_color('WARNING')))
                    elif "success" in button.objectName().lower():
                        button.setStyleSheet(Theme.get_button_style(Theme.get_color('SUCCESS')))
                    else:
                        # Default button styling
                        button.setStyleSheet(Theme.get_button_style(Theme.get_color('CONTROL_BG')))
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.BUTTON])} buttons")
        except Exception as e:
            self.logger.error(f"Error applying theme to buttons: {str(e)}")
    
    def _apply_to_inputs(self, theme_id: str) -> None:
        """Apply theme to input components."""
        try:
            for input_widget in self.components[ComponentType.INPUT]:
                if isinstance(input_widget, QLineEdit):
                    input_widget.setStyleSheet(f"""
                        QLineEdit {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border: 2px solid {Theme.get_color('BG_LIGHT')};
                            border-radius: 4px;
                            padding: 4px 8px;
                        }}
                        QLineEdit:focus {{
                            border-color: {Theme.get_color('PRIMARY')};
                        }}
                    """)
                elif isinstance(input_widget, QTextEdit):
                    input_widget.setStyleSheet(f"""
                        QTextEdit {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border: 1px solid {Theme.get_color('BG_LIGHT')};
                            border-radius: 4px;
                            padding: 4px;
                        }}
                    """)
                elif isinstance(input_widget, QComboBox):
                    input_widget.setStyleSheet(f"""
                        QComboBox {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border: 1px solid {Theme.get_color('BG_LIGHT')};
                            border-radius: 4px;
                            padding: 4px 8px;
                        }}
                        QComboBox::drop-down {{
                            border: none;
                            width: 20px;
                        }}
                        QComboBox QAbstractItemView {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            selection-background-color: {Theme.get_color('PRIMARY')};
                        }}
                    """)
                elif isinstance(input_widget, QCheckBox):
                    input_widget.setStyleSheet(f"""
                        QCheckBox {{
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                        QCheckBox::indicator {{
                            width: 16px;
                            height: 16px;
                            border-radius: 3px;
                            border: 1px solid {Theme.get_color('TEXT_SECONDARY')};
                        }}
                        QCheckBox::indicator:checked {{
                            background-color: {Theme.get_color('PRIMARY')};
                            border: 1px solid {Theme.get_color('PRIMARY')};
                        }}
                    """)
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.INPUT])} input widgets")
        except Exception as e:
            self.logger.error(f"Error applying theme to inputs: {str(e)}")
    
    def _apply_to_displays(self, theme_id: str) -> None:
        """Apply theme to display components."""
        try:
            for display in self.components[ComponentType.DISPLAY]:
                if isinstance(display, QLabel):
                    # Title labels have larger font
                    if "title" in display.objectName().lower():
                        display.setFont(Theme.get_font('TITLE'))
                        display.setStyleSheet(f"color: {Theme.get_color('PRIMARY')};")
                    # Subtitle labels
                    elif "subtitle" in display.objectName().lower():
                        display.setFont(Theme.get_font('SUBTITLE'))
                        display.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
                    # Default labels
                    else:
                        display.setStyleSheet(f"color: {Theme.get_color('TEXT_PRIMARY')};")
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.DISPLAY])} display widgets")
        except Exception as e:
            self.logger.error(f"Error applying theme to displays: {str(e)}")
    
    def _apply_to_containers(self, theme_id: str) -> None:
        """Apply theme to container components."""
        try:
            for container in self.components[ComponentType.CONTAINER]:
                if isinstance(container, QFrame):
                    # Cards (elevated containers)
                    if "card" in container.objectName().lower():
                        container.setStyleSheet(Theme.get_card_style())
                    # Standard frames
                    else:
                        container.setStyleSheet(f"""
                            QFrame {{
                                background-color: {Theme.get_color('BG_MEDIUM')};
                                border-radius: 8px;
                            }}
                        """)
                elif isinstance(container, QTabWidget):
                    container.setStyleSheet(f"""
                        QTabWidget::pane {{
                            border: 1px solid {Theme.get_color('BG_LIGHT')};
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            border-radius: 4px;
                        }}
                        QTabBar::tab {{
                            background-color: {Theme.get_color('BG_LIGHT')};
                            color: {Theme.get_color('TEXT_SECONDARY')};
                            border-top-left-radius: 4px;
                            border-top-right-radius: 4px;
                            padding: 6px 12px;
                            margin-right: 2px;
                        }}
                        QTabBar::tab:selected {{
                            background-color: {Theme.get_color('PRIMARY')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                        QTabBar::tab:hover:!selected {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                    """)
                elif isinstance(container, QScrollArea):
                    container.setStyleSheet(f"""
                        QScrollArea {{
                            background-color: transparent;
                            border: none;
                        }}
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
                        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                            height: 0px;
                        }}
                    """)
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.CONTAINER])} container widgets")
        except Exception as e:
            self.logger.error(f"Error applying theme to containers: {str(e)}")
    
    def _apply_to_progress_indicators(self, theme_id: str) -> None:
        """Apply theme to progress indicator components."""
        try:
            for progress in self.components[ComponentType.PROGRESS]:
                if isinstance(progress, QProgressBar):
                    progress.setStyleSheet(f"""
                        QProgressBar {{
                            background-color: {Theme.get_color('BG_LIGHT')};
                            border: none;
                            border-radius: 3px;
                            text-align: center;
                        }}
                        QProgressBar::chunk {{
                            background-color: {Theme.get_color('PRIMARY')};
                            border-radius: 3px;
                        }}
                    """)
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.PROGRESS])} progress indicators")
        except Exception as e:
            self.logger.error(f"Error applying theme to progress indicators: {str(e)}")
    
    def _apply_to_views(self, theme_id: str) -> None:
        """Apply theme to view components."""
        try:
            for view in self.components[ComponentType.VIEW]:
                if isinstance(view, QListWidget) or isinstance(view, QListView):
                    view.setStyleSheet(f"""
                        QListWidget, QListView {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border-radius: 4px;
                            padding: 2px;
                        }}
                        QListWidget::item, QListView::item {{
                            padding: 4px;
                            border-radius: 2px;
                        }}
                        QListWidget::item:selected, QListView::item:selected {{
                            background-color: {Theme.get_color('PRIMARY')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                        QListWidget::item:hover, QListView::item:hover {{
                            background-color: {Theme.get_color('BG_LIGHT')};
                        }}
                    """)
                elif isinstance(view, QTreeView):
                    view.setStyleSheet(f"""
                        QTreeView {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border-radius: 4px;
                            padding: 2px;
                        }}
                        QTreeView::item {{
                            padding: 4px;
                        }}
                        QTreeView::item:selected {{
                            background-color: {Theme.get_color('PRIMARY')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                        QTreeView::item:hover {{
                            background-color: {Theme.get_color('BG_LIGHT')};
                        }}
                    """)
                elif isinstance(view, QTableView):
                    view.setStyleSheet(f"""
                        QTableView {{
                            background-color: {Theme.get_color('BG_MEDIUM')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                            border-radius: 4px;
                            gridline-color: {Theme.get_color('BG_LIGHT')};
                        }}
                        QTableView::item {{
                            padding: 4px;
                        }}
                        QTableView::item:selected {{
                            background-color: {Theme.get_color('PRIMARY')};
                            color: {Theme.get_color('TEXT_PRIMARY')};
                        }}
                        QHeaderView::section {{
                            background-color: {Theme.get_color('BG_LIGHT')};
                            color: {Theme.get_color('TEXT_SECONDARY')};
                            padding: 4px;
                            border: none;
                            border-right: 1px solid {Theme.get_color('BG_MEDIUM')};
                        }}
                    """)
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.VIEW])} view widgets")
        except Exception as e:
            self.logger.error(f"Error applying theme to views: {str(e)}")
    
    def _apply_to_custom_components(self, theme_id: str) -> None:
        """Apply theme to custom components with their own theme handling."""
        try:
            for component in self.components[ComponentType.CUSTOM]:
                # Try different approaches to apply the theme
                if isinstance(component, ThemeAware):
                    # Component implements ThemeAware protocol
                    component.apply_theme(theme_id)
                elif hasattr(component, 'apply_theme') and callable(getattr(component, 'apply_theme')):
                    # Component has apply_theme method
                    component.apply_theme(theme_id)
                elif hasattr(component, 'set_theme') and callable(getattr(component, 'set_theme')):
                    # Component has set_theme method
                    component.set_theme(theme_id)
                else:
                    # No specific theme handling, try to set property for event filter
                    component.setProperty("theme_changed", True)
            self.logger.debug(f"Applied theme to {len(self.components[ComponentType.CUSTOM])} custom components")
        except Exception as e:
            self.logger.error(f"Error applying theme to custom components: {str(e)}")


# Factory functions to simplify integration

def create_theme_integration(main_window: QMainWindow, theme_manager: ThemeManager) -> ThemeIntegrator:
    """
    Create and initialize a theme integrator instance.
    
    Args:
        main_window: The application's main window
        theme_manager: Manager for theme loading and access
        
    Returns:
        Initialized ThemeIntegrator instance
    """
    try:
        integrator = ThemeIntegrator(main_window, theme_manager)
        logging.getLogger(__name__).debug("Created theme integrator")
        return integrator
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create theme integrator: {str(e)}", exc_info=True)
        # Return a basic integrator as fallback
        return ThemeIntegrator(main_window, theme_manager)


def apply_theme_to_component(component: T, main_window: QMainWindow) -> T:
    """
    Apply the current theme to a component and register it for future theme changes.
    
    Args:
        component: UI component to apply theme to
        main_window: The application's main window
        
    Returns:
        The component with theme applied
    """
    try:
        # Get theme integrator if available
        if hasattr(main_window, '_theme_integrator'):
            integrator = main_window._theme_integrator
            
            # Determine component type
            component_type = _determine_component_type(component)
            
            # Register component
            integrator.register_component(component, component_type)
            
            # Apply current theme
            theme_id = main_window.current_theme() if hasattr(main_window, 'current_theme') else "dark"
            
            # Apply theme based on component type
            if component_type == ComponentType.DIALOG:
                integrator._apply_to_dialogs(theme_id)
            elif component_type == ComponentType.BUTTON:
                integrator._apply_to_buttons(theme_id)
            elif component_type == ComponentType.INPUT:
                integrator._apply_to_inputs(theme_id)
            elif component_type == ComponentType.DISPLAY:
                integrator._apply_to_displays(theme_id)
            elif component_type == ComponentType.CONTAINER:
                integrator._apply_to_containers(theme_id)
            elif component_type == ComponentType.PROGRESS:
                integrator._apply_to_progress_indicators(theme_id)
            elif component_type == ComponentType.VIEW:
                integrator._apply_to_views(theme_id)
            elif component_type == ComponentType.CUSTOM:
                integrator._apply_to_custom_components(theme_id)
            
        return component
    except Exception as e:
        logging.getLogger(__name__).error(f"Error applying theme to component: {str(e)}", exc_info=True)
        return component


def _determine_component_type(component: QWidget) -> ComponentType:
    """
    Determine the component type classification for a widget.
    
    Args:
        component: UI component to classify
        
    Returns:
        ComponentType classification
    """
    if isinstance(component, QDialog):
        return ComponentType.DIALOG
    elif isinstance(component, QPushButton):
        return ComponentType.BUTTON
    elif isinstance(component, (QLineEdit, QTextEdit, QComboBox, QCheckBox)):
        return ComponentType.INPUT
    elif isinstance(component, QLabel):
        return ComponentType.DISPLAY
    elif isinstance(component, (QFrame, QTabWidget, QScrollArea)):
        return ComponentType.CONTAINER
    elif isinstance(component, QProgressBar):
        return ComponentType.PROGRESS
    elif isinstance(component, (QListWidget, QListView, QTreeView, QTableView)):
        return ComponentType.VIEW
    else:
        # Default to custom component for specialized widgets
        return ComponentType.CUSTOM