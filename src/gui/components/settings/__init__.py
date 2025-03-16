"""Settings module for GUI components."""

from gui.components.settings.settings_window import SettingsWindow
from gui.components.settings.general_settings import GeneralSettingsTab
from gui.components.settings.system_settings import SystemSettingsTab
from gui.components.settings.tools_settings import ToolsSettingsTab

__all__ = [
    'SettingsWindow',
    'GeneralSettingsTab',
    'SystemSettingsTab',
    'ToolsSettingsTab'
]