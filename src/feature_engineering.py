
# src/features/feature_engineering.py

import pandas as pd
import ta  # Technical Analysis Library (ta-lib alternative)

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators to the OHLCV dataframe."""
    
    df = df.copy()
    
    # Moving Averages
    df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
    df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
    
    # RSI
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    
    # MACD
    macd = ta.trend.macd(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    
    # Volatility
    df['volatility'] = df['high'] - df['low']
    
    # Momentum (ROC)
    df['roc'] = ta.momentum.roc(df['close'], window=10)
    
    # Drop NA values from indicator calculations
    df.dropna(inplace=True)
    
    return df


# 📁 src/feature_engineering.py (recommended)
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def apply_vader_sentiment(news_df):
    """
    Add VADER sentiment scores to news articles.
    
    Args:
        news_df (pd.DataFrame): News dataframe with 'title' or 'description'
    
    Returns:
        pd.DataFrame: News dataframe with VADER scores
    """
    print("🧠 Analyzing sentiment using VADER...")

    analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(text):
        if pd.isna(text):
            return 0.0
        return analyzer.polarity_scores(text)['compound']

    news_df['sentiment_title'] = news_df['title'].apply(get_sentiment)
    news_df['sentiment_description'] = news_df['description'].apply(get_sentiment)
    news_df['sentiment_avg'] = news_df[['sentiment_title', 'sentiment_description']].mean(axis=1)

    return news_df
