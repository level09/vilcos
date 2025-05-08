FROM caddy:2-alpine

WORKDIR /app

# Copy the Caddyfile
COPY docker-deploy/Caddyfile /etc/caddy/Caddyfile

# Copy the static website files - keep structure simple
COPY dist/templates/index.html /srv/index.html
COPY dist/assets/ /srv/assets/

# Make sure files are readable by Caddy
RUN chmod -R 755 /srv

# Expose port 80
EXPOSE 80

# Caddy runs as a non-root user by default 