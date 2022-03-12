from bizdirectoryhandler import *
import config
def main():
    logging.basicConfig(filename=config.BIZ_DIR_BOT_LOGS, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    updater = Updater(token=config.BIZ_DIR_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    help_handler = CommandHandler('help', help)
    show_handler = CommandHandler('show', show)

    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(show_handler)
    
    conv_handler_add = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('add',add)],
        states={
            ADD: [CommandHandler('add',add)],
            NAME: [MessageHandler((Filters.text & (~ Filters.command)), name), CommandHandler('done', done)],
            DESCRIPTION: [MessageHandler((Filters.text & (~ Filters.command)), description), CommandHandler('done', done)],
            CONTACT: [MessageHandler((Filters.text & (~ Filters.command)), contact), CommandHandler('skip', skip_contact)],
            CHOICE: [MessageHandler(Filters.regex('(Yes|No)'), choice)]
        },
    fallbacks=[CommandHandler('done', done)],
    )
    dispatcher.add_handler(conv_handler_add)
    updater.start_polling(1)
    updater.idle()
if __name__ == '__main__':
    main()