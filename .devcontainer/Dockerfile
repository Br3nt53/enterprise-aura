FROM ghcr.io/astral-sh/uv:python3.11-bookworm

# Install mongosh (MongoDB shell client)
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -qO - https://pgp.mongodb.com/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg && \
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update && \
    apt-get install -y mongodb-mongosh && \
    rm -rf /var/lib/apt/lists/*

CMD ["sleep", "infinity"]
