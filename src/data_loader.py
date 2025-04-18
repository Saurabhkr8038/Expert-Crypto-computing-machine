# src/data_loader.py

import ccxt
import pandas as pd
from datetime import datetime
import os
import requests
from time import sleep
import os
# Load from .env
from dotenv import load_dotenv
load_dotenv()
def get_top_10_symbols_vs_usdt():
    """
    Fetch top crypto symbols by market cap from CoinGecko,
    validate 'SYMBOL/USDT' exists in Binance.
    Returns: List of valid tradable symbols.
    """
    exchange = ccxt.binance()
    exchange.load_markets()

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 20,  # Fetch extra to avoid filtering issue
        'page': 1,
        'sparkline': False
    }

    response = requests.get(url, params=params)
    data = response.json()

    valid_symbols = []
    for coin in data:
        symbol = coin['symbol'].upper()
        if symbol == "USDT":  # <- Explicitly skip this
            continue
        pair = f"{symbol}/USDT"
        if pair in exchange.symbols:
            valid_symbols.append(pair)
        else:
            print(f"❌ Skipping invalid pair: {pair}")
        if len(valid_symbols) == 10:
            break


    print("✅ Final Top 10 Symbols:", valid_symbols)
    return valid_symbols


'''
# this is for personal data
load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_SECRET")

exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True
})
'''
# No need for API keys in puclic data
exchange = ccxt.binance({
    'enableRateLimit': True
})

def fetch_ohlcv(symbol, timeframe='1h', limit=1000):
    """Fetch historical OHLCV data."""
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def save_raw_data(df, symbol, folder="data/raw/"):
    """Save OHLCV data to CSV."""
    symbol_clean = symbol.replace('/', '_')
    path = os.path.join(folder, f"{symbol_clean}.csv")
    df.to_csv(path, index=False)
    print(f"[✓] Saved: {path}")


# Fetching news using GNews API
# Make sure to set up your .env file with GNEWS_API_KEY
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")  # Make sure this is in your .env

def fetch_crypto_news_gnews(top_symbols, max_articles_per_symbol=5, sleep_time=1):
    """
    Fetch recent crypto news using GNews API for a list of top symbols.

    Args:
        top_symbols (List[str]): E.g., ['BTC/USDT', 'ETH/USDT']
        max_articles_per_symbol (int): Number of news articles to fetch per symbol
        sleep_time (int): Delay between API calls (to avoid rate limits)

    Returns:
        pd.DataFrame: News articles with metadata
    """
    print("🔎 Fetching crypto news via GNews API...")

    base_url = "https://gnews.io/api/v4/search"
    all_articles = []

    for symbol in top_symbols:
        coin_name = symbol.split('/')[0]
        query = f"{coin_name} crypto"
        params = {
            'q': query,
            'lang': 'en',
            'token': GNEWS_API_KEY,
            'max': max_articles_per_symbol,
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            for article in data.get('articles', []):
                all_articles.append({
                    'symbol': symbol,
                    'coin': coin_name,
                    'title': article['title'],
                    'description': article['description'],
                    'content': article['content'],
                    'publishedAt': article['publishedAt'],
                    'url': article['url'],
                    'source': article['source']['name'],
                    'fetchedAt': datetime.utcnow().isoformat()
                })

        except Exception as e:
            print(f"⚠️ Error fetching news for {coin_name}: {e}")

        sleep(sleep_time)

    news_df = pd.DataFrame(all_articles)
    return news_df



# Fetching Google Trends data using pytrends


from pytrends.request import TrendReq

def fetch_google_trends(top_symbols):
    """
    Fetch Google Trends interest for each top crypto coin.
    
    Args:
        top_symbols (list): List of crypto symbols like ['BTC/USDT', 'ETH/USDT']
    
    Returns:
        pd.DataFrame: Trends data for each symbol
    """
    print("🔍 Fetching Google Trends data...")

    pytrends = TrendReq(hl='en-US', tz=360)
    trend_data = []

    for symbol in top_symbols:
        coin = symbol.split('/')[0]
        kw_list = [f"{coin} crypto"]
        pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')

        df = pytrends.interest_over_time()
        if not df.empty:
            df = df.reset_index()
            df['symbol'] = symbol
            df['coin'] = coin
            df.rename(columns={df.columns[1]: 'trend_score'}, inplace=True)
            trend_data.append(df)

    all_trends = pd.concat(trend_data, ignore_index=True)
    return all_trends



def merge_all_data(ohlcv_dir, trends_path, sentiment_path):
    import os
    import pandas as pd
    from glob import glob

    print("🔗 Merging OHLCV, Trends, and Sentiment...")

    # Load and format Google Trends
    trends_df = pd.read_csv(trends_path)
    trends_df['date'] = pd.to_datetime(trends_df['date']).dt.date  # Only date part

    # Load and format Sentiment
    sentiment_df = pd.read_csv(sentiment_path)
    sentiment_df['publishedAt'] = pd.to_datetime(sentiment_df['publishedAt'], utc=True).dt.date

    all_data = []

    for file in glob(os.path.join(ohlcv_dir, '*.csv')):
        coin = os.path.basename(file).replace('.csv', '')
        df = pd.read_csv(file, parse_dates=['timestamp'])

        df['symbol'] = coin
        df['date'] = df['timestamp'].dt.date

        # Merge trends
        coin_trend = trends_df[trends_df['symbol'] == coin]
        df = df.merge(coin_trend[['date', 'trend_score']], on='date', how='left')

        # Merge sentiment (already has sentiment_avg)
        coin_sentiment = sentiment_df[sentiment_df['symbol'] == coin]
        df = df.merge(coin_sentiment[['publishedAt', 'sentiment_avg']],
                      left_on='date', right_on='publishedAt', how='left')
        df.drop(columns=['publishedAt'], inplace=True)

        all_data.append(df)

    master_df = pd.concat(all_data, ignore_index=True)
    master_df = master_df.sort_values(by=['symbol', 'timestamp'])

    return master_df

