# src/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
from data_loader import fetch_data_from_ccxt
from model import train_model
from ai_intelligence import get_crypto_news
from alerts import send_telegram_message, generate_pdf_report, send_telegram_file

# Initialize scheduler
scheduler = BackgroundScheduler()

# 1. Job: Fetch Data (OHLCV + News)
def fetch_data():
    print("[*] Fetching data...")
    fetch_data_from_ccxt()  # Assuming data_loader.py has this function
    news_data = get_crypto_news("crypto")
    print(f"[✓] Data fetched at {datetime.now()}")

# 2. Job: Train ML Model (for model retraining)
def retrain_model():
    print("[*] Retraining model...")
    train_model()  # Assuming model.py has this function
    print(f"[✓] Model retrained at {datetime.now()}")

# 3. Job: Send Alerts (e.g., signals)
def send_daily_alerts():
    print("[*] Generating daily alert and report...")
    # Generate signals
    signals = {
        "BTC": "Buy",
        "ETH": "Hold",
        "SOL": "Sell"
    }
    # Generate summary using AI
    summary = "Today's market shows moderate bullish sentiment."
    
    # Generate PDF report
    report_path = generate_pdf_report(signals, summary)
    
    # Send alerts
    send_telegram_message("📈 Daily Crypto Signals Ready!")
    send_telegram_file(report_path, caption="📊 Full Report")
    print(f"[✓] Alerts sent at {datetime.now()}")

# 4. Job: Periodic Tasks (every 1 hour, for example)
def schedule_periodic_tasks():
    scheduler.add_job(fetch_data, 'interval', hours=1)
    scheduler.add_job(retrain_model, 'interval', days=1)  # Retrain model every 1 day
    scheduler.add_job(send_daily_alerts, 'interval', hours=24)  # Send alerts every 24 hours

# 5. Start Scheduler
def start_scheduler():
    print("[*] Starting scheduler...")
    schedule_periodic_tasks()
    scheduler.start()

# Keep the scheduler running in the background
if __name__ == "__main__":
    start_scheduler()
    try:
        while True:
            time.sleep(2)  # Keep the main thread alive
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
