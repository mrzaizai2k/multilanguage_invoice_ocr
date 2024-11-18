FROM nginx:latest

# Create directories for both configurations
RUN mkdir -p /etc/nginx/dev /etc/nginx/prod

# Copy configuration files for both environments
COPY dev/nginx.conf.template /etc/nginx/dev/
COPY prod/nginx.conf.template /etc/nginx/prod/

# Copy the startup script into the container
COPY start-nginx.sh /start-nginx.sh

# Set execute permission on the startup script
RUN chmod +x /start-nginx.sh

# Use the startup script to replace the default entrypoint
ENTRYPOINT ["/start-nginx.sh"]