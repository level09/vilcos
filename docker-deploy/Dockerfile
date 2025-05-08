# Multi-stage Dockerfile for Vilcos
# Production-ready static website build

# Stage 1: Build the static website
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files for better caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy configuration files
COPY vite.config.js tailwind.config.js postcss.config.js ./

# Copy the default templates for building
COPY assets/ ./assets/

# Create templates directory structure
RUN mkdir -p templates/src

# Copy default templates to the templates directory
RUN cp assets/default-templates/index.html templates/ && \
    cp -r assets/default-templates/src/* templates/src/

# Build the static site
RUN npm run build

# Stage 2: Serve the website with Caddy (minimal image)
FROM caddy:2-alpine AS deploy

WORKDIR /srv

# Copy the Caddyfile
COPY docker-deploy/Caddyfile /etc/caddy/Caddyfile

# Copy the built static files from builder stage
COPY --from=builder /app/templates/dist/index.html /srv/
COPY --from=builder /app/templates/dist/assets/ /srv/assets/

# Set proper permissions
RUN chmod -R 755 /srv

# Expose HTTP port
EXPOSE 80

# Caddy uses a non-root user by default 