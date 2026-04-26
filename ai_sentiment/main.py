import os
import time
import datetime
import pandas as pd
from google import genai
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Configuracion desde .env
DB_URL = os.getenv("DB_URL", "postgresql://admin:adminpassword@localhost:5432/trading_db")
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Falta la variable de entorno GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

def discover_model():
    """Busca cualquier modelo disponible que sea de la familia Flash."""
    print(f"[{datetime.datetime.now()}] Escaneando modelos disponibles...")
    try:
        # Listamos todos los modelos y buscamos el nombre real
        for m in client.models.list():
            m_name = m.name # Atributo basico del SDK
            if "flash" in m_name.lower():
                # En 2026, el nombre puede ser 'gemini-2.0-flash' o 'models/gemini-1.5-flash'
                print(f"[{datetime.datetime.now()}] Modelo encontrado: {m_name}")
                return m_name
    except Exception as e:
        print(f"Error al listar: {e}")
    
    # Si falla la lista, intentamos el nombre estandar de 2026 sin el prefijo 'models/'
    return "gemini-1.5-flash"

def get_db_engine():
    engine = create_engine(DB_URL)
    while True:
        try:
            with engine.connect(): return engine
        except OperationalError:
            time.sleep(5)

def analyze_sentiment(ticker, engine, model_id):
    query = f"SELECT title, summary FROM daily_news WHERE ticker = '{ticker}' ORDER BY ingested_at DESC LIMIT 5"
    df = pd.read_sql(query, engine)
    
    if df.empty: return
        
    print(f"[{datetime.datetime.now()}] Analizando {ticker} con {model_id}...")
    
    news_text = "\n".join([f"- {row['title']}" for _, row in df.iterrows()])
    
    prompt = f"Analiza estas noticias de {ticker} y responde solo con un JSON (sentimiento: ALCISTA/BAJISTA, puntuacion: -1 a 1, razon_corta):\n{news_text}"
    
    try:
        # Llamada directa al modelo descubierto
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        # Limpieza y salida
        print(f"\n--- IA: {ticker} ---\n{response.text.strip()}\n-----------------\n")
        
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error en llamada: {e}")

def main():
    print(f"[{datetime.datetime.now()}] Reiniciando Cerebro Semantico...")
    engine = get_db_engine()
    
    # Descubrimiento en tiempo de ejecucion
    target_model = discover_model()
    
    tickers = ["SPY", "AAPL"]
    while True:
        for ticker in tickers:
            analyze_sentiment(ticker, engine, target_model)
            time.sleep(5)
        time.sleep(3600)

if __name__ == "__main__":
    main()