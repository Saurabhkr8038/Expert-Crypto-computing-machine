# src/alerts.py

import telegram
from fpdf import FPDF
from datetime import datetime
import os

# Load Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# 1. Send message to Telegram
def send_telegram_message(message: str):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("[✓] Telegram message sent!")
    except Exception as e:
        print(f"[x] Failed to send message: {e}")

# 2. Send a file to Telegram (PDF, CSV, etc.)
def send_telegram_file(file_path: str, caption: str = ""):
    try:
        with open(file_path, "rb") as file:
            bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=file, caption=caption)
        print("[✓] Telegram file sent!")
    except Exception as e:
        print(f"[x] Failed to send file: {e}")


# 3. Generate PDF report
class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Daily Crypto Signal Report", 0, 1, "C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, datetime.now().strftime("%Y-%m-%d %H:%M"), 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_signal_section(self, signal_data):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Signals Summary", 0, 1)
        self.set_font("Arial", "", 12)
        for token, signal in signal_data.items():
            self.cell(0, 10, f"{token}: {signal}", 0, 1)

    def add_summary_section(self, ai_summary):
        self.ln(5)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "AI Summary", 0, 1)
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, ai_summary)


def generate_pdf_report(signal_data: dict, ai_summary: str, filename="daily_signals.pdf"):
    pdf = PDFReport()
    pdf.add_page()
    pdf.add_signal_section(signal_data)
    pdf.add_summary_section(ai_summary)
    pdf.output(filename)
    print(f"[✓] PDF report generated: {filename}")
    return filename
