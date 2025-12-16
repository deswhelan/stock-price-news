import config
import requests

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

def get_date_of_most_recent_fluctuation():
    """Returns a string in format YYYY-MM-DD representing the date of the most recent overnight stock price change to breach the given threshold"""
    stock_data = get_stock_data()

    daily_stock_data_list = [stock_data[daily_stock_data] for daily_stock_data in stock_data]

    for i, daily_stock_data in enumerate(stock_data):
        daily_stock_data_list[i]["date"] = daily_stock_data

    for i, daily_stock_data in enumerate(daily_stock_data_list[:-1]):
        opening_price = float(daily_stock_data["1. open"])
        previous_closing_price = float(daily_stock_data_list[i + 1]['4. close'])
        percentage_diff = ((opening_price - previous_closing_price) / opening_price) * 100

        if abs(percentage_diff) >= config.DAILY_FLUCTUATION_THRESHOLD:
            return daily_stock_data["date"]

        return None

date = get_date_of_most_recent_fluctuation()
if date:
    news_data = get_news_data(date)
    for article in news_data[:3]:
        print(f"{article["publishedAt"]}\n{article["title"]}\n{article["url"]}\n{article["content"]}\n")

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 

#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

