from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import cv2
import numpy as np
import requests
import os
import sqlite3
from database import *
from queue import Queue  # Добавляем импорт класса Queue

# Замените этот токен на ваш собственный
TOKEN = '<7955270752:AAGEV_TwVkA_gks7SUf-tUEDrFeHx65hUwQ>'

# Логотип компании для поиска
LOGO_PATH = 'logo.png'

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.first_name}! Отправь мне фото с нашим фирменным элементом, чтобы получить триппкоины."
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /help."""
    update.message.reply_text("Отправьте мне фото с фирменным элементом нашей компании.")

def photo_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик фотографий."""
    file_id = update.message.photo[-1].file_id
    newFile = context.bot.get_file(file_id)
    filename = f"{update.effective_user.id}.jpg"
    newFile.download(filename)
    
    # Проверяем наличие логотипа на изображении
    logo_found = check_logo(LOGO_PATH, filename)
    
    if logo_found:
        update.message.reply_text("Отлично! Наш фирменный элемент найден. Вы получаете 10 триппкоинов!")
        add_user_to_database(update.effective_user.id, update.effective_user.username)
        update_trippcoins_by_user_id(update.effective_user.id, 10)
    else:
        update.message.reply_text("К сожалению, наш фирменный элемент не был обнаружен. Попробуйте снова.")
    
    # Удаляем временный файл
    os.remove(filename)

def check_logo(logo_path, image_path):
    """Функция для проверки наличия логотипа на изображении."""
    method = cv2.TM_SQDIFF_NORMED
    
    small_image = cv2.imread(logo_path)
    large_image = cv2.imread(image_path)
    
    result = cv2.matchTemplate(small_image, large_image, method)
    
    mn, _, mnLoc, _ = cv2.minMaxLoc(result)
    
    # Если совпадение найдено, возвращаем True
    threshold = 0.8
    return mn <= (1 - threshold)

def balance(update: Update, context: CallbackContext) -> None:
    """Показывает баланс триппкоинов пользователя."""
    user_id = update.effective_user.id
    coins = get_trippcoins_by_user_id(user_id)
    update.message.reply_text(f"Ваш текущий баланс: {coins} триппкоинов.")

def exchange(update: Update, context: CallbackContext) -> None:
    """Обмен триппкоинов на сувениры."""
    user_id = update.effective_user.id
    coins = get_trippcoins_by_user_id(user_id)
    
    if coins >= 100:
        update.message.reply_text("Вы можете обменять свои триппкоины на сувенир! Хотите продолжить?")
    else:
        update.message.reply_text("У вас недостаточно триппкоинов для обмена. Продолжайте собирать!")

def main() -> None:
    # Создаем экземпляр очереди
    update_queue = Queue()
    
    # Инициализируем Updater с передачей очереди
    updater = Updater(TOKEN, update_queue=update_queue)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(filters=Update.FILTERS.photo, callback=photo_handler))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("exchange", exchange))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()