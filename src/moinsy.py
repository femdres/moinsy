#!/usr/bin/env python3
"""
Moinsy - Modular Installation System for Linux
Main application entry point and bootstrap
"""

import sys
import os
import traceback
import logging
import argparse
from typing import Optional, Dict, Any, List, Union, Tuple

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QIcon, QPixmap, QFontDatabase
from PyQt6.QtCore import Qt, QTimer

from gui.main_window import MainWindow
from gui.styles.theme import Theme
from gui.styles.theme_integration import create_theme_integration
from utils.logging_setup import setup_logging
from config import get_resource_path, ensure_directories


def setup_environment() -> None:
    """
    Setup required environment variables and paths.

    Like aligning the stars before a celestial ritual, this function
    establishes the necessary conditions for our application to function.
    """
    try:
        # Get the absolute path to the src directory
        src_dir = os.path.dirname(os.path.abspath(__file__))

        # Add src directory to Python path if not already there
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        # Change to src directory
        os.chdir(src_dir)
        logging.debug(f"Environment setup complete, working directory: {os.getcwd()}")
    except Exception as e:
        logging.error(f"Failed to setup environment: {str(e)}")
        raise


def setup_fonts() -> None:
    """
    Load custom fonts for use in the application.

    Like installing new typefaces into the fabric of our digital reality,
    this function enriches our textual expression capabilities.
    """
    try:
        # Define commonly available monospace fonts to check for
        desired_fonts = [
            "JetBrains Mono", "Fira Code", "Source Code Pro",
            "Cascadia Code", "Ubuntu Mono", "Consolas", "Courier New"
        ]

        # Check if any are already installed in the system
        available_families = QFontDatabase.families()

        has_good_mono = False
        for font in desired_fonts:
            if font in available_families:
                logging.debug(f"Found suitable monospace font: {font}")
                has_good_mono = True
                break

        # If no good monospace fonts found, could load custom fonts here
        if not has_good_mono:
            logging.warning("No preferred monospace fonts found in system")
            # Future enhancement: load bundled fonts

        logging.debug("Font setup complete")
    except Exception as e:
        logging.error(f"Failed to setup fonts: {str(e)}")
        # Continue without custom fonts


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Like interpreting the whispers of users at the threshold of our
    digital domain, this function extracts meaning from their cryptic invocations.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Moinsy - Modular Installation System")

    # Add command line options
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--theme', type=str, choices=['dark', 'light', 'high_contrast'],
                        help='Set initial theme')
    parser.add_argument('--no-splash', action='store_true', help='Disable splash screen')

    return parser.parse_args()


def show_splash_screen() -> Optional[QSplashScreen]:
    """
    Show a splash screen during application startup.

    Like displaying a ceremonial banner before entering a grand hall,
    this function presents our identity while preparations continue behind the scenes.

    Returns:
        QSplashScreen instance or None if splash screen is disabled
    """
    try:
        # Get splash image path
        splash_path = get_resource_path("icons", "splash.png")

        # Check if splash image exists
        if not os.path.exists(splash_path):
            logging.warning(f"Splash screen image not found at {splash_path}")
            return None

        # Create splash screen
        splash_pixmap = QPixmap(splash_path)
        splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)

        # Add version text
        splash.showMessage("Version 1.0.0", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                           Qt.GlobalColor.white)

        # Show splash screen
        splash.show()
        logging.debug("Splash screen displayed")

        return splash
    except Exception as e:
        logging.error(f"Failed to show splash screen: {str(e)}")
        return None


def main() -> int:
    """
    Main application entry point.

    Like the genesis moment of our digital universe, this function
    initiates the chain reaction that brings our application into being.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse command line arguments first
        args = parse_arguments()

        # Setup logging with appropriate level
        log_level = logging.DEBUG if args.debug else logging.INFO
        setup_logging(log_level=log_level)
        logging.info("Moinsy starting up - digital awakening initiated")

        # Setup environment
        setup_environment()

        # Ensure required directories exist
        ensure_directories()

        # Create application instance
        app = QApplication(sys.argv)

        # Show splash screen if not disabled
        splash = None if args.no_splash else show_splash_screen()

        # Setup fonts
        setup_fonts()

        # Set application metadata
        app.setApplicationName("Moinsy")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Moinsy")
        app.setOrganizationDomain("moinsy.org")

        # Set application icon
        icon_path = get_resource_path("icons", "moinsy.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        else:
            logging.warning(f"Application icon not found at {icon_path}")

        # Process events to update splash screen
        if splash:
            app.processEvents()
            splash.showMessage("Initializing...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                               Qt.GlobalColor.white)

        # Apply base theme initially (will be updated from settings later)
        initial_theme = args.theme or "dark"
        Theme.set_theme(initial_theme)
        Theme.apply_base_styles(app)
        logging.debug(f"Initial theme '{initial_theme}' applied")

        # Process events again for theme application
        if splash:
            app.processEvents()
            splash.showMessage("Loading interface...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                               Qt.GlobalColor.white)

        # Create and show main window
        window = MainWindow()

        # Close splash screen with a slight delay for smoother transition
        if splash:
            QTimer.singleShot(800, splash.close)

        window.show()
        logging.info("Main window displayed - digital interface manifested")

        # Start event loop
        return app.exec()

    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        logging.debug(traceback.format_exc())
        print(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)