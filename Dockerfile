# Utiliser une image Python légère comme base
FROM python:3.9-slim

# Installer les dépendances système nécessaires pour Google Chrome et Selenium
RUN apt-get update && apt-get install -y \
    wget unzip curl libglib2.0-0 libnss3 libnspr4 libxss1 libappindicator3-1 fonts-liberation \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 libasound2 libpangocairo-1.0-0 \
    libgbm1 libgtk-3-0 && apt-get clean

# Télécharger et installer Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install

# Télécharger et installer Chromedriver correspondant à la version de Chrome
RUN CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+") \
    && CHROMEDRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) \
    && wget -q https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver

# Copier les fichiers de votre application dans le conteneur
WORKDIR /app
COPY . .

# Installer les dépendances Python (Selenium et autres)
RUN pip install --no-cache-dir -r requirements.txt

# Définir la commande par défaut
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
