import os
import logging
import requests
import json
import time
from telegram import Bot

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Bot Token from Environment Variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Add this variable in Railway later

bot = Bot(token=BOT_TOKEN)

# Data Sources
DATA_SOURCES = [
    "https://api.pump.fun",
    "https://api.dexscreener.com/latest/dex/pairs/solana",
    "https://api.birdeye.so",
    "https://api.geckoterminal.com/api/v2/networks/solana",
    "https://api.solscan.io",
]

# Function to Check New Tokens
def fetch_new_tokens():
    results = []
    for url in DATA_SOURCES:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                results.append(data)
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
    return results

# Scoring Function
def calculate_scores(token_data):
    project_score = 50
    safety_score = 50
    popularity_score = 50

    if "whales" in token_data:
        project_score += 20
    if "rugpull" in token_data:
        safety_score -= 30
    if "trending" in token_data:
        popularity_score += 25

    return project_score, safety_score, popularity_score

# Send Alert to Telegram
def send_alert(token_name, project_score, safety_score, popularity_score):
    message = f"""
    🚀 *New Token Found: {token_name}*
    📊 *Project Score:* {project_score}/100
    🛡️ *Safety Score:* {safety_score}/100
    🔥 *Popularity Score:* {popularity_score}/100
    """
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# Main Loop
while True:
    tokens = fetch_new_tokens()
    for token in tokens:
        name = token.get("name", "Unknown Token")
        project_score, safety_score, popularity_score = calculate_scores(token)
        send_alert(name, project_score, safety_score, popularity_score)
    
    time.sleep(300)  # Wait 5 minutes before checking again
