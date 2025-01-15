#!/bin/bash

# Mettre à jour les paquets
apt-get update && apt-get install -y \
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
    libsecret-1-0

# Installer les dépendances de Playwright
npx playwright install-deps
