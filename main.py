import requests
import asyncio
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes

BITQUERY_API_KEY = "ory_at_Cl2GFt1woVbMXFnxhZNBVh_50BxC-rojZ5MIcLLGR-k.uA7w5EChs5Buoq5CIfNPa8In-_ui7lsZXn9TdtOqsWE"
TELEGRAM_TOKEN = "8764476062:AAFffDxJTogKq-2lxXTybJOeqqaIs5CT8p8"
GROUP_ID = -1003647005142
CHECK_INTERVAL = 3600
AXIOM_BASE_URL = "https://axiom.trade/@wahrungs"

sent_tokens = set()

# ================= ALERTA =================

def build_message(symbol, price, volume):
    return f"""
🚨 LIVE WHALE MOVEMENT DETECTED

AI detected early accumulation.

━━━━━━━━━━━━━━━━━━

🐋 Whale Entry Signal

Token: #{symbol}

Price:
${price:.6f}

Detected Volume:
${volume:.2f}

━━━━━━━━━━━━━━━━━━

📊 Analysis

• Large wallets entering
• Liquidity increasing
• Early phase detected

━━━━━━━━━━━━━━━━━━

⏳ Public discovery phase not started

Data still not visible on public trackers.

Only early members can see this phase.

━━━━━━━━━━━━━━━━━━

🌍 GLOBAL SCANNER ACTIVE

🇺🇸 Early accumulation detected
🇧🇷 Acumulação inicial detectada
🇩🇪 Frühe Akkumulation erkannt
🇪🇸 Acumulación temprana detectada

━━━━━━━━━━━━━━━━━━

👇 Inspect activities:
"""

# ================= BITQUERY =================

def fetch_tokens():

    url = "https://graphql.bitquery.io"

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": BITQUERY_API_KEY
    }

    query = """
{
  Solana {
    DEXTrades(
      limit: {count: 5}
      orderBy: {descending: Block_Time}
    ) {
      Block {
        Time
      }
      Trade {

        Buy {
          AmountInUSD
          Currency {
            Symbol
            MintAddress
          }
        }

        Sell {
          AmountInUSD
          Currency {
            Symbol
            MintAddress
          }
        }

      }
    }
  }
}
"""

    try:

        response = requests.post(
            url,
            json={'query': query},
            headers=headers,
            timeout=10
        )

        print("STATUS:", response.status_code)

        data = response.json()

        print("RAW:", data)

        if not data:
            return []

        if data.get("data") is None:
            print("NO DATA RETURNED")
            return []

        trades = data["data"]["Solana"]["DEXTrades"]

        print("TOKENS FOUND:", len(trades))

        return trades

    except Exception as e:

        print("Bitquery error:", e)
        return []

    try:

        response = requests.post(
            url,
            json={'query': query},
            headers=headers,
            timeout=10
        )

        print("STATUS:", response.status_code)

        data = response.json()

        if not data:
            print("NO RESPONSE")
            return []

        if "data" not in data:
            print("INVALID RESPONSE")
            return []

        if data["data"] is None:
            print("NO DATA RETURNED")
            return []

        trades = data["data"]["Solana"]["DEXTrades"]

        print("TOKENS FOUND:", len(trades))

        return trades

    except Exception as e:

        print("Bitquery error:", e)
        return []
# ================= ALERTAS =================

async def detect_pumps(context: ContextTypes.DEFAULT_TYPE):

    tokens = fetch_tokens()

    for item in tokens:

    try:

        symbol = item['Trade']['Buy']['Currency']['Symbol']
        address = item['Trade']['Buy']['Currency']['MintAddress']
        price = 0.000001
        volume = float(item['Trade']['Buy']['Amount'])

        if address in sent_tokens:
            continue

        sent_tokens.add(address)

        message = build_message(symbol, price, volume)

        keyboard = [[InlineKeyboardButton(
            "👁 See the whales' entry points 🐋",
            url=f"{AXIOM_BASE_URL}?token={address}"
        )]]

        markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=message,
            reply_markup=markup
        )

        print("ALERT SENT:", symbol)

    except Exception as e:

        print("TOKEN ERROR:", e)
# ================= GATILHOS =================

trigger_messages = [
"""📡 Scanner Status

System operating normally.

Multiple early accumulation patterns detected today.

Next signal possible anytime.
""",

"""🐋 Whale Behavior Update

Large wallets accumulating quietly.

Smart money moves before price.
""",

"""⚡ Early Phase Activity

AI detecting accumulation patterns.

Monitoring continues 24/7.
"""
]

async def send_trigger(context):

    msg = random.choice(trigger_messages)

    try:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=msg
        )
    except:
        pass

# ================= MAIN =================

async def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.job_queue.run_repeating(
        detect_pumps,
        interval=CHECK_INTERVAL,
        first=60
    )

    app.job_queue.run_repeating(
        send_trigger,
        interval=21600,
        first=120
    )

    print("ELITE WHALE BOT RUNNING")

    await app.run_polling()

# ========= START BOT =========

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# ALERTAS BITQUERY
app.job_queue.run_repeating(
    detect_pumps,
    interval=CHECK_INTERVAL,
    first=60
)

# GATILHOS 6 HORAS
app.job_queue.run_repeating(
    send_trigger,
    interval=21600,
    first=120
)

print("ELITE WHALE BOT RUNNING")

app.run_polling()
