FROM python:3.11-slim

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libenchant-2-2 \
    libgtk-3-0 \
    libxshmfence1 \
    libgbm1 \
    libxtst6 \
    libpci3 \
    libgdk-pixbuf2.0-0 \
    libegl1 \
    libgl1-mesa-glx \
    libdrm2 \
    libxinerama1 \
    libxkbcommon0 \
    libsecret-1-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installer les navigateurs Playwright
RUN pip install playwright && playwright install

# Copier votre application
WORKDIR /app
COPY . /app

# Installer les dépendances Python
RUN pip install -r requirements.txt

# Lancer votre application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
