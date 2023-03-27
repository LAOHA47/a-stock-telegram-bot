import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import datetime
from iexfinance.stocks import get_historical_data
from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_intraday
import plotly.graph_objs as go
from telegram.ext import CallbackContext



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Hello, I'm a stock bot made by duansq. \nYou can send me the following commands:\n/help - to get the list of available commands")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Available commands:\n/get_stock <ticker> - to get the current stock price\n/help - to get the list of available commands\n/get_historical_data <ticker> - to get historical stock price data between Jan 1, 2022 and Feb 1, 2022\n/get_candlestick_chart <ticker> - to gain a picture of price data\n/get_advanced_stats <ticker> - to gain a detailed report about stock data\n/compare_stocks <ticker1> <ticker2> - to compare several stock datas"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)



async def get_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    ticker = args[0].upper()
    token="sk_a73e34ea683c4b6595ba8e0ca55b79f4"
    stock_quote = Stock(ticker, token=token).get_quote()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{ticker} stock quote: {stock_quote['latestPrice']} USD")


async def get_historical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ticker = "TSLA"
    start_date = datetime.datetime(2022, 1, 1)
    end_date = datetime.datetime(2022, 2, 1)
    token = "sk_a73e34ea683c4b6595ba8e0ca55b79f4"
    historical_data = get_historical_data(ticker, start_date, end_date, token=token)
    message = f"{ticker} historical data:\n{historical_data}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def get_candlestick_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    ticker = args[0].upper()
    token = "sk_a73e34ea683c4b6595ba8e0ca55b79f4"
    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    end_date = datetime.datetime.now()
    historical_data = get_historical_intraday(ticker, start_date=start_date, end_date=end_date, token=token, output_format='pandas')
    fig = go.Figure(data=[go.Candlestick(x=historical_data.index,
                                          open=historical_data['open'],
                                          high=historical_data['high'],
                                          low=historical_data['low'],
                                          close=historical_data['close'])])
    fig.update_layout(title=f"{ticker} Candlestick Chart",
                      xaxis_rangeslider_visible=False)
    image_bytes = fig.to_image(format='png')
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes)



async def get_advanced_stats(update: Update, context: CallbackContext):
    args = context.args
    ticker = args[0].upper()
    token = "sk_a73e34ea683c4b6595ba8e0ca55b79f4"
    stats = Stock(ticker, token=token).get_quote()
    message = f"Advanced stats for {ticker}:\n\n{stats}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def compare_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    tickers = [ticker.strip().upper() for ticker in args[0].split(',')]
    token = "sk_a73e34ea683c4b6595ba8e0ca55b79f4"
    stats = {}
    for ticker in tickers:
        stats[ticker] = Stock(ticker, token=token).get_quote()
    message = "Key stats comparison for:\n"
    for ticker, values in stats.items():
        pe_ratio = values.get('peRatio', 'N/A')
        price_to_sales = values.get('priceToSales', 'N/A')
        message += f"{ticker} - peRatio: {pe_ratio} | Price to Sales Ratio: {price_to_sales}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


if __name__ == '__main__':
    application = ApplicationBuilder().token('5913732674:AAGBl0R6Sr242Ar_6eDTz7EYh1VieiMY8M0').build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    get_stock_handler = CommandHandler('get_stock', get_stock)
    application.add_handler(get_stock_handler)

    get_historical_handler = CommandHandler('get_historical_data', get_historical)
    application.add_handler(get_historical_handler)

    get_candlestick_chart_handler = CommandHandler('get_candlestick_chart', get_candlestick_chart)
    application.add_handler(get_candlestick_chart_handler)

    get_advanced_stats_handler = CommandHandler('get_advanced_stats', get_advanced_stats)
    application.add_handler(get_advanced_stats_handler)

    compare_stocks_handler = CommandHandler('compare_stocks', compare_stocks)
    application.add_handler(compare_stocks_handler)

    application.run_polling()
