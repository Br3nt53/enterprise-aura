# Dockerfile.v2
# Build stage
FROM python:3.11-slim as builder
WORKDIR /build
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry export -f requirements.txt > requirements.txt

# Development stage
FROM python:3.11-slim as development
WORKDIR /app
COPY --from=builder /build/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV AURA_ENV=development
CMD ["python", "-m", "aura_v2.main"]

# Test stage
FROM development as test
RUN pip install pytest pytest-asyncio pytest-cov
COPY tests/ tests/
RUN pytest tests/

# Production stage
FROM python:3.11-slim as production
WORKDIR /app
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY aura_v2/ aura_v2/
COPY config/ config/
ENV AURA_ENV=production
CMD ["python", "-m", "aura_v2.main"]