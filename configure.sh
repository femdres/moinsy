#!/usr/bin/env bash
#
# Moinsy Configuration Script
# This script sets up the Moinsy application environment
#

# Set strict mode
set -eo pipefail

# Script variables
SCRIPT_VERSION="1.0.1"
LOG_FILE="/tmp/moinsy-setup-$(date +%Y%m%d-%H%M%S).log"
INSTALL_DIR="/opt/moinsy"
DESKTOP_FILE="/usr/share/applications/moinsy.desktop"
POLICY_FILE="/usr/share/polkit-1/actions/com.ubuntu.pkexec.moinsy.policy"
REQUIRED_PACKAGES=("python3" "python3-pip" "python3-venv" "python3-dev")

# ANSI color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# =====================================================
# Utility functions
# =====================================================

# Display banner with script information
display_banner() {
    echo -e "${BLUE}${BOLD}"
    echo "======================================================"
    echo "          Moinsy Configuration Script v${SCRIPT_VERSION}"
    echo "======================================================"
    echo -e "${NC}"
    echo "This script will configure Moinsy on your system."
    echo "Log file: ${LOG_FILE}"
    echo
}

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Log to file
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"
    
    # Also display to console with colors for certain levels
    case "${level}" in
        "ERROR")
            echo -e "${RED}${BOLD}[ERROR] ${message}${NC}" >&2
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING] ${message}${NC}" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS] ${message}${NC}"
            ;;
        "INFO")
            echo -e "[INFO] ${message}"
            ;;
        "DEBUG")
            # Only print debug messages if debugging is enabled
            if [[ "${DEBUG}" == "true" ]]; then
                echo -e "${BLUE}[DEBUG] ${message}${NC}"
            fi
            ;;
    esac
}

# Check if running with root/sudo privileges
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log "WARNING" "This script needs to be run with sudo or as root"
        log "INFO" "Attempting to re-run with sudo..."
        
        # Get the full path of the script for reliable re-execution
        local script_path=$(readlink -f "$0")
        
        # Re-execute with sudo, preserving the real user's home directory
        if sudo bash -c "SOURCE_DIR='$SOURCE_DIR' '$script_path'"; then
            exit 0  # Exit after successful sudo execution
        else
            log "ERROR" "Failed to obtain sudo privileges"
            exit 1
        fi
    fi
    
    log "INFO" "Running with sufficient privileges"
}

# Check required commands
check_requirements() {
    log "INFO" "Checking system requirements..."
    
    # Check for apt (only runs on Debian/Ubuntu based systems)
    if ! command -v apt-get &> /dev/null; then
        log "ERROR" "This script requires apt-get. Only Debian/Ubuntu based systems are supported."
        exit 1
    fi
    
    # Check for other required commands
    for cmd in "wget" "mkdir" "chmod"; do
        if ! command -v "${cmd}" &> /dev/null; then
            log "ERROR" "Required command not found: ${cmd}"
            exit 1
        fi
    done
    
    log "SUCCESS" "System requirements check passed"
}

# Check if directory exists and is not empty
check_source_dir() {
    if [[ ! -d "${SOURCE_DIR}" ]]; then
        log "ERROR" "Source directory not found: ${SOURCE_DIR}"
        echo -e "\nPlease make sure Moinsy is downloaded to ${SOURCE_DIR}"
        exit 1
    fi

    # Check if the directory contains the expected files
    if [[ ! -f "${SOURCE_DIR}/src/moinsy.py" ]]; then
        log "ERROR" "Moinsy source code not found in ${SOURCE_DIR}"
        echo -e "\nThe source directory does not contain the expected files."
        exit 1
    fi
    
    log "INFO" "Source directory verified: ${SOURCE_DIR}"
}

# Execute command with error handling
execute() {
    local cmd="$1"
    local error_msg="$2"
    local success_msg="$3"
    
    log "DEBUG" "Executing: ${cmd}"
    
    # Execute the command and capture output
    local output
    if ! output=$(eval "${cmd}" 2>&1); then
        log "ERROR" "${error_msg}"
        log "ERROR" "Command output: ${output}"
        return 1
    fi
    
    log "DEBUG" "Command output: ${output}"
    
    if [[ -n "${success_msg}" ]]; then
        log "SUCCESS" "${success_msg}"
    fi
    
    return 0
}

# =====================================================
# Main installation functions
# =====================================================

# Install required packages
install_dependencies() {
    log "INFO" "Installing required packages..."
    
    # Update package lists
    execute "apt-get update -q" "Failed to update package lists" "Package lists updated"
    
    # Install required packages
    local packages_str="${REQUIRED_PACKAGES[*]}"
    execute "apt-get install -y ${packages_str}" "Failed to install required packages" "Required packages installed"
}

# Move files to installation directory
move_files() {
    log "INFO" "Moving files to installation directory..."
    
    # Create installation directory if it doesn't exist
    if [[ ! -d "${INSTALL_DIR}" ]]; then
        execute "mkdir -p ${INSTALL_DIR}" "Failed to create installation directory" "Installation directory created"
    fi
    
    # Copy files
    execute "cp -r ${SOURCE_DIR}/* ${INSTALL_DIR}/" "Failed to copy files to installation directory" "Files copied to installation directory"
    
    # Set permissions - use the real user who ran sudo
    local real_user="${SUDO_USER:-$USER}"
    execute "chown -R ${real_user}:${real_user} ${INSTALL_DIR}" "Failed to set permissions" "Permissions set for user: ${real_user}"
}

# Create username file
create_username() {
    log "INFO" "Creating username file..."
    
    # Get the actual user who ran sudo
    local real_user="${SUDO_USER:-$USER}"
    
    # Create the username file
    execute "echo '${real_user}' > ${INSTALL_DIR}/src/resources/texts/username.txt" "Failed to create username file" "Username file created with: ${real_user}"
}

# Create desktop launcher
create_launcher() {
    log "INFO" "Creating application launcher..."
    
    # Check if desktop file exists
    if [[ -f "${DESKTOP_FILE}" ]]; then
        log "INFO" "Launcher already exists. Replacing..."
    fi
    
    # Copy the desktop file
    execute "cp -f ${INSTALL_DIR}/src/resources/desktops/moinsy.desktop ${DESKTOP_FILE}" "Failed to create launcher" "Application launcher created"
    
    # Make it executable
    execute "chmod +x ${DESKTOP_FILE}" "Failed to set launcher permissions" "Launcher permissions set"
}

# Create policy file
create_policy() {
    log "INFO" "Creating authentication policy..."
    
    # Check if policy file exists
    if [[ -f "${POLICY_FILE}" ]]; then
        log "INFO" "Policy already exists. Replacing..."
    fi
    
    # Copy the policy file
    execute "cp -f ${INSTALL_DIR}/src/resources/policies/com.ubuntu.pkexec.moinsy.policy ${POLICY_FILE}" "Failed to create authentication policy" "Authentication policy created"
}

# Create Python virtual environment
create_environment() {
    log "INFO" "Creating Python virtual environment..."
    
    # Set up the virtual environment
    execute "cd ${INSTALL_DIR}/src && python3 -m venv py-venv" "Failed to create virtual environment" "Virtual environment created"
    
    # Install required Python packages
    log "INFO" "Installing Python packages (this may take a moment)..."
    
    execute "cd ${INSTALL_DIR}/src && ./py-venv/bin/pip install --upgrade pip" "Failed to upgrade pip" "Pip upgraded"
    
    # Check for requirements file in different locations
    if [[ -f "${INSTALL_DIR}/requirements.py" ]]; then
        # Requirements at root level
        execute "cd ${INSTALL_DIR} && ./src/py-venv/bin/pip install -r requirements.py" "Failed to install Python requirements" "Python packages installed from requirements.py"
    elif [[ -f "${INSTALL_DIR}/src/requirements.py" ]]; then
        # Requirements in src directory
        execute "cd ${INSTALL_DIR}/src && ./py-venv/bin/pip install -r requirements.py" "Failed to install Python requirements" "Python packages installed from requirements.py"
    else
        # Otherwise install the individual packages
        log "INFO" "No requirements file found, installing default packages"
        execute "cd ${INSTALL_DIR}/src && ./py-venv/bin/pip install PyQt6 psutil humanize" "Failed to install Python packages" "Python packages installed"
    fi
}

# Create run script
create_run_script() {
    log "INFO" "Setting up run script..."
    
    # Make sure run script is executable
    execute "chmod +x ${INSTALL_DIR}/run-moinsy.sh" "Failed to set run script permissions" "Run script permissions set"
}

# Display final information
display_completion() {
    echo -e "\n${GREEN}${BOLD}============================"
    echo "Moinsy Setup Complete!"
    echo -e "============================${NC}\n"
    
    echo "Moinsy has been successfully installed on your system."
    echo "Installation directory: ${INSTALL_DIR}"
    echo "Log file: ${LOG_FILE}"
    echo -e "\n${BOLD}You can launch Moinsy from your applications menu or by running:${NC}"
    echo "   ${INSTALL_DIR}/run-moinsy.sh"
    echo -e "\n${YELLOW}NOTE: You may need to restart your system or session before running Moinsy for the first time.${NC}"
}

# Clean up temporary files
cleanup() {
    log "INFO" "Performing cleanup..."
    
    # Nothing to clean up for now
    log "DEBUG" "No cleanup tasks defined"
}

# Main function
main() {
    # Determine the source directory
    # If we're running with sudo, use the original user's home directory for the source path
    if [[ -n "$SUDO_USER" ]]; then
        local user_home=$(eval echo ~${SUDO_USER})
        # Use SOURCE_DIR if passed from the non-sudo invocation
        SOURCE_DIR=${SOURCE_DIR:-"$user_home/Downloads/moinsy"}
    else
        # Normal execution without sudo
        SOURCE_DIR=${SOURCE_DIR:-"$HOME/Downloads/moinsy"}
    fi
    
    # Start logging
    echo "Starting Moinsy configuration at $(date)" > "${LOG_FILE}"
    log "INFO" "Beginning Moinsy setup process v${SCRIPT_VERSION}"
    log "DEBUG" "Source directory set to: ${SOURCE_DIR}"
    
    # Display banner
    display_banner
    
    # Verify we're running with sufficient privileges
    check_privileges
    
    # Check requirements
    check_requirements
    
    # Check source directory
    check_source_dir
    
    # Install dependencies
    install_dependencies
    
    # Move files
    move_files
    
    # Create username file
    create_username
    
    # Create launcher
    create_launcher
    
    # Create policy
    create_policy
    
    # Create Python environment
    create_environment
    
    # Create run script
    create_run_script
    
    # Update packages
    log "INFO" "Updating system packages..."
    execute "apt-get upgrade -y" "Failed to upgrade system packages" "System packages upgraded"
    
    # Cleanup
    cleanup
    
    # Log completion
    log "SUCCESS" "Configuration completed successfully"
    
    # Display completion message
    display_completion
}

# Call main function
main "$@"
