import requests
from flask import Flask, request
import logging

app = Flask(__name__)

YOUR_BOT_TOKEN = "6958224511:AAHZAzGFssAlYhTFLGXwUIIaeq-LjGMjxPI"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{YOUR_BOT_TOKEN}/"
WEB_APP_URL = "https://localhost:5000/"  # URL вашої Web App

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")
        if "message" in data:
            chat_id = data['message']['chat']['id']
            app.logger.debug(f"Chat ID: {chat_id}")
            # Перевірка команди
            if data['message'].get('text') == "/start":
                send_web_app_button(chat_id)
            else:
                response = requests.post(TELEGRAM_API_URL + "sendMessage", json={
                    'chat_id': chat_id,
                    'text': "Send /start to get the game link."
                })
                app.logger.debug(f"Telegram response: {response.json()}")
        return "ok", 200
    except Exception as e:
        app.logger.error(f"Error in /webhook: {str(e)}")
        return "Internal Server Error", 500

def send_web_app_button(chat_id):
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "Open Game",
                "web_app": {"url": WEB_APP_URL}
            }
        ]]
    }
    response = requests.post(TELEGRAM_API_URL + "sendMessage", json={
        'chat_id': chat_id,
        'text': "Click the button below to start the game:",
        'reply_markup': keyboard
    })
    app.logger.debug(f"Telegram response: {response.json()}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=5001, debug=True)

def send_message(chat_id, text):
    response = requests.post(TELEGRAM_API_URL + "sendMessage", json={
        'chat_id': chat_id,
        'text': text
    })
    app.logger.debug(f"Telegram response: {response.json()}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=5001, debug=True)

def get_telegram_user_data(chat_id):
    url = TELEGRAM_API_URL + f"getChat?chat_id={chat_id}"
    response = requests.get(url)
    app.logger.debug(f"getChat response: {response.json()}")
    if response.status_code == 200 and 'result' in response.json():
        return response.json()['result']
    else:
        raise Exception(f"Error fetching user data: {response.json()}")


def register_user(chat_id):
    user_data = get_telegram_user_data(chat_id)
    telegram_id = user_data['id']
    username = user_data.get('username', 'unknown')

    # Реєстрація користувача на сервері
    server_response = requests.post('http://127.0.0.1:5000/register', json={
        'telegram_id': telegram_id,
        'username': username
    })

    if server_response.status_code == 201:
        message = "User registered successfully."
    else:
        message = "User already registered."

    send_message(chat_id, message)


def process_click(chat_id):
    telegram_id = chat_id
    # Обробка кліку на сервері
    server_response = requests.post('http://127.0.0.1:5000/click', json={
        'telegram_id': telegram_id
    })

    if server_response.status_code == 200:
        balance = server_response.json()['balance']
        message = f"Click registered! Your new balance is {balance} coins."
    else:
        message = "Error processing click."

    send_message(chat_id, message)


def check_balance(chat_id):
    telegram_id = chat_id
    # Перевірка балансу на сервері
    server_response = requests.get(f'http://127.0.0.1:5000/balance/{telegram_id}')

    if server_response.status_code == 200:
        balance = server_response.json()['balance']
        message = f"Your balance is {balance} coins."
    else:
        message = "Error retrieving balance."

    send_message(chat_id, message)


def send_message(chat_id, text):
    response = requests.post(TELEGRAM_API_URL + "sendMessage", json={
        'chat_id': chat_id,
        'text': text
    })
    app.logger.debug(f"Telegram response: {response.json()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=5001, debug=True)