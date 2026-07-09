import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set!")
    exit(1)

print("Bot starting...")

def get_btc():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        return r.json()["bitcoin"]["usd"]
    except:
        return None

def format_currency_whole(num):
    try:
        if num is None:
            return "0"
        rounded = round(num)
        formatted = f"{rounded:,}"
        return formatted
    except:
        return str(num)

def format_currency_decimal(num):
    try:
        if num is None:
            return "0"
        formatted = f"{num:,.2f}"
        if formatted.endswith('.00'):
            formatted = formatted[:-3]
        return formatted
    except:
        return str(num)

async def start(update: Update, context):
    await update.message.reply_text("Send me the USD amount you want to convert to BTC")

async def handle(update: Update, context):
    try:
        usd = float(update.message.text)
        price = get_btc()
        
        if price is None:
            await update.message.chat.send_message("⚠️ Could not fetch BTC price. Please try again.")
            return
        
        if usd <= 133.33:
            numerator = usd - 20
            denominator = price
            btc = numerator / denominator
            
            msg = "📊 BTC SPOT PRICE: $" + format_currency_whole(price) + "\n\n"
            msg = msg + "💰 You send: $" + format_currency_decimal(usd) + "\n"
            msg = msg + "📝 Math: (" + format_currency_decimal(usd) + " - 20) ÷ " + format_currency_whole(denominator) + "\n"
            msg = msg + "   = " + format_currency_decimal(numerator) + " ÷ " + format_currency_whole(denominator) + "\n\n"
            msg = msg + "BTC you will receive is:"
        else:
            numerator = usd * 0.85
            denominator = price
            btc = numerator / denominator
            
            msg = "📊 BTC SPOT PRICE: $" + format_currency_whole(price) + "\n\n"
            msg = msg + "💰 You send: $" + format_currency_decimal(usd) + "\n"
            msg = msg + "📝 Math: (" + format_currency_decimal(usd) + " × 0.85) ÷ " + format_currency_whole(denominator) + "\n"
            msg = msg + "   = " + format_currency_decimal(numerator) + " ÷ " + format_currency_whole(denominator) + "\n\n"
            msg = msg + "BTC you will receive is:"
        
        await update.message.chat.send_message(msg)
        
        btc_str = str(round(btc, 8)).rstrip('0').rstrip('.')
        await update.message.chat.send_message(btc_str)
        
    except Exception as e:
        return

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
print("Bot is running...")
app.run_polling()
