"""
Disk Cleanup Tool module for identifying and removing unnecessary files to free up space.

Like a digital custodian perpetually battling the inexorable accumulation of
computational debris, this module provides the necessary tools for eliminating
the artifacts of prior calculations - a temporary reprieve from the inevitability
of filled storage, yet another form of digital mortality.
"""

from core.tools.disk_cleanup import DiskCleanup, CleanupCategory, CleanupTarget, CleanupResult

__all__ = ['DiskCleanup', 'CleanupCategory', 'CleanupTarget', 'CleanupResult']