# -*- coding: utf-8 -*-
__author__ = 'CubexX'

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import handlers
from config import TOKEN


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    job_queue = updater.job_queue
    job_queue.put(handlers.job, 15, repeat=True)

    dp.add_handler(CommandHandler('start', handlers.start))
    dp.add_handler(CommandHandler('stat', handlers.stat))
    dp.add_handler(CommandHandler('me', handlers.me))
    dp.add_handler(MessageHandler([Filters.text,
                                   Filters.photo,
                                   Filters.command,
                                   Filters.video,
                                   Filters.audio,
                                   Filters.voice,
                                   Filters.document], handlers.message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
