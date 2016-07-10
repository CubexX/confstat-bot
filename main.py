# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import CONFIG
import handlers
import memcache
import logging

cache = memcache.Client(CONFIG['cache']['servers'], debug=CONFIG['cache']['debug'])

logging.basicConfig(
    format=CONFIG['logging']['format'],
    level=logging.INFO,
    filename=CONFIG['logging']['file']
)
logger = logging.getLogger(__name__)


def main():
    updater = Updater(CONFIG['bot_token'])
    dp = updater.dispatcher

    job_queue = updater.job_queue
    job_queue.put(handlers.job, CONFIG['query_interval'], repeat=True)

    dp.add_handler(CommandHandler('start', handlers.start))
    dp.add_handler(CommandHandler('stat', handlers.stat))
    dp.add_handler(CommandHandler('me', handlers.me))
    dp.add_handler(CommandHandler('setprivacy', handlers.set_privacy))
    dp.add_handler(MessageHandler([Filters.status_update], handlers.update_to_supergroup))

    dp.add_handler(MessageHandler([Filters.text,
                                   Filters.photo,
                                   Filters.command,
                                   Filters.video,
                                   Filters.audio,
                                   Filters.voice,
                                   Filters.document], handlers.message))

    logger.info('Bot started')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
