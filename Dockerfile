FROM python:3.13-bookworm

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers along with all required system dependencies
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

CMD ["python", "main.py"]
