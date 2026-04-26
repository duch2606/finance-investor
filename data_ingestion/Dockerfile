FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de los archivos
COPY . .

# Usamos -u para que los prints salgan directo en la consola de Docker
CMD ["python", "-u", "main.py"]