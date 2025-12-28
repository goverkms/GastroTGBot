# Telegram Bot - Gastroshop Bali

## Overview
A Telegram bot for Gastroshop Bali that helps users place orders. The bot collects user contact information and provides a link to the web app for ordering.

## Project Structure
- `bot.py` - Main bot application
- `requirements.txt` - Python dependencies

## How It Works
1. User starts the bot with `/start` command
2. Bot prompts user to share their phone number
3. After sharing, user info is sent to a Telegram channel
4. User receives a button to open the Gastroshop web app

## Environment Variables
- `TELEGRAM_BOT_TOKEN` - Required. Get from @BotFather on Telegram

## Running the Bot
The bot runs using polling mode and requires no web server. Simply run:
```
python bot.py
```

## Deployment
This bot is configured for VM-style deployment since it needs to run continuously for polling.
