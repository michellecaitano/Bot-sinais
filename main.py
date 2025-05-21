import time
import requests
import pytz
from datetime import datetime
from binance.client import Client
from ta.momentum import RSIIndicator
import pandas as pd

# === CONFIGURAÇÕES ===
API_KEY = '' # Opcional — use se precisar acessar dados privados da Binance
API_SECRET = ''
TOKEN = '8154039659:AAHFoDc-ki06NfinbSHXdDoKYX7IOPVqiIw' # Seu token do Telegram
CHAT_ID = '809142405' # Seu chat_id do Telegram
HORARIO_BSB = pytz.timezone('America/Sao_Paulo')
ATIVOS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'IDXUSDT', 'MEMXUSDT', 'TBCUSDT']

# Conecta à API da Binance
client = Client(API_KEY, API_SECRET)

# === ENVIO DE MENSAGEM PARA TELEGRAM ===
def enviar_mensagem(mensagem):
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {'chat_id': CHAT_ID, 'text': mensagem}
response = requests.post(url, data=payload)
print(f"[{datetime.now(HORARIO_BSB).strftime('%H:%M:%S')}] Sinal enviado.")
return response
payload = {'chat_id': CHAT_ID, 'text': mensagem}
response = requests.post(url, data=payload)
print(f"[{datetime.now(HORARIO_BSB).strftime('%H:%M:%S')}] Sinal enviado.")
return response

# === ESTRATÉGIA 1: SUPORTE + PULLBACK COM REJEIÇÃO ===
def estrategia_suporte_resistencia(ativo):
klines = client.get_klines(symbol=ativo, interval=Client.KLINE_INTERVAL_15MINUTE, limit=20)
ultimos = [float(c[1]) for c in klines] # Preços de abertura

zona = min(ultimos[-5:]) # Simula zona de suporte recente
atual = float(klines[-1][1]) # Preço de abertura atual

# Verifica se o candle tem rejeição (pavio > corpo)
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

# === ESTRATÉGIA 2: TENDÊNCIA + PULLBACK + RSI ===
def estrategia_tendencia_rsi(ativo):
klines = client.get_klines(symbol=ativo, interval=Client.KLINE_INTERVAL_15MINUTE, limit=50)
closes = [float(c[4]) for c in klines] # Fechamentos
rsi = RSIIndicator(pd.Series(closes), window=14).rsi().iloc[-1]
atual = closes[-1]
tendencia = closes[-1] > closes[-14] # Tendência de alta simples

if 40 < rsi < 60 and tendencia:
mensagem = (
f"[SINAL - TENDÊNCIA + RSI]\nAtivo: {ativo}\n"
f"Estratégia: Tendência de alta + Pullback com RSI\n"
f"RSI: {rsi:.2f}\n"
f"Preço: {atual:.2f}\n"
f"Horário: {datetime.now(HORARIO_BSB).strftime('%H:%M:%S')}"
)
enviar_mensagem(mensagem)

# === LOOP PRINCIPAL — Roda a cada 15 minutos ===
print("BOT INICIADO - MONITORAMENTO 24H")

while True:
for ativo in ATIVOS:
try:
estrategia_suporte_resistencia(ativo)
estrategia_tendencia_rsi(ativo)
except Exception as e:
print(f"Erro ao analisar {ativo}: {e}")
time.sleep(60 * 15) # Espera 15 minutos antes da próxima análise
