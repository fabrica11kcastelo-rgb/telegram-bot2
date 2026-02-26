import requests
import asyncio
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes

# ========= CONFIG =========

BITQUERY_API_KEY = "ory_at_Cl2GFt1woVbMXFnxhZNBVh_50BxC-rojZ5MIcLLGR-k.uA7w5EChs5Buoq5CIfNPa8In-_ui7lsZXn9TdtOqsWE"

TELEGRAM_TOKEN = "8764476062:AAFffDxJTogKq-2lxXTybJOeqqaIs5CT8p8"

GROUP_ID = -1003647005142

# 1 hora = ~720 consultas mês
CHECK_INTERVAL = 3600

AXIOM_BASE_URL = "https://axiom.trade/@wahrungs"

sent_tokens = set()

# ========= ALERTA VIRAL OTIMIZADO =========

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

تم الكشف عن التراكم الأولي 🇦🇪

🇧🇷 Acumulação inicial detectada

🇩🇪 Frühe Akkumulation erkannt

🇨🇳检测到初始积累

🇪🇸 Acumulación temprana detectada

🇷🇺 Обнаружено первоначальное накопление

━━━━━━━━━━━━━━━━━━

👇Inspect activities:
"""


# ========= BITQUERY =========

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
          limit: {count: 4}
          orderBy: {descending: Trade_Buy_Amount}
          where: {
            Trade_Buy_Amount: {gt: 300}
          }
        ) {
          Trade {
            Buy {
              Currency {
                Symbol
                MintAddress
              }
              Amount
            }
            Price
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

        data = response.json()

        return data['data']['Solana']['DEXTrades']

    except Exception as e:

        print("Bitquery error:", e)
        return []


# ========= ALERTAS =========

async def detect_pumps(context: ContextTypes.DEFAULT_TYPE):

    tokens = fetch_tokens()

    for item in tokens:

        symbol = item['Trade']['Buy']['Currency']['Symbol']
        address = item['Trade']['Buy']['Currency']['MintAddress']
        price = item['Trade']['Price']
        volume = item['Trade']['Buy']['Amount']

        if address in sent_tokens:
            continue

        sent_tokens.add(address)

        message = build_message(symbol, price, volume)

        keyboard = [[InlineKeyboardButton(

            "👁 See the whales' entry points 🐋",

            url=f"{AXIOM_BASE_URL}?token={address}"

        )]]

        markup = InlineKeyboardMarkup(keyboard)

        try:

            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                reply_markup=markup
            )

            # UPDATE depois de 10 minutos (truque profissional)
            await asyncio.sleep(600)

            update_message = f"""
📈 Signal Update

Token #{symbol}

Liquidity expanding faster than expected.

Early entries positioning.

AI monitoring continues.
"""

            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=update_message
            )

        except Exception as e:

            print("Telegram error:", e)


# ========= GATILHOS PSICOLÓGICOS =========

trigger_messages = [

"""📡 Scanner Status

System operating normally.

Multiple early accumulation patterns detected today.

Most traders enter too late.

Next signal possible anytime.
""",

"""🐋 Whale Behavior Update

Several large wallets accumulating quietly.

Smart money moves before price.

Stay prepared.
""",

"""⚡ Early Phase Activity

AI detecting accumulation patterns.

Best entries happen early.

Monitoring continues.
""",

"""📊  Market Intelligence

Liquidity increasing.

Breakouts usually start quietly.

Next alert coming soon.""",

"""🔎 AI Scanner Report

New accumulation waves detected.

Early positioning matters.

System running 24/7.
""",

"""🌍 Global Scan Active

Signals detected across ecosystem.

Early traders benefit most.

Next detection anytime.
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


# ========= START BOT =========

async def main():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # ALERTAS REAIS BITQUERY
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

    await app.run_polling()

  if __name__ == "__main__":
    import asyncio

    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())

            
