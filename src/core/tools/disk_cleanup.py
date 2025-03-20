#!/usr/bin/env python3
"""
Disk Cleanup Tool for removing unnecessary files and freeing system space.

Like a digital entropy reducer battling the inevitable accumulation of
informational detritus, this module scours the filesystem for unnecessary
artifacts - temporary fragments, cached duplications, and abandoned logs -
all in service of the transient illusion of order in the digital void.
"""

from PyQt6.QtCore import QObject, pyqtSignal
import os
import shutil
import subprocess
import logging
import re
import json
from typing import Dict, List, Optional, Tuple, Set, Union, Any
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CleanupResult:
    """
    Result of a cleanup operation.

    Like the accountant's ledger of our digital exorcism,
    this structure tallies what was discovered and removed.
    """
    target_id: str
    target_name: str
    scanned: bool = False
    cleaned: bool = False
    error: Optional[str] = None
    items_found: int = 0
    items_removed: int = 0
    space_found: int = 0  # In bytes
    space_freed: int = 0  # In bytes

    @property
    def space_found_formatted(self) -> str:
        """Get human-readable format of space found."""
        return self._format_bytes(self.space_found)

    @property
    def space_freed_formatted(self) -> str:
        """Get human-readable format of space freed."""
        return self._format_bytes(self.space_freed)

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable format."""
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.1f} KB"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"


class CleanupCategory(Enum):
    """
    Categories of cleanup operations.

    Like chapters in our digital decluttering narrative,
    these categories organize our systematic erasure into
    comprehensible domains of purging.
    """
    TEMPORARY = auto()
    PACKAGE_CACHE = auto()
    LOGS = auto()
    APPLICATION_CACHE = auto()
    TRASH = auto()
    OLD_KERNELS = auto()
    CUSTOM = auto()

@dataclass
class CleanupTarget:
    """
    A specific location or file pattern that can be cleaned.

    Like a digital gravestone marking where bits once lived,
    this structure identifies spaces for systematic erasure.
    """
    id: str
    name: str
    description: str
    path: str  # Can be a specific path or a pattern
    requires_sudo: bool = False
    can_scan: bool = True
    can_remove: bool = True
    dangerous: bool = False  # Requires extra confirmation
    recursive: bool = True
    pattern: Optional[str] = None  # For pattern-based matching
    age_days: Optional[int] = None  # For age-based cleanup
    # Don't auto-expand path in post_init - we'll handle it with custom logic
    _path_expanded: bool = False  # Track if path has been expanded with the correct user

    def __post_init__(self) -> None:
        """Validate the cleanup target after initialization."""
        # Format path for consistency, but DON'T expand ~ yet
        self.path = self.path.strip()

        # Ensure ID is valid
        if not self.id or not isinstance(self.id, str):
            raise ValueError("Cleanup target must have a valid ID")

class DiskCleanup(QObject):
    """
    Disk Cleanup Tool for scanning and removing unnecessary files.

    Like a digital sanitation worker collecting the accumulated waste
    products of computing, this class methodically identifies and
    removes the byproducts of software entropy - the inevitable digital
    detritus that accumulates in our finite storage spaces.
    """

    # Signal definitions for GUI communication
    update_progress = pyqtSignal(int)
    log_output = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    scan_complete = pyqtSignal(dict)  # Emits scan results as dict
    cleanup_complete = pyqtSignal(dict)  # Emits cleanup results as dict
    request_input = pyqtSignal(str, str)  # For confirmation prompts

    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize the disk cleanup tool with proper logging and signal setup.

        Args:
            parent: Parent QObject for this tool
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Initialize internal state
        self._targets: Dict[str, CleanupTarget] = {}
        self._results: Dict[str, CleanupResult] = {}
        self._categories: Dict[CleanupCategory, List[str]] = {cat: [] for cat in CleanupCategory}
        self._selected_targets: Set[str] = set()
        self._username: Optional[str] = None

        # Get the real username first thing
        self._username = self._get_real_username()

        # Configure cleanup targets
        self._configure_cleanup_targets()

        self.logger.debug(f"Disk Cleanup tool initialized with username '{self._username}'")

    def _get_real_username(self) -> str:
        """
        Determine the actual username from username.txt.

        Returns:
            Username as string, or a safe fallback

        Like an existential detective searching for the true identity of
        the digital self, this method scours the filesystem for clues to
        the user's existence, knowing full well that in the end, we're all
        just patterns of bits pretending to have meaning.
        """
        try:
            # Define possible locations for the username file in order of preference
            possible_locations = [
                # Standard Moinsy installation location
                "/opt/moinsy/src/resources/texts/username.txt",

                # Development environment locations
                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "resources", "texts", "username.txt"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "..", "resources", "texts", "username.txt"),
            ]

            # Attempt to read the username from each location
            for location in possible_locations:
                try:
                    if os.path.exists(location) and os.path.isfile(location):
                        self.logger.debug(f"Checking username file at: {location}")
                        with open(location, 'r') as f:
                            username = f.read().strip()
                            if username:
                                self.logger.info(f"Found username '{username}' from {location}")
                                return username
                except (IOError, PermissionError) as e:
                    self.logger.warning(f"Could not read username file at {location}: {e}")
                    continue

            # If we get here, we couldn't find/read the username file
            # Try to get username from environment as fallback
            import getpass
            import os

            # Try SUDO_USER first (original user when using sudo)
            sudo_user = os.environ.get('SUDO_USER')
            if sudo_user:
                self.logger.warning(f"Username file not found, using SUDO_USER: {sudo_user}")
                return sudo_user

            # Try USER environment variable
            env_user = os.environ.get('USER')
            if env_user and env_user != 'root':
                self.logger.warning(f"Username file not found, using USER env: {env_user}")
                return env_user

            # Last resort: use getpass
            current_user = getpass.getuser()
            if current_user != 'root':
                self.logger.warning(f"Username file not found, using getpass: {current_user}")
                return current_user

            # If even that fails or returns root, use a safe hardcoded fallback
            self.logger.error("Could not determine real username, using fallback")
            return "user"  # Safe fallback

        except Exception as e:
            self.logger.error(f"Error determining username: {str(e)}", exc_info=True)
            return "user"  # Safe fallback on any exception

    def _resolve_path(self, path: str) -> str:
        """
        Resolve paths containing tilde to use the correct username.

        Args:
            path: Path string potentially containing a tilde

        Returns:
            Path with tilde expanded to the correct home directory

        Like a weary translator converting between the symbolic and literal,
        this method transforms the abstract notation of home into concrete
        filesystem paths - replacing the universally recognized '~' with
        the specificity of a particular user's digital abode.
        """
        if not path or not isinstance(path, str):
            return path

        # Skip if no tilde or already processed
        if '~' not in path:
            return path

        # Replace tilde with actual home directory for the correct user
        expanded_path = path.replace('~', f'/home/{self._username}', 1)
        self.logger.debug(f"Expanded path: {path} → {expanded_path}")
        return expanded_path

    def _configure_cleanup_targets(self) -> None:
        """
        Configure the available cleanup targets with proper path resolution.

        Like a cartographer mapping the landscape of digital decay,
        this method defines the territories of unnecessary data
        that our cleanup expeditions will explore.
        """
        # Temporary Files
        self._add_target(
            CleanupTarget(
                id="temp_files",
                name="Temporary Files",
                description="System temporary files in /tmp directory",
                path="/tmp",
                requires_sudo=True,
                pattern="*",
                age_days=7  # Files older than 7 days
            ),
            CleanupCategory.TEMPORARY
        )

        self._add_target(
            CleanupTarget(
                id="user_temp_files",
                name="User Temporary Files",
                description="User temporary files in ~/tmp",
                path="~/tmp",  # Will be properly expanded in _add_target
                pattern="*",
                age_days=7  # Files older than 7 days
            ),
            CleanupCategory.TEMPORARY
        )

        # Package Caches
        self._add_target(
            CleanupTarget(
                id="apt_cache",
                name="APT Cache",
                description="Cached package files from APT",
                path="/var/cache/apt/archives",
                requires_sudo=True,
                pattern="*.deb",
            ),
            CleanupCategory.PACKAGE_CACHE
        )

        self._add_target(
            CleanupTarget(
                id="flatpak_cache",
                name="Flatpak Cache",
                description="Cached Flatpak application data",
                path="~/.cache/flatpak",  # Will be properly expanded in _add_target
            ),
            CleanupCategory.PACKAGE_CACHE
        )

        self._add_target(
            CleanupTarget(
                id="snap_cache",
                name="Snap Cache",
                description="Cached Snap package data",
                path="/var/lib/snapd/cache",
                requires_sudo=True,
            ),
            CleanupCategory.PACKAGE_CACHE
        )

        # Application Caches
        self._add_target(
            CleanupTarget(
                id="browser_cache",
                name="Browser Cache",
                description="Browser cached data (Firefox, Chrome)",
                path="~/.cache/mozilla",  # Will be properly expanded in _add_target
            ),
            CleanupCategory.APPLICATION_CACHE
        )

        self._add_target(
            CleanupTarget(
                id="chrome_cache",
                name="Chrome Cache",
                description="Google Chrome cached data",
                path="~/.cache/google-chrome",  # Will be properly expanded in _add_target
            ),
            CleanupCategory.APPLICATION_CACHE
        )

        # Logs
        self._add_target(
            CleanupTarget(
                id="system_logs",
                name="System Logs",
                description="System log files older than 30 days",
                path="/var/log",
                requires_sudo=True,
                pattern="*.log.*",
                age_days=30
            ),
            CleanupCategory.LOGS
        )

        self._add_target(
            CleanupTarget(
                id="journal_logs",
                name="Journal Logs",
                description="Systemd journal logs",
                path="/var/log/journal",
                requires_sudo=True,
                can_scan=False,  # Use journalctl to scan/clean
                can_remove=False  # Use journalctl to clean
            ),
            CleanupCategory.LOGS
        )

        # Trash
        self._add_target(
            CleanupTarget(
                id="user_trash",
                name="User Trash",
                description="Items in the user's trash",
                path="~/.local/share/Trash",  # Will be properly expanded in _add_target
            ),
            CleanupCategory.TRASH
        )

        # Old Kernels
        self._add_target(
            CleanupTarget(
                id="old_kernels",
                name="Old Kernels",
                description="Old kernel packages",
                path="",  # No path, handled by special logic
                requires_sudo=True,
                can_scan=False,  # Special scan using apt
                can_remove=False,  # Special cleanup using apt
                dangerous=True,  # Requires extra care
            ),
            CleanupCategory.OLD_KERNELS
        )

    def _add_target(self, target: CleanupTarget, category: CleanupCategory) -> None:
        """
        Add a cleanup target to the available targets with proper path resolution.

        Args:
            target: The cleanup target to add
            category: Category for the target
        """
        # Resolve path with correct username before adding
        if '~' in target.path:
            target.path = self._resolve_path(target.path)
            target._path_expanded = True  # Mark path as already expanded

        self._targets[target.id] = target
        self._categories[category].append(target.id)
        self._results[target.id] = CleanupResult(
            target_id=target.id,
            target_name=target.name
        )

        # Log the properly resolved path for debugging
        self.logger.debug(f"Added target '{target.name}' with path: {target.path}")

    def _scan_path(self, target: CleanupTarget) -> None:
        """
        Scan a filesystem path to identify cleanable items and space.

        Args:
            target: Cleanup target to scan

        Like a digital archaeologist carefully examining the artifacts of
        computation past, this method surveys the filesystem for remnants
        that have outlived their usefulness - each file an echo of some
        long-forgotten action, now reduced to mere bytes awaiting deletion.
        """
        # Double-check path is properly expanded, just to be sure
        if not target._path_expanded and '~' in target.path:
            target.path = self._resolve_path(target.path)
            target._path_expanded = True
            self.logger.debug(f"Late path expansion for {target.name}: {target.path}")

        result = self._results[target.id]

        # Skip if path doesn't exist
        if not os.path.exists(target.path):
            self.logger.debug(f"Path does not exist, skipping: {target.path}")
            return

    def get_cleanup_targets(self) -> Dict[CleanupCategory, List[Dict[str, Any]]]:
        """
        Get all cleanup targets organized by category.

        Returns:
            Dictionary mapping categories to lists of target information

        Like a catalog of potential digital purges, this method
        provides an organized inventory of the filesystem artifacts
        that could be eliminated to reclaim space.
        """
        result: Dict[CleanupCategory, List[Dict[str, Any]]] = {}

        for category, target_ids in self._categories.items():
            target_list = []
            for target_id in target_ids:
                target = self._targets.get(target_id)
                if target:
                    # Get result for this target if available
                    result_data = {}
                    if target_id in self._results:
                        cleanup_result = self._results[target_id]
                        result_data = {
                            "scanned": cleanup_result.scanned,
                            "items_found": cleanup_result.items_found,
                            "space_found": cleanup_result.space_found,
                            "space_found_formatted": cleanup_result.space_found_formatted,
                            "cleaned": cleanup_result.cleaned,
                            "space_freed": cleanup_result.space_freed,
                            "space_freed_formatted": cleanup_result.space_freed_formatted,
                            "error": cleanup_result.error
                        }

                    target_list.append({
                        "id": target.id,
                        "name": target.name,
                        "description": target.description,
                        "requires_sudo": target.requires_sudo,
                        "dangerous": target.dangerous,
                        "can_scan": target.can_scan,
                        "can_remove": target.can_remove,
                        **result_data
                    })

            if target_list:
                result[category] = target_list

        return result

    def scan_disk_space(self) -> None:
        """
        Scan disk space usage and report available cleanup targets.

        Like a digital archaeologist surveying the layers of accumulated
        data sediment, this method calculates how much space can be
        reclaimed from each category of system detritus.
        """
        self.logger.info("Starting disk space scan")
        self.log_output.emit("Starting disk space scan...")
        self.update_progress.emit(0)

        # Reset all scan results
        for target_id in self._targets:
            self._results[target_id] = CleanupResult(
                target_id=target_id,
                target_name=self._targets[target_id].name
            )

        # Calculate total targets for progress tracking
        total_targets = len(self._targets)
        processed_targets = 0

        # Scan each target
        for target_id, target in self._targets.items():
            try:
                self.log_output.emit(f"Scanning {target.name}...")

                # Skip targets that can't be scanned
                if not target.can_scan:
                    # Handle special cases
                    if target_id == "old_kernels":
                        self._scan_old_kernels(target)
                    elif target_id == "journal_logs":
                        self._scan_journal_logs(target)
                    else:
                        self.logger.warning(f"Skipping scan for {target.name} - no scan method available")
                else:
                    # Normal path-based scan
                    self._scan_path(target)

                # Update progress after each target
                processed_targets += 1
                progress = int((processed_targets / total_targets) * 90)  # Save 10% for summary
                self.update_progress.emit(progress)

            except Exception as e:
                error_msg = f"Error scanning {target.name}: {str(e)}"
                self.error_occurred.emit(error_msg)
                self.logger.error(error_msg, exc_info=True)

                # Update result with error
                self._results[target_id] = CleanupResult(
                    target_id=target_id,
                    target_name=target.name,
                    error=str(e)
                )

        # Generate summary
        total_space = sum(result.space_found for result in self._results.values())

        if total_space > 0:
            self.log_output.emit("\n—— Scan Complete ——")
            self.log_output.emit(f"Total space that can be freed: {self._format_bytes(total_space)}")

            # Emit detailed results by category
            for category in CleanupCategory:
                category_targets = self._categories.get(category, [])
                if not category_targets:
                    continue

                category_space = sum(self._results[target_id].space_found for target_id in category_targets)
                if category_space > 0:
                    category_name = category.name.replace("_", " ").title()
                    self.log_output.emit(f"\n{category_name}: {self._format_bytes(category_space)}")

                    # List individual items with significant space
                    for target_id in category_targets:
                        result = self._results[target_id]
                        if result.space_found > 1024 * 1024:  # Only show items > 1MB
                            self.log_output.emit(f"  • {result.target_name}: {result.space_found_formatted}")
        else:
            self.log_output.emit("\nNo unnecessary files found to clean up.")

        # Complete progress
        self.update_progress.emit(100)

        # Emit scan_complete signal with results
        self.scan_complete.emit(self._get_results_dict())
        self.logger.info("Disk space scan completed")

    def _scan_old_kernels(self, target: CleanupTarget) -> None:
        """
        Scan for old kernels that can be safely removed.

        Args:
            target: Old kernels cleanup target
        """
        result = self._results[target.id]

        try:
            # Get current kernel version
            current_kernel = self._run_command(
                ["uname", "-r"],
                "Failed to determine current kernel version"
            )

            if not isinstance(current_kernel, str) or not current_kernel.strip():
                raise RuntimeError("Could not determine current kernel version")

            current_kernel = current_kernel.strip()
            self.logger.debug(f"Current kernel: {current_kernel}")

            # List all installed kernel packages
            kernel_list = self._run_command(
                ["dpkg", "--list", "linux-image-*", "linux-headers-*"],
                "Failed to list kernel packages"
            )

            if not isinstance(kernel_list, str):
                raise RuntimeError("Could not list installed kernel packages")

            # Parse kernel list to find old ones
            old_kernels = []
            total_size = 0

            # Each line in kernel_list should start with 'ii' for installed packages
            for line in kernel_list.split('\n'):
                if line.startswith('ii'):
                    parts = line.split()
                    if len(parts) >= 2:
                        package_name = parts[1]

                        # Check if it's a kernel package and not the current one
                        if ('linux-image' in package_name or 'linux-headers' in package_name) \
                                and current_kernel not in package_name:
                            # Get package size
                            size_output = self._run_command(
                                ["dpkg-query", "-W", "-f=${Installed-Size}", package_name],
                                f"Failed to get size of {package_name}"
                            )

                            if isinstance(size_output, str) and size_output.strip().isdigit():
                                # Size is in KB, convert to bytes
                                package_size = int(size_output.strip()) * 1024
                                old_kernels.append((package_name, package_size))
                                total_size += package_size

            # Update result
            result.scanned = True
            result.items_found = len(old_kernels)
            result.space_found = total_size

            self.logger.debug(f"Found {len(old_kernels)} old kernels, {self._format_bytes(total_size)}")

        except Exception as e:
            self.logger.error(f"Error scanning for old kernels: {str(e)}")
            raise RuntimeError(f"Failed to scan for old kernels: {str(e)}") from e

    def _scan_journal_logs(self, target: CleanupTarget) -> None:
        """
        Scan systemd journal logs to determine disk usage.

        Args:
            target: Journal logs cleanup target

        Like an archaeologist deciphering the enigmatic runes of systemd's
        cryptic outputs, this method attempts to parse the arcane metrics
        of journal space consumption - a task made all the more Sisyphean
        by the whimsical formatting choices of our daemon overlords.
        """
        result = self._results[target.id]

        try:
            # Get journal disk usage
            usage_output = self._run_command(
                ["sudo", "journalctl", "--disk-usage"],
                "Failed to get journal disk usage"
            )

            if not isinstance(usage_output, str) or not usage_output.strip():
                raise RuntimeError("Could not determine journal disk usage")

            self.logger.debug(f"Journal usage output: {usage_output}")

            # Parse the output - format can be either:
            # "Archived and active journals take up X.Y MB on disk."
            # or "Archived and active journals take up X.Y MB in the file system."
            # Try multiple patterns to be resilient
            match = re.search(r'take up (\d+\.?\d*)\s*([KMG])B', usage_output)

            if match:
                size_str, unit = match.groups()
                size_float = float(size_str)

                # Convert to bytes
                if unit == "K":
                    total_size = int(size_float * 1024)
                elif unit == "M":
                    total_size = int(size_float * 1024 * 1024)
                elif unit == "G":
                    total_size = int(size_float * 1024 * 1024 * 1024)
                else:
                    total_size = int(size_float)

                # Update result
                result.scanned = True
                result.items_found = 1  # Just counting as one item since it's a log collection
                result.space_found = total_size

                self.logger.debug(f"Journal size: {self._format_bytes(total_size)}")
            else:
                self.logger.warning(f"Could not parse journal disk usage: {usage_output}")

                # Fallback: try to extract just any number followed by a unit as last resort
                fallback_match = re.search(r'(\d+\.?\d*)\s*([KMG])B', usage_output)
                if fallback_match:
                    self.logger.debug("Using fallback parsing for journal size")
                    size_str, unit = fallback_match.groups()
                    size_float = float(size_str)

                    # Convert to bytes
                    if unit == "K":
                        total_size = int(size_float * 1024)
                    elif unit == "M":
                        total_size = int(size_float * 1024 * 1024)
                    elif unit == "G":
                        total_size = int(size_float * 1024 * 1024 * 1024)
                    else:
                        total_size = int(size_float)

                    # Update result
                    result.scanned = True
                    result.items_found = 1
                    result.space_found = total_size
                    self.logger.debug(f"Journal size (fallback parse): {self._format_bytes(total_size)}")
                else:
                    raise RuntimeError("Could not determine journal disk usage")

        except Exception as e:
            self.logger.error(f"Error scanning journal logs: {str(e)}")
            raise RuntimeError(f"Failed to scan journal logs: {str(e)}") from e

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """
        Check if filename matches the given pattern.

        Args:
            filename: Filename to check
            pattern: Pattern to match against (glob style)

        Returns:
            True if filename matches pattern, False otherwise
        """
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)

    def _is_old_enough(self, file_path: str, age_days: int) -> bool:
        """
        Check if a file is older than the specified number of days.

        Args:
            file_path: Path to the file to check
            age_days: Minimum age in days

        Returns:
            True if file is older than age_days, False otherwise
        """
        try:
            modified_time = os.path.getmtime(file_path)
            modified_date = datetime.fromtimestamp(modified_time)
            current_date = datetime.now()

            # Calculate age in days
            age_delta = current_date - modified_date
            return age_delta.days >= age_days

        except (OSError, PermissionError):
            # If we can't access the file, assume it's not old enough
            return False

    def set_selected_targets(self, target_ids: List[str]) -> None:
        """
        Set which targets are selected for cleanup.

        Args:
            target_ids: List of target IDs to clean

        Like a curator selecting exhibits for removal, this method
        identifies which digital artifacts have been deemed dispensable,
        marking them for the upcoming purge.
        """
        self._selected_targets = set(target_ids)
        self.logger.debug(f"Selected {len(self._selected_targets)} targets for cleanup")

    def cleanup_selected(self) -> None:
        """
        Clean up the selected targets.

        Like a digital sanitation worker executing the purge of
        unnecessary bits, this method methodically removes the
        selected data fragments, freeing up space for future
        computational activities.
        """
        if not self._selected_targets:
            self.log_output.emit("No cleanup targets selected.")
            return

        self.logger.info(f"Starting cleanup of {len(self._selected_targets)} targets")
        self.log_output.emit("\n—— Starting Cleanup ——")
        self.update_progress.emit(0)

        # Reset cleanup status in results
        for target_id in self._selected_targets:
            if target_id in self._results:
                result = self._results[target_id]
                result.cleaned = False
                result.items_removed = 0
                result.space_freed = 0
                result.error = None

        # Calculate total targets for progress tracking
        total_targets = len(self._selected_targets)
        processed_targets = 0
        total_freed = 0

        # Clean each selected target
        for target_id in self._selected_targets:
            try:
                target = self._targets.get(target_id)
                if not target:
                    self.logger.warning(f"Unknown target ID: {target_id}")
                    continue

                self.log_output.emit(f"Cleaning {target.name}...")

                # Check if target needs special handling
                if not target.can_remove:
                    # Handle special cases
                    if target_id == "old_kernels":
                        self._cleanup_old_kernels(target)
                    elif target_id == "journal_logs":
                        self._cleanup_journal_logs(target)
                    else:
                        self.logger.warning(f"No cleanup method available for {target.name}")
                        continue
                else:
                    # Standard path-based cleanup
                    self._cleanup_path(target)

                # Update progress
                processed_targets += 1
                progress = int((processed_targets / total_targets) * 90)  # Save 10% for final processing
                self.update_progress.emit(progress)

                # Update total freed space
                if target_id in self._results:
                    result = self._results[target_id]
                    if result.cleaned and result.space_freed > 0:
                        total_freed += result.space_freed
                        self.log_output.emit(f"  Freed {result.space_freed_formatted}")

            except Exception as e:
                error_msg = f"Error cleaning {target.name}: {str(e)}"
                self.error_occurred.emit(error_msg)
                self.logger.error(error_msg, exc_info=True)

                # Update result with error
                if target_id in self._results:
                    self._results[target_id].error = str(e)

        # Generate summary
        self.log_output.emit("\n—— Cleanup Complete ——")
        if total_freed > 0:
            self.log_output.emit(f"Total space freed: {self._format_bytes(total_freed)}")
        else:
            self.log_output.emit("No space was freed during cleanup.")

        # Update progress to complete
        self.update_progress.emit(100)

        # Emit cleanup_complete signal with results
        self.cleanup_complete.emit(self._get_results_dict())
        self.logger.info(f"Cleanup completed, freed {self._format_bytes(total_freed)}")

    def _cleanup_path(self, target: CleanupTarget) -> None:
        """
        Clean up a filesystem path by removing files.

        Args:
            target: Cleanup target to process
        """
        result = self._results[target.id]

        # Skip if path doesn't exist
        if not os.path.exists(target.path):
            self.logger.debug(f"Path does not exist, skipping: {target.path}")
            return

        items_removed = 0
        space_freed = 0

        try:
            # Check if this is a directory or file
            if os.path.isdir(target.path):
                if target.requires_sudo:
                    # Use sudo to remove files
                    find_cmd = ["sudo", "find", target.path]

                    # Add age filter if specified
                    if target.age_days:
                        find_cmd.extend(["-mtime", f"+{target.age_days}"])

                    # Add pattern filter if specified
                    if target.pattern:
                        find_cmd.extend(["-name", target.pattern])

                    # Add type filter (files only)
                    find_cmd.extend(["-type", "f"])

                    # Get sizes before deletion for tracking
                    du_cmd = find_cmd.copy()
                    du_cmd.extend(["-exec", "du", "-b", "{}", ";"])

                    sizes_output = self._run_command(
                        du_cmd,
                        f"Failed to get sizes for {target.name}"
                    )

                    # Parse sizes output to estimate space freed
                    if isinstance(sizes_output, str):
                        for line in sizes_output.strip().split('\n'):
                            if line:
                                parts = line.split()
                                if parts and parts[0].isdigit():
                                    space_freed += int(parts[0])
                                    items_removed += 1

                    # Delete the files
                    delete_cmd = find_cmd.copy()
                    delete_cmd.extend(["-delete"])

                    self._run_command(
                        delete_cmd,
                        f"Failed to clean {target.name}"
                    )
                else:
                    # Walk directory to find and remove files
                    for root, dirs, files in os.walk(target.path, topdown=False):
                        # Skip if not recursive and not at the top level
                        if not target.recursive and root != target.path:
                            continue

                        for file in files:
                            file_path = os.path.join(root, file)

                            # Check pattern if specified
                            if target.pattern and not self._match_pattern(file, target.pattern):
                                continue

                            # Check age if specified
                            if target.age_days and not self._is_old_enough(file_path, target.age_days):
                                continue

                            # Get file size before removal
                            try:
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                items_removed += 1
                                space_freed += file_size
                            except (OSError, PermissionError) as e:
                                self.logger.warning(f"Cannot remove {file_path}: {str(e)}")
            else:
                # Single file path
                if (not target.pattern or self._match_pattern(target.path, target.pattern)) and \
                        (not target.age_days or self._is_old_enough(target.path, target.age_days)):
                    try:
                        file_size = os.path.getsize(target.path)
                        os.remove(target.path)
                        items_removed += 1
                        space_freed += file_size
                    except (OSError, PermissionError) as e:
                        if target.requires_sudo:
                            # Try with sudo
                            file_size_output = self._run_command(
                                ["sudo", "du", "-b", target.path],
                                f"Failed to get size of {target.path}"
                            )

                            if isinstance(file_size_output, str) and file_size_output.strip():
                                parts = file_size_output.strip().split()
                                if parts and parts[0].isdigit():
                                    space_freed = int(parts[0])
                                    items_removed = 1

                            # Remove with sudo
                            self._run_command(
                                ["sudo", "rm", "-f", target.path],
                                f"Failed to remove {target.path}"
                            )
                        else:
                            self.logger.warning(f"Cannot remove {target.path}: {str(e)}")
                            raise

            # Update result
            result.cleaned = True
            result.items_removed = items_removed
            result.space_freed = space_freed

            self.logger.debug(f"Cleaned {target.name}: {items_removed} items, {self._format_bytes(space_freed)}")

        except (PermissionError, OSError) as e:
            self.logger.error(f"Cleanup error for {target.name}: {str(e)}")
            raise RuntimeError(f"Cannot clean {target.name}: {str(e)}") from e

    def _cleanup_old_kernels(self, target: CleanupTarget) -> None:
        """
        Remove old kernels from the system.

        Args:
            target: Old kernels cleanup target
        """
        result = self._results[target.id]

        try:
            # Get current kernel version
            current_kernel = self._run_command(
                ["uname", "-r"],
                "Failed to determine current kernel version"
            )

            if not isinstance(current_kernel, str) or not current_kernel.strip():
                raise RuntimeError("Could not determine current kernel version")

            current_kernel = current_kernel.strip()

            # List all installed kernel packages
            kernel_list = self._run_command(
                ["dpkg", "--list", "linux-image-*", "linux-headers-*"],
                "Failed to list kernel packages"
            )

            if not isinstance(kernel_list, str):
                raise RuntimeError("Could not list installed kernel packages")

            # Find old kernel packages
            old_kernels = []
            total_size = 0

            for line in kernel_list.split('\n'):
                if line.startswith('ii'):
                    parts = line.split()
                    if len(parts) >= 2:
                        package_name = parts[1]

                        # Check if it's a kernel package and not the current one
                        if ('linux-image' in package_name or 'linux-headers' in package_name) \
                                and current_kernel not in package_name:
                            # Get package size
                            size_output = self._run_command(
                                ["dpkg-query", "-W", "-f=${Installed-Size}", package_name],
                                f"Failed to get size of {package_name}"
                            )

                            if isinstance(size_output, str) and size_output.strip().isdigit():
                                # Size is in KB, convert to bytes
                                package_size = int(size_output.strip()) * 1024
                                old_kernels.append((package_name, package_size))
                                total_size += package_size

            # Remove old kernels
            if old_kernels:
                # Use apt to remove packages
                package_list = [pkg[0] for pkg in old_kernels]

                # Execute the removal
                self._run_command(
                    ["sudo", "apt-get", "remove", "--purge", "-y"] + package_list,
                    "Failed to remove old kernels"
                )

                # Run autoremove to clean up any dependencies
                self._run_command(
                    ["sudo", "apt-get", "autoremove", "-y"],
                    "Failed to clean up kernel dependencies"
                )

                # Update result
                result.cleaned = True
                result.items_removed = len(old_kernels)
                result.space_freed = total_size
            else:
                self.logger.info("No old kernels found to remove")

        except Exception as e:
            self.logger.error(f"Error removing old kernels: {str(e)}")
            raise RuntimeError(f"Failed to remove old kernels: {str(e)}") from e

    def _cleanup_journal_logs(self, target: CleanupTarget) -> None:
        """
        Clean up systemd journal logs.

        Args:
            target: Journal logs cleanup target

        Like a digital mortician preparing the remains of dead logs for
        their final journey into the /dev/null beyond, this method
        vacuums the journal - that most verbose of storytellers,
        chronicling the mundane tragedies of daemon lifecycles with
        a thoroughness that would make Proust blush.
        """
        result = self._results[target.id]

        try:
            # Get journal size before cleanup
            initial_usage = self._run_command(
                ["sudo", "journalctl", "--disk-usage"],
                "Failed to get journal disk usage"
            )

            # Parse initial usage
            initial_size = 0
            if isinstance(initial_usage, str):
                match = re.search(r'take up (\d+\.?\d*)\s*([KMG])B', initial_usage)
                if match:
                    size_str, unit = match.groups()
                    size_float = float(size_str)

                    # Convert to bytes
                    if unit == "K":
                        initial_size = int(size_float * 1024)
                    elif unit == "M":
                        initial_size = int(size_float * 1024 * 1024)
                    elif unit == "G":
                        initial_size = int(size_float * 1024 * 1024 * 1024)
                    else:
                        initial_size = int(size_float)
                else:
                    # Fallback parsing
                    fallback_match = re.search(r'(\d+\.?\d*)\s*([KMG])B', initial_usage)
                    if fallback_match:
                        size_str, unit = fallback_match.groups()
                        size_float = float(size_str)

                        # Convert to bytes
                        if unit == "K":
                            initial_size = int(size_float * 1024)
                        elif unit == "M":
                            initial_size = int(size_float * 1024 * 1024)
                        elif unit == "G":
                            initial_size = int(size_float * 1024 * 1024 * 1024)
                        else:
                            initial_size = int(size_float)

            # Vacuum the journal (clean older entries)
            self._run_command(
                ["sudo", "journalctl", "--vacuum-time=7d"],
                "Failed to clean journal logs"
            )

            # Get journal size after cleanup
            final_usage = self._run_command(
                ["sudo", "journalctl", "--disk-usage"],
                "Failed to get journal disk usage after cleanup"
            )

            # Parse final usage
            final_size = 0
            if isinstance(final_usage, str):
                match = re.search(r'take up (\d+\.?\d*)\s*([KMG])B', final_usage)
                if match:
                    size_str, unit = match.groups()
                    size_float = float(size_str)

                    # Convert to bytes
                    if unit == "K":
                        final_size = int(size_float * 1024)
                    elif unit == "M":
                        final_size = int(size_float * 1024 * 1024)
                    elif unit == "G":
                        final_size = int(size_float * 1024 * 1024 * 1024)
                    else:
                        final_size = int(size_float)
                else:
                    # Fallback parsing
                    fallback_match = re.search(r'(\d+\.?\d*)\s*([KMG])B', final_usage)
                    if fallback_match:
                        size_str, unit = fallback_match.groups()
                        size_float = float(size_str)

                        # Convert to bytes
                        if unit == "K":
                            final_size = int(size_float * 1024)
                        elif unit == "M":
                            final_size = int(size_float * 1024 * 1024)
                        elif unit == "G":
                            final_size = int(size_float * 1024 * 1024 * 1024)
                        else:
                            final_size = int(size_float)

            # Calculate space freed
            space_freed = max(0, initial_size - final_size)

            # Update result
            result.cleaned = True
            result.items_removed = 1  # Just counting as one operation
            result.space_freed = space_freed

            self.logger.debug(f"Cleaned journal logs: freed {self._format_bytes(space_freed)}")

        except Exception as e:
            self.logger.error(f"Error cleaning journal logs: {str(e)}")
            raise RuntimeError(f"Failed to clean journal logs: {str(e)}") from e

    def _run_command(self, command: List[str], error_message: str = "") -> Union[str, int]:
        """
        Execute a system command and handle its output.

        Args:
            command: Command list to execute
            error_message: Custom error message on failure

        Returns:
            Command output as string if successful, or exit code on failure

        Raises:
            RuntimeError: If command execution fails
        """
        try:
            self.logger.debug(f"Running command: {' '.join(command)}")
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            return process.stdout

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed ({e.returncode}): {e.stderr}")

            if error_message:
                # Add more context to the error
                raise RuntimeError(f"{error_message}: {e.stderr}") from e
            return e.returncode

        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")

            if error_message:
                raise RuntimeError(f"{error_message}: {str(e)}") from e
            return 1

    def _format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes into human-readable format.

        Args:
            bytes_value: Number of bytes to format

        Returns:
            Human-readable string representation
        """
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.1f} KB"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"

    def _get_results_dict(self) -> Dict[str, Any]:
        """
        Convert results to a serializable dictionary.

        Returns:
            Dictionary with all results
        """
        results_dict = {
            "targets": {},
            "categories": {},
            "total_found": 0,
            "total_space_found": 0,
            "total_cleaned": 0,
            "total_space_freed": 0
        }

        # Convert target results
        for target_id, result in self._results.items():
            results_dict["targets"][target_id] = {
                "id": result.target_id,
                "name": result.target_name,
                "scanned": result.scanned,
                "cleaned": result.cleaned,
                "error": result.error,
                "items_found": result.items_found,
                "items_removed": result.items_removed,
                "space_found": result.space_found,
                "space_freed": result.space_freed,
                "space_found_formatted": result.space_found_formatted,
                "space_freed_formatted": result.space_freed_formatted
            }

            # Add to totals
            results_dict["total_found"] += result.items_found
            results_dict["total_space_found"] += result.space_found

            if result.cleaned:
                results_dict["total_cleaned"] += result.items_removed
                results_dict["total_space_freed"] += result.space_freed

        # Add formatted versions of totals
        results_dict["total_space_found_formatted"] = self._format_bytes(results_dict["total_space_found"])
        results_dict["total_space_freed_formatted"] = self._format_bytes(results_dict["total_space_freed"])

        # Add category summaries
        for category, target_ids in self._categories.items():
            category_name = category.name.lower()
            category_found = sum(self._results[tid].items_found for tid in target_ids if tid in self._results)
            category_space = sum(self._results[tid].space_found for tid in target_ids if tid in self._results)
            category_cleaned = sum(self._results[tid].items_removed for tid in target_ids if
                                   tid in self._results and self._results[tid].cleaned)
            category_freed = sum(self._results[tid].space_freed for tid in target_ids if
                                 tid in self._results and self._results[tid].cleaned)

            results_dict["categories"][category_name] = {
                "items_found": category_found,
                "space_found": category_space,
                "items_cleaned": category_cleaned,
                "space_freed": category_freed,
                "space_found_formatted": self._format_bytes(category_space),
                "space_freed_formatted": self._format_bytes(category_freed)
            }

        return results_dict