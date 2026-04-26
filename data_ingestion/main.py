import time
import datetime
import os
import yfinance as yf
import pandas as pd
import feedparser
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DB_URL = os.getenv("DB_URL", "postgresql://admin:adminpassword@localhost:5432/trading_db")

def get_db_engine():
    print(f"[{datetime.datetime.now()}] Iniciando motor de base de datos...")
    engine = create_engine(DB_URL)
    
    while True:
        try:
            with engine.connect() as conn:
                print(f"[{datetime.datetime.now()}] Conexion a PostgreSQL establecida.")
                break
        except OperationalError:
            print(f"[{datetime.datetime.now()}] Esperando a PostgreSQL (reintento en 5s)...")
            time.sleep(5)
            
    return engine

def fetch_and_store_prices(ticker_symbol, engine):
    print(f"[{datetime.datetime.now()}] Descargando precios para {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="5d")
    
    if hist.empty:
        print(f"[{datetime.datetime.now()}] Advertencia: Sin precios para {ticker_symbol}")
        return
    
    hist.reset_index(inplace=True)
    hist.columns = [c.lower().replace(' ', '_') for c in hist.columns]
    hist['ticker'] = ticker_symbol
    
    try:
        hist.to_sql(name='daily_prices', con=engine, if_exists='append', index=False)
        print(f"[{datetime.datetime.now()}] Precios de {ticker_symbol} guardados.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error guardando precios: {e}")

def fetch_and_store_news(ticker_symbol, engine):
    print(f"[{datetime.datetime.now()}] Descargando noticias para {ticker_symbol}...")
    # URL del feed RSS gratuito de Yahoo Finance
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker_symbol}&region=US&lang=en-US"
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        print(f"[{datetime.datetime.now()}] Advertencia: Sin noticias para {ticker_symbol}")
        return
        
    news_data = []
    # Tomamos solo las 5 noticias mas recientes para no saturar a la IA despues
    for entry in feed.entries[:5]:
        news_data.append({
            'ticker': ticker_symbol,
            'title': entry.title,
            'summary': entry.summary if 'summary' in entry else '',
            'published_at': entry.published,
            'link': entry.link,
            'ingested_at': datetime.datetime.now()
        })
        
    df_news = pd.DataFrame(news_data)
    
    try:
        df_news.to_sql(name='daily_news', con=engine, if_exists='append', index=False)
        print(f"[{datetime.datetime.now()}] Noticias de {ticker_symbol} guardadas ({len(news_data)} articulos).")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error guardando noticias: {e}")

def main():
    print(f"[{datetime.datetime.now()}] Servicio de Ingestion de Datos Iniciado.")
    
    engine = get_db_engine()
    tickers_a_monitorear = ["SPY", "AAPL"]
    
    for ticker in tickers_a_monitorear:
        print("-" * 40)
        fetch_and_store_prices(ticker, engine)
        time.sleep(1) # Pausa ligera
        fetch_and_store_news(ticker, engine)
        time.sleep(2) 
    
    while True:
        print(f"[{datetime.datetime.now()}] Ciclo completado. El microservicio entra en espera...")
        time.sleep(3600)

if __name__ == "__main__":
    main()