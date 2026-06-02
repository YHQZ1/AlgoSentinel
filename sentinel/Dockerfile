FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the sentinel code
COPY . .

# Run the AI Sentinel
CMD ["python", "main.py"]