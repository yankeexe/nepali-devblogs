# ── Stage 1: Build ────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything needed to build
COPY README.md       .
COPY scripts/        ./scripts/

# Run the build — outputs index.html at /app/index.html
RUN python scripts/build.py


# ── Stage 2: Serve ────────────────────────────────────────────────────────
FROM nginx:alpine AS server

# Copy the built site into nginx's web root
COPY --from=builder /app/index.html /usr/share/nginx/html/index.html

EXPOSE 80

# Healthcheck so you know when it's ready
HEALTHCHECK --interval=5s --timeout=3s \
  CMD wget -qO- http://localhost/ || exit 1
