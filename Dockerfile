FROM python:3.13-slim

# Install system dependencies required by Playwright browsers
# (Chromium, Firefox, WebKit)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcups2 \
    libglib2.0-0 \
    libgio-2.0-0 \
    libgobject-2.0-0 \
    libdrm2 \
    libnss3 \
    libexpat1 \
    libnssutil3 \
    libxcb1 \
    libsmime3 \
    libxkbcommon0 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libatk-bridge2.0-0 \
    # Additional dependencies commonly needed by Playwright
    libfontconfig1 \
    libfreetype6 \
    ca-certificates \
    fonts-liberation \
    wget \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and their dependencies
RUN playwright install chromium firefox webkit

# Copy application code
COPY . .

CMD ["python", "main.py"]
