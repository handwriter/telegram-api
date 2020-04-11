from telegram.ext import Updater, MessageHandler, Filters
from auth import TOKEN
from telegram.ext import CallbackContext, CommandHandler
from datetime import datetime


# Определяем функцию-обработчик сообщений.
# У неё два параметра, сам бот и класс updater, принявший сообщение.
def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        # args[0] должен содержать значение аргумента (секунды таймера)
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, не умеем возвращаться в прошлое')
            return

        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(task, due, context=chat_id)
        # Запоминаем созданную задачу в данных чата.
        context.chat_data['job'] = new_job
        # Присылаем сообщение о том, что всё получилось.
        update.message.reply_text(f'Вернусь через {due} секунд')

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')


def task(context):
    job = context.job
    context.bot.send_message(job.context, text='Вернулся!')


def unset_timer(update, context):
    # Проверяем, что задача ставилась
    if 'job' not in context.chat_data:
        update.message.reply_text('Нет активного таймера')
        return
    job = context.chat_data['job']
    # планируем удаление задачи (выполнится, когда будет возможность)
    job.schedule_removal()
    # и очищаем пользовательские данные
    del context.chat_data['job']
    update.message.reply_text('Хорошо, вернулся сейчас!')


def main():
    # Создаём объект updater.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://96.96.33.133:1080',  # Адрес прокси сервера
        # Опционально, если требуется аутентификация:
        # 'urllib3_proxy_kwargs': {
        #     'assert_hostname': 'False',
        #     'cert_reqs': 'CERT_NONE'
        #     'username': 'user',
        #     'password': 'password'
        # }
    }

    updater = Updater(TOKEN, use_context=True,
                      request_kwargs=REQUEST_KWARGS)

    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    # Создаём обработчик сообщений типа Filters.text
    # из описанной выше функции echo()
    # После регистрации обработчика в диспетчере
    # эта функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset_timer,
                                  pass_chat_data=True)
                   )
    # Запускаем цикл приема и обработки сообщений.

    updater.start_polling()

    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()