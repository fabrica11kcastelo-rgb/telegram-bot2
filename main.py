import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes

# ================= CONFIGURAÇÕES =================

BITQUERY_API_KEY = "ory_at_Cl2GFt1woVbMXFnxhZNBVh_50BxC-rojZ5MIcLLGR-k.uA7w5EChs5Buoq5CIfNPa8In-_ui7lsZXn9TdtOqsWE"

TELEGRAM_TOKEN = "8764476062:AAFffDxJTogKq-2lxXTybJOeqqaIs5CT8p8"

GROUP_ID = -1003647005142

CHECK_INTERVAL = 1800  # 30 minutos

AXIOM_BASE_URL = "https://axiom.trade/@wahrungs"

# ================= CONTROLE ANTI-SPAM =================

sent_tokens = set()

# ================= MENSAGEM ALERTA =================

def build_message(symbol, price, volume):
    return f"""
🧠 AI ACCUMULATION SIGNAL

Automated blockchain scan detected unusual buying activity.

🇺🇸 ENGLISH
Token: #{symbol}
Price: ${price:.6f}
Volume: ${volume:.2f}

🇩🇪 DEUTSCH
Token: #{symbol}
Preis: ${price:.6f}
Volumen: ${volume:.2f}

🇪🇸 ESPAÑOL
Token: #{symbol}
Precio: ${price:.6f}
Volumen: ${volume:.2f}

🇧🇷 PORTUGUÊS
Token: #{symbol}
Preço: ${price:.6f}
Volume: ${volume:.2f}

🇫🇷 FRANÇAIS
Token: #{symbol}
Prix: ${price:.6f}
Volume: ${volume:.2f}

🇮🇹 ITALIANO
Token: #{symbol}
Prezzo: ${price:.6f}
Volume: ${volume:.2f}

⚡ Large wallets entered this token recently.

Liquidity increasing fast.

👇 Secure your position before public breakout:
"""

# ================= MARKET UPDATE 12H =================

async def market_update(context: ContextTypes.DEFAULT_TYPE):
    message = """
📊 Market Update

Crypto market is heating up again.

Early signals are appearing more frequently.

Stay ready for the next opportunity.

⚡ Next alert could come anytime.
"""

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=message
    )

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
          limit: {count: 3}
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

# ================= ALERTAS =================

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
            "🚀 BUY EARLY (PUMP SOON)",
            url=f"{AXIOM_BASE_URL}?token={address}"
        )]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                reply_markup=reply_markup
            )
        except Exception as e:
            print("Telegram error:", e)

# ================= START BOT =================

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Adiciona os jobs repetitivos
application.job_queue.run_repeating(
    detect_pumps,
    interval=CHECK_INTERVAL,
    first=30
)

# MARKET UPDATE 12 HORAS (43200 segundos = 12h)
application.job_queue.run_repeating(
    market_update,
    interval=43200,
    first=60
)

print("BOT ULTRA GLOBAL RODANDO...")

# Inicia o polling (sem necessidade de porta exposta)
application.run_polling(
    allowed_updates=["message", "callback_query"],  # Otimiza polling
    drop_pending_updates=True  # Ignora mensagens antigas ao iniciar
)
