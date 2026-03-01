import requests
import time
import random

#########################################
# CONFIGURAÇÃO
#########################################

TELEGRAM_TOKEN = "8764476062:AAFffDxJTogKq-21xXTybJ0eqqaIs5CT8p8"

GROUP_ID = -1003647005142

BITQUERY_API_KEY = "ory_at_Cl2GFt1woVbMXFnxhZNBVh_50BxC-rojZ5MIcLLGR-k.uA7w5EChs5Buoq5CIfNPa8In-_ui7lsZXn9TdtOqsWE"

REF_LINK = "https://axiom.trade/@wahrungs"

#########################################
# ENDPOINT BITQUERY V2
#########################################

URL = "https://streaming.bitquery.io/graphql"
#########################################
# CONTROLE
#########################################

sent_tokens = set()

#########################################
# TELEGRAM
#########################################

def send_telegram(text, button=True):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": GROUP_ID,
        "text": text,
        "parse_mode":"HTML"
    }

    if button:

        payload["reply_markup"] = {
            "inline_keyboard":[[
                {
                    "text":"🔥 Check Live Activity",
                    "url":REF_LINK
                }
            ]]
        }

    try:
        requests.post(url,json=payload,timeout=20)
        print("Telegram OK")

    except Exception as e:
        print("Telegram Error:",e)


#########################################
# GET DATA BITQUERY
#########################################

def get_data():

    query = """
query MyQuery {
  Solana(dataset: realtime) {
    DEXTrades(
      limit: {count: 10}
      orderBy: {descendingByField: "TradeAmountInUSD"}
    ) {
      Trade {
        Buy {
          Currency {
            Symbol
            Name
            MintAddress
          }
          Amount
          Price
          PriceInUSD
        }
      }
      TradeAmountInUSD: sum(of: Trade_Buy_AmountInUSD)
      Block {
        Time
      }
    }
  }
}
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BITQUERY_API_KEY}"
    }

    try:

        r = requests.post(URL, json={"query": query}, headers=headers)

        print("STATUS:", r.status_code)
        print("RAW:", r.text[:500])

        data = r.json()

        if "data" not in data or data["data"] is None:
            print("Bitquery data null")
            return None

        return data

    except Exception as e:
        print("Bitquery error:", e)
        return None


#########################################
# FILTRO INTELIGENTE
#########################################

def detect_signals():

    data = get_data()

    if not data:
        print("Bitquery returned empty")
        return

    try:

        if "data" not in data:
            print("Bitquery no data field")
            return

        if data["data"] is None:
            print("Bitquery data null")
            return

        if "Solana" not in data["data"]:
            print("Bitquery no Solana")
            return

        if data["data"]["Solana"] is None:
            print("Bitquery Solana null")
            return

        if "DEXTrades" not in data["data"]["Solana"]:
            print("Bitquery no trades")
            return


        trades = data["data"]["Solana"]["DEXTrades"]

        print("TOKENS FOUND:", len(trades))


        if not trades:
            print("No trades found")
            return


        for t in trades:

            try:

                token = t.get("Trade", {}).get("Buy", {}).get("Currency", {}).get("MintAddress")

                if not token:
                    continue

                if token in sent_tokens:
                    continue


                symbol = t.get("Trade", {}).get("Buy", {}).get("Currency", {}).get("Symbol")

if not symbol or symbol == "":
    symbol = "NEW TOKEN"

                name = t.get("Trade", {}).get("Buy", {}).get("Currency", {}).get("Name")
 
if not name or name == "":
    name = "Unknown"


# VOLUME EM USD REAL
               volume = float(t.get("TradeAmountInUSD", 0))


               buy_amount = float(t.get("Trade", {}).get("Buy", {}).get("Amount", 0))

               price = float(t.get("Trade", {}).get("Buy", {}).get("Price", 0))

            except Exception as e:

                print("Parse error:", e)

                continue


            ###################################
            # FILTROS
            ###################################

            if volume < 3000:
                continue

            if buy_amount < 50:
                continue

            if price <= 0:
                continue


            print("ALERTA ENCONTRADO")

            print(symbol, volume)


            sent_tokens.add(token)

            templates = [

f"""

🚨 <b>EARLY PUMP SIGNAL</b>

Smart money detected accumulation.

Token: <b>{name}</b>
Symbol: <b>${symbol}</b>

💰 Volume Rising
{round(volume,2)}

🐋 Whale Activity Detected

⚡ Possible Early Pump Phase

Traders entering quietly.

⏳ Early entries win.

👇 Track Token Live
""",

f"""

🔥 <b>WHAL E ENTRY ALERT</b>

Large buyers entering position.

Token: <b>{name}</b>
Symbol: <b>${symbol}</b>

🐋 Whale Detected

💰 Volume:
{round(volume,2)}

⚡ Accumulation Phase

Possible breakout forming.

👇 Watch Before Pump
""",

f"""

📈 <b>SMART MONEY FLOW</b>

Unusual activity detected.

Token: <b>{name}</b>
Symbol: <b>${symbol}</b>

💰 Liquidity Increasing

🐋 Institutional Buying

⚡ Early Stage Opportunity

Don't wait for the pump.

👇 Analyze Token
"""
]

            send_telegram(random.choice(templates),True)

    except Exception as e:

        print("Bitquery safe error:",e)


#########################################
# MENSAGENS VIRALIZAÇÃO
#########################################

hooks = [

"""🔥 Most traders enter too late.

This bot detects before pumps.

Stay ready.""",

"""📊 Early signals create big profits.

Watch alerts carefully.

Opportunities appear fast.""",

"""🚀 Smart money moves silently.

Alerts here reveal early moves.

Be prepared.""",

"""⚡ This bot tracks real whale activity.

Next opportunity can appear anytime.

Stay online."""
]


def send_hook():

    msg=random.choice(hooks)

    send_telegram(msg,False)


#########################################
# LOOP
#########################################

print("INSTITUTIONAL BOT V2 RUNNING")

last_hook=0

while True:

    now=time.time()

    detect_signals()

    if now-last_hook>21600:

        send_hook()

        last_hook=now

    time.sleep(3600)
