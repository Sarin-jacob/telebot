# Telebot

Telebot is a Telegram user bot that automates various tasks such as creating channels, adding bots to channels, scheduling commands, and more.
Commands are given through a specified channel.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [Update](#update)
## Installation

To install the necessary packages, run the following command:

```bash
curl -sOL "https://raw.githubusercontent.com/Sarin-jacob/telebot/main/install.sh" && source ./install.sh
```
Note: The script will run for the first time and asks for telegram login. Once login is successful, use `ctlt+C` to exit. The script will run automatically from next restart or you can manualy start it using 
```bash
systemctl --user start telebot
```
## Configuration

Before running the bot, you need to configure it with your Telegram API credentials. The configuration file `telebot.cnf` will be created during the first run if it does not exist.

The configuration file should look like this:

```cnf
TELEGRAM_DAEMON_API_ID=your_api_id
TELEGRAM_DAEMON_API_HASH=your_api_hash
TELEGRAM_DAEMON_CHANNEL=your_channel_id
BOT_TOKEN=bot_token(optional)
```
## Usage

Use the following `systemctl` commands to manage the telebot service:

- **Start the bot:** `systemctl --user start telebot`
- **Stop the bot:** `systemctl --user stop telebot`
- **Restart the bot:** `systemctl --user restart telebot`
- **Check the status of the bot:** `systemctl --user status telebot`

## Commands

This script contains the following commands and their usage:

0. `cmd`: list all the commands. Usage: cmd
1. `cmdr, <command>`: run a command on the system. Usage: cmdr, <command>
2. `channelz`: create a channel with a profile picture and add The Botz. Usage: channelz
3. `roast`: restart the telebot service. Usage: roast
4. `sen:`: send a file to the sender. Usage: sen: <file_path>
5. `delch`: delete channels with specific keywords. Usage: delch <keywords to be added, separated by space>
6. `sd:`: schedule a command to be sent multiple times. Usage: sd:<command> ev:<interval in minutes> fr:<times>
7. `mov <Moviename year>`: send movie added message with button to update channel. Usage: mov <name>
8. `ser <Seriesname season>`: send series added message with button to update channel. Usage: ser <name>
9. `update`: update to the telebot script. Usage: update

## Update

To update the telebot script, you can use the following command:

```bash
cd ~/telebot
curl -sOL "https://raw.githubusercontent.com/Sarin-jacob/telebot/main/telebot.py"
systemctl --user restart telebot
```
##### OR 
execute the following command in the Telegram daemon channel:

```
update
```

This command will download the latest version of the telebot script from the GitHub repository and update your local installation.

Please note that you should always backup your configuration file before performing an update to avoid any potential data loss.
