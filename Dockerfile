FROM python:3.11-slim

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Create www-data home and drop the flag
RUN mkdir -p /home/www-data && \
    echo "ByteVault{SSTI_t0_RCE_1s_cl4ssic_n0?}" > /home/www-data/user.txt && \
    chmod 644 /home/www-data/user.txt

RUN useradd -m -d /home/www-data www-data 2>/dev/null || true
USER www-data

ENV FLAG_USER="ByteVault{SSTI_t0_RCE_1s_cl4ssic_n0?}"
EXPOSE 5000
CMD ["python", "app.py"]
