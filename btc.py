from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from binance.client import Client as BinanceClient
import locale
import decimal

# Configuração do Telegram
TELEGRAM_TOKEN = '6002886491:AAHWbdB2DyExhvnIWJOQxkd26eP7FDCP75Q'

# Configuração da API da Binance
BINANCE_API_KEY = '8jhntBVKAH5rbUmOcm7veI2O4ZND3sLyyA3ZYcwtNPcgJik1jWN28gNh8m8cK5SJ'
BINANCE_API_SECRET = 'BZRgwAmarrXCFmiB1Yup7SHXPQOOuETTBiYwzw1QZVx4OdpdOvXUIEruLaB6DoFM'
client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)

# Variáveis globais para controle das notificações
notification_enabled = False
notification_threshold = 0.1  # Porcentagem de variação para notificar

def format_brl_value(value):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    return locale.currency(value, grouping=True, symbol='R$')

def format_btc_value(value):
    return f"{value:.8f}"

def calculate_investment(investment_value, price):
    invested = decimal.Decimal(investment_value) / decimal.Decimal(price)
    return invested.quantize(decimal.Decimal('0.00000000'))

def start(update: Update, context):
    chat_id = update.effective_chat.id
    btc_price = client.get_avg_price(symbol="BTCBRL")['price']
    usd_price = client.get_avg_price(symbol="USDTBRL")['price']
    message = f"Olá! Sou um bot para te ajudar com o valor do BTC.\n"
    message += f"O preço atual do Bitcoin é {btc_price} BRL e o preço do Dólar é {usd_price} BRL.\n"
    message += "Você gostaria de investir hoje?"
    context.bot.send_message(chat_id=chat_id, text=message)

def invest(update: Update, context):
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower()

    try:
        investment_value = float(message_text)
        btc_price = client.get_avg_price(symbol="BTCBRL")['price']
        usd_price = client.get_avg_price(symbol="USDTBRL")['price']
        btc_quantity = calculate_investment(investment_value, btc_price)
        usdt_quantity = calculate_investment(investment_value, usd_price)
        message = f"Com o valor de {format_brl_value(investment_value)}, você adquirirá:\n"
        message += f"{format_btc_value(btc_quantity)} BTC\n"
        message += f"{format_brl_value(usdt_quantity)} USDT\n"
        message += "Compre Bitcoin e Dólar sem taxa de câmbio aqui no Binance.com."
        message += "\n\n[Visite o Binance.com](https://www.binance.com/pt-BR/activity/referral-entry/CPA?ref=CPA_00YRJDOZZV)"
        context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
    except ValueError:
        message = "Por favor, digite um valor válido para investimento."
        context.bot.send_message(chat_id=chat_id, text=message)

def enable_notifications(update: Update, context):
    global notification_enabled
    notification_enabled = True
    chat_id = update.effective_chat.id
    message = "Notificações ativadas. Você será informado quando houver variação no preço do Bitcoin."
    context.bot.send_message(chat_id=chat_id, text=message)

def disable_notifications(update: Update, context):
    global notification_enabled
    notification_enabled = False
    chat_id = update.effective_chat.id
    message = "Notificações desativadas. Você não receberá mais informações sobre variação no preço do Bitcoin."
    context.bot.send_message(chat_id=chat_id, text=message)

def check_price(update: Update, context):
    global notification_enabled
    global notification_threshold
    chat_id = update.effective_chat.id
    btc_price = client.get_avg_price(symbol="BTCBRL")['price']

    if notification_enabled:
        last_price = context.user_data.get('last_price')
        if last_price:
            price_diff = (float(btc_price) - float(last_price)) / float(last_price)
            if abs(price_diff) >= notification_threshold:
                message = f"O preço do Bitcoin mudou {price_diff:.2%} desde a última atualização."
                context.bot.send_message(chat_id=chat_id, text=message)

    context.user_data['last_price'] = btc_price

def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    updater = Updater(bot=bot, use_context=True)

    start_handler = CommandHandler('start', start)
    invest_handler = MessageHandler(Filters.text & (~Filters.command), invest)
    enable_notifications_handler = CommandHandler('notifications_on', enable_notifications)
    disable_notifications_handler = CommandHandler('notifications_off', disable_notifications)
    check_price_handler = CommandHandler('check_price', check_price)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(invest_handler)
    updater.dispatcher.add_handler(enable_notifications_handler)
    updater.dispatcher.add_handler(disable_notifications_handler)
    updater.dispatcher.add_handler(check_price_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
