# Dockerfile — Render-friendly, installs Google Chrome
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system deps and add Google Chrome repo
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    curl \
    unzip \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Working dir and copy code
WORKDIR /app
COPY . .

# Upgrade pip then install python deps
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Environment variables used by our code
ENV CHROME_BIN=/usr/bin/google-chrome

EXPOSE 8501

# Run streamlit
CMD ["streamlit", "run", "streamlit_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
