from unittest import result
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
import telegram
from telegram.ext import *
import logging
import csv
import pprint
import config
import datetime
import json
from pymongo import MongoClient


STATS, ADD, NAME, DESCRIPTION, CONTACT, PHONE, ADDRESS, EMAIL, DONE, CHOICE = range(10)
command_keyboard = [
    [KeyboardButton('/show'), KeyboardButton('/add')], 
    [ KeyboardButton('/help'),   KeyboardButton('/code')]
    ]
markup = ReplyKeyboardMarkup(command_keyboard, one_time_keyboard=True, selective=True)

message_keyboard = [
    [KeyboardButton('/show'), KeyboardButton('/add')],  
    [KeyboardButton('/help'),  KeyboardButton('/code')]
    ]
markup_msg = ReplyKeyboardMarkup(message_keyboard, one_time_keyboard=True, selective=True)
business = None
client = MongoClient()
db = client.business

def start(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling start command')
    update.message.reply_text(text='**Welcome to the Biz Dir Bot**\n'
                                   'I can help you to advertise your business and also search a business that you need\.\n\n'
                                    
                                   'Here, the list of commands:\n\n'
                                   
                                   '`/add`     \- To get add a business\.\n\n'

                                   '`/show [query]`     \- Search a matching query\.\n\n'
                                   
                                   '`/code`     \- To get the source code\.\n\n'
                                    
                                    '`/help`    \- Helpful to see the list of commands\.',
                              parse_mode="MarkdownV2",
                              reply_markup=markup)
    return ADD

def done(update, context):

    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling done command')
    
    if 'business' in context.user_data:
        del context.user_data['business']
        context.user_data.clear()
        update.message.reply_text(
        "Bye, see you around!", reply_markup=markup
        )
        return ConversationHandler.END
    update.message.reply_text(
        "Bye, see you around!", reply_markup=markup
    )
    return ConversationHandler.END

def help(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling help command')
    update.message.reply_text(text='**Welcome to the Biz Dir Bot**\n'
                                   'I can help you to advertise your business and also search a business that you need\.\n\n'
                                   
                                   'Here, the list of commands:\n\n'
                                   
                                   '`/add`     \- To get add a business\.\n\n'

                                   '`/show [query]`     \- Search a matching query\.\n\n'
                                   
                                   '`/code`     \- To get the source code\.\n\n'
                                    
                                    '`/help`    \- Helpful to see the list of commands\.',
                              parse_mode="MarkdownV2",
                              reply_markup=markup)
    return STATS

def code(update, context):
    update.message.reply_text(text='https://github.com/reynelfals/biz_dir')

def show(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling SHOW command')
    args = context.args
    query =''
    if len(args)!=0:
        results = db.data.find({"$text": {"$search":" ".join(args)}})
    else:
        results = db.data.find()
    for biz in results:
        logging.info(f'Biz {biz}')
        update.message.reply_text(text=f"Business: {biz['name']}")
        update.message.reply_text(text=f"Description: {biz['description']}")
        update.message.reply_text(text=f"Contact: {biz['contact']}")
        update.message.reply_text(text=f"___________________________________")
 
    return ADD

def add(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling SHOWALL command')
    context.user_data["business"]= {'user_id': update.message.chat.id, 'user': update.message.chat.first_name}
    update.message.reply_text(text="Please enter the Name of the business. /done to Abort")
    return NAME

def name(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling name company command')
    name_company = update.message.text.strip()
    context.user_data["business"]['name'] = name_company
    update.message.reply_text(text="Please enter the Description of the business. /done to Abort")
    return DESCRIPTION

def description(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling SHOWALL command')
    company_desc = update.message.text.strip()
    context.user_data["business"]['description'] = company_desc
    update.message.reply_text(text="Please enter the contacts of the business (phone, web, address, etc.). /skip to skip.")
    return CONTACT

def contact(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling phone command')
    context.user_data["business"]['contact'] = update.message.text.strip()
    update.message.reply_text(text="Your business:")
    update.message.reply_text(text=f"Business: {context.user_data['business']['name']}")
    update.message.reply_text(text=f"Description: {context.user_data['business']['description']}")
    update.message.reply_text(text=f"Contact: {context.user_data['business']['contact']}")
    update.message.reply_text(text="Do you want to submit the business information (Yes|No).")
    return CHOICE

def web(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling SHOWALL command')
    context.user_data["business"]['web'] = update.message.text.strip()
    update.message.reply_text(text="Please enter a physical address of the business. /skip to skip.")
    return ADDRESS

def physical_address(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling SHOWALL command')
    context.user_data["business"]['address'] = update.message.text.strip()
    update.message.reply_text(text="Do you want to submit the business information (Yes|No).")
    return CHOICE
    
def choice(update, context):
    logging.info(f'User {update.message.chat.first_name}, id {update.message.chat.id}, calling SHOWALL command')
    save_or_not = update.message.text.strip()
    biz = context.user_data["business"]
    if save_or_not == 'Yes':
        x = db.data.insert_one(biz)
        update.message.reply_text(text=f"The business information was saved as {x.inserted_id}.")
        return done(update, context)
    update.message.reply_text(text="The business information was discarded.")
    return done(update, context)

def skip_contact(update: Update, context: CallbackContext) -> int:
    """Skips the phone and asks for email."""
    user = update.message.from_user
    logging.info("User %s did not send a location.", user.first_name)
    context.user_data['business']['contact']=''
    update.message.reply_text(text="Your business:")
    update.message.reply_text(text=f"Business: {context.user_data['business']['name']}")
    update.message.reply_text(text=f"Description: {context.user_data['business']['description']}")
    update.message.reply_text(text=f"Contact: {context.user_data['business']['contact']}")
    
    update.message.reply_text(
        'Do you want to submit the business information (Yes|No).'
    )

    return CHOICE

def skip_web(update: Update, context: CallbackContext) -> int:
    """Skips the web and asks for address."""
    user = update.message.from_user
    logging.info("User %s did not send a web.", user.first_name)
    update.message.reply_text(
        'Enter address. /skip to skip address.'
    )

    return ADDRESS

def skip_address(update: Update, context: CallbackContext) -> int:
    """Skips the address."""
    user = update.message.from_user
    logging.info("User %s did not send an address.", user.first_name)
    update.message.reply_text(
        'Do you want to submit the business information (Yes|No).'
    )

    return CHOICE