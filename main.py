# -*- coding: utf-8 -*-
__author__ = 'CubexX'

import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from config import CONFIG
from confstat import handlers, models

logging.basicConfig(
    format=CONFIG['logging']['format'],
    level=logging.INFO,
    filename=CONFIG['logging']['file']
)
logger = logging.getLogger(__name__)

db_session_maker = models.make_session_maker(CONFIG['database'])


def make_db_session(func):
    def wrapper(*args, **kwargs):
        db = db_session_maker()
        result = func(*args, **kwargs, db=db)
        db.close()
        return result

    return wrapper


def main():
    updater = Updater(CONFIG['bot_token'])
    dp = updater.dispatcher

    job_queue = updater.job_queue
    job_queue.run_repeating(handlers.job, CONFIG['query_interval'])

    dp.add_handler(CommandHandler('start', handlers.start))
    dp.add_handler(CommandHandler('stat', handlers.stat))
    dp.add_handler(CommandHandler('me', handlers.me))
    dp.add_handler(CommandHandler('setprivacy', handlers.set_privacy))
    dp.add_handler(MessageHandler(Filters.status_update, handlers.update_to_supergroup))

    dp.add_handler(MessageHandler((Filters.text |
                                   Filters.photo |
                                   Filters.video |
                                   Filters.audio |
                                   Filters.voice |
                                   Filters.command |
                                   Filters.document), handlers.message))

    logger.info('Bot started')
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
