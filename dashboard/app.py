# app.py

# Import necessary libraries
from flask import Flask, render_template, jsonify
import plotly.express as px
import pandas as pd
from datetime import datetime
import json

# Initialize Flask app
app = Flask(__name__)

# Example data - This should be dynamically updated with real-time signals
signal_data = {
    "timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 5,
    "symbol": ["Bitcoin"] * 5,
    "signal": [1, 0, 1, -1, 0],  # 1: Buy, 0: Hold, -1: Sell
    "sentiment": [0.5, 0.2, 0.8, -0.3, 0.1],  # Sentiment score
    "trend": [65, 50, 70, 30, 55]  # Google Trend scores
}

# Convert data into a DataFrame
df_signal = pd.DataFrame(signal_data)

# Plotting function to create interactive graphs
def create_signal_plot():
    fig = px.scatter(df_signal, x="timestamp", y="sentiment", color="signal",
                     labels={'timestamp': 'Time', 'sentiment': 'Sentiment Score'},
                     title="Real-Time Sentiment Analysis")
    return fig

def create_trend_plot():
    fig = px.scatter(df_signal, x="timestamp", y="trend", color="signal",
                     labels={'timestamp': 'Time', 'trend': 'Google Trend Score'},
                     title="Real-Time Google Trend Analysis")
    return fig

# Flask route to serve the dashboard
@app.route('/')
def index():
    # Create plots
    sentiment_plot = create_signal_plot()
    trend_plot = create_trend_plot()
    
    # Convert plots to HTML format to be embedded in the page
    sentiment_plot_html = sentiment_plot.to_html(full_html=False)
    trend_plot_html = trend_plot.to_html(full_html=False)

    return render_template('index.html', sentiment_plot=sentiment_plot_html, trend_plot=trend_plot_html)

# Flask route to provide real-time signals via API
@app.route('/api/real_time_signals', methods=['GET'])
def api_real_time_signals():
    # Return current signals data in JSON format
    return jsonify(df_signal.to_dict(orient="records"))

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
