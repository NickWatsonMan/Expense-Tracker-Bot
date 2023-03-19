# Expense-Tracker-Bot
One Day Code Sunday Project

This is a Telegram bot that helps you track your expenses and stay within your daily spending limit.

# Getting Started
To use the bot, follow these steps:

1. Install the required dependencies using pip install -r requirements.txt
2. Create a Telegram bot and get the API token.
3. Replace BOT_TOKEN with your bot API token in the expense_bot.py file.
4. Run the expense_bot.py file to start the bot.

# Usage
The bot supports the following commands:

/start - starts the bot and displays a welcome message.  
/setlimit <amount> - sets your daily spending limit. Replace <amount> with your daily limit.  
/checklimit - checks your current spending limit and when it expires.  
/addexpense <amount> - adds an expense to your tracker. Replace <amount> with the amount spent.  
/checkexpenses - displays a list of all your expenses.  
/showuserdata - displays all your user data, including your limit, daily limit, daily spent amount, and when the data was last updated.  

# Features
Sets a daily limit and calculates daily spending limit automatically.  
Checks the daily spending limit and alerts the user if they have exceeded the limit.  
Records all expenses and displays a list of all expenses recorded.  
Stores user data in a dictionary for easy access and display.  
Calculates the daily limit and expiration date and stores the data in the user dictionary.  
Displays all user data in a formatted message.  

# Built With
Python  
python-telegram-bot - The Python wrapper for the Telegram Bot API  
