#!/bin/bash
set +x
# Create a directory named 'telebot' in the user's home directory
mkdir -p ~/telebot

# Change the current directory to 'telebot'
cd ~/telebot
touch keywords.txt
echo "Downloading files to ~/telebot.."
curl -sOL "https://github.com/Sarin-jacob/files/releases/download/telebot/telebot.py"
curl -sOL "https://github.com/Sarin-jacob/files/releases/download/telebot/telebot.service"
# Copy the telebot.service file to the systemd user directory
sudo cp ./telebot.service /etc/systemd/user/

# Reload the systemd daemon to recognize the new service
echo "Reloading systemd daemon..."
systemctl --user daemon-reload

# Enable the telebot.service to start on boot
echo "Enabling telebot.service..."
systemctl --user enable telebot.service 

echo "installing python-is-python3 package"
sudo apt install python-is-python3 -y
# Install the telethon package using pip
echo "Installing telethon package..."
pip install -q telethon 2>/dev/null
if [ $? -ne 0 ]; then
    # If pip install fails, install python3-telethon using apt
    echo "pip install failed, installing python3-telethon using apt..."
    sudo apt update -qq
    sudo apt install -qq -y python3-telethon
fi

# Run the telebot.py script (this script contains a while loop and does not end)
echo "Running telebot.py script..."
python ./telebot.py