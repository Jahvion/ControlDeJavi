# ControlDeJavi - Telegram Bot for Product Expiration Tracking

## Overview
A Flask-based Telegram bot server that manages product inventory with expiration tracking and sends daily notifications at 22:00 Argentina time (ART/UTC-3).

## Purpose
Track products across five categories and receive automated alerts before expiration dates to prevent stock waste.

## Current State
Initial setup complete with Flask server, Telegram bot integration, and scheduled notifications.

## Recent Changes
- **2025-11-06**: Initial project creation
  - Installed Flask, python-telegram-bot, APScheduler
  - Created project structure with modular components
  - Implemented JSON-based storage system
  - Set up REST API endpoints for product management
  - Configured daily notifications at 22:00 Argentina time

## Project Architecture

### Categories
Products are organized into five categories:
- Gaseosas (Soft drinks)
- Aguas (Water)
- Chocolates
- Alfajores
- Golosinas (Candy/Snacks)

### Expiration Alerts
The bot sends notifications at the following intervals before expiration:
- 30 days
- 15 days
- 7 days
- 4 days
- 3 days
- 2 days
- 1 day

### Components
1. **app.py**: Main Flask application with REST API endpoints
2. **bot.py**: Telegram bot handler and message sending
3. **scheduler.py**: APScheduler configuration for daily notifications
4. **storage.py**: JSON-based product storage management
5. **data/products.json**: Persistent product data storage

### API Endpoints
- `GET /`: Health check and API information
- `POST /products`: Add a new product
- `GET /products`: List all products or filter by category
- `DELETE /products/<id>`: Delete a product by ID

### Environment Variables Required
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID for receiving notifications

## Setup Instructions
1. Create a Telegram bot via @BotFather and get the bot token
2. Get your chat ID by messaging @userinfobot
3. Add the TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as secrets
4. Run the application

## User Preferences
- Language: Spanish (Argentina)
- Timezone: America/Argentina/Buenos_Aires (UTC-3)
- Notification time: 22:00 daily
