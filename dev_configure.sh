#!/usr/bin/env bash
#
# Moinsy Development Configuration Script
# This script configures the Moinsy application for development
# Assumes the repo has been cloned directly to the installation location
#

# Set strict mode (can be disabled with --no-strict flag)
set -eo pipefail

# Script version
DEV_SCRIPT_VERSION="1.0.0"

# Default configuration
INSTALL_DIR="/opt/moinsy"
LOG_FILE="/tmp/moinsy-dev-setup-$(date +%Y%m%d-%H%M%S).log"
DESKTOP_FILE="/usr/share/applications/moinsy.desktop"
POLICY_FILE="/usr/share/polkit-1/actions/com.ubuntu.pkexec.moinsy.policy"
DEBUG=false
SKIP_VENV=false
STRICT_MODE=true
INSTALL_DEV_DEPS=false
SKIP_DEPS=false

# ANSI color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# =====================================================
# Utility functions
# =====================================================

# Print help/usage information
print_usage() {
    cat << EOF
${BOLD}Moinsy Development Configuration Script v${DEV_SCRIPT_VERSION}${NC}

${BOLD}USAGE:${NC}
    $0 [OPTIONS]

${BOLD}OPTIONS:${NC}
    -h, --help             Show this help message
    -d, --debug            Enable debug mode (verbose output)
    --install-dir=PATH     Specify installation directory (default: ${INSTALL_DIR})
    --skip-venv            Skip virtual environment creation
    --no-strict            Disable strict error handling
    --dev-deps             Install development dependencies
    --skip-deps            Skip installing any dependencies

${BOLD}EXAMPLES:${NC}
    $0 --debug                   # Run with debug logging
    $0 --install-dir=/opt/moinsy-dev   # Use custom installation directory
    $0 --dev-deps                # Install development dependencies

For development issues, please report at https://github.com/moinsy/moinsy/issues
EOF
}

# Parse command-line arguments
parse_args() {
    for arg in "$@"; do
        case $arg in
            -h|--help)
                print_usage
                exit 0
                ;;
            -d|--debug)
                DEBUG=true
                shift
                ;;
            --install-dir=*)
                INSTALL_DIR="${arg#*=}"
                shift
                ;;
            --skip-venv)
                SKIP_VENV=true
                shift
                ;;
            --no-strict)
                STRICT_MODE=false
                set +eo pipefail
                shift
                ;;
            --dev-deps)
                INSTALL_DEV_DEPS=true
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $arg${NC}"
                print_usage
                exit 1
                ;;
        esac
    done
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
        "DEV")
            echo -e "${CYAN}[DEV] ${message}${NC}"
            ;;
    esac
}

# Display banner
display_banner() {
    echo -e "${BLUE}${BOLD}"
    echo "======================================================"
    echo "      Moinsy Development Configuration v${DEV_SCRIPT_VERSION}"
    echo "======================================================"
    echo -e "${NC}"

    log "INFO" "Setting up Moinsy for development in: ${INSTALL_DIR}"
    log "INFO" "Log file: ${LOG_FILE}"
    log "DEV" "Development mode is active"

    if [[ "${DEBUG}" == "true" ]]; then
        log "DEBUG" "Debug mode enabled"
    fi

    if [[ "${SKIP_VENV}" == "true" ]]; then
        log "DEV" "Skipping virtual environment creation"
    fi

    if [[ "${INSTALL_DEV_DEPS}" == "true" ]]; then
        log "DEV" "Will install development dependencies"
    fi

    echo
}

# Check if running with root/sudo privileges
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log "WARNING" "This script needs to be run with sudo or as root"
        log "INFO" "Attempting to re-run with sudo..."

        # Get the full path of the script for reliable re-execution
        local script_path=$(readlink -f "$0")

        # Re-execute with sudo, preserving the arguments
        if sudo bash -c "'$script_path' $*"; then
            exit 0  # Exit after successful sudo execution
        else
            log "ERROR" "Failed to obtain sudo privileges"
            exit 1
        fi
    fi

    # Capture the real user for better permissions management
    REAL_USER="${SUDO_USER:-$USER}"
    REAL_USER_HOME=$(eval echo ~${REAL_USER})

    log "INFO" "Running with sufficient privileges as: ${REAL_USER}"
    log "DEBUG" "Real user home directory: ${REAL_USER_HOME}"
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
        if [[ "${STRICT_MODE}" == "true" ]]; then
            return 1
        fi
    fi

    log "DEBUG" "Command output: ${output}"

    if [[ -n "${success_msg}" ]]; then
        log "SUCCESS" "${success_msg}"
    fi

    return 0
}

# =====================================================
# Configuration functions
# =====================================================

# Check the installation directory
check_install_dir() {
    log "INFO" "Checking installation directory: ${INSTALL_DIR}"

    # Check if directory exists
    if [[ ! -d "${INSTALL_DIR}" ]]; then
        log "ERROR" "Installation directory not found: ${INSTALL_DIR}"
        log "INFO" "For development setup, clone the repository to ${INSTALL_DIR} first"
        exit 1
    fi

    # Check for key files
    if [[ ! -f "${INSTALL_DIR}/src/moinsy.py" ]]; then
        log "ERROR" "Moinsy source code not found in ${INSTALL_DIR}/src/"
        log "INFO" "Make sure you've cloned the repository correctly"
        exit 1
    fi

    log "SUCCESS" "Installation directory verified"
}

# Install system dependencies
install_dependencies() {
    if [[ "${SKIP_DEPS}" == "true" ]]; then
        log "INFO" "Skipping dependency installation as requested"
        return 0
    fi

    log "INFO" "Installing system dependencies..."

    # Update package lists
    execute "apt-get update -q" "Failed to update package lists" "Package lists updated"

    # Install basic dependencies
    local base_packages="python3 python3-pip python3-venv python3-dev"
    execute "apt-get install -y ${base_packages}" "Failed to install basic dependencies" "Basic dependencies installed"

    # Install development dependencies if requested
    if [[ "${INSTALL_DEV_DEPS}" == "true" ]]; then
        log "DEV" "Installing development dependencies..."
        local dev_packages="git python3-pytest python3-pytest-cov python3-virtualenv python3-sphinx flake8 pylint black"
        execute "apt-get install -y ${dev_packages}" "Failed to install development dependencies" "Development dependencies installed"
    fi
}

# Create username file
create_username() {
    log "INFO" "Creating username file..."

    # Create the username file
    execute "echo '${REAL_USER}' > ${INSTALL_DIR}/src/resources/texts/username.txt" "Failed to create username file" "Username file created with: ${REAL_USER}"
}

# Setup Python environment
setup_python_env() {
    if [[ "${SKIP_VENV}" == "true" ]]; then
        log "INFO" "Skipping Python environment setup as requested"
        return 0
    fi

    log "INFO" "Setting up Python environment..."

    # Create virtual environment
    execute "cd ${INSTALL_DIR}/src && python3 -m venv py-venv" "Failed to create virtual environment" "Virtual environment created"

    # Update pip
    execute "cd ${INSTALL_DIR}/src && ./py-venv/bin/pip install --upgrade pip" "Failed to upgrade pip" "Pip upgraded"

    # Install Python dependencies
    if [[ -f "${INSTALL_DIR}/requirements.py" ]]; then
        log "INFO" "Installing dependencies from requirements.py..."
        execute "cd ${INSTALL_DIR} && ./src/py-venv/bin/pip install -r requirements.py" "Failed to install requirements" "Requirements installed from requirements.py"
    elif [[ -f "${INSTALL_DIR}/src/requirements.py" ]]; then
        log "INFO" "Installing dependencies from src/requirements.py..."
        execute "cd ${INSTALL_DIR}/src && ./py-venv/bin/pip install -r requirements.py" "Failed to install requirements" "Requirements installed from src/requirements.py"
    else
        log "INFO" "No requirements file found, installing default packages..."
        execute "cd ${INSTALL_DIR}/src && ./py-venv/bin/pip install PyQt6 psutil humanize" "Failed to install Python packages" "Default Python packages installed"
    fi

    # Install development packages if needed
    if [[ "${INSTALL_DEV_DEPS}" == "true" ]]; then
        log "DEV" "Installing Python development packages..."
        execute "cd ${INSTALL_DIR}/src && ./py-venv/bin/pip install pytest pytest-cov sphinx sphinx-rtd-theme flake8 pylint black" "Failed to install Python dev packages" "Python development packages installed"
    fi
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

# Setup run script
setup_run_script() {
    log "INFO" "Setting up run script..."

    # Make sure run script is executable
    execute "chmod +x ${INSTALL_DIR}/run-moinsy.sh" "Failed to set run script permissions" "Run script permissions set"

    # Create development run script for easier debugging
    if [[ "${INSTALL_DEV_DEPS}" == "true" ]]; then
        log "DEV" "Creating development run script..."
        cat > "${INSTALL_DIR}/run-moinsy-dev.sh" << EOF
#!/bin/bash
# Development run script for Moinsy
# Auto-generated by dev_configure.sh

# Enable debug output
export DEBUG=true

# Use local developer environment
cd "${INSTALL_DIR}/src"
source py-venv/bin/activate

# Run without sudo for development (add sudo only when needed)
python3 moinsy.py --debug "\$@"

# Uncomment to run with sudo (when needed)
# sudo -E PYTHONPATH="${INSTALL_DIR}" python3 moinsy.py --debug "\$@"
EOF
        execute "chmod +x ${INSTALL_DIR}/run-moinsy-dev.sh" "Failed to set dev run script permissions" "Development run script created"
        log "DEV" "Development run script created at: ${INSTALL_DIR}/run-moinsy-dev.sh"
    fi
}

# Set correct permissions
set_permissions() {
    log "INFO" "Setting correct permissions..."

    # Set ownership to real user
    execute "chown -R ${REAL_USER}:${REAL_USER} ${INSTALL_DIR}" "Failed to set ownership" "Ownership set to ${REAL_USER}"

    # Set executable permissions on Python files
    execute "find ${INSTALL_DIR} -name '*.py' -exec chmod +x {} \;" "Failed to set Python files as executable" "Python files set as executable"
}

# Display development setup information
display_dev_info() {
    echo -e "\n${GREEN}${BOLD}========================================="
    echo "Moinsy Development Setup Complete!"
    echo -e "==========================================${NC}\n"

    echo "Moinsy has been configured for development."
    echo "Installation directory: ${INSTALL_DIR}"
    echo "Log file: ${LOG_FILE}"

    echo -e "\n${BOLD}Running Moinsy:${NC}"
    echo "   Production: ${INSTALL_DIR}/run-moinsy.sh"

    if [[ "${INSTALL_DEV_DEPS}" == "true" ]]; then
        echo "   Development: ${INSTALL_DIR}/run-moinsy-dev.sh"
    fi

    echo -e "\n${BOLD}Development Tools:${NC}"
    if [[ "${SKIP_VENV}" != "true" ]]; then
        echo "   Activate virtual environment: source ${INSTALL_DIR}/src/py-venv/bin/activate"
    fi

    if [[ "${INSTALL_DEV_DEPS}" == "true" ]]; then
        echo "   Run tests: cd ${INSTALL_DIR} && pytest"
        echo "   Check code style: cd ${INSTALL_DIR} && flake8"
        echo "   Format code: cd ${INSTALL_DIR} && black ."
    fi

    echo -e "\n${YELLOW}NOTE: For development, you may need to adjust permissions or use sudo for certain operations.${NC}"
}

# Main function
main() {
    # Start logging
    echo "Starting Moinsy development setup at $(date)" > "${LOG_FILE}"
    log "INFO" "Beginning Moinsy development setup v${DEV_SCRIPT_VERSION}"

    # Display banner
    display_banner

    # Check privileges
    check_privileges "$@"

    # Check installation directory
    check_install_dir

    # Install dependencies
    install_dependencies

    # Create username file
    create_username

    # Setup Python environment
    setup_python_env

    # Create launcher
    create_launcher

    # Create policy file
    create_policy

    # Setup run scripts
    setup_run_script

    # Set permissions
    set_permissions

    # Display development information
    display_dev_info

    log "SUCCESS" "Development setup completed successfully"
}

# Parse command-line arguments
parse_args "$@"

# Run main function
main "$@"