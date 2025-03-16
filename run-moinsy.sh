#!/bin/bash
# Enhanced run-moinsy.sh - improved error handling and diagnostics

# Define paths
MOINSY_ROOT="/opt/moinsy"
VENV_PATH="$MOINSY_ROOT/src/py-venv"
MOINSY_SCRIPT="$MOINSY_ROOT/src/moinsy.py"
LOG_FILE="/tmp/moinsy-startup.log"

# Timestamp helper function
timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

# Log helper function
log() {
  echo "$(timestamp) - $1" | tee -a "$LOG_FILE"
}

# Error logging with traceback
error() {
  echo "$(timestamp) - ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# Create log file
echo "=== Moinsy startup log $(timestamp) ===" > "$LOG_FILE"
log "Starting Moinsy..."

# Check if paths exist
if [ ! -d "$MOINSY_ROOT" ]; then
  error "Moinsy root directory not found: $MOINSY_ROOT"
  exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
  error "Python virtual environment not found: $VENV_PATH"
  exit 1
fi

if [ ! -f "$MOINSY_SCRIPT" ]; then
  error "Moinsy main script not found: $MOINSY_SCRIPT"
  exit 1
fi

# Check for display server (for graphical applications)
if [ -z "$DISPLAY" ]; then
  error "No display server detected. DISPLAY variable is not set."
  exit 1
fi

# Check XAUTHORITY
if [ -z "$XAUTHORITY" ]; then
  log "XAUTHORITY not set, using default ~/.Xauthority"
  export XAUTHORITY="$HOME/.Xauthority"
fi

# Activate virtual environment
log "Activating Python virtual environment..."
source "$VENV_PATH/bin/activate" || {
  error "Failed to activate virtual environment"
  exit 1
}

# Log Python and PyQt version
log "Python version: $(python3 --version 2>&1)"
python3 -c "import sys; print('Python path:', sys.path)" >> "$LOG_FILE" 2>&1
python3 -c "from PyQt6 import QtCore; print('PyQt6 version:', QtCore.QT_VERSION_STR)" >> "$LOG_FILE" 2>&1 || {
  error "Failed to import PyQt6, check installation"
}

# Run Moinsy with elevated privileges and with PYTHONPATH set to include src directory
log "Running Moinsy..."
command="pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY PYTHONPATH=$MOINSY_ROOT $VENV_PATH/bin/python3 $MOINSY_SCRIPT"

# Log command for debugging
log "Executing: $command"

# Execute with error handling
$command

# Capture exit code
exit_code=$?

if [ $exit_code -ne 0 ]; then
  error "Moinsy exited with code $exit_code. Check the log file for details: $LOG_FILE"
else
  log "Moinsy completed successfully"
fi

# Deactivate virtual environment
deactivate

exit $exit_code