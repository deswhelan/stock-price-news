import config
import requests

# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

def get_stock_data():
    """Returns a dictionary representing stock price data for the given company for the previous 100 days"""
    alpha_vantage_params ={
        # https://www.alphavantage.co/documentation/#daily
        "function": "TIME_SERIES_DAILY",
        "symbol": config.COMPANY["symbol"],
        "apikey": config.ALPHA_VANTAGE["api_key"]
    }

    response = requests.get(config.ALPHA_VANTAGE["request_url"], alpha_vantage_params)
    response.raise_for_status()

    return response.json()["Time Series (Daily)"]

daily_stock_data_dict = get_stock_data()
daily_stock_data_list = [daily_stock_data_dict[daily_stock_data] for daily_stock_data in daily_stock_data_dict]

for i, daily_stock_data in enumerate(daily_stock_data_dict):
    daily_stock_data_list[i]["date"] = daily_stock_data

for i, daily_stock_data in enumerate(daily_stock_data_list[:-1]):
    opening_price = float(daily_stock_data["1. open"])
    previous_closing_price = float(daily_stock_data_list[i + 1]['4. close'])
    percentage_diff = ((opening_price - previous_closing_price)/opening_price) * 100

    if abs(percentage_diff) >= config.DAILY_FLUCTUATION_THRESHOLD:
        print(f"Stock moved by {percentage_diff}% from closing at ${previous_closing_price} on {daily_stock_data_list[i + 1]["date"]} to opening at ${opening_price} on {daily_stock_data["date"]}")

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

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

