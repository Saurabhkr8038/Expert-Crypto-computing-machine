# src/ai_intelligence.py

import requests
import openai
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pytrends.request import TrendReq
from datetime import datetime
import os

# Load OpenAI key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

analyzer = SentimentIntensityAnalyzer()
pytrends = TrendReq(hl='en-US', tz=360)


# 1. Get Crypto News (GNews API)
def get_crypto_news(keyword="crypto", max_articles=10):
    """
    Fetch latest news articles using GNews API.
    """
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    url = f"https://gnews.io/api/v4/search?q={keyword}&lang=en&max={max_articles}&token={GNEWS_API_KEY}"
    print(f"[*] Fetching news for: {keyword}")
    
    response = requests.get(url)
    articles = response.json().get("articles", [])
    
    news_data = [
        {
            "title": article["title"],
            "description": article["description"],
            "publishedAt": article["publishedAt"],
            "source": article["source"]["name"]
        }
        for article in articles
    ]
    return pd.DataFrame(news_data)


# 2. GPT Summarizer
def summarize_with_gpt(text, model="gpt-3.5-turbo"):
    """
    Summarize news headlines or descriptions using OpenAI GPT.
    """
    prompt = f"Summarize the following crypto news in 2-3 bullet points:\n\n{text}"
    
    print("[*] Summarizing with GPT...")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7
    )
    summary = response['choices'][0]['message']['content'].strip()
    return summary


# 3. Google Trends Tracker
def get_trend_score(keyword="Bitcoin"):
    """
    Fetch interest over time for a keyword using Google Trends.
    """
    pytrends.build_payload([keyword], timeframe='now 7-d')
    df = pytrends.interest_over_time()
    if not df.empty:
        score = int(df[keyword].iloc[-1])
        print(f"[✓] Google Trends score for {keyword}: {score}")
        return score
    return 0


# 4. VADER Sentiment Scoring
def analyze_sentiment(text):
    """
    Score sentiment from -1 (negative) to +1 (positive).
    """
    sentiment = analyzer.polarity_scores(text)
    return sentiment['compound']
