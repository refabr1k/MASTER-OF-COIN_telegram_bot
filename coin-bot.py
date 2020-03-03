import logging
import sys
import time
import re
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

API_TOKEN = "<API_KEY>"

choice = {}

commands = {  # command description used in the "help" command
    'start or /help'    : 'Get used to the bot',
    'new'  : 'record new spending',
    'show' : 'Show all spendings'
}


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(API_TOKEN)
bot.set_update_listener(listener)  # register listener
telebot.logger.setLevel(logging.DEBUG)


# handle the "/start" command
@bot.message_handler(commands=['start','help'])
def command_start(m):
    cid = m.chat.id
    help_text = "Welcome! I am the Master Of Coin, how can I help you today?\nThe following commands are available: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)

@bot.message_handler(commands=['show'])
def command_show(message):
    cid = message.chat.id
    bot.send_message(cid, "Patience! I have not learned how to do this yet! Come back next time!")
  
# handle the "/new" command
@bot.message_handler(commands=['new'])
def command_new(message):
    cid = message.chat.id
    print(choice)
    choice.pop(cid, None) #remove temp choice
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Food', 'Groceries', 'Transport', 'Shopping')
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    bot.register_next_step_handler(msg, process_amount_step)

def validateAmount(amountStr):    
    if len(amountStr) >= 0 and len(amountStr) <= 15:
        if amountStr.isdigit: 
            if re.match("^[0-9]*\\.?[0-9]*$", amountStr):
                return str(round(float(amountStr),2))                
    return 0    

def process_amount_step(message):
    try:
        cid = message.chat.id
        
        if not cid in choice:
            choice[cid] = message.text
    
        amount = validateAmount(message.text) #validate
        if amount == 0:
            message = bot.send_message(cid, 'How much did you spent on {}? \nPlease enter numbers only.'.format(str(choice[cid])))
            bot.register_next_step_handler(message, process_amount_step)
            return
        

        # dt = datetime.utcfromtimestamp(int(message.date)+28800)).strftime('%Y-%m-%d %H:%M:%S')
        dt = datetime.utcfromtimestamp(message.date).strftime('%Y-%m-%d')

        bot.send_message(cid, 'Recorded: You spent $' + str(amount) + ' for ' + str(choice[cid]) + ' on (UTC) {}'.format(str(dt)))
        # bot.send_message(cid, 'Record: $' + str(amount) + ' ' + str(choice[cid]) + ' on {}'.format(message.date))
       
    except Exception as e:
        bot.reply_to(message, 'oooops:' + e)




# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()



bot.polling(none_stop=True)



# def main_loop():
#     bot.polling(True)
#     while 1:
#         time.sleep(3)


# if __name__ == '__main__':
#     try:
#         main_loop()
#     except KeyboardInterrupt:
#         print('\nExiting by user request.\n')
#         sys.exit(0)

