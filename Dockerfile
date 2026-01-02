# 1. Python 3.10 tabanlı hafif bir imaj kullanıyoruz
FROM python:3.10-slim

# 2. Uygulama klasörünü oluştur
WORKDIR /app

# 3. OpenCV'nin Linux sunucularda çalışması için gerekli sistem paketlerini kur
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Önce sadece gereksinimleri kopyala ve kur (Hızlı build için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kalan tüm dosyaları (main.py vb.) kopyala
COPY . .

# 6. Uygulamanın çalışacağı portu belirt
EXPOSE 8000

# 7. Uygulamayı başlat (Render gibi platformlar için host 0.0.0.0 olmalı)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]