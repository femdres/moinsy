"""Module for loading and installing themes from various sources."""

import os
import json
import logging
import shutil
from typing import Dict, Any, Optional, List, Union, Tuple, cast
from urllib.request import urlretrieve
from urllib.parse import urlparse
import zipfile
import tempfile

from PyQt6.QtWidgets import QMessageBox, QWidget

from gui.styles.theme import Theme
from gui.styles.theme_events import get_theme_event_bus


class ThemeLoader:
    """
    Utility class for loading, installing and managing theme files.

    This class provides functionality for loading themes from files,
    installing theme packages, and managing theme resources.

    Like a digital interior decorator collecting and applying visual motifs,
    this class manages the acquisition and installation of aesthetic packages.
    """

    def __init__(self, themes_dir: str):
        """
        Initialize the theme loader.

        Args:
            themes_dir: Directory where themes are stored

        Like establishing a wardrobe for our digital fashion collection,
        this method sets up the storage location for our theme assets.
        """
        self.logger = logging.getLogger(__name__)
        self.themes_dir = themes_dir

        # Ensure themes directory exists
        os.makedirs(self.themes_dir, exist_ok=True)

        # Initialize the theme event bus for notifications
        self.event_bus = get_theme_event_bus()

        self.logger.debug(f"ThemeLoader initialized with directory: {themes_dir}")

    def get_available_themes(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available theme metadata.

        Returns:
            List of theme information dictionaries

        Like taking inventory of our digital wardrobe, this method
        catalogs all available aesthetic options in our collection.
        """
        try:
            themes = []

            # Check if themes directory exists
            if not os.path.exists(self.themes_dir):
                self.logger.warning(f"Themes directory doesn't exist: {self.themes_dir}")
                return []

            # List files in themes directory
            for filename in os.listdir(self.themes_dir):
                if filename.endswith('.theme.json'):
                    theme_path = os.path.join(self.themes_dir, filename)
                    try:
                        # Load theme metadata
                        with open(theme_path, 'r') as f:
                            theme_data = json.load(f)

                        # Extract theme ID from filename
                        theme_id = filename.replace('.theme.json', '')

                        # Get theme metadata
                        themes.append({
                            'id': theme_id,
                            'name': theme_data.get('name', theme_id),
                            'description': theme_data.get('description', ''),
                            'author': theme_data.get('author', 'Unknown'),
                            'version': theme_data.get('version', '1.0.0'),
                            'path': theme_path,
                            'is_builtin': theme_id in ['dark', 'light', 'high_contrast']
                        })
                    except Exception as e:
                        self.logger.warning(f"Error loading theme metadata from {filename}: {str(e)}")

            self.logger.debug(f"Found {len(themes)} available themes")
            return themes

        except Exception as e:
            self.logger.error(f"Error getting available themes: {str(e)}")
            return []

    def load_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a theme by its identifier.

        Args:
            theme_id: Theme identifier

        Returns:
            Theme data dictionary or None if not found

        Like retrieving a specific outfit from our digital wardrobe,
        this method loads the definition of a particular aesthetic.
        """
        try:
            # Check if it's a built-in theme
            if theme_id in ['dark', 'light', 'high_contrast']:
                # Get built-in theme data from Theme class
                colors = Theme.COLORS.get(theme_id, {})
                fonts = Theme.FONTS

                # Create theme data dictionary
                theme_data = {
                    'name': f"{theme_id.title()} Theme",
                    'description': f"Built-in {theme_id} theme",
                    'colors': colors,
                    'fonts': fonts
                }

                return theme_data

            # Otherwise load from file
            theme_path = os.path.join(self.themes_dir, f"{theme_id}.theme.json")

            if not os.path.exists(theme_path):
                self.logger.warning(f"Theme file not found: {theme_path}")
                return None

            with open(theme_path, 'r') as f:
                theme_data = json.load(f)

            self.logger.debug(f"Loaded theme: {theme_id}")
            return theme_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid theme file format for {theme_id}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading theme {theme_id}: {str(e)}")
            return None

    def install_theme(self, source_path: str, parent: Optional[QWidget] = None) -> Optional[str]:
        """
        Install a theme from a file or URL.

        Args:
            source_path: Path or URL to the theme file
            parent: Optional parent widget for error dialogs

        Returns:
            Theme ID if installation was successful, None otherwise

        Like a digital fashion designer importing new styles into our collection,
        this method adds new aesthetic options to our thematic repertoire.
        """
        try:
            # Check if source is URL or local file
            is_url = urlparse(source_path).scheme in ['http', 'https']

            if is_url:
                # Download file
                self.logger.info(f"Downloading theme from URL: {source_path}")
                fd, temp_path = tempfile.mkstemp(suffix='.theme.json')
                os.close(fd)

                try:
                    urlretrieve(source_path, temp_path)
                    file_path = temp_path
                except Exception as download_error:
                    self.logger.error(f"Error downloading theme: {str(download_error)}")
                    if parent:
                        QMessageBox.critical(parent, "Download Error",
                                             f"Failed to download theme: {str(download_error)}")
                    return None
            else:
                # Local file
                file_path = source_path

            # Check if it's a single JSON file or a theme package (zip)
            if file_path.endswith('.zip'):
                return self._install_theme_package(file_path, parent)
            else:
                return self._install_theme_file(file_path, parent)

        except Exception as e:
            self.logger.error(f"Error installing theme: {str(e)}")
            if parent:
                QMessageBox.critical(parent, "Installation Error",
                                     f"Failed to install theme: {str(e)}")
            return None
        finally:
            # Clean up temp file if used
            if is_url and 'temp_path' in locals():
                try:
                    os.remove(temp_path)
                except:
                    pass

    def _install_theme_file(self, file_path: str, parent: Optional[QWidget] = None) -> Optional[str]:
        """
        Install a theme from a JSON file.

        Args:
            file_path: Path to the theme JSON file
            parent: Optional parent widget for error dialogs

        Returns:
            Theme ID if installation was successful, None otherwise
        """
        try:
            # Validate the theme file
            try:
                with open(file_path, 'r') as f:
                    theme_data = json.load(f)
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in theme file: {file_path}")
                if parent:
                    QMessageBox.warning(parent, "Invalid Theme",
                                        "The selected file is not a valid theme file.")
                return None

            # Check required fields
            if not isinstance(theme_data, dict) or 'name' not in theme_data or 'colors' not in theme_data:
                self.logger.error(f"Missing required fields in theme file: {file_path}")
                if parent:
                    QMessageBox.warning(parent, "Invalid Theme",
                                        "The theme file is missing required information.")
                return None

            # Generate theme ID from name
            theme_name = theme_data.get('name', 'Custom Theme')
            theme_id = theme_name.lower().replace(' ', '_')

            # Check if theme with this ID already exists
            existing_themes = self.get_available_themes()
            existing_ids = [t['id'] for t in existing_themes]

            # Append number to make unique if needed
            if theme_id in existing_ids:
                counter = 1
                while f"{theme_id}_{counter}" in existing_ids:
                    counter += 1
                theme_id = f"{theme_id}_{counter}"

            # Copy file to themes directory
            dest_path = os.path.join(self.themes_dir, f"{theme_id}.theme.json")
            shutil.copy2(file_path, dest_path)

            self.logger.info(f"Installed theme '{theme_name}' with ID '{theme_id}'")

            # Notify listeners of new theme availability (but don't change current theme)
            self.event_bus.theme_changed.emit(theme_id)

            return theme_id

        except Exception as e:
            self.logger.error(f"Error installing theme file: {str(e)}")
            if parent:
                QMessageBox.critical(parent, "Installation Error",
                                     f"Failed to install theme: {str(e)}")
            return None

    def _install_theme_package(self, file_path: str, parent: Optional[QWidget] = None) -> Optional[str]:
        """
        Install a theme from a zip package that may contain multiple themes and resources.

        Args:
            file_path: Path to the theme package (zip file)
            parent: Optional parent widget for error dialogs

        Returns:
            Theme ID of the primary theme if installation was successful, None otherwise
        """
        temp_dir = None
        try:
            # Create a temporary directory to extract package
            temp_dir = tempfile.mkdtemp(prefix="moinsy_theme_")

            # Extract zip file
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Look for theme files in the package
            theme_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.theme.json'):
                        theme_files.append(os.path.join(root, file))

            if not theme_files:
                self.logger.error(f"No theme files found in package: {file_path}")
                if parent:
                    QMessageBox.warning(parent, "Invalid Package",
                                        "The theme package doesn't contain any theme files.")
                return None

            # Install each theme file
            installed_themes = []
            for theme_file in theme_files:
                theme_id = self._install_theme_file(theme_file, parent)
                if theme_id:
                    installed_themes.append(theme_id)

            if not installed_themes:
                self.logger.error("Failed to install any themes from package")
                if parent:
                    QMessageBox.warning(parent, "Installation Failed",
                                        "Failed to install any themes from the package.")
                return None

            # Copy other resources (images, fonts, etc.)
            resource_types = {
                '.ttf': 'fonts',
                '.otf': 'fonts',
                '.png': 'images',
                '.jpg': 'images',
                '.jpeg': 'images',
                '.svg': 'images'
            }

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in resource_types:
                        resource_type = resource_types[ext]
                        resource_dir = os.path.join(self.themes_dir, resource_type)
                        os.makedirs(resource_dir, exist_ok=True)

                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(resource_dir, file)

                        # Copy resource file
                        shutil.copy2(src_path, dst_path)
                        self.logger.debug(f"Copied resource: {file} to {resource_dir}")

                        # Register fonts if applicable
                        if resource_type == 'fonts' and (ext == '.ttf' or ext == '.otf'):
                            Theme.register_font(dst_path)

            # Return the first theme ID as primary
            self.logger.info(f"Installed {len(installed_themes)} themes from package")
            return installed_themes[0]

        except Exception as e:
            self.logger.error(f"Error installing theme package: {str(e)}")
            if parent:
                QMessageBox.critical(parent, "Installation Error",
                                     f"Failed to install theme package: {str(e)}")
            return None
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

    def delete_theme(self, theme_id: str) -> bool:
        """
        Delete a theme by its identifier.

        Args:
            theme_id: Theme identifier

        Returns:
            True if deletion was successful, False otherwise

        Like removing an outfit from our digital wardrobe, this method
        discards an aesthetic option that is no longer desired.
        """
        try:
            # Check if it's a built-in theme
            if theme_id in ['dark', 'light', 'high_contrast']:
                self.logger.warning(f"Cannot delete built-in theme: {theme_id}")
                return False

            # Get theme file path
            theme_path = os.path.join(self.themes_dir, f"{theme_id}.theme.json")

            # Check if file exists
            if not os.path.exists(theme_path):
                self.logger.warning(f"Theme file not found: {theme_path}")
                return False

            # Delete the file
            os.remove(theme_path)
            self.logger.info(f"Deleted theme: {theme_id}")

            # Notify listeners that a theme was removed
            self.event_bus.theme_changed.emit("theme_deleted")

            return True

        except Exception as e:
            self.logger.error(f"Error deleting theme {theme_id}: {str(e)}")
            return False

    def export_theme(self, theme_id: str, destination: str) -> bool:
        """
        Export a theme to a file.

        Args:
            theme_id: Theme identifier
            destination: Destination file path

        Returns:
            True if export was successful, False otherwise

        Like packaging an outfit for sharing with others, this method
        exports an aesthetic definition for external use.
        """
        try:
            # Load the theme
            theme_data = self.load_theme(theme_id)
            if not theme_data:
                self.logger.warning(f"Theme not found: {theme_id}")
                return False

            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)

            # Write theme data to file
            with open(destination, 'w') as f:
                json.dump(theme_data, f, indent=4)

            self.logger.info(f"Exported theme {theme_id} to: {destination}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting theme {theme_id}: {str(e)}")
            return False

    def create_custom_theme(self, name: str, base_theme: str, color_overrides: Dict[str, str]) -> Optional[str]:
        """
        Create a custom theme based on an existing theme with color overrides.

        Args:
            name: Name for the new theme
            base_theme: Base theme to use as starting point
            color_overrides: Dictionary of color keys and values to override

        Returns:
            Theme ID if creation was successful, None otherwise

        Like a fashion designer creating a customized variant of a classic style,
        this method produces a new aesthetic based on an existing template.
        """
        try:
            # Load the base theme
            base_data = self.load_theme(base_theme)
            if not base_data:
                self.logger.warning(f"Base theme not found: {base_theme}")
                return None

            # Create a copy of the base theme
            theme_data = base_data.copy()

            # Update metadata
            theme_data['name'] = name
            theme_data['description'] = f"Custom theme based on {base_data.get('name', base_theme)}"

            # Apply color overrides
            colors = theme_data.get('colors', {}).copy()
            for key, value in color_overrides.items():
                colors[key] = value
            theme_data['colors'] = colors

            # Generate theme ID
            theme_id = name.lower().replace(' ', '_')

            # Check if theme with this ID already exists
            existing_themes = self.get_available_themes()
            existing_ids = [t['id'] for t in existing_themes]

            # Append number to make unique if needed
            if theme_id in existing_ids:
                counter = 1
                while f"{theme_id}_{counter}" in existing_ids:
                    counter += 1
                theme_id = f"{theme_id}_{counter}"

            # Save theme to file
            theme_path = os.path.join(self.themes_dir, f"{theme_id}.theme.json")
            with open(theme_path, 'w') as f:
                json.dump(theme_data, f, indent=4)

            self.logger.info(f"Created custom theme '{name}' with ID '{theme_id}'")

            # Notify listeners of new theme
            self.event_bus.theme_changed.emit(theme_id)

            return theme_id

        except Exception as e:
            self.logger.error(f"Error creating custom theme: {str(e)}")
            return None