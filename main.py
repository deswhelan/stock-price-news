import config
import requests
from twilio.rest import Client

def get_stock_data():
    """Returns a dictionary representing stock price data for the given company for the previous 100 days"""
    params = {
        # https://www.alphavantage.co/documentation/#daily
        "function": "TIME_SERIES_DAILY",
        "symbol": config.COMPANY["symbol"],
        "apikey": config.ALPHA_VANTAGE["api_key"]
    }

    response = requests.get(config.ALPHA_VANTAGE["request_url"], params)
    response.raise_for_status()

    return response.json()["Time Series (Daily)"]

def get_news_data(date):
    """Returns a list representing recent/popular news stories related to the given company up to the specified date"""
    params = {
        # https://newsapi.org/docs/endpoints/everything
        "apikey": config.NEWS_API["api_key"],
        "q": config.COMPANY["name"],
        "searchIn": "title",
        "sortBy": "popularity",
        "to": date
    }

    response = requests.get(config.NEWS_API["request_url"], params)
    response.raise_for_status()

    return response.json()["articles"]

# TODO: stretch - refactor out tuple return type (i.e. into separate functions for each value)
def get_most_recent_threshold_stock_change():
    """Returns a tuple comprising a string representing the date of the most recent overnight stock price change to breach the given threshold, and a float representing the percentage change"""
    stock_data = get_stock_data()

    # Manipulate data into a more user-friendly list of dictionairies
    daily_stock_data_list = [stock_data[daily_stock_data] for daily_stock_data in stock_data]

    for i, daily_stock_data in enumerate(stock_data):
        daily_stock_data_list[i]["date"] = daily_stock_data

    for i, daily_stock_data in enumerate(daily_stock_data_list[:-1]):
        opening_price = float(daily_stock_data["1. open"])
        previous_closing_price = float(daily_stock_data_list[i + 1]['4. close'])
        percentage_diff = ((opening_price - previous_closing_price) / opening_price) * 100

        if abs(percentage_diff) >= config.DAILY_FLUCTUATION_THRESHOLD:
            return daily_stock_data["date"], percentage_diff

    return None

def send_sms_notifications(articles, date, percentage_change):
    """Sends SMS notifications including stock price change for the given company along with up to three links to related news stories"""
    account_sid = config.TWILIO["account_sid"]
    auth_token = config.TWILIO["auth_token"]
    client = Client(account_sid, auth_token)

    # Send message indicating stock price % change
    arrow_emoji = "🔺" if percentage_change > 0 else "🔻"
    message_body = f"\n{config.COMPANY["name"]}: {arrow_emoji}{round(abs(percentage_change), 2)}% at open of {date}\n"

    message = client.messages.create(
        from_=config.TWILIO["from"],
        body=message_body,
        to=config.TWILIO["to"]
    )
    print(message.status)

    # Send links to related articles
    for article in articles:
        # TODO: stretch = handle sms message character limit
        message_body = f"{article["url"]}\n"
        message = client.messages.create(
            from_=config.TWILIO["from"],
            body=message_body,
            to=config.TWILIO["to"]
        )
        print(message.status)

stock_change = get_most_recent_threshold_stock_change()
if stock_change:
    date = stock_change[0]
    percentage_change = stock_change[1]

    news_data = get_news_data(date)
    send_sms_notifications(news_data[:3], date, percentage_change)


