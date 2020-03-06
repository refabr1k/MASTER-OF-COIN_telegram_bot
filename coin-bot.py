import logging
import sys
import time
import re
import os
import telebot
import json
import sched, time
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime


commands = {  # command description used in the "help" command
    'help'    : 'Display this menu',
    'new'  : 'Record new spending',
    'show' : 'Show sum spendings',
    'history' : 'Show spending history',
    'clear': 'debugger: clear all your records',
    'feedback': 'Yay or Nay? Tell me how I can be better!'
}

dateFormat = '%d-%b-%Y'
timeFormat = '%H:%M'
monthFormat = '%b-%Y'


choice = {}
global_users_dict = {}
CATEGORIES = ['Food', 'Groceries', 'Transport', 'Shopping']
SHOW_MODE = ['Day', 'Month']
bot = telebot.TeleBot(API_TOKEN)

# telebot.logger.setLevel(logging.DEBUG)
telebot.logger.setLevel(logging.INFO)


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print("{} name:{} chatid:{} \nmessage: {}\n".format(str(datetime.now()),str(m.chat.first_name),str(m.chat.id),str(m.text)))


bot.set_update_listener(listener)  # register listener

def writeJson(global_users_dict):
    try:
        with open('data.json', 'w') as json_file: 
            json.dump(global_users_dict, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        print('!!!!!!!!!!!!!!!!!!! File data.json not found !!!!!!!!!!!!!!!!!!!')


def loadJson():
    global global_users_dict
    try:
        if not  os.stat('data.json').st_size == 0: #check if file is empty or not
            with open('data.json') as json_file:
                data = json.load(json_file)
            global_users_dict = data    #assign loaded file to global users
        # else:
        #     print("!!!!!!!!!!!!  file is empty !!!!!!!!!!!!!!!!")
    except FileNotFoundError:
        print('!!!!!!!!!!!!!!!!!!! File data.json not found !!!!!!!!!!!!!!!!!!!')




# handle the "/start" command
@bot.message_handler(commands=['start','help'])
def command_start(m):
    loadJson()
    global global_users_dict
    cid = m.chat.id
        
    help_text = "Welcome! I am the Master Of Coin, how can I help you today?\nThe following commands are available: \n\n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)

# handle "/show" command - lists all spendings so far
@bot.message_handler(commands=['show'])
def command_show(message):
    loadJson()
    cid = message.chat.id
    history = getUserHistory
    if history == None:
        bot.send_message(cid, "I'm sorry! It appears that you do not have any spending records!")
    else:
        # bot.send_message(cid, "Patience! I have not learned how to do this yet! Come back next time!")
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for mode in SHOW_MODE:
            markup.add(mode)
        # markup.add('Day', 'Month')
        msg = bot.reply_to(message, 'Show Spendings For?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_show_spending)


def calculate_spendings(queryResult):
    total_dict = {}

    for row in queryResult:
        s = row.split(',')    #date,cat,money
        cat = s[1]  #cat
        if cat in total_dict:
            total_dict[cat] = round(total_dict[cat] + float(s[2]),2)    #round up to 2 decimal
        else:
            total_dict[cat] = float(s[2])
    total_text = ""
    for key, value in total_dict.items():
        total_text += str(key) + " $" + str(value) + "\n"
    return total_text
        
def process_show_spending(message):
    try:
        cid = message.chat.id
        DayWeekMonth = message.text

        if not DayWeekMonth in SHOW_MODE:
            raise Exception("Sorry I can't show spendings for \"{}\"!".format(DayWeekMonth))

        history = getUserHistory(cid)
        if history is None:
            raise Exception("I'm sorry! It appears that you do not have any spending records!")

        bot.send_message(cid, "Hold on! Gathering my thoughts...")
        bot.send_chat_action(cid, 'typing')  # show the bot "typing" (max. 5 secs)
        time.sleep(0.5)
        
        total_text = ""

        if DayWeekMonth == 'Day':
            query = datetime.now().today().strftime(dateFormat)
            queryResult = [value for index, value in enumerate(history) if str(query) in value] #query all that contains today's date
        elif DayWeekMonth == 'Month':
            query = datetime.now().today().strftime(monthFormat)
            queryResult = [value for index, value in enumerate(history) if str(query) in value] #query all that contains today's date
        total_text = calculate_spendings(queryResult)

        spending_text = ""
        if len(total_text) == 0:
            spending_text = "You have no spendings for current {}!".format(DayWeekMonth)
        else:
            spending_text = "Here are your total spendings for current {}:\nCATEGORIES,AMOUNT \n----------------------\n{}".format(DayWeekMonth.lower(), total_text)
            
        bot.send_message(cid, spending_text)
    except Exception as e:
        bot.reply_to(message, 'Opps! ' + str(e))

# handle "/history" command
@bot.message_handler(commands=['history'])
def command_history(message):
    try:
        loadJson()
        cid = message.chat.id

        history = getUserHistory(cid)
        if history is None:
            raise Exception("I'm sorry! It appears that you do not have any spending records!")

        total_spending_text = "Here is your spendings history : \nDATE, CATEGORY, AMOUNT\n------------------------------------\n"

        if len(history) == 0:
            total_spending_text = "I'm sorry! It appears that you do not have any spending records!"
        else:
            for s in history:
                total_spending_text += str(s) + "\n"
        bot.send_message(cid, total_spending_text)      
    except Exception as e:
        bot.reply_to(message, 'Opps! ' + str(e))

# handle the "/new" command
@bot.message_handler(commands=['new'])
def command_new(message):
    loadJson()
    cid = message.chat.id
    choice.pop(cid, None) #remove temp choice
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for cat in CATEGORIES:
        markup.add(cat)
    #markup.add('Food', 'Groceries', 'Transport', 'Shopping')
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    bot.register_next_step_handler(msg, process_category_step)

def validateAmount(amountStr):    
    if len(amountStr) > 0 and len(amountStr) <= 15:
        if amountStr.isdigit: 
            if re.match("^[0-9]*\\.?[0-9]*$", amountStr):
                amount = round(float(amountStr),2)
                if amount > 0:
                    return str(amount)                
    return 0

def process_category_step(message):
    try:
        cid = message.chat.id
        cat_text = message.text
        if not cat_text in CATEGORIES:
            raise Exception("Sorry I don't recognise this category \"{}\"!".format(cat_text))

        choice[cid] = cat_text
        message = bot.send_message(cid, 'How much did you spent on {}? \n(Enter numbers only)'.format(str(choice[cid])))
        bot.register_next_step_handler(message, process_amount_step)
    except Exception as e:
        bot.reply_to(message, 'Opps! ' + str(e))

def process_amount_step(message):
    try:
        # global global_users_dict
        cid = message.chat.id
        # history = getUserHistory(cid)
        amount_text = message.text
        amount_num = validateAmount(message.text) #validate
        if amount_num == 0: #cannot be $0 spending
            raise Exception("Amount cannot be $0!")

        dt = datetime.today().strftime(dateFormat+' '+timeFormat)
        dtText, catText, amtText = str(dt), str(choice[cid]), str(amount_num)
        writeJson(addUserHistory(cid,"{},{},{}".format(dtText,catText,amtText)))
        bot.send_message(cid, 'Recorded: You spent ${} for {} on {}'.format(amtText,catText,dtText))
       
    except Exception as e:
        bot.reply_to(message, 'Opps! ' + str(e))


def getUserHistory(cid):
    global global_users_dict
    if (str(cid) in global_users_dict):
        return global_users_dict[str(cid)]
    return None

def deleteHistory(cid):
    global global_users_dict
    if (str(cid) in global_users_dict):
        del global_users_dict[str(cid)]
    return global_users_dict

def addUserHistory(cid, recordText):
    global global_users_dict
    # getUserHistory(cid).append(recordText)
    if not (str(cid) in global_users_dict):
        global_users_dict[str(cid)] = []
        
    global_users_dict[str(cid)].append(recordText)
    return global_users_dict

# handle "/clear" command
@bot.message_handler(commands=['clear'])
def command_clear(message):
    global global_users_dict
    cid = message.chat.id
    loadJson()
    clear_history_text = ""
    if (str(cid) in global_users_dict):
        writeJson(deleteHistory(cid))
        clear_history_text = "Cleared history!"
    else:
        clear_history_text = "I'm sorry! It appears that you do not have any spending records!"
    bot.send_message(cid, clear_history_text)
    
    

def process_feed_back(message):
    cid = message.chat.id
    feedback_text = message.text
    print("****************FEEDBACK********************")
    print("chatid:{} feedback: {}".format(str(cid),feedback_text))
    print("*********************************************")
    bot.send_message(cid, 'Got it! Thanks for the feedback!')

# handle "/feedback" command
@bot.message_handler(commands=['feedback'])
def command_feedback(message):
    cid = message.chat.id
    message = bot.send_message(cid, 'How can I be a better bot? Any feedback is appreciated!')
    bot.register_next_step_handler(message, process_feed_back)

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

# bot.polling(none_stop=True)



def main():
	try:
		bot.polling(none_stop=True)
	except Exception:
		time.sleep(5)
		print("Internet error!")

if __name__ == '__main__':
	main()
    
  