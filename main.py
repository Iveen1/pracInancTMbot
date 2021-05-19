import telebot
from db import BotDB
import datetime
from threading import Thread
import time
bot = telebot.TeleBot('1724611900:AAHZN_5Q3D3wHs4mRYN83ZcGFPp_FVIjGVI')

@bot.message_handler(commands=['addtodo'])
def add_todo(message):
    user_id = message.from_user.id
    userLogin = message.from_user.username
    userName = f"{message.from_user.first_name} {message.from_user.last_name}"
    messageText = message.text
    description = messageText[messageText.find(' ') + 1 : ] # хз как это работает, но работает

    result = BotDB().addTodo(user_id, userLogin, userName, description)
    if result == True:
        bot.send_message(message.chat.id, "Задача успешно добавлена!")

@bot.message_handler(commands=['addtimedtodo'])
def add_todo(message):
    user_id = message.from_user.id
    userLogin = message.from_user.username
    userName = f"{message.from_user.first_name} {message.from_user.last_name}"
    messageText = message.text
    description = messageText[messageText.find(' ') + 1 : ] # хз как это работает, но работает

    result = BotDB().addTodo(user_id, userLogin, userName, description)
    if result == True:
        bot.send_message(message.chat.id, "Напиши дату и время для напоминания\nНапример: 26.11.2021 16:21\n\nЕсли не хочешь добавлять напоминание, напишите 'отмена'")
        bot.register_next_step_handler(message, setTime)

def setTime(message):
    if message.text.lower() == 'отмена':
        pass
    else:
        user_id = message.from_user.id
        try:
            timeObject = datetime.datetime.strptime(message.text, '%d.%m.%Y %H:%M').strftime("%Y-%m-%d %H:%M")
            print(timeObject)
            todo = BotDB().getTodosByUserId(user_id, 1)[-1]
            print(todo)
            print(BotDB().insertTimeByIds(user_id, todo[4], timeObject))
        except Exception:
            bot.send_message(message.chat.id, "Неправильный формат.\nПример: 26.11.2021 16:21")
            bot.send_message(message.chat.id, "Напиши дату и время для напоминания\n\nЕсли не хочешь добавлять напоминание, напишите 'отмена'")
            bot.register_next_step_handler(message, setTime)
            return
    bot.send_message(message.chat.id, "Задача успешно добавлена!")

@bot.message_handler(commands=['todos'])
def get_todos(message):
    user_id = message.from_user.id
    todos = BotDB().getTodosByUserId(user_id, 1)
    out = ''
    counter = 1
    for i in todos:
        out += f'\n{counter}. {i[6]}\n<strong>ToDoID - {i[4]}</strong>\n'
        counter += 1
    if out == '':
        out = 'У тебя нет задач!'
    bot.send_message(message.chat.id, out, parse_mode='HTML')

@bot.message_handler(commands=['completetodo'])
def complete_todo(message):
    user_id = message.from_user.id
    todoId = message.text[-1]

    if not todoId.isdigit():
        bot.send_message(message.chat.id, "Пример использования:\n/completetodo 1")
        return

    result = BotDB().completeTodoByIds(user_id, todoId)
    if result == None:
        bot.send_message(message.chat.id, "Задачи с таким ID не найдено")
    elif result == False:
        bot.send_message(message.chat.id, "Задача уже выполнена")
    else:
        bot.send_message(message.chat.id, "Вы успешно выполнили задачу!")

@bot.message_handler(commands=['completedtodos'])
def completed_todos(message):
    user_id = message.from_user.id
    todos = BotDB().getTodosByUserId(user_id, 0)
    out = ''
    counter = 1
    for i in todos:
        out += f'\n{counter}. {i[6]}\n<strong>ToDoID - {i[4]}</strong>\n'
        counter += 1
    if out == '':
        out = 'У тебя нет сделанных задач!'
    bot.send_message(message.chat.id, out, parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def document(message):
    user_id = message.from_user.id
    message_id = message.message_id
    bot.send_message(message.chat.id, f"Привеет! У бота есть команды:\n<strong>/addtodo</strong> - добавить задачу\n<strong>/addtimedtodo</strong> - добавить задачу с напоминанием\n<strong>/todos</strong> - просмотреть текущие задачи\n<strong>/completetodo</strong> - выполнить задачу\n<strong>/completedtodos</strong> - просмотреть выполненные задачи",
    parse_mode='HTML')

class Starter():
    def startBot(self):
        try:
            print("Бот запущен")
            bot.polling()
        except Exception as E:
            print("Какая-то ошибка...")
            print(E)
            self.startBot()

    def timeChecker(self):
        while True:
            times = BotDB().getRowsWithTime()
            for i in times:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                if i[7] == current_time:
                    print(i)
                    BotDB().updateNotificationDeliveryStatusByIds(i[1], i[4])
                    bot.send_message(i[1], f"<strong>Напоминание!</strong>\nПриступи к выполнению задачи {i[6]}\n<strong>ToDoID - {i[4]}</strong>", parse_mode='HTML')
            time.sleep(2)
if __name__ == '__main__':
    Thread(target=Starter().startBot).start()
    Thread(target=Starter().timeChecker).start()