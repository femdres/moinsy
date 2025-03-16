#!/bin/bash

move_moinsy() {
    # Move the entire moinsy directory to /opt
    printf "Moving files...\n"
    sudo mv /home/$USER/Downloads/moinsy /opt
    sudo chown -R $USER:$USER /opt/moinsy
}

create_username() {
    # Store username for installer use
    printf "\nFetching username...\n"
    printf "$USER" > /opt/moinsy/src/resources/texts/username.txt
}

create_launcher() {
    printf "\nCreating launcher..."
    if [ -f "/usr/share/applications/moinsy.desktop" ]; then
        printf "\nMoinsy launcher already exists.\nReplacing...\n"
        sudo cp -f /opt/moinsy/src/resources/desktops/moinsy.desktop /usr/share/applications/moinsy.desktop
    else
        sudo cp /opt/moinsy/src/resources/desktops/moinsy.desktop /usr/share/applications
        printf "\nMoinsy launcher has been created.\n"
    fi
}

create_policy() {
    printf "\nCreating policy..."
    if [ -f "/usr/share/polkit-1/actions/com.ubuntu.pkexec.moinsy.policy" ]; then
        printf "\nMoinsy authentication policy already exists.\nReplacing...\n"
        sudo cp -f /opt/moinsy/src/resources/policies/com.ubuntu.pkexec.moinsy.policy /usr/share/polkit-1/actions/com.ubuntu.pkexec.moinsy.policy
    else
        sudo cp /opt/moinsy/src/resources/policies/com.ubuntu.pkexec.moinsy.policy /usr/share/polkit-1/actions
        printf "\nMoinsy authentication policy has been created.\n"
    fi
}

create_environment() {
    printf "\nCreating Python environment...\n"
    # Install Python and required packages
    sudo apt-get install python3 python3-pip python3-venv -y
    
    # Create and activate virtual environment
    cd /opt/moinsy/src
    python3 -m venv py-venv
    source py-venv/bin/activate
    
    # Install required Python packages
    pip install PyQt6 psutil humanize
}

move_moinsy

create_username

create_launcher

create_policy

create_environment

printf "\nUpdating packages...\n"
sudo apt-get update -y

printf "\nUpgrading packages...\n"
sudo apt-get upgrade -y

printf "\nConfiguration complete. You may now exit.\n"
printf "Ensure the Moinsy launcher is in the menu, then reboot your system\n"
printf "before running the application.\n\n"
