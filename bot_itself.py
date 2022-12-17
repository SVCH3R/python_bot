import telebot
import requests
import json
import base64
import os
import random
import configparser


def main():

    config = configparser.ConfigParser()
    config.read("config.ini")
    token = config["token"]["token"]
    print(token)
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start(m, res=False):
        bot.send_message(m.chat.id, 'напишите /help')

    @bot.message_handler(commands=["help"])
    def help(m, res=False):
        bot.send_message(
            m.chat.id, 'Бот генерирует изображения на основе введенного текста. Просто отправьте текст (желательно на английском языке) \n подробнее /info')

    @bot.message_handler(commands=["info"])
    def info(m, res=False):
        bot.send_message(
            m.chat.id, 'оригинальный сайт: https://www.craiyon.com/ \n про нейросеть DALL-E https://en.wikipedia.org/wiki/DALL-E')

    @bot.message_handler(content_types=["text"])
    def handle_text(message):
        bot.send_message(message.chat.id, 'подождите... до 2 минут')
        url = "https://backend.craiyon.com/generate"
        payload = json.dumps({"prompt": message.text})
        headers = {
            'Content-Type': 'application/json'
        }
        # генерация post запроса на сайт с заренее введенными параметрами
        response = requests.request(
            "POST", url, headers=headers, data=payload).json()
        # генерация рандомного ключа названия файлов во избежание одноименных файлов
        key = str(random.randint(1, 1000000000))
        for i in range(9):
            # из ответной страницы вытаскиваем base64 представление изображений в bin файл
            file = open("imgbyte" + key + str(i) + ".bin", 'w+')
            file.write(response.get('images')[i])
            file.close()
            file = open("imgbyte" + key + str(i) + ".bin", 'rb')
            # копируем код
            byte = file.read()
            file.close()
            # декодируем base64 string в png
            decodeit = open("img" + key + str(i) + '.png', 'wb')
            decodeit.write(base64.b64decode((byte)))
            decodeit.close()
            # удаляем bin файлы
            os.remove("imgbyte" + key + str(i) + ".bin")
        bot.send_message(message.chat.id, 'готово!')
        images = []
        for i in range(9):
            # генерируем массив названий изображений
            img = "img" + key + str(i) + '.png'
            images.append(img)
        # отправляем изображения
        bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(
            open(photo, 'rb')) for photo in images])
        # удаляем изображения
        for i in images:
            os.remove(i)
    # запускаем
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
