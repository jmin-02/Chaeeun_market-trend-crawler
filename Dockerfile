FROM python:3.11-slim-bookworm

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY market_trend_crawler/ market_trend_crawler/
COPY main.py .

CMD ["python", "main.py"]
