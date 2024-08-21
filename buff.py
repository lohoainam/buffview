from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import random
import os

# Thay thế bằng token của bot bạn nhận từ BotFather
TOKEN = '7133052805:AAG6SE4DRkPCHOj8OXk6CBi9U6yZSt1rFoE'

PROXY_FILE = 'proxy.txt'
PROXY_LIST = []

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Chào bạn! Gửi file chứa proxy và sau đó gửi link video TikTok.')

def handle_document(update: Update, context: CallbackContext):
    file = update.message.document.get_file()
    file.download(PROXY_FILE)
    load_proxies()  # Tải lại proxy khi có file mới
    update.message.reply_text('Đã tải file proxy thành công. Gửi link video TikTok để tăng view.')

def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    if url.startswith('https://www.tiktok.com'):
        if not PROXY_LIST:
            update.message.reply_text('Chưa có proxy. Hãy gửi file proxy trước.')
            return
        
        num_views = 0
        failed_proxies = []
        for _ in range(10):  # Số lượng yêu cầu xem video
            proxy = get_random_proxy(PROXY_LIST)
            if fetch_video(url, proxy):
                num_views += 1
            else:
                failed_proxies.append(proxy)

        report = f'Đã gửi {num_views} yêu cầu xem đến video TikTok.\n'
        if failed_proxies:
            report += 'Proxy không thành công:\n' + '\n'.join(failed_proxies)
        
        update.message.reply_text(report)
    else:
        update.message.reply_text('Link không hợp lệ. Hãy gửi link video TikTok.')

def get_random_proxy(proxies):
    return random.choice(proxies)

def fetch_video(url, proxy):
    proxy_dict = {
        'http': proxy,
        'https': proxy
    }
    try:
        response = requests.get(url, proxies=proxy_dict, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def load_proxies():
    global PROXY_LIST
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, 'r') as file:
            PROXY_LIST = [line.strip() for line in file if line.strip()]

def main():
    load_proxies()

    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), handle_document))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
