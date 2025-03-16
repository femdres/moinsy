from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QScrollArea, QWidget, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import logging
from typing import Optional, Dict, Any, List

from managers.config_manager import ConfigManager


class HardwareMonitorWindow(QDialog):
    """Dialog window for hardware monitoring"""

    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None):
        """Initialize the hardware monitor window.

        Args:
            config_manager: Application configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.monitor = None
        self.update_timer = None
        self.is_paused = False

        self.setup_ui()
        self.setup_monitor()
        self.setup_update_timer()

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Hardware Monitor")
        self.setMinimumSize(800, 500)  # Reduced window size

        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Reduced spacing
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins

        self.setup_header(layout)
        self.setup_content_area(layout)
        self.setup_controls(layout)

    def setup_header(self, layout: QVBoxLayout) -> None:
        """Setup the header with title and status"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)  # Reduced spacing

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)  # Minimal spacing between title and status

        header = QLabel("Hardware Monitor")
        header.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))  # Smaller font
        header.setStyleSheet("color: #4CAF50;")
        title_layout.addWidget(header)

        self.status_label = QLabel("Monitoring Active")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")  # Smaller font
        title_layout.addWidget(self.status_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

    def setup_content_area(self, layout: QVBoxLayout) -> None:
        """Setup the scrollable content area with metric cards"""
        # Create a scrollable area for metrics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Container for metric cards
        metrics_container = QWidget()
        self.metrics_layout = QGridLayout(metrics_container)
        self.metrics_layout.setSpacing(10)  # Reduced spacing
        self.metrics_layout.setContentsMargins(0, 0, 0, 0)  # No margins for grid

        scroll.setWidget(metrics_container)
        layout.addWidget(scroll)

        # Create metric cards
        self.create_metric_cards()

    def create_metric_cards(self) -> None:
        """Create the hardware metric display cards"""
        self.cards = {}

        # CPU Card
        self.cards['cpu'] = self.create_metric_card("CPU", [
            ("Temperature", "°C", "#FF6B6B"),
            ("Frequency", "MHz", "#4ECDC4"),
            ("Usage", "%", "#45B7D1")
        ])
        self.metrics_layout.addWidget(self.cards['cpu'], 0, 0)

        # Memory Card
        self.cards['memory'] = self.create_metric_card("Memory", [
            ("RAM Used", "GB", "#FFD93D"),
            ("RAM Total", "GB", "#6C5CE7"),
            ("RAM Usage", "%", "#A8E6CF"),
            ("Swap Used", "GB", "#FF8B94")
        ])
        self.metrics_layout.addWidget(self.cards['memory'], 0, 1)

        # GPU Card
        self.cards['gpu'] = self.create_metric_card("GPU", [
            ("Temperature", "°C", "#FF6B6B"),
            ("Utilization", "%", "#45B7D1"),
            ("VRAM Used", "GB", "#FFD93D"),
            ("VRAM Total", "GB", "#6C5CE7")
        ])
        self.metrics_layout.addWidget(self.cards['gpu'], 1, 0)

        # Storage Card
        self.cards['storage'] = self.create_metric_card("Storage", [
            ("Space Used", "GB", "#FFD93D"),
            ("Space Total", "GB", "#6C5CE7"),
            ("Read Speed", "MB/s", "#4ECDC4"),
            ("Write Speed", "MB/s", "#FF8B94")
        ])
        self.metrics_layout.addWidget(self.cards['storage'], 1, 1)

    def create_metric_card(self, title: str, metrics: List[tuple]) -> QFrame:
        """Create a card for displaying related metrics

        Args:
            title: Card title
            metrics: List of metrics in (name, unit, color) format

        Returns:
            Frame containing the metric card
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2e32;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)  # Reduced spacing
        layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins

        # Card title
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))  # Smaller font
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)

        # Metric labels with units
        metric_widgets = {}
        for metric, unit, color in metrics:
            metric_frame = QFrame()
            metric_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #3d3e42;
                    border-radius: 8px;
                    padding: 8px;
                }}
            """)
            metric_layout = QHBoxLayout(metric_frame)  # Changed to horizontal layout
            metric_layout.setSpacing(5)
            metric_layout.setContentsMargins(8, 5, 8, 5)  # Reduced margins

            # Metric name
            name_label = QLabel(metric)
            name_label.setStyleSheet("color: #888888; font-size: 12px;")
            metric_layout.addWidget(name_label)

            metric_layout.addStretch()

            # Value and unit container
            value_container = QHBoxLayout()
            value_container.setSpacing(2)

            value_label = QLabel("--")
            value_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
            value_container.addWidget(value_label)

            unit_label = QLabel(unit)
            unit_label.setStyleSheet("color: #888888; font-size: 12px;")
            value_container.addWidget(unit_label)

            metric_layout.addLayout(value_container)
            layout.addWidget(metric_frame)

            # Store the value label for updating later
            key = metric.lower().replace(" ", "_")
            metric_widgets[key] = value_label

        card.metric_widgets = metric_widgets
        return card

    def setup_controls(self, layout: QVBoxLayout) -> None:
        """Setup the control section at the bottom of the window"""
        controls = QHBoxLayout()
        controls.setSpacing(8)  # Reduced spacing

        # Update frequency
        update_frame = QFrame()
        update_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2e32;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        update_layout = QHBoxLayout(update_frame)
        update_layout.setContentsMargins(8, 5, 8, 5)  # Reduced margins

        update_label = QLabel("Update every:")
        update_label.setStyleSheet("color: white; font-size: 12px;")
        update_layout.addWidget(update_label)

        # Get refresh rate from settings
        refresh_rate = self.config_manager.get_setting("tools", "hardware_monitor_refresh_rate", 1000)
        refresh_text = f"{refresh_rate}ms"

        self.update_btn = QPushButton(refresh_text)
        self.update_btn.setFixedSize(60, 25)  # Smaller fixed size
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3e42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
        """)
        update_layout.addWidget(self.update_btn)

        controls.addWidget(update_frame)
        controls.addStretch()

        # Action buttons
        button_style = """
            QPushButton {
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 15px;
                font-weight: bold;
                font-size: 12px;
            }
        """

        self.pause_btn = QPushButton("❚❚ Pause")
        self.pause_btn.clicked.connect(self.toggle_monitoring)
        self.pause_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #FFC107;
                color: black;
            }
            QPushButton:hover {
                background-color: #FFA000;
            }
        """)
        controls.addWidget(self.pause_btn)

        refresh_btn = QPushButton("⟳ Refresh")
        refresh_btn.clicked.connect(self.refresh_metrics)
        refresh_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #4CAF50;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        controls.addWidget(refresh_btn)

        layout.addLayout(controls)

    def setup_monitor(self) -> None:
        """Initialize the hardware monitor"""
        from core.tools.hardware_monitor import HardwareMonitor
        self.monitor = HardwareMonitor(self)
        self.monitor.metrics_updated.connect(self.update_metrics)
        self.monitor.error_occurred.connect(self.handle_error)

        self.logger.debug("Hardware monitor initialized")

    def setup_update_timer(self) -> None:
        """Setup the periodic update timer using rate from settings"""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_metrics)

        # Get refresh rate from settings
        refresh_rate = self.config_manager.get_setting("tools", "hardware_monitor_refresh_rate", 1000)
        self.update_timer.start(refresh_rate)

        self.logger.debug(f"Hardware monitor refresh rate set to {refresh_rate}ms")

    def refresh_metrics(self) -> None:
        """Manually refresh all metrics"""
        if self.monitor and not self.is_paused:
            self.monitor.get_all_metrics()

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update the UI with new metrics

        Args:
            metrics: Dictionary of hardware metrics
        """
        try:
            # Update CPU metrics
            if 'cpu' in metrics:
                cpu = metrics['cpu']
                cpu_card = self.cards['cpu'].metric_widgets

                if 'temperature' in cpu:
                    cpu_card['temperature'].setText(f"{cpu['temperature']:.1f}")

                if 'frequency' in cpu and 'current' in cpu['frequency']:
                    cpu_card['frequency'].setText(f"{cpu['frequency']['current']:.0f}")

                if 'usage_per_core' in cpu and cpu['usage_per_core']:
                    # Calculate average CPU usage
                    avg_usage = sum(cpu['usage_per_core']) / len(cpu['usage_per_core'])
                    cpu_card['usage'].setText(f"{avg_usage:.1f}")

            # Update memory metrics
            if 'memory' in metrics:
                mem = metrics['memory']
                mem_card = self.cards['memory'].metric_widgets

                if 'used' in mem:
                    mem_card['ram_used'].setText(f"{mem['used'] / (1024 ** 3):.1f}")
                if 'total' in mem:
                    mem_card['ram_total'].setText(f"{mem['total'] / (1024 ** 3):.1f}")
                if 'percent' in mem:
                    mem_card['ram_usage'].setText(f"{mem['percent']:.1f}")
                if 'swap_used' in mem:
                    mem_card['swap_used'].setText(f"{mem['swap_used'] / (1024 ** 3):.1f}")

            # Update GPU metrics if available
            if 'gpu' in metrics and 'error' not in metrics['gpu']:
                gpu = metrics['gpu']
                gpu_card = self.cards['gpu'].metric_widgets

                if 'temperature' in gpu:
                    gpu_card['temperature'].setText(f"{gpu['temperature']:.1f}")
                if 'utilization' in gpu:
                    gpu_card['utilization'].setText(f"{gpu['utilization']:.1f}")
                if 'memory_used' in gpu:
                    gpu_card['vram_used'].setText(f"{gpu['memory_used'] / 1024:.1f}")
                if 'memory_total' in gpu:
                    gpu_card['vram_total'].setText(f"{gpu['memory_total'] / 1024:.1f}")

            # Update storage metrics
            if 'storage' in metrics and metrics['storage'] and len(metrics['storage']) > 0:
                storage = metrics['storage'][0]  # Show first storage device
                storage_card = self.cards['storage'].metric_widgets

                if 'used' in storage:
                    storage_card['space_used'].setText(f"{storage['used'] / (1024 ** 3):.1f}")
                if 'total' in storage:
                    storage_card['space_total'].setText(f"{storage['total'] / (1024 ** 3):.1f}")

                if 'io_stats' in storage:
                    io = storage['io_stats']
                    if hasattr(io, 'read_bytes'):
                        storage_card['read_speed'].setText(f"{io.read_bytes / (1024 ** 2):.1f}")
                    if hasattr(io, 'write_bytes'):
                        storage_card['write_speed'].setText(f"{io.write_bytes / (1024 ** 2):.1f}")

        except Exception as e:
            self.logger.exception(f"Error updating metrics: {str(e)}")
            self.handle_error(f"Error updating metrics: {str(e)}")

    def toggle_monitoring(self) -> None:
        """Pause or resume monitoring"""
        if self.update_timer.isActive():
            self.update_timer.stop()
            self.pause_btn.setText("▶ Resume")
            self.status_label.setText("Monitoring Paused")
            self.status_label.setStyleSheet("color: #FFC107; font-size: 12px;")
            self.is_paused = True
            self.logger.debug("Hardware monitoring paused")
        else:
            self.update_timer.start()
            self.pause_btn.setText("❚❚ Pause")
            self.status_label.setText("Monitoring Active")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
            self.is_paused = False
            self.logger.debug("Hardware monitoring resumed")

    def handle_error(self, error_message: str) -> None:
        """Handle and display errors

        Args:
            error_message: Error message to display
        """
        self.status_label.setText("Error Occurred")
        self.status_label.setStyleSheet("color: #dc2626; font-size: 12px;")
        self.logger.error(f"Hardware monitor error: {error_message}")

    def closeEvent(self, event):
        """Clean up when window is closed"""
        if self.update_timer:
            self.update_timer.stop()
            self.logger.debug("Hardware monitor closed, timer stopped")
        event.accept()