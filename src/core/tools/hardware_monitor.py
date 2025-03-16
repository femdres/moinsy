# src/core/tools/hardware_monitor.py
"""Hardware monitoring tool that tracks system metrics."""

from PyQt6.QtCore import QObject, pyqtSignal
import psutil
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any, Union

from utils.system_utils import execute_command
from config import get_resource_path

# Setup module logger
logger = logging.getLogger(__name__)


class HardwareMonitor(QObject):
    """Hardware monitoring tool that tracks system metrics.

    This class provides real-time monitoring of system hardware including
    CPU, memory, GPU, storage, fans, and power consumption metrics.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    metrics_updated = pyqtSignal(dict)

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize hardware monitoring capabilities.

        Args:
            parent: Parent QObject for this monitor
        """
        super().__init__(parent)
        self.sensors_configured = False
        logger.debug("Hardware monitor initialized")
        self.ensure_dependencies()

    def ensure_dependencies(self) -> None:
        """Ensure required system packages are installed."""
        try:
            self.log_output.emit("Checking system dependencies...")
            logger.info("Checking hardware monitoring dependencies")

            # Check for lm-sensors
            result = subprocess.run(
                ["which", "sensors"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.log_output.emit("Installing lm-sensors...")
                logger.info("Installing lm-sensors package")

                subprocess.run(
                    ["sudo", "apt-get", "install", "-y", "lm-sensors"],
                    check=True
                )

                # Run sensors-detect to configure sensors
                self.log_output.emit("Configuring sensors...")
                logger.info("Running sensors-detect")

                subprocess.run(
                    ["sudo", "sensors-detect", "--auto"],
                    check=True
                )

            self.sensors_configured = True
            self.log_output.emit("Dependencies configured successfully")
            logger.info("Hardware monitoring dependencies configured successfully")

        except Exception as e:
            error_msg = f"Failed to configure dependencies: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            self.sensors_configured = False

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU metrics including temperature and frequency.

        Returns:
            Dictionary containing CPU metrics including:
            - frequency: current, min, max frequencies in MHz
            - usage_per_core: List of per-core CPU usage percentages
            - temperature: CPU temperature in degrees Celsius
        """
        try:
            # Get CPU frequency
            freq = psutil.cpu_freq()

            # Get per-core usage
            cpu_percent = psutil.cpu_percent(percpu=True)

            # Get CPU temperature using lm-sensors
            cpu_temp = None
            if self.sensors_configured:
                temp_output = execute_command(
                    ["sensors", "-j"],
                    return_output=True
                )

                if isinstance(temp_output, str):
                    temp_data = json.loads(temp_output)
                    # Extract CPU temperature
                    cpu_temp = self._extract_cpu_temp(temp_data)

            cpu_info = {
                "frequency": {
                    "current": freq.current if freq else 0,
                    "min": freq.min if freq else 0,
                    "max": freq.max if freq else 0
                },
                "usage_per_core": cpu_percent
            }

            if cpu_temp is not None:
                cpu_info["temperature"] = cpu_temp

            return cpu_info

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing CPU temperature data: {str(e)}")
            return {
                "frequency": {"current": 0, "min": 0, "max": 0},
                "usage_per_core": [],
                "error": "Failed to parse CPU data"
            }
        except Exception as e:
            error_msg = f"Error getting CPU info: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return {
                "frequency": {"current": 0, "min": 0, "max": 0},
                "usage_per_core": [],
                "error": str(e)
            }

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage and swap information.

        Returns:
            Dictionary containing memory and swap metrics in bytes
        """
        try:
            virtual_mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                "total": virtual_mem.total,
                "available": virtual_mem.available,
                "used": virtual_mem.used,
                "percent": virtual_mem.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent
            }

        except Exception as e:
            error_msg = f"Error getting memory info: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return {
                "error": f"Failed to retrieve memory information: {str(e)}"
            }

    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU metrics if available.

        Returns:
            Dictionary containing GPU metrics or error information
        """
        try:
            # Try to get NVIDIA GPU info using nvidia-smi
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                temp, util, mem_used, mem_total = result.stdout.strip().split(",")
                return {
                    "temperature": float(temp),
                    "utilization": float(util),
                    "memory_used": float(mem_used),
                    "memory_total": float(mem_total)
                }

            # If nvidia-smi fails, try to detect other GPUs (AMD, Intel)
            # This is a placeholder for future implementation
            logger.info("NVIDIA GPU not detected, checking for other GPUs")

            return {"error": "No GPU detected or drivers not installed"}

        except subprocess.SubprocessError as e:
            logger.warning(f"GPU detection error: {str(e)}")
            return {"error": "GPU detection failed"}
        except Exception as e:
            logger.error(f"Error getting GPU info: {str(e)}")
            return {"error": f"Error getting GPU info: {str(e)}"}

    def get_storage_info(self) -> List[Dict[str, Any]]:
        """Get storage devices information.

        Returns:
            List of dictionaries containing information for each storage device
        """
        try:
            storage_info = []

            # Get disk partitions
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)

                    # Get disk I/O statistics
                    disk_io = psutil.disk_io_counters(perdisk=True)
                    device_name = partition.device.split("/")[-1]

                    partition_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }

                    # Add IO stats if available
                    if disk_io and device_name in disk_io:
                        partition_info["io_stats"] = disk_io[device_name]

                    storage_info.append(partition_info)

                except PermissionError:
                    logger.warning(f"Permission denied for {partition.mountpoint}")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing partition {partition.mountpoint}: {str(e)}")
                    continue

            return storage_info

        except Exception as e:
            error_msg = f"Error getting storage info: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return []

    def get_fan_speeds(self) -> Dict[str, float]:
        """Get system fan speeds.

        Returns:
            Dictionary mapping fan names to speeds (RPM)
        """
        if not self.sensors_configured:
            return {}

        try:
            fan_output = execute_command(
                ["sensors", "-j"],
                return_output=True
            )

            if isinstance(fan_output, str):
                fan_data = json.loads(fan_output)
                return self._extract_fan_speeds(fan_data)
            return {}

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing fan data: {str(e)}")
            return {}
        except Exception as e:
            error_msg = f"Error getting fan speeds: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return {}

    def _extract_cpu_temp(self, sensor_data: Dict[str, Any]) -> Optional[float]:
        """Extract CPU temperature from sensors data.

        Args:
            sensor_data: JSON data from 'sensors -j' command

        Returns:
            CPU temperature in degrees Celsius or None if not found
        """
        try:
            # Look for common CPU temperature sensor names
            for device in sensor_data:
                if any(cpu_name in device.lower() for cpu_name in ["coretemp", "k10temp", "cpu_thermal"]):
                    # Get the first temperature reading
                    for key in sensor_data[device]:
                        if "temp1_input" in sensor_data[device][key]:
                            return sensor_data[device][key]["temp1_input"]
            return None

        except Exception as e:
            logger.warning(f"Error extracting CPU temperature: {str(e)}")
            return None

    def _extract_fan_speeds(self, sensor_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract fan speeds from sensors data.

        Args:
            sensor_data: JSON data from 'sensors -j' command

        Returns:
            Dictionary mapping fan names to speeds
        """
        fan_speeds = {}

        try:
            for device in sensor_data:
                # Look for fan readings
                for key in sensor_data[device]:
                    if "fan" in key.lower():
                        if "input" in sensor_data[device][key]:
                            fan_speeds[key] = sensor_data[device][key]["input"]
            return fan_speeds

        except Exception as e:
            logger.warning(f"Error extracting fan speeds: {str(e)}")
            return {}

    def get_power_info(self) -> Dict[str, Any]:
        """Get power consumption information if available.

        Returns:
            Dictionary containing power consumption metrics
        """
        if not self.sensors_configured:
            return {}

        try:
            power_output = execute_command(
                ["sensors", "-j"],
                return_output=True
            )

            if isinstance(power_output, str):
                power_data = json.loads(power_output)
                return self._extract_power_info(power_data)
            return {}

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing power data: {str(e)}")
            return {}
        except Exception as e:
            error_msg = f"Error getting power info: {str(e)}"
            self.error_occurred.emit(error_msg)
            logger.error(error_msg)
            return {}

    def _extract_power_info(self, sensor_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract power consumption from sensors data.

        Args:
            sensor_data: JSON data from 'sensors -j' command

        Returns:
            Dictionary containing power metrics
        """
        power_info = {}

        try:
            for device in sensor_data:
                # Look for power-related readings
                if any(power_name in device.lower() for power_name in ["power", "energy"]):
                    for key in sensor_data[device]:
                        if "power" in key.lower() and "input" in sensor_data[device][key]:
                            power_info[key] = sensor_data[device][key]["input"]
            return power_info

        except Exception as e:
            logger.warning(f"Error extracting power info: {str(e)}")
            return {}

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all hardware metrics.

        Returns:
            Dictionary containing all hardware metrics organized by component
        """
        logger.debug("Collecting all hardware metrics")
        metrics = {
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "gpu": self.get_gpu_info(),
            "storage": self.get_storage_info(),
            "fans": self.get_fan_speeds(),
            "power": self.get_power_info()
        }

        self.metrics_updated.emit(metrics)
        return metrics