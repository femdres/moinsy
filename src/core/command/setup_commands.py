"""Module for setting up command resources and directory structure."""

import os
import json
import logging
import shutil
from typing import Optional, Dict, Any, List


def setup_commands_directory(logger: Optional[logging.Logger] = None) -> str:
    """
    Create the directory structure for commands.json and copy the file there if needed.
    This should be called during application initialization.

    Args:
        logger: Optional logger instance

    Returns:
        Path to the commands.json file
    """
    # Setup logger if not provided
    if logger is None:
        logger = logging.getLogger(__name__)

    # Get base directory (src directory)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Path to commands.json
    commands_json_path = os.path.join(base_dir, "resources", "data", "commands.json")

    # Check if file already exists
    if not os.path.exists(commands_json_path):
        logger.info(f"Creating commands.json at {commands_json_path}")

        # Create a basic JSON structure with example commands
        example_commands = {
            "categories": [
                {
                    "id": "navigation",
                    "name": "Navigation",
                    "icon": "🧭",
                    "commands": [
                        {
                            "name": "cd",
                            "description": "Change the current working directory to a specified path. If no directory is specified, changes to the user's home directory.",
                            "syntax": "cd [options] [directory]",
                            "options": [
                                {"flag": "-L", "description": "Follow symbolic links (default behavior)"},
                                {"flag": "-P",
                                 "description": "Use physical directory structure without following symbolic links"},
                                {"flag": "-e", "description": "Exit with status 1 if the directory does not exist"},
                                {"flag": "--help", "description": "Display help information and exit"}
                            ],
                            "examples": [
                                {"command": "cd /home/user/Documents",
                                 "description": "Change to the Documents directory"},
                                {"command": "cd ..", "description": "Move up one directory level"},
                                {"command": "cd ~", "description": "Change to home directory"},
                                {"command": "cd -", "description": "Change to previous directory"}
                            ]
                        },
                        {
                            "name": "ls",
                            "description": "List directory contents with information about the files and directories.",
                            "syntax": "ls [options] [file/directory]",
                            "options": [
                                {"flag": "-a",
                                 "description": "Show all files including hidden files (starting with .)"},
                                {"flag": "-l",
                                 "description": "Use long listing format with permissions and ownership details"},
                                {"flag": "-h", "description": "Print file sizes in human-readable format"}
                            ],
                            "examples": [
                                {"command": "ls", "description": "List files in the current directory"},
                                {"command": "ls -la", "description": "List all files in long format"},
                                {"command": "ls -lh /var/log",
                                 "description": "List files in /var/log with human-readable sizes"}
                            ]
                        }
                    ]
                },
                {
                    "id": "system",
                    "name": "System Management",
                    "icon": "⚙️",
                    "commands": [
                        {
                            "name": "systemctl",
                            "description": "Control the systemd system and service manager. Used to manage system services.",
                            "syntax": "systemctl [options] command [unit]",
                            "options": [
                                {"flag": "--user",
                                 "description": "Run as user service manager, not system service manager"},
                                {"flag": "--system", "description": "Run as system service manager (default)"}
                            ],
                            "examples": [
                                {"command": "systemctl status apache2",
                                 "description": "Check status of Apache web server"},
                                {"command": "systemctl restart networking", "description": "Restart networking service"}
                            ]
                        }
                    ]
                }
            ]
        }

        try:
            # Write example commands to file
            with open(commands_json_path, 'w') as f:
                json.dump(example_commands, f, indent=2)

            logger.info("Successfully created commands.json with example data")
        except Exception as e:
            logger.error(f"Failed to write commands.json: {str(e)}")
            raise
    else:
        logger.debug(f"Commands.json already exists at {commands_json_path}")

    return commands_json_path


if __name__ == "__main__":
    # This allows running this file directly to set up the commands.json
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    setup_commands_directory(logger)
    print("Commands directory setup complete!")