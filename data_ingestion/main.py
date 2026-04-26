import time
import datetime
import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Obtenemos la URL de la base de datos desde el docker-compose
DB_URL = os.getenv("DB_URL", "postgresql://admin:adminpassword@localhost:5432/trading_db")

def get_db_engine():
    print(f"[{datetime.datetime.now()}] Iniciando motor de base de datos...")
    engine = create_engine(DB_URL)
    
    # Reintento de conexion: el contenedor de Python puede levantar mas rapido que el de Postgres
    while True:
        try:
            with engine.connect() as conn:
                print(f"[{datetime.datetime.now()}] Conexion a PostgreSQL establecida exitosamente.")
                break
        except OperationalError:
            print(f"[{datetime.datetime.now()}] Esperando a que PostgreSQL inicie (reintento en 5s)...")
            time.sleep(5)
            
    return engine

def fetch_and_store_daily_data(ticker_symbol, engine):
    print(f"[{datetime.datetime.now()}] Descargando datos para {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="5d")
    
    if hist.empty:
        print(f"[{datetime.datetime.now()}] Advertencia: No se encontraron datos para {ticker_symbol}")
        return
    
    # Limpiamos los datos para la base de datos relacional
    hist.reset_index(inplace=True) # Convierte el indice de fecha en una columna
    hist.columns = [c.lower().replace(' ', '_') for c in hist.columns] # Nombres en minusculas
    hist['ticker'] = ticker_symbol # Agregamos una columna para saber de que accion es el precio
    
    # Volcamos los datos a PostgreSQL
    try:
        # if_exists='append' inserta los datos nuevos al final de la tabla
        # index=False evita que se cree una columna de indice numerico innecesaria
        hist.to_sql(name='daily_prices', con=engine, if_exists='append', index=False)
        print(f"[{datetime.datetime.now()}] Datos de {ticker_symbol} guardados en PostgreSQL.")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error guardando en base de datos: {e}")

def main():
    print(f"[{datetime.datetime.now()}] Servicio de Ingestion de Datos Iniciado.")
    
    engine = get_db_engine()
    tickers_a_monitorear = ["SPY", "AAPL"]
    
    for ticker in tickers_a_monitorear:
        fetch_and_store_daily_data(ticker, engine)
        time.sleep(2) 
    
    while True:
        print(f"[{datetime.datetime.now()}] Ciclo completado. El microservicio entra en espera...")
        time.sleep(3600)

if __name__ == "__main__":
    main()