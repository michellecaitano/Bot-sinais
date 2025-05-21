import time
import requests
import pytz
from datetime import datetime
from binance.client import Client
from ta.momentum import RSIIndicator
import pandas as pd

# === CONFIGURAÇÕES ===
API_KEY = '' # Opcional, pode deixar em branco
API_SECRET = ''
TOKEN = '8154039659:AAHFoDc-ki06NfinbSHXdDoKYX7IOPVqiIw'
CHAT_ID = '809142405'
HORARIO_BSB = pytz.timezone('America/Sao_Paulo')
ATIVOS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'IDXUSDT', 'MEMXUSDT', 'TBCUSDT']

client = Client(API_KEY, API_SECRET)

# === ENVIA MENSAGEM PARA TELEGRAM ===
def enviar_mensagem(mensagem):
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {'chat_id': CHAT_ID, 'text': mensagem}
response = requests.post(url, data=payload)
print(f"[{datetime.now(HORARIO_BSB).strftime('%H:%M:%S')}] Sinal enviado.")
return response

# === ESTRATÉGIA 1: SUPORTE + REJEIÇÃO ===
def estrategia_suporte_resistencia(ativo):
klines = client.get_klines(symbol=ativo, interval=Client.KLINE_INTERVAL_15MINUTE, limit=20)
ultimos = [float(c[1]) for c in klines] # Preços de abertura
zona = min(ultimos[-5:])
atual = float(klines[-1][1]) # Preço atual

# Análise do candle atual
candle = klines[-1]
open_price = float(candle[1])
close_price = float(candle[4])
low_price = float(candle[3])
body = abs(close_price - open_price)
pavio = abs(open_price - low_price)

if pavio > body * 2 and atual <= zona * 1.01:
mensagem = (
f"[SINAL - SUPORTE/REJEIÇÃO]\nAtivo: {ativo}\n"
f"Estratégia: Suporte + Pullback com Rejeição\n"
f"Preço: {atual:.2f}\n"
f"Horário: {datetime.now(HORARIO_BSB).strftime('%H:%M:%S')}"
)
enviar_mensagem(mensagem)

# === ESTRATÉGIA 2: TENDÊNCIA + RSI ===
def estrategia_tendencia_rsi(ativo):
klines = client.get_klines(symbol=ativo, interval=Client.KLINE_INTERVAL_15MINUTE, limit=50)
closes = [float(c[4]) for c in klines]
rsi = RSIIndicator(pd.Series(closes), window=14).rsi().iloc[-1]
atual = closes[-1]
tendencia = closes[-1] > closes[-14]

if 40 < rsi < 60 and tendencia:
mensagem = (
f"[SINAL - TENDÊNCIA + RSI]\nAtivo: {ativo}\n"
f"Estratégia: Tendência de alta + Pullback com RSI\n"
f"RSI: {rsi:.2f}\n"
f"Preço: {atual:.2f}\n"
f"Horário: {datetime.now(HORARIO_BSB).strftime('%H:%M:%S')}"
)
enviar_mensagem(mensagem)

# === LOOP PRINCIPAL 24H ===
print("BOT INICIADO - MONITORAMENTO 24H")

while True:
for ativo in ATIVOS:
try:
estrategia_suporte_resistencia(ativo)
estrategia_tendencia_rsi(ativo)
except Exception as e:
print(f"Erro ao analisar {ativo}: {e}")
time.sleep(60 * 15)
