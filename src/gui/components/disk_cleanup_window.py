from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QScrollArea, QWidget, QGridLayout,
    QCheckBox, QProgressBar, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
import logging
from typing import Dict, List, Optional, Set, Any, Tuple, cast

from core.tools.disk_cleanup import DiskCleanup, CleanupCategory


class DiskCleanupWindow(QDialog):
    """
    Dialog window for disk cleanup operations.

    Like a control panel for digital janitorial operations, this interface
    provides access to the various system detritus categories, allowing users
    to selectively remove the accumulated cruft of their computational existence.
    """

    # Signals
    scan_requested = pyqtSignal()
    cleanup_requested = pyqtSignal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the disk cleanup window."""
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Initialize internal state
        self._selected_targets: Set[str] = set()
        self._results: Dict[str, Any] = {}
        self._scan_complete: bool = False
        self._cleanup_in_progress: bool = False

        # Initialize disk cleanup tool
        self.cleanup_tool = DiskCleanup(self)

        # Connect signals
        self.cleanup_tool.update_progress.connect(self.update_progress)
        self.cleanup_tool.log_output.connect(self.handle_log_output)
        self.cleanup_tool.error_occurred.connect(self.handle_error)
        self.cleanup_tool.scan_complete.connect(self.handle_scan_complete)
        self.cleanup_tool.cleanup_complete.connect(self.handle_cleanup_complete)

        # Setup window properties
        self.setWindowTitle("Disk Cleanup")
        self.setMinimumSize(900, 680)

        # Setup UI
        self.setup_ui()

        # Initialize
        self.update_targets()

        self.logger.debug("Disk Cleanup window initialized")

    def setup_ui(self) -> None:
        """Initialize the user interface components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        self.setup_header(layout)

        # Content area with targets
        self.setup_content_area(layout)

        # Progress section
        self.setup_progress_section(layout)

        # Log output area
        self.setup_log_area(layout)

        # Button row
        self.setup_button_row(layout)

        # Apply styling - first without category details
        self.apply_styling()

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup the header section with title and explanation."""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        # Title
        title_label = QLabel("Disk Cleanup")
        title_label.setFont(QFont('Segoe UI', 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4CAF50;")
        header_layout.addWidget(title_label)

        # Subtitle
        subtitle = QLabel("Scan and remove unnecessary files to free up disk space")
        subtitle.setStyleSheet("color: #888888; font-size: 14px;")
        header_layout.addWidget(subtitle)

        # Space summary
        self.space_summary = QLabel("Click \"Scan\" to analyze disk usage")
        self.space_summary.setStyleSheet("color: #FFFFFF; font-size: 15px; margin-top: 10px;")
        self.space_summary.setObjectName("SpaceSummary")
        header_layout.addWidget(self.space_summary)

        layout.addLayout(header_layout)

    def setup_content_area(self, layout: QVBoxLayout) -> None:
        """Setup the main content area with cleanup targets."""
        # Create scrollable area for cleanup targets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Container for cleanup targets
        self.targets_container = QWidget()
        self.targets_layout = QVBoxLayout(self.targets_container)
        self.targets_layout.setSpacing(15)
        self.targets_layout.setContentsMargins(5, 5, 5, 5)

        # Will be populated in update_targets()

        scroll.setWidget(self.targets_container)
        layout.addWidget(scroll)

    def setup_progress_section(self, layout: QVBoxLayout) -> None:
        """Setup the progress indicator section."""
        progress_frame = QFrame()
        progress_frame.setObjectName("ProgressFrame")
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(8)
        progress_layout.setContentsMargins(15, 15, 15, 15)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)

        # Progress label
        self.progress_label = QLabel("Ready to scan")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_frame)

    def setup_log_area(self, layout: QVBoxLayout) -> None:
        """Setup the log output area for operation feedback."""
        # Log frame
        log_frame = QFrame()
        log_frame.setObjectName("LogFrame")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setSpacing(8)
        log_layout.setContentsMargins(15, 15, 15, 15)

        # Log output area with scroll
        log_scroll = QScrollArea()
        log_scroll.setWidgetResizable(True)
        log_scroll.setMinimumHeight(120)
        log_scroll.setMaximumHeight(180)

        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.setSpacing(2)
        self.log_layout.setContentsMargins(5, 5, 5, 5)
        self.log_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        log_scroll.setWidget(self.log_container)
        log_layout.addWidget(log_scroll)

        layout.addWidget(log_frame)

    def setup_button_row(self, layout: QVBoxLayout) -> None:
        """Setup the action buttons row at the bottom."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Select All button
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_targets)
        button_layout.addWidget(self.select_all_btn)

        # Select None button
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_no_targets)
        button_layout.addWidget(self.select_none_btn)

        button_layout.addStretch()

        # Scan button
        self.scan_btn = QPushButton("Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setMinimumWidth(100)
        button_layout.addWidget(self.scan_btn)

        # Clean button
        self.clean_btn = QPushButton("Clean Up")
        self.clean_btn.clicked.connect(self.start_cleanup)
        self.clean_btn.setEnabled(False)
        self.clean_btn.setMinimumWidth(100)
        button_layout.addWidget(self.clean_btn)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setMinimumWidth(100)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def apply_styling(self) -> None:
        """Apply themed styling to all components."""
        # Primary and background colors
        primary_color = "#4CAF50"  # Green
        bg_dark = "#121212"
        bg_medium = "#1E1E1E"
        bg_light = "#2A2A2A"
        text_primary = "#FFFFFF"
        text_secondary = "#888888"

        # Main dialog
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_dark};
                color: {text_primary};
            }}
        """)

        # Frame styling
        self.findChild(QFrame, "ProgressFrame").setStyleSheet(f"""
            QFrame#ProgressFrame {{
                background-color: {bg_medium};
                border: 1px solid {bg_light};
                border-radius: 8px;
            }}
        """)

        self.findChild(QFrame, "LogFrame").setStyleSheet(f"""
            QFrame#LogFrame {{
                background-color: {bg_medium};
                border: 1px solid {bg_light};
                border-radius: 8px;
            }}
        """)

        # Progress bar styling
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {bg_light};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {primary_color};
                border-radius: 3px;
            }}
        """)

        self.progress_label.setStyleSheet(f"""
            color: {text_secondary};
            font-size: 13px;
        """)

        # Button styling
        button_style = f"""
            QPushButton {{
                background-color: {bg_light};
                color: {text_primary};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #374151;
            }}
            QPushButton:disabled {{
                background-color: #2d2d2d;
                color: #555555;
            }}
        """

        self.scan_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary_color};
                color: {text_primary};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
            QPushButton:disabled {{
                background-color: #2d2d2d;
                color: #555555;
            }}
        """)

        self.clean_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFC107;
                color: black;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FFB000;
            }}
            QPushButton:disabled {{
                background-color: #2d2d2d;
                color: #555555;
            }}
        """)

        self.close_btn.setStyleSheet(button_style)
        self.select_all_btn.setStyleSheet(button_style)
        self.select_none_btn.setStyleSheet(button_style)

        # Checkbox styling
        checkbox_style = f"""
            QCheckBox {{
                color: {text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid {text_secondary};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {bg_medium};
            }}
            QCheckBox::indicator:checked {{
                background-color: {primary_color};
                border: 1px solid {primary_color};
                image: url(:/resources/icons/check.svg);
            }}
            QCheckBox::indicator:checked:disabled {{
                background-color: #555555;
                border: 1px solid #555555;
            }}
            QCheckBox:disabled {{
                color: #555555;
            }}
        """

        # Apply checkbox style to all checkboxes (will be created later)
        self.setStyleSheet(self.styleSheet() + checkbox_style)

    def update_targets(self) -> None:
        """Update the cleanup targets display based on available targets."""
        # Get targets from the cleanup tool
        targets_by_category = self.cleanup_tool.get_cleanup_targets()

        # Clear existing widgets
        for i in reversed(range(self.targets_layout.count())):
            widget = self.targets_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Create a group for each category
        for category, targets in targets_by_category.items():
            # Skip empty categories
            if not targets:
                continue

            # Create group box for category
            category_name = category.name.replace("_", " ").title()
            group_box = QGroupBox(category_name)
            group_box.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 15px;
                    color: #4CAF50;
                    border: 1px solid #2A2A2A;
                    border-radius: 8px;
                    margin-top: 15px;
                    padding-top: 16px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)

            # Layout for targets in this category
            group_layout = QVBoxLayout(group_box)
            group_layout.setSpacing(5)
            group_layout.setContentsMargins(15, 20, 15, 15)

            # Add each target in this category
            for target in targets:
                target_frame = self._create_target_item(target)
                group_layout.addWidget(target_frame)

            # Add group to main layout
            self.targets_layout.addWidget(group_box)

        # Add stretch to push everything to the top
        self.targets_layout.addStretch()

    def _create_target_item(self, target: Dict[str, Any]) -> QFrame:
        """
        Create a UI item for a cleanup target.

        Args:
            target: Target information dictionary

        Returns:
            Frame containing the target item UI
        """
        # Create frame for this target
        frame = QFrame()
        frame.setObjectName(f"Target_{target['id']}")
        frame.setStyleSheet(f"""
            QFrame#Target_{target['id']} {{
                background-color: #1E1E1E;
                border-radius: 6px;
                margin: 2px 0px;
            }}
        """)

        # Layout for target item
        layout = QHBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Checkbox for selection
        checkbox = QCheckBox(target['name'])
        checkbox.setObjectName(f"Checkbox_{target['id']}")

        # Set checked state from previous selection
        checkbox.setChecked(target['id'] in self._selected_targets)

        # Connect checkbox to selection handler
        checkbox.stateChanged.connect(
            lambda state, target_id=target['id']: self._handle_target_selection(target_id, state))

        # Disable if dangerous and not scanned
        if target['dangerous'] and not target.get('scanned', False):
            checkbox.setEnabled(False)

        layout.addWidget(checkbox, 1)  # Give checkbox stretch priority

        # Space information
        if target.get('scanned', False):
            space_label = QLabel(target['space_found_formatted'])
            space_label.setStyleSheet("color: #64B5F6; font-weight: bold;")
            layout.addWidget(space_label)

            # Add checkmark if cleaned
            if target.get('cleaned', False):
                cleaned_label = QLabel("✓")
                cleaned_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                layout.addWidget(cleaned_label)

        # Error indicator if needed
        if target.get('error'):
            error_label = QLabel("⚠")
            error_label.setStyleSheet("color: #F44336; font-weight: bold;")
            error_label.setToolTip(target['error'])
            layout.addWidget(error_label)

        return frame

    def select_all_targets(self) -> None:
        """Select all available cleanup targets."""
        targets_by_category = self.cleanup_tool.get_cleanup_targets()

        for category, targets in targets_by_category.items():
            for target in targets:
                checkbox = self.findChild(QCheckBox, f"Checkbox_{target['id']}")
                if checkbox and checkbox.isEnabled():
                    checkbox.setChecked(True)

    def select_no_targets(self) -> None:
        """Deselect all cleanup targets."""
        targets_by_category = self.cleanup_tool.get_cleanup_targets()

        for category, targets in targets_by_category.items():
            for target in targets:
                checkbox = self.findChild(QCheckBox, f"Checkbox_{target['id']}")
                if checkbox:
                    checkbox.setChecked(False)

    def _handle_target_selection(self, target_id: str, state: int) -> None:
        """
        Handle selection state change for a cleanup target.

        Args:
            target_id: ID of the target being selected/deselected
            state: Qt checkbox state
        """
        if state == Qt.CheckState.Checked.value:
            self._selected_targets.add(target_id)
        else:
            self._selected_targets.discard(target_id)

        # Update Clean button state based on selections
        self.clean_btn.setEnabled(bool(self._selected_targets) and self._scan_complete)

    def start_scan(self) -> None:
        """Initiate the disk space scan operation."""
        # Clear log
        self._clear_log()

        # Reset scan state
        self._scan_complete = False
        self.clean_btn.setEnabled(False)

        # Reset space summary
        self.space_summary.setText("Scanning disk space usage...")

        # Update progress
        self.progress_label.setText("Scanning...")
        self.progress_bar.setValue(0)

        # Disable scan button during scan
        self.scan_btn.setEnabled(False)

        # Add initial log message
        self.handle_log_output("Starting disk space scan...")

        # Start scan in the cleanup tool
        self.cleanup_tool.scan_disk_space()

    def start_cleanup(self) -> None:
        """Initiate the cleanup operation for selected targets."""
        if not self._selected_targets:
            self.handle_log_output("No cleanup targets selected.")
            return

        # Confirm dangerous operations if needed
        dangerous_targets = []
        targets_by_category = self.cleanup_tool.get_cleanup_targets()

        for category, targets in targets_by_category.items():
            for target in targets:
                if target['id'] in self._selected_targets and target.get('dangerous', False):
                    dangerous_targets.append(target['name'])

        if dangerous_targets:
            warning_text = "You're about to perform potentially dangerous cleanup operations:\n\n"
            warning_text += "\n".join([f"• {name}" for name in dangerous_targets])
            warning_text += "\n\nThese operations could affect system functionality if misused."
            warning_text += "\n\nAre you sure you want to continue?"

            reply = QMessageBox.warning(
                self,
                "Confirm Dangerous Operations",
                warning_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                self.handle_log_output("Cleanup cancelled.")
                return

        # Clear log
        self._clear_log()

        # Set cleanup in progress
        self._cleanup_in_progress = True

        # Update UI state
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)

        # Update progress
        self.progress_label.setText("Cleaning...")
        self.progress_bar.setValue(0)

        # Add initial log message
        self.handle_log_output("Starting cleanup...")

        # Set selected targets
        self.cleanup_tool.set_selected_targets(list(self._selected_targets))

        # Start cleanup
        self.cleanup_tool.cleanup_selected()

    def handle_scan_complete(self, results: Dict[str, Any]) -> None:
        """
        Handle scan completion and update UI.

        Args:
            results: Scan results dictionary
        """
        self._results = results
        self._scan_complete = True

        # Update UI state
        self.scan_btn.setEnabled(True)

        # Update progress
        self.progress_label.setText("Scan complete")

        # Enable cleanup button if targets are selected
        self.clean_btn.setEnabled(bool(self._selected_targets))

        # Update space summary
        total_space = results.get('total_space_found', 0)
        if total_space > 0:
            total_space_formatted = results.get('total_space_found_formatted', '')
            self.space_summary.setText(f"Total space that can be freed: {total_space_formatted}")
        else:
            self.space_summary.setText("No unnecessary files found to clean up.")

        # Update targets display
        self.update_targets()

    def handle_cleanup_complete(self, results: Dict[str, Any]) -> None:
        """
        Handle cleanup completion and update UI.

        Args:
            results: Cleanup results dictionary
        """
        self._results = results
        self._cleanup_in_progress = False

        # Update UI state
        self.scan_btn.setEnabled(True)
        self.clean_btn.setEnabled(bool(self._selected_targets))

        # Update progress
        self.progress_label.setText("Cleanup complete")

        # Update space summary
        total_freed = results.get('total_space_freed', 0)
        if total_freed > 0:
            total_freed_formatted = results.get('total_space_freed_formatted', '')
            self.space_summary.setText(f"Total space freed: {total_freed_formatted}")
        else:
            self.space_summary.setText("No space was freed during cleanup.")

        # Update targets display
        self.update_targets()

    def update_progress(self, value: int) -> None:
        """
        Update progress bar with new value.

        Args:
            value: Progress percentage (0-100)
        """
        self.progress_bar.setValue(value)

    def handle_log_output(self, message: str) -> None:
        """
        Add message to log output area.

        Args:
            message: Message to display
        """
        # Create label for this log entry
        log_label = QLabel(message)
        log_label.setWordWrap(True)
        log_label.setStyleSheet("color: white; font-family: monospace;")

        # Add to log container
        self.log_layout.addWidget(log_label)

        # Scroll to bottom
        QTimer.singleShot(10, self._scroll_log_to_bottom)

    def _scroll_log_to_bottom(self) -> None:
        """Scroll the log view to show the latest entries."""
        if hasattr(self, 'log_container') and self.log_container.parent():
            scroll_area = self.log_container.parent()
            if hasattr(scroll_area, 'verticalScrollBar'):
                scroll_bar = scroll_area.verticalScrollBar()
                scroll_bar.setValue(scroll_bar.maximum())

    def _clear_log(self) -> None:
        """Clear all log entries."""
        for i in reversed(range(self.log_layout.count())):
            widget = self.log_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def handle_error(self, error_message: str) -> None:
        """
        Handle error message from the cleanup tool.

        Args:
            error_message: Error message to display
        """
        # Create label with error styling
        error_label = QLabel(f"Error: {error_message}")
        error_label.setWordWrap(True)
        error_label.setStyleSheet("color: #F44336; font-family: monospace;")

        # Add to log container
        self.log_layout.addWidget(error_label)

        # Scroll to bottom
        QTimer.singleShot(10, self._scroll_log_to_bottom)

        # If this is during scan, re-enable scan button
        if not self._scan_complete and not self._cleanup_in_progress:
            self.scan_btn.setEnabled(True)
            self.progress_label.setText("Scan failed")

        # If this is during cleanup, re-enable buttons
        if self._cleanup_in_progress:
            self.scan_btn.setEnabled(True)
            self.clean_btn.setEnabled(bool(self._selected_targets))
            self._cleanup_in_progress = False
            self.progress_label.setText("Cleanup failed")

    def closeEvent(self, event):
        """Clean up when window is closed."""
        # Only allow close if not in the middle of operations
        if self._cleanup_in_progress:
            QMessageBox.warning(
                self,
                "Operation in Progress",
                "A cleanup operation is currently in progress.\nPlease wait for it to complete.",
                QMessageBox.StandardButton.Ok
            )
            event.ignore()
        else:
            event.accept()