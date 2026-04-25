# AutoAgent-TW Dockerfile (Phase 129: Headless CI/CD)
# Standardized execution environment for GitHub Actions / GitLab CI

# Stage 1: Build
FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
# Note: We filter out Windows-only dependencies during headless install
COPY requirements.txt .
RUN grep -vE "pywinauto|pyautogui|mss" requirements.txt > requirements_headless.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements_headless.txt

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Install runtime utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Set environment variables
ENV AA_HEADLESS=1
ENV AA_MAX_LOOPS=3
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default entrypoint
ENTRYPOINT ["python", "-m", "src.harness.cli.main", "--headless"]
CMD ["doctor"]
