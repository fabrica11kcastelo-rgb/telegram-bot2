import requests
import logging
import os  # <--- Adicionado aqui
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes

# Configura logging para ver melhor nos logs do Shard Cloud
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= CONFIGURAÇÕES =================
# Agora lendo das variáveis de ambiente do Shard Cloud

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não encontrado nas variáveis de ambiente! Adicione no Shard Cloud.")

BITQUERY_API_KEY = os.getenv("BITQUERY_API_KEY")
if not BITQUERY_API_KEY:
    raise ValueError("BITQUERY_API_KEY não encontrado nas variáveis de ambiente! Adicione no Shard Cloud.")

GROUP_ID = int(os.getenv("GROUP_ID", "-1003647005142"))  # fallback caso esqueça de adicionar

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
    try:
        await context.bot.send_message(chat_id=GROUP_ID, text=message)
        logger.info("Market update enviado com sucesso")
    except Exception as e:
        logger.error("Erro ao enviar market update: %s", e)

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
        response = requests.post(url, json={'query': query}, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}).get('Solana', {}).get('DEXTrades', [])
    except Exception as e:
        logger.error("Bitquery error: %s", e)
        return []

# ================= ALERTAS =================

async def detect_pumps(context: ContextTypes.DEFAULT_TYPE):
    tokens = fetch_tokens()
    if not tokens:
        logger.info("Nenhum token detectado nesta rodada")
        return

    for item in tokens:
        try:
            symbol = item['Trade']['Buy']['Currency']['Symbol']
            address = item['Trade']['Buy']['Currency']['MintAddress']
            price = float(item['Trade']['Price']) if item['Trade']['Price'] else 0.0
            volume = float(item['Trade']['Buy']['Amount']) if item['Trade']['Buy']['Amount'] else 0.0

            if address in sent_tokens:
                continue

            sent_tokens.add(address)
            logger.info("Novo pump detectado: %s (%s)", symbol, address)

            message = build_message(symbol, price, volume)

            keyboard = [[InlineKeyboardButton(
                "🚀 BUY EARLY (PUMP SOON)",
                url=f"{AXIOM_BASE_URL}?token={address}"
            )]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error("Erro processando token %s: %s", item.get('Trade', {}).get('Buy', {}).get('Currency', {}).get('Symbol'), e)

# ================= START BOT =================

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Job de teste inicial
    async def start_message(context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text="🤖 Bot ultra global iniciado! Checando pumps a cada 30 min."
        )

    application.job_queue.run_once(start_message, when=10)

    # Jobs repetitivos
    application.job_queue.run_repeating(
        detect_pumps,
        interval=CHECK_INTERVAL,
        first=30
    )

    application.job_queue.run_repeating(
        market_update,
        interval=43200,  # 12 horas
        first=60
    )

    logger.info("BOT ULTRA GLOBAL RODANDO...")
    print("BOT ULTRA GLOBAL RODANDO...")

    application.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
