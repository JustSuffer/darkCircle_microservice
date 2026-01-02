# 1. Python imajı
FROM python:3.10-slim

# 2. Çalışma dizini
WORKDIR /app

# 3. Güncellenmiş sistem paketleri (Hata veren paketler düzeltildi)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Gereksinimleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kodları kopyala
COPY . .

# 6. Port ve Başlatma
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]