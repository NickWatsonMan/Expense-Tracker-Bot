import telegram
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Replace YOUR_BOT_TOKEN with your actual bot token
BOT_TOKEN = ''

# Dictionary to store user data
user_data = {}

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, welcome to my bot!")

def set_limit(update, context):
    user_id = update.effective_chat.id

    # Check if limit is provided in the command
    if len(context.args) == 0:
        context.bot.send_message(chat_id=user_id, text="Please provide a limit.")
        return

    limit = context.args[0]

    # Calculate daily limit
    limit_float = float(limit)
    num_days = 30
    day_limit = round(limit_float / num_days, 2)

    # Store limit and expiration date for user
    user_data[user_id] = {
        'limit': limit,
        'expiration_date': (datetime.datetime.now() + datetime.timedelta(days=30)).date(),
        'day_limit': day_limit,
        'day_spent': 0,
        'expenses': [],
        'updated_date': datetime.datetime.now()
    }

    context.bot.send_message(chat_id=user_id, text=f"Your limit has been set to {limit}. It will expire on {user_data[user_id]['expiration_date']}.")


def check_limit(update, context):
    user_id = update.effective_chat.id

    # Check if user has a limit set and if it's still valid
    if user_id in user_data and user_data[user_id]['expiration_date'] > datetime.datetime.now():
        updated_date = user_data[user_id]['updated_date'].date()
        if updated_date < datetime.datetime.now().date():
            recalculate_day_limit(update, context, 1)

        limit = user_data[user_id]['limit']
        expiration_date = user_data[user_id]['expiration_date']
        context.bot.send_message(chat_id=user_id, text=f"Your limit is {limit}. Until {expiration_date}")
    else:
        context.bot.send_message(chat_id=user_id, text="You don't have a limit set or it has expired. Please set a new limit using /setlimit.")

def add_expense(update, context):
    user_id = update.effective_chat.id

    updated_date = user_data[user_id]['updated_date'].date()
    if updated_date < datetime.datetime.now().date():
        recalculate_day_limit(update, context, 1)

    # Check if expense and amount are provided in the command
    if len(context.args) < 1:
        context.bot.send_message(chat_id=user_id, text="Please provide an expense amount.")
        return

    amount = context.args[0]

    # Store expense and amount for user
    user_data[user_id]['expenses'].append({
        'amount': amount,
        'timestamp': datetime.datetime.now()
    })

    # Update Day Spent Amount
    user_data[user_id]['day_spent'] = int(user_data[user_id]['day_spent']) + int(amount)

    # Check Day Limit
    if user_data[user_id]['day_spent'] > user_data[user_id]['day_limit']:
        recalculate_day_limit(update, context)
        context.bot.send_message(chat_id=user_id, text=f"You have exceeded the limit. So the daily limit was recalculated. You don't have money to spend today.")

    else:
        context.bot.send_message(chat_id=user_id, text=f"Expense of {amount} has been added.")

def check_expenses(update, context):
    user_id = update.effective_chat.id
    
    updated_date = user_data[user_id]['updated_date'].date()
    if updated_date < datetime.datetime.now().date():
        recalculate_day_limit(update, context, 1)

    # Check if user has expenses recorded
    if user_id in user_data and len(user_data[user_id]['expenses']) > 0:
        expenses = user_data[user_id]['expenses']
        expense_str = "Your expenses:\n"
        for expense in expenses:
            expense_str += f"- {expense['amount']} ({expense['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})\n"
        context.bot.send_message(chat_id=user_id, text=expense_str)
    else:
        context.bot.send_message(chat_id=user_id, text="You don't have any expenses recorded. Please add an expense using /addexpense.")

def show_user_data(update, context):
    user_id = update.effective_chat.id

    updated_date = user_data[user_id]['updated_date'].date()
    if updated_date < datetime.datetime.now().date():
        recalculate_day_limit(update, context, 1)

    if user_id in user_data:
        data = user_data[user_id]
        message = f"""
Your limit is {data['limit']} and it expires on {data['expiration_date']}. 
You have spent {data['day_spent']} today out of your daily limit of {data['day_limit']}.
You data was updated {data['updated_date']}
            """
        context.bot.send_message(chat_id=user_id, text=message)

        check_expenses(update, context)
        
    else:
        context.bot.send_message(chat_id=user_id, text="No data found for this user.")

def recalculate_day_limit(update, context, daily=0):
    # Get user data
    user_id = update.effective_chat.id
    user = user_data[user_id]

    # Calculate spent amount today
    today = datetime.datetime.now().date()
    spent_today = sum(float(expense['amount']) for expense in user['expenses'] if expense['timestamp'].date() == today)
    
    # Calculate new daily limit based on remaining days
    num_remaining_days = (user['expiration_date'] - today).days
    

    # Check if spent amount exceeds daily limit
    if spent_today > user['day_limit']:

        new_day_limit = round((float(user['limit']) - user['day_spent']) / num_remaining_days, 2)
        # Update day limit and day spent amount
        user['day_limit'] = new_day_limit
        user['day_spent'] = new_day_limit

        # Send message to user about the new daily limit
        message = f"Your daily limit has been updated to {new_day_limit}. You have spent {spent_today} today."
        context.bot.send_message(user_id, message)

    # Check if spent amount less then daily limit
    if spent_today < user['day_limit'] and daily == 1:
        new_day_limit = round((float(user['limit']) - user['day_spent']) / num_remaining_days, 2)

        # Calculate how much additional budget is available per day
        additional_budget_per_day = (int(user_data[user_id]['limit']) - int(user['day_spent']) ) / num_remaining_days

        # Calculate the new daily limit
        new_day_limit = round(int(user['day_spent']) / (num_remaining_days - 1) + additional_budget_per_day, 2)

        # Update the daily limit and send a message to the user
        user_data[user_id]['day_limit'] = new_day_limit
        context.bot.send_message(chat_id=user_id, text=f"Your new daily limit is {new_day_limit}.")


def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setlimit", set_limit))
    dp.add_handler(CommandHandler("checklimit", check_limit))
    dp.add_handler(CommandHandler("addexpense", add_expense))
    dp.add_handler(CommandHandler("checkexpenses", check_expenses))
    dp.add_handler(CommandHandler("showuserdata", show_user_data))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
